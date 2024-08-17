from django.shortcuts import render, get_object_or_404
from django.db.models import F, Count
from django.db.models.functions import ExtractYear
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic

# Create your views here.
from .models import ExaminationPlan, ExaminationFact
from .utils import get_plan_years

def get_filter_options(request):
    # years = ExaminationPlan.objects.annotate(year=ExtractYear("date_on")).values("year").order_by("year").distinct()
    options = get_plan_years() # [purchase["year"] for purchase in years]
    print(options)
    return JsonResponse({
        "options": options,
    })


class DefaultView(generic.ListView):
    template_name = "health/charts.html"
    model = ExaminationPlan

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context['iam'] = "I am good"
        return context


def get_health_chart(request, year):
    years = get_plan_years()
    qs = ExaminationPlan.objects.annotate(
        year=ExtractYear("date_on")
    ).values("year").annotate(count=Count('id')).order_by("year")
    print(f'qs ={qs}')
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
