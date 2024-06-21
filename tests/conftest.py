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
    return ac


@pytest.fixture()
def woot():
    woot = get_woot()
    woot.addr = os.getenv("WOOT_ADDR", "ebemtzxws@nine.testrun.org")
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
