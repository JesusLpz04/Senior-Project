# Generated by Django 5.1.1 on 2025-03-24 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('FundFlow', '0006_customcategory_remove_createticket_balance_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='createticket',
            name='custom_category',
        ),
        migrations.DeleteModel(
            name='CustomCategory',
        ),
    ]
