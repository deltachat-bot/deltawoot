import os
from deltachat_rpc_client.pytestplugin import get_temp_credentials


def test_create_contact(woot, lp):
    if not os.getenv("CHATMAIL_DOMAIN"):
        os.environ["CHATMAIL_DOMAIN"] = "nine.testrun.org"
    email = get_temp_credentials()['email']
    lp.sec("trying to create contact: " + email)
    first_try = woot.create_contact_if_not_exists(email)
    second_try = woot.create_contact_if_not_exists(email)
    assert first_try == second_try
    assert first_try == second_try


def test_get_contact(woot):
    email = get_temp_credentials()["email"]
    woot.create_contact_if_not_exists(email)
    assert email == woot.get_contact(email)['email']
