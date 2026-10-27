from django.contrib import admin

from party.models import (
    ConsentRecord,
    ContactPoint,
    ExternalIdentity,
    Party,
    PartyAccount,
    PartyFact,
    PartyMergeEvent,
    PostalAddress,
)


class ContactPointInline(admin.TabularInline):
    model = ContactPoint
    extra = 0


class PartyAccountInline(admin.TabularInline):
    model = PartyAccount
    extra = 0


class PartyFactInline(admin.TabularInline):
    model = PartyFact
    extra = 0
    fields = ("key", "value", "source", "trust", "valid_from", "valid_to")


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("id", "kind", "status", "display_name", "updated_at")
    list_filter = ("kind", "status")
    search_fields = ("given_name", "family_name", "legal_name")
    inlines = [ContactPointInline, PartyFactInline, PartyAccountInline]


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

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PartyMergeEvent)
class PartyMergeEventAdmin(admin.ModelAdmin):
    list_display = ("survivor", "merged", "actor", "created_at")
    readonly_fields = ("survivor", "merged", "actor", "payload", "created_at")


@admin.register(PartyFact)
class PartyFactAdmin(admin.ModelAdmin):
    list_display = ("key", "source", "party", "trust", "valid_from", "valid_to")
    list_filter = ("source", "key")
    search_fields = ("key", "value", "source")


admin.site.register(PostalAddress)
