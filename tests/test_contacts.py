"""ContactPoint upsert helpers."""
from django.test import TestCase
from django.utils import timezone

from party.models import ContactPoint, Party
from party.services import upsert_contact_point


class ContactUpsertTests(TestCase):
    def test_upsert_same_value_is_idempotent(self):
        party = Party.objects.create(kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace")
        now = timezone.now()
        a = upsert_contact_point(
            party, channel=ContactPoint.Channel.EMAIL, value="ada@example.com", valid_from=now
        )
        b = upsert_contact_point(
            party, channel=ContactPoint.Channel.EMAIL, value="ada@example.com", valid_from=now
        )
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(
            ContactPoint.objects.filter(party=party, channel="email", valid_to__isnull=True).count(),
            1,
        )

    def test_empty_value_rejected(self):
        party = Party.objects.create(
            kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace"
        )
        with self.assertRaises(ValueError):
            upsert_contact_point(
                party,
                channel=ContactPoint.Channel.EMAIL,
                value="  ",
                valid_from=timezone.now(),
            )
