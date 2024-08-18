from django.shortcuts import render, get_object_or_404
from django.db.models import F, Count, ExpressionWrapper, IntegerField
from django.db.models.functions import ExtractYear
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic

# Create your views here.
from .models import ExaminationPlan, ExaminationFact
from .utils import get_plan_years, get_years_qs, get_directions, get_diseases, get_plan_count, get_fact_count
from .filters import ExaminationPlanFilter, ExaminationFactFilter

from .utils_chart import colorPalette, colorDanger, colorSuccess, colorPrimary

def get_filter_options(request):
    # years = ExaminationPlan.objects.annotate(year=ExtractYear("date_on")).values("year").order_by("year").distinct()
    years = get_plan_years() # [purchase["year"] for purchase in years]
    directions = get_directions()
    direction_ids = [x[0] for x in directions]
    diseases = get_diseases(direction_ids)
    return JsonResponse({
        "years": years,
        "directions": directions,
        "diseases": diseases
    })


class DefaultView(generic.ListView):
    template_name = "health/charts.html"
    model = ExaminationPlan

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['iam'] = "I am good"
        return context


def get_health_plan_chart(request):
    qs = get_plan_count(request.GET)
    print(f'qs ={qs.query}')
    years = list(get_years_qs(qs, "date_on"))
    result = {
        "title": f"План за годы {years}",
        "data": {
            "labels": years,
            "datasets": [{
                "label": "Количество",
                "data": list(qs.values_list('count', flat=True))
            }]
        }

    }
    print(f'result = {result}')
    return JsonResponse(result)


def get_health_fact_chart(request):
    qs = get_fact_count(request.GET)
    years = list(get_years_qs(qs, "date"))
    result = {
        "title": f"Факт за годы {years}",
        "data": {
            "labels": years,
            "datasets": [{
                "label": "Количество",
                "data": list(qs.values_list('count', flat=True))
            }]
        }

    }
    print(f'result = {result}')
    return JsonResponse(result)


def get_health_plan_fact_chart(request):
    fact_qs = get_fact_count(request.GET)
    plan_qs = get_plan_count(request.GET)
    plan_years = list(get_years_qs(plan_qs, "date_on"))
    fact_years = list(get_years_qs(fact_qs, "date"))
    result = {
        "title": f"Факт за годы {fact_years}",
        "data": {
            "labels": plan_years,
            "datasets": [{
                "label": ["План"],
                "backgroundColor": [colorSuccess],
                "borderColor": [colorSuccess],
                "data": list(plan_qs.values_list('count', flat=True)),
            },
                {
                    "label": ["Факт"],
                    "backgroundColor": [colorDanger],
                    "borderColor": [colorDanger],
                    "data": list(fact_qs.values_list('count', flat=True)),

                }
            ]
        }

    }
    print(f'result = {result}')
    return JsonResponse(result)
