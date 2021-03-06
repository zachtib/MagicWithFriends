# Generated by Django 3.1.6 on 2021-02-21 14:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('drafts', '0003_draft_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='draftcard',
            name='card_uuid',
            field=models.UUIDField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='draftcard',
            name='card_name',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]
