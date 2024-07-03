from django.db import models

# Create your models here.


_RELATED_BASE_NAME = "%(model_name)s_from_"


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name="Регион")
    code = models.CharField(max_length=2, verbose_name="Код региона")

    def __str__(self):
        return f'{self.code} - {self.name}'

    class Meta:
        verbose_name = "Регион"
        verbose_name_plural = "Регионы"


class Direction(models.Model):
    name = models.CharField(max_length=100, verbose_name="Направление")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"


class State(models.Model):
    name = models.CharField(max_length=100, verbose_name="Группа")

    class Meta:
        verbose_name = "Группа населения"
        verbose_name_plural = "Группы населения"


class GenderEnum(models.TextChoices):
    MAN = "М"
    WOMAN = "Ж"


class Person(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО")
    gender = models.CharField(choices=GenderEnum.choices, max_length=1, verbose_name="Пол")
    birthday = models.DateTimeField(verbose_name="Дата рождения")
    diseases = models.ManyToManyField(
        to="Disease", blank=True,
        through="PersonDisease",
        related_name=_RELATED_BASE_NAME + "Disease",
        verbose_name="Заболевания"
    )

    class Meta:
        verbose_name = "Гражданин"
        verbose_name_plural = "Граждане"


class Disease(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Заболевание")
    direction = models.ForeignKey(to=Direction, on_delete=models.CASCADE, verbose_name="Направление заболевания")

    class Meta:
        verbose_name = "Заболевание"
        verbose_name_plural = "Заболевания"


class PersonDisease(models.Model):
    person = models.ForeignKey(
        to=Person,
        on_delete=models.CASCADE,
        verbose_name="Гражданин",
        related_name=_RELATED_BASE_NAME + 'person'
    )
    disease = models.ForeignKey(
        to=Disease,
        on_delete=models.CASCADE,
        verbose_name="Заболевание",
        related_name=_RELATED_BASE_NAME + 'disease'
    )
    state = models.ForeignKey(
        to=State,
        on_delete=models.CASCADE,
        verbose_name="Статус",
        related_name=_RELATED_BASE_NAME + 'state'
    )
    start_from = models.DateTimeField(verbose_name="Дата диагноза")

    class Meta:
        verbose_name = "Заболевание гражданина"
        verbose_name_plural = "Заболевания граждан"


class Examination(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Обследование")
    direction = models.ForeignKey(
        to=Direction, on_delete=models.CASCADE, verbose_name="Направление",
        related_name=_RELATED_BASE_NAME + "direction"
    )

    class Meta:
        verbose_name = "Обследование"
        verbose_name_plural = "Обследования"


class ExaminationScheme(models.Model):
    examination = models.ForeignKey(to=Examination, on_delete=models.CASCADE, verbose_name="Обследование",
                                    related_name=_RELATED_BASE_NAME + "examination")
    scheme = models.JSONField(verbose_name="Схема обследования")

    class Meta:
        verbose_name = "Схема обследования"
        verbose_name_plural = "Схемы обследований"


class ExaminationPlan(models.Model):
    person = models.ForeignKey(to=Person, on_delete=models.CASCADE, verbose_name="Гражданин",
                               related_name=_RELATED_BASE_NAME + "person")
    examination = models.ForeignKey(to=Examination, on_delete=models.CASCADE, verbose_name="Обследование",
                                    related_name=_RELATED_BASE_NAME + "examination")
    date = models.DateField(verbose_name="Плановая дата обследования")

    class Meta:
        verbose_name = "План обследования"
        verbose_name_plural = "Планы обследований"


class ExaminationFact(models.Model):
    person = models.ForeignKey(to=Person, on_delete=models.CASCADE, verbose_name="Гражданин",
                               related_name=_RELATED_BASE_NAME + "person")
    examination = models.ForeignKey(to=Examination, on_delete=models.CASCADE, verbose_name="Обследование",
                                    related_name=_RELATED_BASE_NAME + "examination")
    date = models.DateField(verbose_name="Фактическая дата обследования")
    examination_plan = models.ForeignKey(to=ExaminationPlan, on_delete=models.CASCADE,
                                         verbose_name="Плановое обследование",
                                         related_name=_RELATED_BASE_NAME + "examination_plan",
                                         null=True, blank=True)

    class Meta:
        verbose_name = "Проведенное обследование"
        verbose_name_plural = "Проведенные обследования"


