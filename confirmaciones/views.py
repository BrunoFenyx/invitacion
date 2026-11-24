import json
from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from openpyxl.styles import Font

from .forms import InvitadoForm
from .models import Invitado, Localidad

DIAS_GRAFICO = 20


def _es_staff(request):
    return request.user.is_authenticated and request.user.is_staff


def _no_autorizado():
    return JsonResponse(
        {"ok": False, "error": "No tenés permiso para realizar esta acción."},
        status=403,
    )


def _leer_json(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        return None


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

    invitados_por_localidad = {}
    invitados = Invitado.objects.select_related("vive_en", "viaja_con").annotate(
        asignados=Count(
            "acompanados", filter=Q(acompanados__necesita_movilidad=True)
        )
    )
    for invitado in invitados:
        if not invitado.necesita_movilidad:
            estado = "verde"
        elif invitado.viaja_con and invitado.viaja_con.puede_acercar:
            estado = "amarillo"
        else:
            estado = "rojo"

        invitados_por_localidad.setdefault(invitado.vive_en.nombre, []).append(
            {
                "id": invitado.id,
                "nombre": invitado.nombre,
                "telefono": invitado.telefono or "",
                "estado": estado,
                "necesita_movilidad": invitado.necesita_movilidad,
                "puede_acercar": invitado.puede_acercar,
                "cupo": max(0, invitado.lleva_personas - invitado.asignados),
                "viaja_con": (
                    invitado.viaja_con.nombre if invitado.viaja_con else ""
                ),
                "viaja_con_id": invitado.viaja_con_id,
                "orden_necesitan": invitado.orden_necesitan,
                "orden_pueden": invitado.orden_pueden,
            }
        )

    contexto = {
        "localidades": localidades,
        "total_confirmados": Invitado.objects.count(),
        "dias_labels": [dia.strftime("%d/%m") for dia in dias],
        "dias_datos": [por_dia.get(dia, 0) for dia in dias],
        "localidades_labels": [localidad.nombre for localidad in localidades],
        "localidades_datos": [localidad.confirmados for localidad in localidades],
        "invitados_por_localidad": invitados_por_localidad,
    }
    return render(request, "confirmaciones/dashboard.html", contexto)


def exportar_invitados(request):
    if not _es_staff(request):
        return redirect("confirmaciones:confirmacion")

    workbook = Workbook()
    hoja = workbook.active
    hoja.title = "Invitados"

    encabezados = [
        "Nombre y apellido",
        "Teléfono",
        "Localidad",
        "¿Necesita movilidad?",
        "¿Puede acercar a alguien?",
        "Personas que puede llevar",
        "Pregunta",
        "Fecha de confirmación",
    ]
    hoja.append(encabezados)
    for celda in hoja[1]:
        celda.font = Font(bold=True)

    for invitado in Invitado.objects.select_related("vive_en").order_by("nombre"):
        hoja.append(
            [
                invitado.nombre,
                invitado.telefono or "",
                invitado.vive_en.nombre,
                "Sí" if invitado.necesita_movilidad else "No",
                "Sí" if invitado.puede_acercar else "No",
                invitado.lleva_personas,
                invitado.pregunta,
                timezone.localtime(invitado.confirmado_en).strftime("%d/%m/%Y %H:%M"),
            ]
        )

    anchos = [28, 18, 20, 20, 26, 24, 50, 20]
    for indice, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[chr(64 + indice)].width = ancho

    respuesta = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    )
    nombre = f"invitados_{timezone.localdate():%Y%m%d}.xlsx"
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    workbook.save(respuesta)
    return respuesta


def _cupo_disponible(conductor, excluir_id=None):
    asignados = conductor.acompanados.filter(necesita_movilidad=True)
    if excluir_id is not None:
        asignados = asignados.exclude(pk=excluir_id)
    return max(0, conductor.lleva_personas - asignados.count())


@require_POST
def conectar_movilidad(request):
    if not _es_staff(request):
        return _no_autorizado()

    datos = _leer_json(request)
    if datos is None:
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    try:
        necesita_id = int(datos.get("necesita_id"))
        puede_id = int(datos.get("puede_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    necesita = get_object_or_404(Invitado, pk=necesita_id)
    puede = get_object_or_404(Invitado, pk=puede_id)

    if necesita.pk == puede.pk:
        return JsonResponse(
            {"ok": False, "error": "No puede conectarse consigo misma."},
            status=400,
        )
    if not necesita.necesita_movilidad:
        return JsonResponse(
            {"ok": False, "error": "La persona no necesita movilidad."},
            status=400,
        )
    if not puede.puede_acercar:
        return JsonResponse(
            {"ok": False, "error": "La persona no puede acercar a otros."},
            status=400,
        )
    if necesita.vive_en_id != puede.vive_en_id:
        return JsonResponse(
            {
                "ok": False,
                "error": "Ambas personas deben pertenecer a la misma localidad.",
            },
            status=400,
        )
    if necesita.viaja_con_id == puede.pk:
        return JsonResponse(
            {
                "ok": True,
                "viaja_con": puede.nombre,
                "cupo": _cupo_disponible(puede),
            }
        )
    if _cupo_disponible(puede, excluir_id=necesita.pk) <= 0:
        return JsonResponse(
            {"ok": False, "error": "La persona no tiene espacios disponibles."},
            status=400,
        )

    necesita.viaja_con = puede
    necesita.save(update_fields=["viaja_con"])

    return JsonResponse(
        {
            "ok": True,
            "viaja_con": puede.nombre,
            "cupo": _cupo_disponible(puede),
        }
    )


@require_POST
def desconectar_movilidad(request):
    if not _es_staff(request):
        return _no_autorizado()

    datos = _leer_json(request)
    if datos is None:
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    try:
        necesita_id = int(datos.get("necesita_id"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    necesita = get_object_or_404(Invitado, pk=necesita_id)
    conductor = necesita.viaja_con
    necesita.viaja_con = None
    necesita.save(update_fields=["viaja_con"])

    cupo = _cupo_disponible(conductor) if conductor else None
    return JsonResponse({"ok": True, "cupo": cupo})


@require_POST
def reordenar_logistica(request):
    if not _es_staff(request):
        return _no_autorizado()

    datos = _leer_json(request)
    if datos is None:
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    lista = datos.get("lista")
    campos = {
        "necesitan": "orden_necesitan",
        "pueden": "orden_pueden",
    }
    campo = campos.get(lista)
    ids = datos.get("ids")
    if not campo or not isinstance(ids, list) or not ids:
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    try:
        ids = [int(pk) for pk in ids]
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    if len(ids) != len(set(ids)):
        return JsonResponse({"ok": False, "error": "Datos inválidos."}, status=400)

    with transaction.atomic():
        existentes = set(
            Invitado.objects.filter(pk__in=ids).values_list("pk", flat=True)
        )
        if existentes != set(ids):
            return JsonResponse(
                {"ok": False, "error": "Hay invitados inexistentes."},
                status=400,
            )
        for posicion, pk in enumerate(ids):
            Invitado.objects.filter(pk=pk).update(**{campo: posicion})

    return JsonResponse({"ok": True})
