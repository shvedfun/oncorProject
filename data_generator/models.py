from django.db import models
from health.models import _RELATED_BASE_NAME, Region
# Create your models here.
class PopulationDistribution(models.Model):
    region = models.ForeignKey(
        to=Region, on_delete=models.CASCADE, verbose_name="Регион", related_name=_RELATED_BASE_NAME + "region"
    )
    distribution = models.JSONField(verbose_name="Распределение популяции")
    updated_at = models.DateTimeField(verbose_name="Изменено", auto_now=True)
    generate_at = models.DateTimeField(verbose_name="Время генерации данных", null=True, blank=True)
