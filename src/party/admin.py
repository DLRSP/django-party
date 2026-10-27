from django.contrib import admin

from party.models import (
    ConsentRecord,
    ContactPoint,
    ExternalIdentity,
    Party,
    PartyAccount,
    PartyMergeEvent,
    PostalAddress,
)


class ContactPointInline(admin.TabularInline):
    model = ContactPoint
    extra = 0


class PartyAccountInline(admin.TabularInline):
    model = PartyAccount
    extra = 0


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "status", "display_name", "updated_at")
    list_filter = ("kind", "status")
    search_fields = ("given_name", "family_name", "legal_name")
    inlines = [ContactPointInline, PartyAccountInline]


@admin.register(ExternalIdentity)
class ExternalIdentityAdmin(admin.ModelAdmin):
    list_display = ("namespace", "scheme", "value", "party", "trust", "valid_to")
    list_filter = ("namespace", "scheme")
    search_fields = ("value",)


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ("party", "purpose", "decision", "recorded_at", "source")
    list_filter = ("purpose", "decision")
    readonly_fields = ("party", "purpose", "decision", "source", "recorded_at", "created_at")

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PartyMergeEvent)
class PartyMergeEventAdmin(admin.ModelAdmin):
    list_display = ("survivor", "merged", "actor", "created_at")
    readonly_fields = ("survivor", "merged", "actor", "payload", "created_at")


admin.site.register(PostalAddress)
