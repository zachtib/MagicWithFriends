# Generated by Django 3.1.6 on 2021-05-19 17:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('cards', '0007_printing_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommanderJumpstartDeck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(
                    choices=[('W', 'White'), ('U', 'Blue'), ('B', 'Black'), ('R', 'Red'), ('G', 'Green'),
                             ('C', 'Colorless')], max_length=1)),
                ('slug', models.SlugField(unique=True)),
                ('commander', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.card')),
            ],
        ),
        migrations.CreateModel(
            name='DualColoredDeck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('colors', models.CharField(
                    choices=[('WU', 'White / Blue'), ('UB', 'Blue / Black'), ('BR', 'Black / Red'),
                             ('RG', 'Red / Green'), ('GW', 'Green / White'), ('WB', 'White / Black'),
                             ('BG', 'Black / Green'), ('GU', 'Green / Blue'), ('UR', 'Blue / Red'),
                             ('RW', 'Red / White')], max_length=2, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DualColoredEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(
                    choices=[('C', 'Creature'), ('P', 'Planeswalker'), ('S', 'Sorcery'), ('I', 'Instant'),
                             ('A', 'Artifact'), ('E', 'Enchantment'), ('L', 'Land')], max_length=1)),
                ('card',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='cards.card')),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards',
                                           to='cmdrjump.dualcoloreddeck')),
            ],
        ),
        migrations.CreateModel(
            name='CommanderJumpstartEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(
                    choices=[('C', 'Creature'), ('P', 'Planeswalker'), ('S', 'Sorcery'), ('I', 'Instant'),
                             ('A', 'Artifact'), ('E', 'Enchantment'), ('L', 'Land')], max_length=1)),
                ('card',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='cards.card')),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cards',
                                           to='cmdrjump.commanderjumpstartdeck')),
            ],
        ),
    ]