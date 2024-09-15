import django_filters as df
from django.db.models.functions import ExtractYear

from .models import ExaminationPlan, ExaminationFact

class NumberInFilter(df.NumberFilter, df.BaseInFilter):
    pass


class ExaminationPlanFilter(df.FilterSet):
    years = df.BaseInFilter(method="filter_years")
    directions = NumberInFilter(field_name="examination__disease__direction_id", lookup_expr='in')
    diseases = NumberInFilter(field_name="examination__disease_id", lookup_expr='in')

    class Meta:
        model = ExaminationPlan
        fields = ["person",]

    def filter_years(self, queryset, name, value):
        print(f'name = {name}, value = {value}')
        qs = queryset.annotate(
            _year=ExtractYear("date_on")
        ).filter(_year__in=value)
        return qs


class ExaminationFactFilter(df.FilterSet):
    years = df.BaseInFilter(method="filter_years")
    directions = NumberInFilter(field_name="examination__disease__direction_id", lookup_expr='in')
    diseases = NumberInFilter(field_name="examination__disease_id", lookup_expr='in')

    class Meta:
        model = ExaminationFact
        fields = ["person",]

    def filter_years(self, queryset, name, value):
        print(f'name = {name}, value = {value}')
        qs = queryset.annotate(
            _year=ExtractYear("date")
        ).filter(_year__in=value)
        return qs
