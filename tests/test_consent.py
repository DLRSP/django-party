"""Consent append-only + deny-by-default marketing."""
from django.test import TestCase
from django.utils import timezone

from party.models import ConsentRecord, Party
from party.services import marketing_allowed, record_consent, refuse_beddy_consent_mapping


class ConsentLedgerTests(TestCase):
    def setUp(self):
        self.party = Party.objects.create(
            kind=Party.Kind.PERSON, given_name="Ada", family_name="Lovelace"
        )

    def test_delete_raises(self):
        row = record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="hitl",
        )
        with self.assertRaises(ValueError):
            row.delete()

    def test_queryset_update_raises(self):
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="hitl",
        )
        with self.assertRaises(ValueError):
            ConsentRecord.objects.filter(party=self.party).update(
                decision=ConsentRecord.Decision.WITHDRAWN
            )

    def test_withdraw_after_grant_denies_marketing(self):
        from datetime import timedelta

        now = timezone.now()
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="hitl",
            recorded_at=now,
        )
        self.assertTrue(marketing_allowed(self.party))
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.WITHDRAWN,
            source="hitl",
            recorded_at=now + timedelta(seconds=1),
        )
        self.assertFalse(marketing_allowed(self.party))

    def test_refuse_beddy_consent_mapping(self):
        with self.assertRaises(ValueError):
            refuse_beddy_consent_mapping({"privacy_check": 1})
