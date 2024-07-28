from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# Create your models here.


_RELATED_BASE_NAME = "%(model_name)s_from_"


class Region(models.Model):
    code = models.CharField(max_length=2, verbose_name="Код региона", db_comment="Код региона",
                            primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Регион", db_comment="Регион",)

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
    ALL = "МЖ"

    @classmethod
    def only_m_w_validator(cls, value):
        if value == cls.ALL:
            raise ValidationError(
                _("%(value)s не поддерживается для гражданина"),
                params={"value": value},
            )


class Person(models.Model):
    name = models.CharField(max_length=200, verbose_name="ФИО", db_comment="ФИО")
    gender = models.CharField(choices=GenderEnum.choices, max_length=2, verbose_name="Пол", db_comment="Пол",
                              validators=[GenderEnum.only_m_w_validator])
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

    def __str__(self):
        return f'{self.name} ({self.id})'

    class Meta:
        db_table_comment = "Гражданин"
        verbose_name = "Гражданин"
        verbose_name_plural = "Граждане"


class DiseaseCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование", db_comment="Наименование")

    def __str__(self):
        return f'{self.name}({self.id})'

    class Meta:
        db_table_comment = "Категория заболевания"
        verbose_name = "Категория заболевания"
        verbose_name_plural = "Категории заболеваний"


class Disease(models.Model):
    name = models.CharField(max_length=1000, verbose_name="Заболевание", db_comment="Заболевание",)
    direction = models.ForeignKey(to=Direction, on_delete=models.CASCADE,
                                  verbose_name="Направление заболевания", db_comment="Направление заболевания",
                                  related_name=_RELATED_BASE_NAME + "direction"
                                  )
    category = models.ForeignKey(
        to=DiseaseCategory, on_delete=models.PROTECT, verbose_name="Категория", db_comment="Категория",
        related_name=_RELATED_BASE_NAME + "category", null=True
    )
    gender = models.CharField(
        choices=GenderEnum.choices, max_length=2, verbose_name="Пол", db_comment="Пол", default=GenderEnum.ALL
    )

    def __str__(self):
        return f'{self.name} - ({self.id})'

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

    def __str__(self):
        return f'person_id({self.person_id}) - disease_id({self.disease_id})'

    class Meta:
        db_table_comment = "Заболевание гражданина"
        verbose_name = "Заболевание гражданина"
        verbose_name_plural = "Заболевания граждан"


class Procedure(models.Model):
    name = models.CharField(max_length=100, verbose_name="Наименование", db_comment="Наименование")

    def __str__(self):
        return f'{self.name} ({self.id})'

    class Meta:
        db_table_comment = "Процедура обследования"
        verbose_name = "Процедура обследования"
        verbose_name_plural = "Процедуры обследования"


class Applicability(models.Model):
    from_age = models.PositiveSmallIntegerField(verbose_name="Возраст начала обследования")
    to_age = models.PositiveSmallIntegerField(verbose_name="Возраст окончания обследования")
    periodicity = models.FloatField(verbose_name="период обследования в годах")

    def __str__(self):
        return f'С {self.from_age} до {self.to_age} лет. Периодичность раз в {self.periodicity} год(а).'

    class Meta:
        db_table_comment = "Применимость обследования"
        verbose_name = "Применимость обследования"
        verbose_name_plural = "Применимость обследований"

        unique_together = [
            ("from_age", "to_age", "periodicity")
        ]


class Examination(models.Model):
    name = models.CharField(max_length=200, verbose_name="Обследование", db_comment="Обследование",)
    disease = models.ForeignKey(
        to=Disease,
        on_delete=models.CASCADE,
        verbose_name="Заболевание",
        related_name=_RELATED_BASE_NAME + 'disease',
        db_comment="Заболевание",
        null=True
    )
    applicability = models.ForeignKey(
        to=Applicability, on_delete=models.PROTECT, verbose_name="Применимость",
        related_name=_RELATED_BASE_NAME + "applicability", db_comment="Применимость", null=True
    )
    procedure = models.ManyToManyField(to=Procedure, related_name=_RELATED_BASE_NAME + "procedure")
    examination_scheme = models.JSONField(
        verbose_name="Схема обследования", db_comment="Схема обследования", null=True
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table_comment = "Обследование"
        verbose_name = "Обследование"
        verbose_name_plural = "Обследования"


class ExaminationScheme(models.Model):
    examination = models.ForeignKey(to=Examination, on_delete=models.CASCADE, verbose_name="Обследование",
                                    related_name=_RELATED_BASE_NAME + "examination",
                                    db_comment="Обследование")
    scheme = models.JSONField(verbose_name="Схема обследования", db_comment="Схема обследования")

    def __str__(self):
        return f'{self.examination_id}'

    class Meta:
        db_table_comment = "Схема обследования"
        verbose_name = "Схема обследования"
        verbose_name_plural = "Схемы обследований"


class ExaminationPlan(models.Model):
    person = models.ForeignKey(to=Person, on_delete=models.CASCADE, verbose_name="Гражданин",
                               related_name=_RELATED_BASE_NAME + "person",
                               db_comment="Гражданин",)
    examination = models.ForeignKey(
        to=Examination, on_delete=models.CASCADE,
        verbose_name="Обследование", related_name=_RELATED_BASE_NAME + "examination",
        db_comment="Обследование",
    )
    date_on = models.DateField(verbose_name="Плановая дата обследования", db_comment="Плановая дата обследования")

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


