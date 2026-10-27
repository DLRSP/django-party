from django.apps import AppConfig


class PartyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "party"
    label = "party"
    verbose_name = "Party"

    def ready(self) -> None:
        from party.rbac import connect_rbac_signals

        connect_rbac_signals()
