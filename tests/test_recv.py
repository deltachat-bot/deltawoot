import os

import pytest
from deltachat_rpc_client.pytestplugin import get_temp_credentials, acfactory
from deltachat_rpc_client import Rpc, AttrDict
from deltachat_rpc_client.rpc import JsonRpcError

from deltawoot.recv import (
    get_bot, get_config_from_env, configure_bot, pass_delta_to_woot,
    DEFAULT_AVATAR_PATH, DEFAULT_LEAVE_MSG, DEFAULT_HELP_MSG
)
from deltawoot.send import download_file


def test_dont_pass_info_messages(acfactory):
    bot, user = acfactory.get_online_accounts(2)
    joincode = bot.get_qr_code()
    chat = user.secure_join(joincode)
    info_msg = chat.get_messages()[-1]
    event = AttrDict(command="", payload="", message_snapshot=info_msg.get_snapshot())
    assert not pass_delta_to_woot(event)


def test_config_options(bot_addr, monkeypatch, tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)

    monkeypatch.delenv('DELTAWOOT_AVATAR', raising=False)
    monkeypatch.delenv('DELTAWOOT_LEAVE_MSG', raising=False)
    monkeypatch.delenv('DELTAWOOT_HELP_MSG', raising=False)
    monkeypatch.delenv('DELTAWOOT_ADDR', raising=False)
    monkeypatch.delenv('DELTAWOOT_PASSWORD', raising=False)
    monkeypatch.delenv('DELTAWOOT_NAME', raising=False)

    with Rpc() as rpc:
        bot = get_bot(rpc)

        config = get_config_from_env(bot_addr)
        with pytest.raises(JsonRpcError, match="Missing email address."):
            configure_bot(bot, config)

        assert not config.get('user') or bot.account.get_config('addr')
        assert not config.get('password') or bot.account.get_config('mail_pw')
        assert config.get('displayname') == bot_addr
        assert config.get('avatar_path') == DEFAULT_AVATAR_PATH
        assert config.get('leave_msg') == DEFAULT_LEAVE_MSG
        assert config.get('help_msg') == DEFAULT_HELP_MSG % (bot_addr,)

        new_display_name = "Soo friendly"
        new_avatar_path = download_file("https://delta.chat/assets/blog/green-check-chain.png")
        new_leave_msg = "Извините, но вы должны связаться со мной 1:1. Отправьте /help мне, чтобы узнать больше."
        new_help_msg = "Привет :) Я из службы поддержки, чем могу помочь?"
        monkeypatch.setenv('DELTAWOOT_AVATAR', new_avatar_path)
        monkeypatch.setenv('DELTAWOOT_LEAVE_MSG', new_leave_msg)
        monkeypatch.setenv('DELTAWOOT_HELP_MSG', new_help_msg)
        monkeypatch.setenv('DELTAWOOT_NAME', new_display_name)
        creds = get_temp_credentials()
        monkeypatch.setenv('DELTAWOOT_ADDR', creds['email'])
        monkeypatch.setenv('DELTAWOOT_PASSWORD', creds['password'])

        config = get_config_from_env(bot_addr)
        configure_bot(bot, config)

        assert config.get('user') == creds['email'] == bot.account.get_config('addr')
        assert config.get('password') == creds['password'] == bot.account.get_config('mail_pw')
        assert config.get('displayname') == new_display_name == bot.account.get_config('displayname')
        assert config.get('avatar_path') == new_avatar_path
        assert config.get('leave_msg') == new_leave_msg
        assert config.get('help_msg') == new_help_msg

        final_display_name = "Even friendlier"
        monkeypatch.setenv('DELTAWOOT_AVATAR', DEFAULT_AVATAR_PATH)
        monkeypatch.setenv('DELTAWOOT_NAME', final_display_name)

        config = get_config_from_env(bot.account.get_config('addr'))
        configure_bot(bot, config)

        assert config.get('displayname') == final_display_name == bot.account.get_config('displayname')
        assert config.get('avatar_path') == DEFAULT_AVATAR_PATH
