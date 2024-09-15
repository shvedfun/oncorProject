from django.shortcuts import render, get_object_or_404
from django.db.models import F, Count, QuerySet
from django.db.models.functions import ExtractYear
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic

from .models import ExaminationPlan, ExaminationFact, Direction, Disease
from .filters import ExaminationPlanFilter, ExaminationFactFilter


def get_plan_years() -> list:
    years = ExaminationPlan.objects.annotate(year=ExtractYear("date_on")).values_list(
        "year", flat=True
    ).order_by("year").distinct()
    return list(years)


def get_years_qs(qs: QuerySet, name_date_fileld: str) -> QuerySet:
    return qs.annotate(_year=ExtractYear(name_date_fileld)).values_list(
        "_year", flat=True
    ).order_by("_year").distinct()


def get_directions() -> list:
    directions = Direction.objects.values_list("id", "name").order_by("name")
    return list(directions)

def get_diseases(directions_ids: list=None ):
    qs = Disease.objects.values_list("id", "name").order_by("id")
    if directions_ids:
        qs = qs.filter(direction_id__in=directions_ids)
    return list(qs)

def get_fact_count(query_params={}) -> QuerySet:
    qs = ExaminationFact.objects.annotate(
        year=ExtractYear("date")
    ).values("year").annotate(count=Count('id')).order_by("year")
    print(f'qs ={qs}')
    qs = ExaminationFactFilter(query_params, queryset=qs).qs
    return qs


def get_plan_count(query_params={}) -> QuerySet:
    qs = ExaminationPlan.objects.annotate(
        year=ExtractYear("date_on")
    ).values("year").annotate(count=Count('id')).order_by("year")
    print(f'qs ={qs}')
    qs = ExaminationPlanFilter(query_params, queryset=qs).qs
    return qs