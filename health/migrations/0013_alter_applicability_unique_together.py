# Generated by Django 5.0.6 on 2024-07-15 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0012_applicability_procedure_disease_gender_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='applicability',
            unique_together={('from_age', 'to_age', 'periodicity')},
        ),
    ]
