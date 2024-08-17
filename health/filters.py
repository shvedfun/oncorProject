import django_filters as df
from django.db.models.functions import ExtractYear

from .models import ExaminationPlan


class ExaminationPlanFilter(df.FilterSet):
    years = df.AllValuesMultipleFilter(method="filter_by_year", null_value=True)

    class Meta:
        model = ExaminationPlan
        fields = ["years", "person"]

    def filter_by_year(self, queryset, name, value):
        print(f'name = {name}')
        qs = queryset.annotate(
            _year=ExtractYear("date_on")
        ).filter(_year__in=value)
        return qs
