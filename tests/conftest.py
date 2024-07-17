import os
import pytest
from deltachat_rpc_client.pytestplugin import acfactory

from deltawoot.woot import get_woot


@pytest.fixture()
def delta(acfactory):
    if not os.getenv("CHATMAIL_DOMAIN"):
        os.environ["CHATMAIL_DOMAIN"] = "nine.testrun.org"
    ac = acfactory.get_online_account()
    ac.set_config('displayname', 'CI account')
    print("Creating Test account", ac.get_config('addr'))
    return ac


@pytest.fixture()
def bot_addr():
    return os.getenv("WOOT_ADDR", "deltawoot@nine.testrun.org")


@pytest.fixture()
def woot(bot_addr):
    woot = get_woot()
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
