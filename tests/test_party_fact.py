import pytest
from django.contrib.auth.models import Group
from django.utils import timezone

from party.models import Party, PartyFact
from party.rbac import CRM_FEATURE_GROUPS, seed_crm_feature_groups
from party.services import close_party_fact, upsert_party_fact
from party.services.facts import refuse_forbidden_fact_key


@pytest.mark.django_db
def test_upsert_and_close_party_fact():
    party = Party.objects.create(
        kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace"
    )
    row = upsert_party_fact(
        party, key="idp.google.language", value="en", source="google"
    )
    assert row.key == "idp.google.language"
    assert PartyFact.objects.filter(party=party, valid_to__isnull=True).count() == 1
    closed = close_party_fact(party, key="idp.google.language", source="google")
    assert closed is not None
    assert closed.valid_to is not None
    rebound = upsert_party_fact(
        party, key="idp.google.language", value="it", source="google"
    )
    assert rebound.valid_to is None
    assert rebound.value == "it"


@pytest.mark.django_db
def test_refuse_forbidden_fact_keys():
    party = Party.objects.create(kind=Party.Kind.PERSON, given_name="X", family_name="Y")
    for key in ("codice_fiscale", "piva", "iban", "oauth_access_token"):
        with pytest.raises(ValueError):
            refuse_forbidden_fact_key(key)
        with pytest.raises(ValueError):
            upsert_party_fact(party, key=key, value="x", source="test")


@pytest.mark.django_db
def test_obsolete_google_plus_as_closed_fact():
    party = Party.objects.create(kind=Party.Kind.PERSON, given_name="X", family_name="Y")
    upsert_party_fact(
        party,
        key="idp.google.is_plus_user",
        value="1",
        source="google",
        valid_to=timezone.now(),
    )
    assert PartyFact.objects.filter(party=party, valid_to__isnull=True).count() == 0
    assert PartyFact.objects.filter(party=party).count() == 1


@pytest.mark.django_db
def test_crm_feature_groups_seed():
    from django.contrib.auth.management import create_permissions
    from django.apps import apps as django_apps

    create_permissions(django_apps.get_app_config("party"), verbosity=0)
    seed_crm_feature_groups()
    names = set(Group.objects.values_list("name", flat=True))
    for name in CRM_FEATURE_GROUPS:
        assert name in names, f"missing feature group {name}; have {names}"
    assert "dlrsp:crm.contatti_view" not in names

