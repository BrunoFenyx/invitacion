from django.contrib import admin

from .models import Invitado, Localidad


@admin.register(Localidad)
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Invitado)
class InvitadoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "telefono",
        "vive_en",
        "necesita_movilidad",
        "puede_acercar",
        "lleva_personas",
        "viaja_con",
    )
    list_filter = ("necesita_movilidad", "puede_acercar", "vive_en")
    list_select_related = ("vive_en", "viaja_con")
    search_fields = ("nombre", "telefono")
    autocomplete_fields = ("viaja_con",)
