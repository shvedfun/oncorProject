from django.db import models
from health.models import _RELATED_BASE_NAME, Region, Direction


class PopulationDistribution(models.Model):
    region = models.ForeignKey(
        to=Region, on_delete=models.CASCADE, verbose_name="Регион", related_name=_RELATED_BASE_NAME + "region"
    )
    distribution = models.JSONField(verbose_name="Распределение популяции")
    updated_at = models.DateTimeField(verbose_name="Изменено", auto_now=True)
    generate_at = models.DateTimeField(verbose_name="Время генерации данных", null=True, blank=True)

    def __str__(self):
        return f'{self.region}'


class GenerateDataType(models.TextChoices):
    population = "population"
    plan = "plan"
    fact = "fact"


class RegionDirectionGenerateData(models.Model):
    region = models.ForeignKey(
        to=Region, on_delete=models.CASCADE, verbose_name="Регион", null=True,
        related_name=_RELATED_BASE_NAME + "region",
    )
    direction = models.ForeignKey(
        to=Direction, on_delete=models.CASCADE, verbose_name="Направление медицины",
        related_name=_RELATED_BASE_NAME + "direction", null=True, blank=True
    )
    date = models.DateTimeField(verbose_name="Дата")
    type = models.CharField(
        choices=GenerateDataType.choices, max_length=10, verbose_name="Тип"
    )
    is_active = models.BooleanField(verbose_name="Активна", default=False)
    data = models.JSONField(verbose_name="Данные")

    class Meta:
        verbose_name = "Данные для генерации распределений"
        verbose_name_plural = "Данные для генерации распределений"

    def __str__(self):
        return "{region} / {direction} / {type}".format(region=self.region, direction=self.direction, type=self.type)