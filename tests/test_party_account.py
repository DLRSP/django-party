import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from party.models import Party, PartyAccount
from party.services.accounts import get_default_party_account, upsert_party_account
from party.services.consent import marketing_allowed
from party.models import ConsentRecord


@pytest.mark.django_db
def test_upsert_and_default_account():
    party = Party.objects.create(
        kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace"
    )
    acc = upsert_party_account(
        party, code="401.12", kind=PartyAccount.Kind.RECEIVABLE, is_default=True
    )
    assert acc.code == "401.12"
    found = get_default_party_account(party, PartyAccount.Kind.RECEIVABLE)
    assert found is not None
    assert found.pk == acc.pk


@pytest.mark.django_db
def test_reject_numeric_pms_id_as_code():
    party = Party.objects.create(kind=Party.Kind.PERSON, given_name="X", family_name="Y")
    with pytest.raises(ValidationError):
        upsert_party_account(
            party, code="18856052", kind=PartyAccount.Kind.PAYABLE, is_default=True
        )


@pytest.mark.django_db
def test_reject_short_all_digit_code():
    party = Party.objects.create(kind=Party.Kind.PERSON, given_name="X", family_name="Y")
    with pytest.raises(ValidationError):
        upsert_party_account(
            party, code="12345", kind=PartyAccount.Kind.PAYABLE, is_default=True
        )


@pytest.mark.django_db
def test_reject_empty_code():
    party = Party.objects.create(kind=Party.Kind.PERSON, given_name="X", family_name="Y")
    with pytest.raises(ValidationError):
        upsert_party_account(
            party, code="  ", kind=PartyAccount.Kind.MEMO, is_default=False
        )


@pytest.mark.django_db
def test_marketing_allowed_requires_granted():
    party = Party.objects.create(kind=Party.Kind.PERSON, given_name="A", family_name="B")
    assert marketing_allowed(party) is False
    ConsentRecord.objects.create(
        party=party,
        purpose=ConsentRecord.Purpose.MARKETING,
        decision=ConsentRecord.Decision.GRANTED,
        recorded_at=timezone.now(),
        source="test",
    )
    assert marketing_allowed(party) is True
