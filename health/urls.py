from django.urls import path
from . import views

app_name = "health"


urlpatterns = [
    path("", views.DefaultView.as_view(), name='charts'),
]