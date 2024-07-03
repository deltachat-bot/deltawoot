import deltachat_rpc_client
from flask import Flask, request


def create_app(ac: deltachat_rpc_client.Account):
    app = Flask("deltawoot-webhook")

    @app.post("/")
    def pass_woot_to_delta():
        email = request.json['conversation']['meta']['sender']['email']
        if request.json['conversation']['messages'][0]['sender'].get('email') != email:
            text = request.json['conversation']['messages'][0]['processed_message_content']
            chat = ac.create_contact(email).create_chat()
            chat.send_text(text)
            return "successfully delivered"
        return "message was from outside contact"

    return app
