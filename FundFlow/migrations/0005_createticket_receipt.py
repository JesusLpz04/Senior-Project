# Generated by Django 5.1.7 on 2025-03-18 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FundFlow', '0004_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='createticket',
            name='receipt',
            field=models.FileField(blank=True, null=True, upload_to='receipts/'),
        ),
    ]
