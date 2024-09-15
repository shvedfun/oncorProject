# Generated by Django 5.0.6 on 2024-07-28 09:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_generator', '0001_initial'),
        ('health', '0017_delete_regiondirectiongeneratedata'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionDirectionGenerateData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(verbose_name='Дата')),
                ('type', models.CharField(choices=[('population', 'Population'), ('plan', 'Plan'), ('fact', 'Fact')], max_length=10, verbose_name='Тип')),
                ('is_active', models.BooleanField(default=False, verbose_name='Активна')),
                ('data', models.JSONField(verbose_name='Данные')),
                ('direction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(model_name)s_from_direction', to='health.direction', verbose_name='Направление медицины')),
                ('region', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(model_name)s_from_region', to='health.region', verbose_name='Регион')),
            ],
            options={
                'verbose_name': 'Данные для генерации распределений',
                'verbose_name_plural': 'Данные для генерации распределений',
            },
        ),
    ]
