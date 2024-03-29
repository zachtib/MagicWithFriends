# Generated by Django 3.1.6 on 2021-05-20 19:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('cards', '0008_cardface_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='color_indicator',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='card',
            name='layout',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='card',
            name='loyalty',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='card',
            name='oracle_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='card',
            name='power',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='card',
            name='type_line',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cardface',
            name='type_line',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
    ]
