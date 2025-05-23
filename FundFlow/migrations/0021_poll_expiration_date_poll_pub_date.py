# Generated by Django 5.1.7 on 2025-05-04 01:55

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FundFlow', '0020_remove_item_tags_item_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='expiration_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='poll',
            name='pub_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
