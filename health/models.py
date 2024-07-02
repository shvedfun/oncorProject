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
    directions = models.ManyToManyField(
        to=Direction, blank=True,
        through="PersonDirection",
        related_name=_RELATED_BASE_NAME + "direction",
        verbose_name="Направления заболеваний"
    )

    class Meta:
        verbose_name = "Гражданин"
        verbose_name_plural = "Граждане"


class Disease(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Заболевание")
    direction = models.ForeignKey(to=Direction, on_delete=models.PROTECT, verbose_name="Направление заболевания")

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



