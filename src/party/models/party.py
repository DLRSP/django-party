"""Canonical party (person or organization) — identity only."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Party(models.Model):
    class Kind(models.TextChoices):
        PERSON = "person", _("Person")
        ORGANIZATION = "organization", _("Organization")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        MERGED = "merged", _("Merged")
        HIDDEN = "hidden", _("Hidden")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=32, choices=Kind.choices)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE, db_index=True
    )
    merged_into = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="merged_from",
    )
    given_name = models.CharField(max_length=128, blank=True, default="")
    family_name = models.CharField(max_length=128, blank=True, default="")
    legal_name = models.CharField(max_length=255, blank=True, default="")
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("party")
        verbose_name_plural = _("parties")
        indexes = [
            models.Index(fields=["kind", "status"]),
            models.Index(fields=["family_name", "given_name"]),
            models.Index(fields=["legal_name"]),
        ]

    def __str__(self) -> str:
        if self.kind == self.Kind.ORGANIZATION:
            return self.legal_name or str(self.id)
        name = f"{self.given_name} {self.family_name}".strip()
        return name or self.legal_name or str(self.id)

    @property
    def display_name(self) -> str:
        return str(self)
