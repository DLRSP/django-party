"""PartyOutbox enqueue + close_contact_point / close_postal_address."""
from django.test import TestCase
from django.utils import timezone

from party.models import ContactPoint, Party, PartyOutbox, PostalAddress
from party.services import (
    close_contact_point,
    close_postal_address,
    enqueue_party_change,
    mark_outbox,
    pending_outbox,
    upsert_contact_point,
    upsert_postal_address,
)


class OutboxAndCloseTests(TestCase):
    def test_enqueue_and_pending(self):
        party = Party.objects.create(
            kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace"
        )
        entry = enqueue_party_change(
            party, field="contact.email", new_value="ada@example.com", old_value=""
        )
        self.assertEqual(entry.status, PartyOutbox.Status.PENDING)
        pending = pending_outbox(target="beddy", limit=10)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].pk, entry.pk)
        mark_outbox(entry, status=PartyOutbox.Status.SENT)
        entry.refresh_from_db()
        self.assertEqual(entry.status, PartyOutbox.Status.SENT)
        self.assertEqual(pending_outbox(target="beddy"), [])

    def test_close_contact_point(self):
        party = Party.objects.create(
            kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace"
        )
        now = timezone.now()
        cp = upsert_contact_point(
            party,
            channel=ContactPoint.Channel.EMAIL,
            value="ada@example.com",
            valid_from=now,
        )
        close_contact_point(cp)
        cp.refresh_from_db()
        self.assertIsNotNone(cp.valid_to)
        self.assertEqual(
            ContactPoint.objects.filter(
                party=party, channel="email", valid_to__isnull=True
            ).count(),
            0,
        )

    def test_close_postal_address(self):
        party = Party.objects.create(
            kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace"
        )
        addr = upsert_postal_address(
            party, line1="Via Roma 1", city="Bergamo", postal_code="24100", country="IT"
        )
        close_postal_address(addr)
        addr.refresh_from_db()
        self.assertIsNotNone(addr.valid_to)
        self.assertEqual(
            PostalAddress.objects.filter(party=party, valid_to__isnull=True).count(), 0
        )
