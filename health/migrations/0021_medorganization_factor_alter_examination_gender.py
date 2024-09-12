# Generated by Django 5.1.1 on 2024-09-08 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health', '0020_examination_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='medorganization',
            name='factor',
            field=models.PositiveSmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], default=6, verbose_name='Размер организации (от 1 до 10)'),
        ),
        migrations.AlterField(
            model_name='examination',
            name='gender',
            field=models.CharField(choices=[('М', 'Мужчина'), ('Ж', 'Женщина'), ('МЖ', 'Все')], db_comment='Пол', default='МЖ', max_length=2, verbose_name='Пол'),
        ),
    ]
