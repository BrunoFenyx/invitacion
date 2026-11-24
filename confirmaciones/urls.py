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
    path(
        "dashboard/logistica/conectar/",
        views.conectar_movilidad,
        name="conectar_movilidad",
    ),
    path(
        "dashboard/logistica/desconectar/",
        views.desconectar_movilidad,
        name="desconectar_movilidad",
    ),
    path(
        "dashboard/logistica/reordenar/",
        views.reordenar_logistica,
        name="reordenar_logistica",
    ),
]
