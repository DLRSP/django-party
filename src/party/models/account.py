"""Thin counterpart account codes (not a double-entry ledger)."""
from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from party.models.party import Party


class PartyAccount(models.Model):
    """Optional studio/partitario code on a party. No balances or postings."""

    class Kind(models.TextChoices):
        RECEIVABLE = "receivable", _("Receivable")
        PAYABLE = "payable", _("Payable")
        MEMO = "memo", _("Memo")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        CLOSED = "closed", _("Closed")
        MERGED = "merged", _("Merged")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="accounts"
    )
    code = models.CharField(max_length=64)
    label = models.CharField(max_length=255, blank=True, default="")
    kind = models.CharField(max_length=16, choices=Kind.choices)
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    is_default = models.BooleanField(default=False)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("party account")
        verbose_name_plural = _("party accounts")
        constraints = [
            models.UniqueConstraint(
                fields=["party", "code"],
                condition=models.Q(valid_to__isnull=True),
                name="party_account_open_code_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["party", "kind"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} ({self.kind})"

    def clean(self) -> None:
        # Never treat opaque external PMS numeric ids as studio account codes.
        if self.code and self.code.isdigit() and len(self.code) >= 6:
            raise ValidationError(
                {
                    "code": _(
                        "Numeric identifiers from external PMS must not be used "
                        "as account codes; assign a studio code instead."
                    )
                }
            )
