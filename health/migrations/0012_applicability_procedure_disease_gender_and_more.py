# Generated by Django 5.0.6 on 2024-07-14 10:42

import django.db.models.deletion
import health.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0011_remove_examination_direction_examination_disease_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_age', models.PositiveSmallIntegerField(verbose_name='Возраст начала обследования')),
                ('to_age', models.PositiveSmallIntegerField(verbose_name='Возраст окончания обследования')),
                ('periodicity', models.FloatField(verbose_name='период обследования в годах')),
            ],
            options={
                'verbose_name': 'Применимость обследования',
                'verbose_name_plural': 'Применимость обследований',
                'db_table_comment': 'Применимость обследования',
            },
        ),
        migrations.CreateModel(
            name='Procedure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_comment='Наименование', max_length=100, verbose_name='Наименование')),
            ],
            options={
                'verbose_name': 'Процедура обследования',
                'verbose_name_plural': 'Процедуры обследования',
                'db_table_comment': 'Процедура обследования',
            },
        ),
        migrations.AddField(
            model_name='disease',
            name='gender',
            field=models.CharField(choices=[('М', 'Man'), ('Ж', 'Woman'), ('МЖ', 'All')], db_comment='Пол', default='МЖ', max_length=2, verbose_name='Пол'),
        ),
        migrations.AddField(
            model_name='examination',
            name='examination_scheme',
            field=models.JSONField(db_comment='Схема обследования', null=True, verbose_name='Схема обследования'),
        ),
        migrations.AlterField(
            model_name='person',
            name='gender',
            field=models.CharField(choices=[('М', 'Man'), ('Ж', 'Woman'), ('МЖ', 'All')], db_comment='Пол', max_length=2, validators=[health.models.GenderEnum.only_m_w_validator], verbose_name='Пол'),
        ),
        migrations.AddField(
            model_name='examination',
            name='applicability',
            field=models.ForeignKey(db_comment='Применимость', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(model_name)s_from_applicability', to='health.applicability', verbose_name='Применимость'),
        ),
        migrations.AddField(
            model_name='examination',
            name='procedure',
            field=models.ManyToManyField(related_name='%(model_name)s_from_procedure', to='health.procedure'),
        ),
    ]
