# Generated by Django 4.2.3 on 2023-07-24 06:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0004_source_parser_class"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="subscriber",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscriptions",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Subscriber to the source",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="post",
            name="popularity",
            field=models.IntegerField(default=50, verbose_name="Post popularity"),
        ),
        migrations.AlterUniqueTogether(
            name="subscription",
            unique_together={("source", "subscriber")},
        ),
        migrations.RemoveField(
            model_name="subscription",
            name="subscribers",
        ),
    ]
