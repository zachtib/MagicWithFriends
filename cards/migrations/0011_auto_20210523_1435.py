# Generated by Django 3.1.6 on 2021-05-23 14:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cards', '0010_card_toughness'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='layout',
            field=models.CharField(default='normal', max_length=20),
        ),
    ]
