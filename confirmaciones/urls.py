from django.urls import path

from . import views

app_name = "confirmaciones"

urlpatterns = [
    path("", views.confirmacion, name="confirmacion"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "dashboard/exportar/",
        views.exportar_invitados,
        name="exportar_invitados",
    ),
]
