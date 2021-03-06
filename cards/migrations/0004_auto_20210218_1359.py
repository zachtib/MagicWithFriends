# Generated by Django 3.1.6 on 2021-02-18 13:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cards', '0003_auto_20210215_2305'),
    ]

    operations = [
        migrations.RenameField(
            model_name='magicset',
            old_name='printings',
            new_name='cards',
        ),
        migrations.AlterField(
            model_name='magicset',
            name='code',
            field=models.CharField(max_length=5, unique=True),
        ),
        migrations.AlterField(
            model_name='printing',
            name='magic_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='printings',
                                    to='cards.magicset'),
        ),
    ]
