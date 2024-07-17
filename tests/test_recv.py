import os

from deltachat_rpc_client.pytestplugin import get_temp_credentials

from deltawoot.recv import get_config_from_env, DEFAULT_AVATAR_PATH, DEFAULT_LEAVE_MSG, DEFAULT_HELP_MSG


def test_config_options(bot_addr, monkeypatch):
    monkeypatch.delenv('DELTAWOOT_AVATAR', raising=False)
    monkeypatch.delenv('DELTAWOOT_LEAVE_MSG', raising=False)
    monkeypatch.delenv('DELTAWOOT_HELP_MSG', raising=False)
    monkeypatch.delenv('DELTAWOOT_ADDR', raising=False)
    monkeypatch.delenv('DELTAWOOT_PASSWORD', raising=False)
    monkeypatch.delenv('DELTAWOOT_NAME', raising=False)

    config = get_config_from_env(bot_addr)

    assert not config.get('user')
    assert not config.get('password')
    assert config.get('displayname') == bot_addr
    assert config.get('avatar_path') == DEFAULT_AVATAR_PATH
    assert config.get('leave_msg') == DEFAULT_LEAVE_MSG
    assert config.get('help_msg') == DEFAULT_HELP_MSG % (bot_addr,)

    new_display_name = "Soo friendly"
    new_avatar_path = "testpath"
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

    assert config.get('user') == creds['email']
    assert config.get('password') == creds['password']
    assert config.get('displayname') == new_display_name
    assert config.get('avatar_path') == new_avatar_path
    assert config.get('leave_msg') == new_leave_msg
    assert config.get('help_msg') == new_help_msg
