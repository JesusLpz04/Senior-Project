# Generated by Django 5.1.1 on 2025-04-22 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('FundFlow', '0012_createticket_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='createticket',
            name='description',
            field=models.TextField(blank=True, default='Description Here', null=True),
        ),
    ]
