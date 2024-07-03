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
import threading

from deltachat_rpc_client import Bot, DeltaChat, EventType, Rpc, events

from woot import get_woot
from send import create_app

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


@hooks.on(events.NewMessage(func=lambda e: not e.command))
def pass_delta_to_woot(event):
    snapshot = event.message_snapshot
    woot = snapshot.chat.account.woot
    if snapshot.text:
        sender = snapshot.sender.get_snapshot()
        logging.info(str(sender))
        woot_contact = woot.create_contact_if_not_exists(
            sender.address,
            sender.display_name,
        )
        woot_conv = woot.create_conversation_if_not_exists(woot_contact)
        woot.send_message(woot_conv, snapshot.text)


@hooks.on(events.NewMessage(command="/help"))
def help_command(event):
    snapshot = event.message_snapshot
    name = snapshot.chat.account.get_config('displayname')
    snapshot.chat.send_text(f"Hi :) I am the helpdesk for {name}, what can I do for you?")


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
            bot.account.set_config('displayname', user)

        flask = create_app(bot.account)
        flaskthread = threading.Thread(
            target=lambda: flask.run(
                host='0.0.0.0',
                port='5000',
                debug=True,
                use_reloader=False,
            )
        )
        flaskthread.start()
        bot.run_forever()
    flaskthread.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()