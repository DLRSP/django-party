"""Contact points and postal addresses with half-open validity intervals."""
from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from party.models.party import Party


class ContactPoint(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", _("Email")
        PHONE = "phone", _("Phone")
        MOBILE = "mobile", _("Mobile")
        PEC = "pec", _("PEC")
        FAX = "fax", _("Fax")
        OTHER = "other", _("Other")

    class Use(models.TextChoices):
        HOME = "home", _("Home")
        WORK = "work", _("Work")
        BILLING = "billing", _("Billing")
        MARKETING = "marketing", _("Marketing")
        OTHER = "other", _("Other")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="contact_points"
    )
    channel = models.CharField(max_length=16, choices=Channel.choices)
    use = models.CharField(
        max_length=16, choices=Use.choices, default=Use.OTHER, blank=True
    )
    value = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    trust = models.PositiveSmallIntegerField(default=50)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("contact point")
        verbose_name_plural = _("contact points")
        indexes = [
            models.Index(fields=["party", "channel"]),
            models.Index(fields=["value"]),
        ]

    def __str__(self) -> str:
        return f"{self.channel}:{self.value}"


class PostalAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party, on_delete=models.PROTECT, related_name="postal_addresses"
    )
    line1 = models.CharField(max_length=255, blank=True, default="")
    line2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=128, blank=True, default="")
    postal_code = models.CharField(max_length=32, blank=True, default="")
    region = models.CharField(max_length=64, blank=True, default="")
    country = models.CharField(max_length=2, blank=True, default="")
    use = models.CharField(max_length=32, blank=True, default="")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("postal address")
        verbose_name_plural = _("postal addresses")

    def __str__(self) -> str:
        return f"{self.line1} {self.city}".strip() or str(self.id)
