# Generated by Django 5.0.6 on 2024-07-08 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0007_remove_region_id_alter_region_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='region',
        ),
    ]
