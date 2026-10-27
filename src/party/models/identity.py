"""External system identifiers linked to a party (multi-source)."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from party.models.party import Party


class ExternalIdentity(models.Model):
    """One external id in a namespace/scheme (e.g. pms + guest, fiscal + supplier)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="external_identities"
    )
    namespace = models.CharField(max_length=64, db_index=True)
    scheme = models.CharField(max_length=64, db_index=True)
    value = models.CharField(max_length=255, db_index=True)
    trust = models.PositiveSmallIntegerField(default=50)
    payload_hash = models.CharField(max_length=64, blank=True, default="")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("external identity")
        verbose_name_plural = _("external identities")
        constraints = [
            models.UniqueConstraint(
                fields=["namespace", "scheme", "value"],
                condition=models.Q(valid_to__isnull=True),
                name="party_extid_open_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["namespace", "scheme", "value"]),
            models.Index(fields=["party", "namespace"]),
        ]

    def __str__(self) -> str:
        return f"{self.namespace}:{self.scheme}={self.value}"
