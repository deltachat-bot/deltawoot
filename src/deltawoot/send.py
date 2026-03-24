import logging
import os.path
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import deltachat_rpc_client
from flask import Flask, request
import requests

from deltawoot.woot import get_contact_mapping


def create_app(ac: deltachat_rpc_client.Account):
    app = Flask("deltawoot-webhook")

    @app.get("/error")
    def error():
        1 / 0
        return "Testing sentry_sdk"

    @app.post("/")
    def pass_woot_to_delta():
        if not request.json["inbox"]["id"] == ac.woot.inbox_id:
            logging.info("Inbox %s ignoring msg from other Inbox %s" % (ac.woot.inbox_id, request.json["inbox"]["id"]))
            return "ignoring message from other Inbox"
        if not request.json.get("conversation"):
            return "message was from outside contact"
        woot_contact_id = int(request.json["conversation"]["meta"]["sender"]["id"])
        message = request.json["conversation"]["messages"][0]
        if int(message["sender"].get("id")) != woot_contact_id:
            dc_id, _ = get_contact_mapping(ac, woot_id=woot_contact_id)
            chat = ac.get_contact_by_id(dc_id).create_chat()
            text = message["processed_message_content"]
            if text:
                chat.send_text(text)
            for attachment in message.get("attachments", []):
                print(attachment["data_url"], file=sys.stderr)
                url = attachment["data_url"]
                if not os.getenv("WOOT_API_URL"):
                    url = urlparse(url)._replace(netloc="rails:3000", scheme="http").geturl()
                print(url, file=sys.stderr)
                filename = download_file(url)
                chat.send_file(filename)
            return "successfully delivered"
        return "message was from outside contact"

    return app


def download_file(url: str) -> str:
    """Download a file and return the file name.

    :param url: the URL of the file, usually https://chatwoot.testrun.org/rails/active_storage/blobs/...
    :return: the file name of the file on the system.
    """
    user_agent = {"User-Agent": "Deltawoot Bot (https://github.com/deltachat-bot/deltawoot/)"}
    r = requests.get(url, stream=True, headers=user_agent)
    dir_name = os.path.join(os.getcwd(), "files", "attachments")
    Path(dir_name).mkdir(parents=True, exist_ok=True)
    file_name = os.path.join(dir_name, unquote(url.split("/")[-1]))
    with open(file_name, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return file_name
