# Generated by Django 5.1.7 on 2025-03-25 01:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FundFlow', '0007_fundingrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fundingrequest',
            name='organization',
        ),
    ]
