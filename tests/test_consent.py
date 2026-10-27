"""Consent append-only + deny-by-default marketing."""
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.utils import timezone

from party.admin import ConsentRecordAdmin
from party.models import ConsentRecord, Party
from party.services import (
    marketing_allowed,
    record_consent,
    refuse_untrusted_consent_mapping,
)


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
            source="operator",
        )
        with self.assertRaises(ValueError):
            row.delete()

    def test_queryset_update_raises(self):
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="operator",
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
            source="operator",
            recorded_at=now,
        )
        self.assertTrue(marketing_allowed(self.party))
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.WITHDRAWN,
            source="operator",
            recorded_at=now + timedelta(seconds=1),
        )
        self.assertFalse(marketing_allowed(self.party))

    def test_refuse_untrusted_consent_mapping(self):
        with self.assertRaises(ValueError):
            refuse_untrusted_consent_mapping({"privacy_check": 1})

    def test_consent_admin_has_no_add_change_delete(self):
        admin = ConsentRecordAdmin(ConsentRecord, AdminSite())
        request = RequestFactory().get("/")
        self.assertFalse(admin.has_add_permission(request))
        self.assertFalse(admin.has_change_permission(request))
        self.assertFalse(admin.has_delete_permission(request))
