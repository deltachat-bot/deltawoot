import requests
import os
import subprocess
from pprint import pprint


def get_woot():
    url = os.getenv("WOOT_DOMAIN", "chatwoot.testrun.org")
    token = os.getenv("WOOT_PROFILE_ACCESS_TOKEN", None)
    if not token:
        try:
            token = get_pass("delta/chatwoot.testrun.org/profile_access_token")
        except FileNotFoundError:
            # pass is not installed, ignore
            pass
        except subprocess.CalledProcessError:
            # password is not saved in pass, ignore
            pass
        if not token:
            raise Exception("You have to set the WOOT_PROFILE_ACCESS_TOKEN environment variable")
    account_id = int(os.getenv("WOOT_ACCOUNT_ID", "1"))
    inbox_id = int(os.getenv("WOOT_INBOX_ID", "4"))
    return Woot(url, token, account_id, inbox_id)


class Woot:
    def __init__(self, url: str, token: str, account_id: int, inbox_id: int):
        self.url = url
        self.account_id = account_id
        self.inbox_id = inbox_id
        self.headers = dict(api_access_token=token)

    def create_contact(self):
        payload = dict(inbox_id=self.inbox_id)
        url = f"{self.url}/api/v1/accounts/{self.account_id}/contacts"
        r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()

        d=r.json()
        pprint(d)
        return d["payload"]["contact"]

    def get_source_id_from_contact(self, contact):
        contact_inboxes = contact["contact_inboxes"]
        assert len(contact_inboxes) == 1
        contact_inbox = contact_inboxes[0]
        return contact_inbox["source_id"]

    def create_conversation(self, source_id):
        payload = dict(
            source_id=source_id,
            inbox_id=self.inbox_id,
        )

        url = f"{self.url}/api/v1/accounts/{self.account_id}/conversations"
        r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()

        conversation_id = r.json()["id"]
        return conversation_id

    def get_messages(self, conversation_id):
        url = f"{self.url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def send_message(self, conversation_id, content):
        # send a message
        payload = dict(
            content=content,
            message_type="incoming",
        )
        url = f"{self.url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()


def get_pass(filename: str) -> str:
    """Get the data from the password manager."""
    r = subprocess.run(["pass", "show", filename], capture_output=True, check=True)
    return r.stdout.decode('utf-8').strip()
