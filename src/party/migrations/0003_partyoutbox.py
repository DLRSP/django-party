from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("party", "0002_partyfact"),
    ]

    operations = [
        migrations.CreateModel(
            name="PartyOutbox",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "target",
                    models.CharField(
                        db_index=True,
                        default="beddy",
                        help_text="Adapter namespace (beddy, …).",
                        max_length=32,
                    ),
                ),
                ("field", models.CharField(max_length=64)),
                ("old_value", models.TextField(blank=True, default="")),
                ("new_value", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("sent", "Sent"),
                            ("failed", "Failed"),
                            ("skipped", "Skipped"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("last_error", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "party",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outbox_entries",
                        to="party.party",
                    ),
                ),
            ],
            options={
                "verbose_name": "party outbox entry",
                "verbose_name_plural": "party outbox entries",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="partyoutbox",
            index=models.Index(
                fields=["status", "target", "created_at"],
                name="party_party_status_7b0c0a_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="partyoutbox",
            index=models.Index(
                fields=["party", "status"],
                name="party_party_party_i_0f1a2b_idx",
            ),
        ),
    ]
