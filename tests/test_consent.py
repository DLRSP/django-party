"""Consent append-only + deny-by-default marketing."""
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from party.admin import ConsentRecordAdmin
from party.models import ConsentRecord, Party
from party.services import (
    marketing_allowed,
    record_consent,
    refuse_untrusted_consent_mapping,
)


_PMS_PRIVACY_KEYS = frozenset(
    {
        "privacy_check",
        "privacy_check_from_admin",
        "promotion_check",
        "promotion_check_from_admin",
    }
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

    def test_queryset_delete_raises(self):
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="operator",
        )
        with self.assertRaises(ValueError):
            ConsentRecord.objects.filter(party=self.party).delete()
        self.assertEqual(
            ConsentRecord.objects.filter(party=self.party).count(), 1
        )

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

    def test_queryset_update_internal_raises(self):
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="operator",
        )
        with self.assertRaises(ValueError):
            ConsentRecord.objects.filter(party=self.party)._update([])

    def test_queryset_raw_delete_raises(self):
        record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="operator",
        )
        with self.assertRaises(ValueError):
            ConsentRecord.objects.filter(party=self.party)._raw_delete(
                using=ConsentRecord.objects.db
            )

    def test_instance_save_update_raises(self):
        row = record_consent(
            self.party,
            purpose=ConsentRecord.Purpose.MARKETING,
            decision=ConsentRecord.Decision.GRANTED,
            source="operator",
        )
        row.decision = ConsentRecord.Decision.WITHDRAWN
        with self.assertRaises(ValueError):
            row.save()

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

    def test_refuse_untrusted_consent_mapping_explicit_keys(self):
        with self.assertRaises(ValueError):
            refuse_untrusted_consent_mapping(
                {"privacy_check": 1}, forbidden_keys=_PMS_PRIVACY_KEYS
            )

    def test_refuse_untrusted_empty_default_is_noop(self):
        refuse_untrusted_consent_mapping({"privacy_check": 1})

    @override_settings(PARTY_CONSENT_FORBIDDEN_PAYLOAD_KEYS=_PMS_PRIVACY_KEYS)
    def test_refuse_untrusted_from_settings(self):
        with self.assertRaises(ValueError):
            refuse_untrusted_consent_mapping({"promotion_check": 1})

    @override_settings(PARTY_CONSENT_FORBIDDEN_PAYLOAD_KEYS=_PMS_PRIVACY_KEYS)
    def test_record_consent_rejects_forbidden_source_token(self):
        with self.assertRaises(ValueError):
            record_consent(
                self.party,
                purpose=ConsentRecord.Purpose.MARKETING,
                decision=ConsentRecord.Decision.GRANTED,
                source="privacy_check",
            )

    def test_consent_admin_has_no_add_change_delete(self):
        admin = ConsentRecordAdmin(ConsentRecord, AdminSite())
        request = RequestFactory().get("/")
        self.assertFalse(admin.has_add_permission(request))
        self.assertFalse(admin.has_change_permission(request))
        self.assertFalse(admin.has_delete_permission(request))
