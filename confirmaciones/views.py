from datetime import timedelta

from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import InvitadoForm
from .models import Invitado, Localidad

DIAS_GRAFICO = 20


def _es_staff(request):
    return request.user.is_authenticated and request.user.is_staff


def confirmacion(request):
    if _es_staff(request):
        return redirect("confirmaciones:dashboard")

    if request.method == "POST":
        form = InvitadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Gracias! Tu confirmación fue registrada.")
            return redirect("confirmaciones:confirmacion")
    else:
        form = InvitadoForm()

    return render(request, "confirmaciones/confirmacion.html", {"form": form})


def dashboard(request):
    if not _es_staff(request):
        return redirect("confirmaciones:confirmacion")

    localidades = Localidad.objects.annotate(
        confirmados=Count("invitado"),
        necesitan_movilidad=Count(
            "invitado", filter=Q(invitado__necesita_movilidad=True)
        ),
        pueden_acercar=Count("invitado", filter=Q(invitado__puede_acercar=True)),
    ).order_by("nombre")

    hoy = timezone.localdate()
    desde = hoy - timedelta(days=DIAS_GRAFICO - 1)
    por_dia = {
        dia: total
        for dia, total in Invitado.objects.filter(
            confirmado_en__date__gte=desde
        )
        .annotate(dia=TruncDate("confirmado_en"))
        .values("dia")
        .annotate(total=Count("id"))
        .values_list("dia", "total")
    }
    dias = [desde + timedelta(days=i) for i in range(DIAS_GRAFICO)]

    contexto = {
        "localidades": localidades,
        "total_confirmados": Invitado.objects.count(),
        "dias_labels": [dia.strftime("%d/%m") for dia in dias],
        "dias_datos": [por_dia.get(dia, 0) for dia in dias],
        "localidades_labels": [localidad.nombre for localidad in localidades],
        "localidades_datos": [localidad.confirmados for localidad in localidades],
    }
    return render(request, "confirmaciones/dashboard.html", contexto)
