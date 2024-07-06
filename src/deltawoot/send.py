import deltachat_rpc_client
from flask import Flask, request
import requests
from pprint import pprint


def create_app(ac: deltachat_rpc_client.Account):
    app = Flask("deltawoot-webhook")

    @app.post("/")
    def pass_woot_to_delta():
        email = request.json['conversation']['meta']['sender']['email']
        message = request.json['conversation']['messages'][0]
        pprint(message)
        if message['sender'].get('email') != email:
            chat = ac.create_contact(email).create_chat()
            text = message['processed_message_content']
            if text:
                chat.send_text(text)
            for attachment in message.get('attachments', []):
                url = attachment['data_url'].replace('http://', 'https://').replace(':3000/rails', '/rails')
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
    r = requests.get(url, stream=True)
    file_name = url.split("/")[-1]
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return file_name
