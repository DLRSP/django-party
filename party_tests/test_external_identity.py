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
        p_contact, namespace="beddy", scheme="contact", value="12345"
    )
    upsert_external_identity(
        p_customer, namespace="beddy", scheme="customer", value="12345"
    )
    assert p_contact.external_identities.filter(scheme="contact").count() == 1
    assert p_customer.external_identities.filter(scheme="customer").count() == 1


@pytest.mark.django_db
def test_same_scheme_value_cannot_bind_two_parties():
    a = Party.objects.create(kind=Party.Kind.PERSON, given_name="A", family_name="A")
    b = Party.objects.create(kind=Party.Kind.PERSON, given_name="B", family_name="B")
    upsert_external_identity(a, namespace="beddy", scheme="customer", value="99")
    with pytest.raises(ValueError):
        upsert_external_identity(b, namespace="beddy", scheme="customer", value="99")
