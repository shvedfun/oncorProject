from django.urls import path
from . import views

app_name = "health"


urlpatterns = [
    path("filter-options/", views.get_filter_options, name="filter-options"),
    path("health-chart/<int:year>/", views.get_health_chart, name="health-chart"),
    path("", views.DefaultView.as_view(), name='charts'),
]

