# Generated by Django 4.2.3 on 2023-07-24 06:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0005_subscription_subscriber_alter_post_popularity_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={"ordering": ("-created_at",)},
        ),
    ]
