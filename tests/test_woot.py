import os
import pytest
from deltachat_rpc_client.pytestplugin import acfactory

from deltawoot.woot import get_contact_mapping, add_contact_mapping

def test_create_contact(woot, lp, acfactory):
    if not os.getenv("CHATMAIL_DOMAIN"):
        os.environ["CHATMAIL_DOMAIN"] = "nine.testrun.org"
    email, _ = acfactory.get_credentials()
    lp.sec("trying to create contact: " + email)
    first_try = woot.create_contact_if_not_exists(email)
    second_try = woot.create_contact_if_not_exists(email)
    assert first_try == second_try
    assert first_try == second_try


def test_search_contact(woot, acfactory):
    email, _ = acfactory.get_credentials()
    woot.create_contact_if_not_exists(email)
    assert email == woot.search_contact(email)['email']


def test_contact_mappings(delta):
    assert not delta.get_config("ui.deltawoot_mappings")
    assert get_contact_mapping(delta, delta_id=2) == (None, None)
    assert delta.get_config("ui.deltawoot_mappings") == "[]"
    assert get_contact_mapping(delta, woot_id=2) == (None, None)
    assert delta.get_config("ui.deltawoot_mappings") == "[]"
    add_contact_mapping(delta, 2, 2)
    assert delta.get_config("ui.deltawoot_mappings") == "[[2, 2]]"
    assert get_contact_mapping(delta, delta_id=2) == (2, 2)
    assert get_contact_mapping(delta, woot_id=2) == (2, 2)
    with pytest.raises(AssertionError):
        add_contact_mapping(delta, 2, 3)
    assert get_contact_mapping(delta, delta_id=2) == (2, 2)
    assert get_contact_mapping(delta, woot_id=2) == (2, 2)
    add_contact_mapping(delta, 3, 3)
    assert get_contact_mapping(delta, delta_id=3) == (3, 3)
    assert get_contact_mapping(delta, woot_id=3) == (3, 3)
    assert get_contact_mapping(delta, delta_id=2) == (2, 2)
    assert get_contact_mapping(delta, woot_id=2) == (2, 2)
    assert delta.get_config("ui.deltawoot_mappings") == "[[2, 2], [3, 3]]"

