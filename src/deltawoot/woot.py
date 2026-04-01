import json
import logging
import os
import requests
import subprocess
import sys
import time
from pprint import pprint

from deltachat_rpc_client import Account


def get_woot(inbox_id=None, inbox_name="Delta Chat"):
    api_url = os.getenv("WOOT_API_URL", "http://rails:3000/api/v1")
    token = os.getenv("WOOT_PROFILE_ACCESS_TOKEN", None)
    if not token:
        try:
            token = get_pass("delta/chatwoot.testrun.org/profile_access_token").strip()
        except NotADirectoryError:
            # pass is not installed, ignore
            pass
        except subprocess.CalledProcessError:
            # password is not saved in pass, ignore
            pass
        if not token:
            raise Exception("You have to set the WOOT_PROFILE_ACCESS_TOKEN environment variable")
    account_id = int(os.getenv("WOOT_ACCOUNT_ID", "1"))
    inbox_id = os.getenv("WOOT_INBOX_ID", inbox_id)
    return Woot(api_url, token, account_id, inbox_id, inbox_name=inbox_name)


class Woot:
    def __init__(self, api_url: str, token: str, account_id: int, inbox_id, inbox_name: str):
        self.baseurl = api_url
        self.account_id = account_id
        self.headers = dict(api_access_token=token)
        try:
            self.inbox_id = int(inbox_id)
        except TypeError:
            self.create_inbox(inbox_name)

    def create_inbox(self, inbox_name):
        """Creates a new API inbox in chatwoot, no agents are added to it so far.
        This only runs if there is
        neither a WOOT_INBOX_ID environment variable specifying the inbox,
        nor a ui.woot_inbox_id deltachat config key from last time.
        """
        payload = dict(
            name=inbox_name,
            channel=dict(
                type="api",
                webhook_url="",
            ),
        )
        url = f"{self.baseurl}/accounts/{self.account_id}/inboxes"
        r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()
        self.inbox_id = r.json()["channel_id"]
        link = self.baseurl[:-6] + f"app/accounts/{self.account_id}/settings/inboxes/{self.inbox_id}"
        logging.info("New chatwoot inbox created for deltawoot, please add agents to it here: %s", link)

    def create_contact_if_not_exists(self, email: str, name: str = None) -> dict:
        """Get a woot contact for a delta contact, create it if necessary.

        :param email: the last seen email address of the contact
        :param name: the display name of the contact
        :return: the chatwoot contact in json format
        """
        try:
            contact = self.search_contact(email)
        except requests.exceptions.HTTPError:
            contact = None
        if not contact:
            if not name:
                name = email
            try:
                contact = self.create_contact(email, name)
            except requests.exceptions.HTTPError:
                time.sleep(5)  # wait a bit for workers to become available
                contact = self.create_contact(email, name)
        return contact

    def create_contact(self, email: str, name: str):
        payload = dict(inbox_id=self.inbox_id, email=email, name=name)
        url = f"{self.baseurl}/accounts/{self.account_id}/contacts"
        r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()
        return r.json()["payload"]["contact"]

    def get_contact(self, woot_contact_id: int) -> dict:
        url = f"{self.baseurl}/accounts/{self.account_id}/contacts/{woot_contact_id}"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()["payload"]

    def search_contact(self, email: str) -> list:
        url = f"{self.baseurl}/accounts/{self.account_id}/contacts/search"
        payload = dict(q=email, sort="email")
        r = requests.get(url, json=payload, headers=self.headers)
        r.raise_for_status()
        for contact in r.json()["payload"]:
            if contact["email"] == email:
                return contact

    def create_conversation_if_not_exists(self, contact: dict) -> dict:
        conversations = self.get_conversations(contact)
        for conversation in conversations:
            for message in conversation.get("messages"):
                if message["inbox_id"] == self.inbox_id:
                    return conversation
        else:
            source_id = self.get_source_id_from_contact(contact)
            payload = dict(
                source_id=source_id,
                inbox_id=self.inbox_id,
            )
            url = f"{self.baseurl}/accounts/{self.account_id}/conversations"
            r = requests.post(url, json=payload, headers=self.headers)
            r.raise_for_status()
            conversation = r.json()
        return conversation

    def get_conversations(self, contact):
        url = f"{self.baseurl}/accounts/{self.account_id}/contacts/{contact['id']}/conversations"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()["payload"]

    def get_source_id_from_contact(self, contact):
        for inbox in contact["contact_inboxes"]:
            if inbox["inbox"]["id"] == self.inbox_id:
                return inbox["source_id"]
        return contact["contact_inboxes"][0]["source_id"]  # if this fails, create conversation in web interface

    def get_messages(self, conversation: dict) -> list:
        payload = dict(inbox_id=self.inbox_id)
        url = f"{self.baseurl}/accounts/{self.account_id}/conversations/{conversation['id']}/messages"
        r = requests.get(url, json=payload, headers=self.headers)
        r.raise_for_status()
        return r.json()["payload"]

    def send_message(self, conversation, content, message_type="incoming", filename=None, mime_type=None):
        url = f"{self.baseurl}/accounts/{self.account_id}/conversations/{conversation['id']}/messages"
        print("mime_type:", mime_type, file=sys.stderr)
        if filename:
            file = {"attachments[]": (filename, open(filename, "rb"), mime_type)}
            data = {
                "content": content,
                "message_type": message_type,
                "file_type": mime_type,
            }
            r = requests.post(url, headers=self.headers, files=file, data=data)
        else:
            payload = {
                "content": content,
                "message_type": message_type,
            }
            r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()


def get_contact_mapping(account: Account, delta_id: int = None, woot_id: int = None) -> (int | None, int | None):
    """For either a Delta Chat contact ID or Chatwoot contact ID, get a contact mapping which involves both.
    If mapping entry doesn't exist yet, create an empty mapping list in the Delta Chat config table.

    :param account: the Delta Chat account object
    :param delta_id: the ID of a Delta Chat contact
    :param woot_id: the ID of a Chatwoot contact
    :return: a tuple with (Delta Chat contact ID, Chatwoot contact ID)
    """
    mappings_json = account.get_config("ui.deltawoot_mappings")
    if mappings_json:
        mappings = json.loads(mappings_json)
        for m in mappings:
            if m[0] == delta_id or m[1] == woot_id:
                return int(m[0]), int(m[1])
    else:
        print("Initializing Delta/Chatwoot contact mappings in the Delta Chat config table")
        account.set_config("ui.deltawoot_mappings", json.dumps([]))
    return None, None


def add_contact_mapping(account: Account, delta_id: int, woot_id: int):
    """Update the Delta/Chatwoot contact mappings with a new mapping."""
    mappings_json = account.get_config("ui.deltawoot_mappings")
    if not mappings_json:
        print("Initializing Delta/Chatwoot contact mappings in the Delta Chat config table")
        mappings = []
    else:
        mappings = json.loads(mappings_json)
    no_chatwoot_contact = get_contact_mapping(account, delta_id=delta_id) == (None, None)
    assert no_chatwoot_contact, f"Chatwoot contact for Delta contact {delta_id} already exists"
    no_delta_contact = get_contact_mapping(account, woot_id=woot_id) == (None, None)
    assert no_delta_contact, f"Delta contact for Chatwoot contact {woot_id} already exists"

    mappings.append((delta_id, woot_id))
    account.set_config("ui.deltawoot_mappings", json.dumps(mappings))


def get_pass(filename: str) -> str:
    """Get the data from the password manager."""
    r = subprocess.run(["pass", "show", filename], capture_output=True, check=True)
    return r.stdout.decode("utf-8").strip()


if __name__ == "__main__":
    w = get_woot()
    for contact in w.create_contact_if_not_exists("nami@systemli.org"):
        print("Sending message to", contact["email"])
        conv = w.create_conversation_if_not_exists(contact)
        for msg in w.get_messages(conv):
            pprint(msg)
            print()
