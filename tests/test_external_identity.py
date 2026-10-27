import pytest
from django.utils import timezone

from party.models import Party
from party.services.identity import upsert_external_identity


@pytest.mark.django_db
def test_contact_and_customer_namespaces_are_distinct():
    p_contact = Party.objects.create(
        kind=Party.Kind.PERSON, given_name="C", family_name="Ontact"
    )
    p_customer = Party.objects.create(
        kind=Party.Kind.PERSON, given_name="C", family_name="Ustomer"
    )
    upsert_external_identity(
        p_contact, namespace="pms", scheme="contact", value="12345"
    )
    upsert_external_identity(
        p_customer, namespace="pms", scheme="customer", value="12345"
    )
    assert p_contact.external_identities.filter(scheme="contact").count() == 1
    assert p_customer.external_identities.filter(scheme="customer").count() == 1


@pytest.mark.django_db
def test_same_scheme_value_cannot_bind_two_parties():
    a = Party.objects.create(kind=Party.Kind.PERSON, given_name="A", family_name="A")
    b = Party.objects.create(kind=Party.Kind.PERSON, given_name="B", family_name="B")
    upsert_external_identity(a, namespace="pms", scheme="customer", value="99")
    with pytest.raises(ValueError):
        upsert_external_identity(b, namespace="pms", scheme="customer", value="99")


@pytest.mark.django_db
def test_same_party_upsert_is_idempotent():
    party = Party.objects.create(kind=Party.Kind.PERSON, given_name="A", family_name="A")
    first = upsert_external_identity(
        party, namespace="pms", scheme="customer", value="99", trust=40
    )
    second = upsert_external_identity(
        party, namespace="pms", scheme="customer", value="99", trust=80
    )
    assert first.pk == second.pk
    assert second.trust == 80
    assert party.external_identities.filter(valid_to__isnull=True).count() == 1


@pytest.mark.django_db
def test_closed_extid_may_rebind_to_another_party():
    a = Party.objects.create(kind=Party.Kind.PERSON, given_name="A", family_name="A")
    b = Party.objects.create(kind=Party.Kind.PERSON, given_name="B", family_name="B")
    prior = upsert_external_identity(
        a, namespace="pms", scheme="customer", value="99"
    )
    prior.valid_to = timezone.now()
    prior.save(update_fields=["valid_to"])
    rebound = upsert_external_identity(
        b, namespace="pms", scheme="customer", value="99"
    )
    assert rebound.party_id == b.id
    assert rebound.valid_to is None
    assert a.external_identities.filter(valid_to__isnull=True).count() == 0
    assert b.external_identities.filter(valid_to__isnull=True).count() == 1


@pytest.mark.django_db
def test_same_numeric_value_ok_across_namespaces():
    """Adopters may reuse id spaces; namespace isolates PMS vs fiscal (etc.)."""
    party = Party.objects.create(
        kind=Party.Kind.ORGANIZATION, legal_name="Acme"
    )
    upsert_external_identity(
        party, namespace="pms", scheme="guest", value="42"
    )
    upsert_external_identity(
        party, namespace="fiscal", scheme="supplier", value="42"
    )
    assert party.external_identities.filter(valid_to__isnull=True).count() == 2
