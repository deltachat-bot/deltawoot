from pprint import pprint
import requests
import os

url = "https://chatwoot.testrun.org"

account_id = 1

# https://chatwoot.testrun.org/app/accounts/1/profile/settings (scroll to bottom)
profile_access_token = os.getenv("PROFILE_ACCESS_TOKEN", None)
if not profile_access_token:
    raise Exception("You have to set the PROFILE_ACCESS_TOKEN environment variable")

# according to https://www.chatwoot.com/developers/api/#tag/Contacts/operation/contactCreate
headers = dict(api_access_token=profile_access_token)


def create_contact(inbox_id=4):
    # create a contact
    payload = dict(inbox_id=4)
    r = requests.post(f"{url}/api/v1/accounts/{account_id}/contacts", json=payload, headers=headers)
    r.raise_for_status()

    d=r.json()
    pprint(d)
    return d["payload"]["contact"]


def get_source_id_from_contact(contact):
    contact_inboxes = contact["contact_inboxes"]
    assert len(contact_inboxes) == 1
    contact_inbox = contact_inboxes[0]
    return contact_inbox["source_id"]


# create a conversation

def create_conversation(source_id, inbox_id=4):
    payload = dict(
        source_id=source_id,
        inbox_id=inbox_id,
    )

    r = requests.post(f"{url}/api/v1/accounts/{account_id}/conversations",
                      json=payload, headers=headers)
    r.raise_for_status()

    conversation_id = r.json()["id"]
    return conversation_id


def get_messages(conversation_id):
    r = requests.get(f"{url}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages",
                      headers=headers)
    r.raise_for_status()
    return r.json()


def send_message(conversation_id, content):
    # send a message
    payload = dict(
        content=content,
        message_type="incoming",
    )
    r = requests.post(f"{url}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages",
                      json=payload, headers=headers)
    r.raise_for_status()


if __name__ == "__main__":
    contact = create_contact()
    source_id = get_source_id_from_contact(contact)
    conversation_id = create_conversation(source_id)

    print(f"starting conversation {conversation_id}")

    import time

    while 1:
        s = input("your-question: ")
        send_message(conversation_id, s)

        num_messages = len(get_messages(conversation_id)["payload"])
        while 1:
            time.sleep(1)
            messages = get_messages(conversation_id)["payload"]
            if len(messages) > num_messages:
                for msg in messages[num_messages:]:
                    print("---> ", msg["content"])
                num_messages = len(messages)
                break

    import pdb ; pdb.set_trace()

