# Generated by Django 3.1.6 on 2021-03-01 15:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('drafts', '0007_auto_20210301_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='draftcard',
            name='seat',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='draft_cards', to='drafts.draftseat'),
        ),
    ]
