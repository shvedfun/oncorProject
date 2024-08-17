from django.shortcuts import render, get_object_or_404
from django.db.models import F, Count
from django.db.models.functions import ExtractYear
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic

from .models import ExaminationPlan, ExaminationFact


def get_plan_years() -> list:
    years = ExaminationPlan.objects.annotate(year=ExtractYear("date_on")).values_list(
        "year", flat=True
    ).order_by("year").distinct()
    return list(years.all())