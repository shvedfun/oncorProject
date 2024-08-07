from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

# Create your views here.
from .models import ExaminationPlan, ExaminationFact

class DefaultView(generic.ListView):
    template_name = "health/charts.html"
    model = ExaminationPlan

