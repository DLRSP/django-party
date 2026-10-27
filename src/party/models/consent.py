"""Append-only consent ledger (privacy / marketing)."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from party.models.party import Party


class ConsentRecordQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError(
            "ConsentRecord is append-only; do not update existing rows. "
            "Insert a new row via record_consent()."
        )

    def delete(self):
        raise ValueError(
            "ConsentRecord is append-only; do not delete ledger rows. "
            "Record a withdrawn decision instead."
        )


class ConsentRecordManager(models.Manager.from_queryset(ConsentRecordQuerySet)):
    pass


class ConsentRecord(models.Model):
    class Purpose(models.TextChoices):
        PRIVACY = "privacy", _("Privacy")
        MARKETING = "marketing", _("Marketing")

    class Decision(models.TextChoices):
        GRANTED = "granted", _("Granted")
        WITHDRAWN = "withdrawn", _("Withdrawn")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="consent_records"
    )
    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    decision = models.CharField(max_length=16, choices=Decision.choices)
    source = models.CharField(max_length=64, blank=True, default="")
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ConsentRecordManager()

    class Meta:
        verbose_name = _("consent record")
        verbose_name_plural = _("consent records")
        ordering = ("-recorded_at",)
        indexes = [
            models.Index(fields=["party", "purpose", "-recorded_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.purpose}:{self.decision}"

    def save(self, *args, **kwargs):
        if self.pk and ConsentRecord.objects.filter(pk=self.pk).exists():
            raise ValueError(
                "ConsentRecord is append-only; do not update existing rows."
            )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError(
            "ConsentRecord is append-only; do not delete ledger rows. "
            "Record a withdrawn decision instead."
        )
