from django.db import migrations


ZONAS_ANTERIORES = ["Centro", "Norte", "Sur", "Costa", "Sierras"]
ZONAS_NUEVAS = [
    "Los Claveles",
    "Salto de las Rosas",
    "Calle Larga",
    "Linea Ancha",
    "El Tropezón",
    "La Pichana",
    "Otro",
]


def actualizar_zonas(apps, schema_editor):
    Localidad = apps.get_model("confirmaciones", "Localidad")
    Localidad.objects.filter(nombre__in=ZONAS_ANTERIORES).delete()
    for nombre in ZONAS_NUEVAS:
        Localidad.objects.get_or_create(nombre=nombre)


def revertir_zonas(apps, schema_editor):
    Localidad = apps.get_model("confirmaciones", "Localidad")
    Localidad.objects.filter(nombre__in=ZONAS_NUEVAS).delete()
    for nombre in ZONAS_ANTERIORES:
        Localidad.objects.get_or_create(nombre=nombre)


class Migration(migrations.Migration):

    dependencies = [
        ("confirmaciones", "0002_localidades_iniciales"),
    ]

    operations = [
        migrations.RunPython(actualizar_zonas, revertir_zonas),
    ]
