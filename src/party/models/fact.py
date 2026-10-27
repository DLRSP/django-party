"""Party facts — keyed attributes with validity (IdP snapshots, historical attrs)."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from party.models.party import Party


# Keys that must never be stored as PartyFact (fiscal / payment / tokens).
PARTY_FACT_FORBIDDEN_KEYS = frozenset(
    {
        "cf",
        "codice_fiscale",
        "fiscal_code",
        "piva",
        "vat",
        "partita_iva",
        "sdi",
        "codice_sdi",
        "iban",
        "oauth_access_token",
        "oauth_refresh_token",
        "access_token",
        "refresh_token",
        "password",
        "secret",
    }
)


class PartyFact(models.Model):
    """Non-channel attribute on a party (bio, IdP snapshot, obsolete metrics)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="facts"
    )
    key = models.CharField(max_length=128, db_index=True)
    value = models.TextField(blank=True, default="")
    source = models.CharField(max_length=64, blank=True, default="")
    trust = models.PositiveSmallIntegerField(default=50)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("party fact")
        verbose_name_plural = _("party facts")
        indexes = [
            models.Index(fields=["party", "key"]),
            models.Index(fields=["key", "source"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["party", "key", "source"],
                condition=models.Q(valid_to__isnull=True),
                name="party_fact_open_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.key}={self.value[:40]}"
