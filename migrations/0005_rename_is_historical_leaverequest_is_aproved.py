# Generated by Django 4.2.6 on 2023-11-11 04:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0004_remove_leaverequest_is_half'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leaverequest',
            old_name='is_historical',
            new_name='is_aproved',
        ),
    ]