import requests
import os
import subprocess


def get_woot():
    domain = os.getenv("WOOT_DOMAIN", "chatwoot.testrun.org")
    token = os.getenv("WOOT_PROFILE_ACCESS_TOKEN", None)
    if not token:
        try:
            token = get_pass("delta/chatwoot.testrun.org/profile_access_token")
        except NotADirectoryError:
            # pass is not installed, ignore
            pass
        except subprocess.CalledProcessError:
            # password is not saved in pass, ignore
            pass
        if not token:
            raise Exception("You have to set the WOOT_PROFILE_ACCESS_TOKEN environment variable")
    account_id = int(os.getenv("WOOT_ACCOUNT_ID", "1"))
    inbox_id = int(os.getenv("WOOT_INBOX_ID", "4"))
    return Woot(domain, token, account_id, inbox_id)


class Woot:
    def __init__(self, domain: str, token: str, account_id: int, inbox_id: int):
        self.baseurl = f"https://{domain}/api/v1"
        self.account_id = account_id
        self.inbox_id = inbox_id
        self.headers = dict(api_access_token=token)

    def create_contact_if_not_exists(self, email: str, name: str = None):
        contact = self.get_contact(email)
        if not contact:
            if not name:
                name = email
            contact = self.create_contact(email, name)
        return contact

    def create_contact(self, email: str, name: str):
        payload = dict(inbox_id=self.inbox_id, email=email, name=name)
        url = f"{self.baseurl}/accounts/{self.account_id}/contacts"
        r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()
        return r.json()["payload"]["contact"]

    def get_contact(self, email: str) -> list:
        url = f"{self.baseurl}/accounts/{self.account_id}/contacts/search"
        payload = dict(q=email, sort='email')
        r = requests.get(url, json=payload, headers=self.headers)
        r.raise_for_status()
        for contact in r.json()['payload']:
            if contact['email'] == email:
                return contact

    def create_conversation_if_not_exists(self, contact: dict) -> dict:
        try:
            conversation = self.get_conversations(contact)[0]
        except IndexError:
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
        return r.json()['payload']

    def get_source_id_from_contact(self, contact):
        contact_inboxes = contact["contact_inboxes"]
        assert len(contact_inboxes) == 1
        contact_inbox = contact_inboxes[0]
        return contact_inbox["source_id"]

    def get_messages(self, conversation: dict) -> list:
        payload = dict(
            inbox_id=self.inbox_id
        )
        url = f"{self.baseurl}/accounts/{self.account_id}/conversations/{conversation['id']}/messages"
        r = requests.get(url, json=payload, headers=self.headers)
        r.raise_for_status()
        return r.json()['payload']

    def send_message(self, conversation, content, message_type='incoming'):
        # send a message
        payload = dict(
            content=content,
            message_type=message_type,
        )
        url = f"{self.baseurl}/accounts/{self.account_id}/conversations/{conversation['id']}/messages"
        r = requests.post(url, json=payload, headers=self.headers)
        r.raise_for_status()


def get_pass(filename: str) -> str:
    """Get the data from the password manager."""
    r = subprocess.run(["pass", "show", filename], capture_output=True, check=True)
    return r.stdout.decode('utf-8').strip()


if __name__ == "__main__":
    w = get_woot()
    for contact in w.get_contact():
        print("Sending message to", contact['email'])
        conv = w.create_conversation_if_not_exists(contact)
        w.send_message(conv, "testing woot")
