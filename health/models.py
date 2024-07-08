from django.db import models

# Create your models here.


_RELATED_BASE_NAME = "%(model_name)s_from_"


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name="Регион", db_comment="Регион",)
    code = models.CharField(max_length=2, verbose_name="Код региона", db_comment="Код региона")

    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        db_table_comment = "Регион"
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


class Direction(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование", db_comment="Наименование")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table_comment = "Направление"
        verbose_name = "Направление"
        verbose_name_plural = "Направления"


class StageDisease(models.Model):
    name = models.CharField(max_length=100, verbose_name="Этап", db_comment="Этап")

    class Meta:
        db_table_comment = "Этап заболевания"
        verbose_name = "Этап заболевания"
        verbose_name_plural = "Этапы заболеваний"


class GenderEnum(models.TextChoices):
    MAN = "М"
    WOMAN = "Ж"


class Person(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО", db_comment="ФИО")
    gender = models.CharField(choices=GenderEnum.choices, max_length=1, verbose_name="Пол", db_comment="Пол")
    birthday = models.DateField(verbose_name="Дата рождения", db_comment="Дата рождения")
    diseases = models.ManyToManyField(
        to="Disease", blank=True,
        through="PersonDisease",
        related_name=_RELATED_BASE_NAME + "Disease",
        verbose_name="Заболевания",
    )
    region = models.ForeignKey(
        to=Region, on_delete=models.CASCADE, verbose_name="Регион",
        related_name=_RELATED_BASE_NAME + "region", db_comment="Регион", null=True
    )

    class Meta:
        db_table_comment = "Гражданин"
        verbose_name = "Гражданин"
        verbose_name_plural = "Граждане"


class Disease(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Заболевание", db_comment="Заболевание",)
    direction = models.ForeignKey(to=Direction, on_delete=models.CASCADE,
                                  verbose_name="Направление заболевания", db_comment="Направление заболевания")

    class Meta:
        db_table_comment = "Заболевание"
        verbose_name = "Заболевание"
        verbose_name_plural = "Заболевания"


class PersonDisease(models.Model):
    person = models.ForeignKey(
        to=Person,
        on_delete=models.CASCADE,
        verbose_name="Гражданин",
        related_name=_RELATED_BASE_NAME + 'person',
        db_comment="Гражданин",
    )
    disease = models.ForeignKey(
        to=Disease,
        on_delete=models.CASCADE,
        verbose_name="Заболевание",
        related_name=_RELATED_BASE_NAME + 'disease',
        db_comment="Заболевание",
    )
    stage = models.ForeignKey(
        to=StageDisease,
        on_delete=models.CASCADE,
        verbose_name="Этап",
        related_name=_RELATED_BASE_NAME + 'stage',
        null=True
    )
    start_from = models.DateTimeField(verbose_name="Дата диагноза", db_comment="Дата диагноза",)
    finish_at = models.DateTimeField(verbose_name="Дата окончания", db_comment="Дата окончания",
                                     null=True, blank=True
                                     )

    class Meta:
        db_table_comment = "Заболевание гражданина"
        verbose_name = "Заболевание гражданина"
        verbose_name_plural = "Заболевания граждан"


class Examination(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Обследование", db_comment="Обследование",)
    direction = models.ForeignKey(
        to=Direction, on_delete=models.CASCADE, verbose_name="Направление",
        related_name=_RELATED_BASE_NAME + "direction", db_comment="Направление",
    )

    class Meta:
        db_table_comment = "Обследование"
        verbose_name = "Обследование"
        verbose_name_plural = "Обследования"


class ExaminationScheme(models.Model):
    examination = models.ForeignKey(to=Examination, on_delete=models.CASCADE, verbose_name="Обследование",
                                    related_name=_RELATED_BASE_NAME + "examination",
                                    db_comment="Обследование")
    scheme = models.JSONField(verbose_name="Схема обследования", db_comment="Схема обследования")

    class Meta:
        db_table_comment = "Схема обследования"
        verbose_name = "Схема обследования"
        verbose_name_plural = "Схемы обследований"


class ExaminationPlan(models.Model):
    person = models.ForeignKey(to=Person, on_delete=models.CASCADE, verbose_name="Гражданин",
                               related_name=_RELATED_BASE_NAME + "person",
                               db_comment="Гражданин",)
    examination = models.ForeignKey(to=Examination, on_delete=models.CASCADE, verbose_name="Обследование",
                                    related_name=_RELATED_BASE_NAME + "examination", db_comment="Обследование",)
    date = models.DateField(verbose_name="Плановая дата обследования", db_comment="Плановая дата обследования")

    class Meta:
        db_table_comment = "План обследования"
        verbose_name = "План обследования"
        verbose_name_plural = "Планы обследований"


class ExaminationFact(models.Model):
    person = models.ForeignKey(to=Person, on_delete=models.CASCADE, verbose_name="Гражданин",
                               related_name=_RELATED_BASE_NAME + "person", db_comment="Гражданин",)
    examination = models.ForeignKey(to=Examination, on_delete=models.CASCADE, verbose_name="Обследование",
                                    related_name=_RELATED_BASE_NAME + "examination", db_comment="Обследование")
    date = models.DateField(verbose_name="Фактическая дата обследования", db_comment="Фактическая дата обследования")
    examination_plan = models.ForeignKey(to=ExaminationPlan, on_delete=models.CASCADE,
                                         verbose_name="Плановое обследование",
                                         related_name=_RELATED_BASE_NAME + "examination_plan",
                                         null=True, blank=True,
                                         db_comment="Плановое обследование",)

    class Meta:
        db_table_comment = "Проведенное обследование"
        verbose_name = "Проведенное обследование"
        verbose_name_plural = "Проведенные обследования"

