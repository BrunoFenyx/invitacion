from django.db import migrations


LOCALIDADES = ["Centro", "Norte", "Sur", "Costa", "Sierras"]


def crear_localidades(apps, schema_editor):
    Localidad = apps.get_model("confirmaciones", "Localidad")
    for nombre in LOCALIDADES:
        Localidad.objects.get_or_create(nombre=nombre)


def borrar_localidades(apps, schema_editor):
    Localidad = apps.get_model("confirmaciones", "Localidad")
    Localidad.objects.filter(nombre__in=LOCALIDADES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("confirmaciones", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_localidades, borrar_localidades),
    ]
