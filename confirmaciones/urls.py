from django.urls import path

from . import views

app_name = "confirmaciones"

urlpatterns = [
    path("", views.confirmacion, name="confirmacion"),
]
