import logging
import os
import sys
import threading

from deltachat_rpc_client import Bot, DeltaChat, EventType, Rpc, events
from deltachat_rpc_client.const import ChatType

from deltawoot.woot import get_woot
from deltawoot.send import create_app

hooks = events.HookCollection()


DEFAULT_LEAVE_MSG = "Sorry, but you have to message me 1:1. Send /help to me to learn more."
DEFAULT_HELP_MSG = "Hi :) I am the helpdesk for %s, what can I do for you?"
DEFAULT_AVATAR_PATH = os.path.join(os.getcwd(), "src", "deltawoot", "avatar.jpg")


@hooks.on(events.RawEvent)
def log_event(event):
    if event.kind == EventType.INFO:
        logging.info(event.msg)
    elif event.kind == EventType.WARNING:
        logging.warning(event.msg)
    if event.kind == EventType.SECUREJOIN_INVITER_PROGRESS:
        if event.progress == 1000:
            contact = event.account.create_contact(event.contact_id)
            chat = contact.create_chat()
            chat.send_text(event.account.deltawoot_config.get('help_msg'))


@hooks.on(events.RawEvent(EventType.ERROR))
def log_error(event):
    logging.error(event.msg)


@hooks.on(events.NewMessage(func=lambda e: not e.command))
def pass_delta_to_woot(event):
    snapshot = event.message_snapshot
    if snapshot.chat.get_basic_snapshot().chat_type == ChatType.GROUP:
        """The bot doesn't want to be in any group and will leave it."""
        dm = snapshot.sender.create_chat()
        dm.send_message(get_leave_msg(), quoted_msg=event.message_snapshot.id)
        snapshot.chat.leave()
        return

    if snapshot.is_info:
        logging.info("Not forwarding info message to chatwoot:", snapshot.id)
        return

    woot = snapshot.chat.account.woot
    sender = snapshot.sender.get_snapshot()
    woot_contact = woot.create_contact_if_not_exists(
        sender.address,
        sender.display_name,
    )
    woot_conv = woot.create_conversation_if_not_exists(woot_contact)
    file_type = snapshot.get('view_type').lower()
    if file_type == "voice" or file_type == "audio":
        file_type = "audio/" + snapshot.get('file').split(".")[-1]
    woot.send_message(
        woot_conv,
        snapshot.text,
        filename=snapshot.get('file'),
        mime_type=file_type,
    )


@hooks.on(events.NewMessage(command="/help"))
def help_command(event):
    snapshot = event.message_snapshot
    snapshot.chat.send_text(snapshot.chat.account.deltawoot_config.get('help_msg'))


def get_leave_msg():
    return os.getenv("DELTAWOOT_LEAVE_MSG", DEFAULT_LEAVE_MSG)


def get_config_from_env(addr: str) -> dict:
    displayname = os.getenv("DELTAWOOT_NAME", addr)
    help_msg = DEFAULT_HELP_MSG % (displayname, )

    return dict(
        user=os.getenv("DELTAWOOT_ADDR"),
        password=os.getenv("DELTAWOOT_PASSWORD"),
        displayname=displayname,
        avatar_path=os.getenv("DELTAWOOT_AVATAR", DEFAULT_AVATAR_PATH),
        help_msg=os.getenv("DELTAWOOT_HELP_MSG", help_msg),
        leave_msg=get_leave_msg(),
    )


def configure_bot(bot, config):
    user = config.get('user')
    password = config.get('password')
    bot.configure(user, password)

    bot.account.set_config('displayname', config.get('displayname'))
    bot.account.set_avatar(config.get('avatar_path'))
    bot.account.deltawoot_config = config
    return bot


def get_flaskthread(bot):
    flaskapp = create_app(bot.account)
    return threading.Thread(
        target=lambda: flaskapp.run(
            host='0.0.0.0',
            port='5000',
            debug=True,
            use_reloader=False,
        ),
        daemon=True,
    )


def get_bot(rpc):
    deltachat = DeltaChat(rpc)
    try:
        account = deltachat.get_all_accounts()[0]
    except IndexError:
        account = deltachat.add_account()
    return Bot(account, hooks)


def main():
    logging.basicConfig(level=logging.INFO)
    path = os.environ.get("PATH")
    venv_path = sys.argv[0].strip("echobot")
    os.environ["PATH"] = path + ":" + venv_path
    with Rpc() as rpc:
        bot = get_bot(rpc)

        config = get_config_from_env(bot.account.get_config('addr'))
        bot = configure_bot(bot, config)

        bot.account.woot = get_woot(inbox_id=bot.account.get_config('ui.woot_inbox_id'))
        bot.account.set_config('ui.woot_inbox_id', str(bot.account.woot.inbox_id))

        joincode = bot.account.get_qr_code()
        print("You can publish this invite code to your users: " + joincode, file=sys.stderr)

        flaskthread = get_flaskthread(bot)
        flaskthread.start()
        bot.run_forever()
    flaskthread.join()


if __name__ == "__main__":
    main()
