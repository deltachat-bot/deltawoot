import pytest
import os
import random
import string
import time
from pprint import pprint

from deltawoot.recv import get_leave_msg, DEFAULT_AVATAR_PATH
from deltachat_rpc_client.const import ChatType


@pytest.mark.timeout(25)
def test_send_message(delta, woot, lp):
    text = "".join(random.choices(string.ascii_lowercase, k=9))

    lp.sec(f"Sending message '{text}' with Delta Chat")
    dcontact = delta.create_contact(woot.addr)
    dchat = dcontact.create_chat()
    dmsg = dchat.send_message(text, file=DEFAULT_AVATAR_PATH)

    wcontact = None
    while not wcontact:
        wcontact = woot.get_contact(delta.get_config('addr'))
        time.sleep(1)  # let's avoid rate limits
    wconversations = []
    while not wconversations:
        wconversations = woot.get_conversations(wcontact)
        time.sleep(1)  # let's avoid rate limits
    wconversation = wconversations[0]

    lp.sec("Polling for new messages in Chatwoot")
    while len(woot.get_messages(wconversation)) < 2:
        lp.sec("printing contact")
        pprint(woot.create_contact_if_not_exists(delta.get_config('addr'), delta.get_config('displayname')))
        lp.sec("printing conversation")
        pprint(woot.create_conversation_if_not_exists(wcontact))
        lp.sec("printing messages")
        pprint(woot.get_messages(wconversation))
        time.sleep(10)

    msg1 = woot.get_messages(wconversation)[-1]

    assert msg1['content'] == text
    assert msg1['attachments'][0]['file_size'] == os.path.getsize(DEFAULT_AVATAR_PATH)

    lp.sec("Responding in Chatwoot")
    text2 = "".join(random.choices(string.ascii_lowercase, k=9))
    woot.send_message(
        conversation=wconversation,
        content=text2,
        message_type='outgoing',
        filename=DEFAULT_AVATAR_PATH,
        mime_type=dmsg.get_snapshot().get('view_type').lower()
    )

    lp.sec("Waiting for new messages in Delta")
    msg2 = delta.wait_for_incoming_msg().get_snapshot()
    lp.sec("First message arrived in Delta")
    assert msg2.text == text2
    msg3 = delta.wait_for_incoming_msg().get_snapshot()
    lp.sec("Second message arrived in Delta")
    assert os.path.getsize(msg3.file) == os.path.getsize(DEFAULT_AVATAR_PATH)


@pytest.mark.timeout(30)
def test_leave_groups(delta, woot, lp):
    lp.sec("Creating Group")
    dgroup = delta.create_group("You don't want to be in here")

    lp.sec("Adding bot to it")
    dcontact = delta.create_contact(woot.addr)
    dgroup.add_contact(dcontact)
    snapshot = dgroup.get_basic_snapshot()
    assert snapshot.chat_type == ChatType.GROUP
    lp.sec("Send message to group to create it")
    dgroup.send_text("Hello, welcome to our group!")

    lp.sec("Waiting for reply")
    reply = delta.wait_for_incoming_msg().get_snapshot()
    assert reply.text == get_leave_msg()
    assert reply.quote
    assert reply.chat != dgroup
    delta.wait_for_incoming_msg()
    assert len(dgroup.get_contacts()) == 1

    assert not woot.get_contact(delta.get_config('addr'))
