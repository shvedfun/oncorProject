from django.urls import path
from . import views

app_name = "health"


urlpatterns = [
    path("filter-options/", views.get_filter_options, name="filter-options"),
    path("health-plan-chart/", views.get_health_plan_chart, name="health-plan-chart"),
    path("health-fact-chart/<int:year>/", views.get_health_fact_chart, name="health-fact-chart"),
    path("", views.DefaultView.as_view(), name='charts'),
]

