import os
import pytest
import requests
from deltachat_rpc_client.pytestplugin import acfactory

from deltawoot.woot import get_woot


@pytest.fixture(autouse=True, scope="session")
def _setenv():
    if not os.getenv("CHATMAIL_DOMAIN"):
        # acfactory uses this environment variable
        os.environ["CHATMAIL_DOMAIN"] = "nine.testrun.org"


@pytest.fixture()
def delta(acfactory):
    ac = acfactory.get_online_account()
    ac.set_config('displayname', 'CI account')
    print("Creating Test account", ac.get_config('addr'))
    return ac


@pytest.fixture()
def bot_addr():
    return os.getenv("DELTAWOOT_ADDR", "deltawoot@nine.testrun.org")


@pytest.fixture()
def woot(bot_addr, monkeypatch):
    path = os.getenv('PATH')
    inbox_id = os.getenv('WOOT_INBOX_ID')
    account_id = os.getenv('WOOT_ACCOUNT_ID', '1')
    monkeypatch.setenv('WOOT_API_URL', os.getenv('WOOT_API_URL', 'https://chatwoot.testrun.org/api/v1'))
    monkeypatch.delenv('PATH')  # let's assume pass isn't installed
    monkeypatch.delenv('WOOT_INBOX_ID', raising=False)
    monkeypatch.delenv('WOOT_ACCOUNT_ID', raising=False)
    woot = get_woot(inbox_name="testing")
    assert woot.account_id == 1

    assert woot.inbox_id != inbox_id
    url = f"{woot.baseurl}/accounts/{woot.account_id}/inboxes/{woot.inbox_id}"
    r = requests.get(url, headers=woot.headers)
    assert r.json()['name'] == "testing"
    assert r.json()['channel_type'] == "Channel::Api"

    monkeypatch.setenv('WOOT_ACCOUNT_ID', account_id)
    print(os.getenv("WOOT_API_URL"))
    monkeypatch.setenv('PATH', path)
    woot = get_woot(inbox_id=inbox_id, inbox_name="testing")

    woot.addr = bot_addr
    return woot


@pytest.fixture()
def lp():
    """Log printer fixture."""

    class Printer:
        def sec(self, msg: str) -> None:
            print()
            print("=" * 10, msg, "=" * 10)

        def step(self, msg: str) -> None:
            print("-" * 5, "step " + msg, "-" * 5)

        def indent(self, msg: str) -> None:
            print("  " + msg)

    return Printer()
