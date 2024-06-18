#!/usr/bin/env python3
"""Advanced echo bot example.

it will echo back any message that has non-empty text and also supports the /help command.
"""
import logging
import os
import string
import sys
import random
import secrets

from deltachat_rpc_client import Bot, DeltaChat, EventType, Rpc, events

from woot import get_woot

hooks = events.HookCollection()


@hooks.on(events.RawEvent)
def log_event(event):
    if event.kind == EventType.INFO:
        logging.info(event.msg)
    elif event.kind == EventType.WARNING:
        logging.warning(event.msg)


@hooks.on(events.RawEvent(EventType.ERROR))
def log_error(event):
    logging.error(event.msg)


@hooks.on(events.MemberListChanged)
def on_memberlist_changed(event):
    logging.info(
        "member %s was %s", event.member, "added" if event.member_added else "removed"
    )


@hooks.on(events.GroupImageChanged)
def on_group_image_changed(event):
    logging.info("group image %s", "deleted" if event.image_deleted else "changed")


@hooks.on(events.GroupNameChanged)
def on_group_name_changed(event):
    logging.info("group name changed, old name: %s", event.old_name)


@hooks.on(events.NewMessage(func=lambda e: not e.command))
def pass_delta_to_woot(event):
    snapshot = event.message_snapshot
    woot = snapshot.account.woot
    if snapshot.text or snapshot.file:
        woot_contact = woot.create_contact()
        source_id = woot.get_source_id_from_contact(woot_contact)
        woot_conv = woot.create_conversation(source_id)
        woot.send_message(woot_conv, snapshot.text)


@hooks.on(events.NewMessage(command="/help"))
def help_command(event):
    snapshot = event.message_snapshot
    snapshot.chat.send_text("Send me any message and I will echo it back")


def main():
    path = os.environ.get("PATH")
    venv_path = sys.argv[0].strip("echobot")
    os.environ["PATH"] = path + ":" + venv_path
    with Rpc() as rpc:
        deltachat = DeltaChat(rpc)
        system_info = deltachat.get_system_info()
        logging.info("Running deltachat core %s", system_info.deltachat_core_version)

        accounts = deltachat.get_all_accounts()
        account = accounts[0] if accounts else deltachat.add_account()

        bot = Bot(account, hooks)
        bot.account.woot = get_woot()

        if not bot.is_configured():
            user = "".join(random.choices(string.ascii_lowercase, k=9)) + "@nine.testrun.org"
            password = "".join(
                secrets.choice(string.ascii_lowercase)
                for _ in range(20)
            )
            bot.configure(user, password)
        bot.run_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
