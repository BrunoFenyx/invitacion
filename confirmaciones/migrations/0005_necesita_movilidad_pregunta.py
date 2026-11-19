from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("confirmaciones", "0004_telefono_puede_acercar"),
    ]

    operations = [
        migrations.RenameField(
            model_name="invitado",
            old_name="puede_llegar",
            new_name="necesita_movilidad",
        ),
        migrations.AlterField(
            model_name="invitado",
            name="necesita_movilidad",
            field=models.BooleanField(
                default=False,
                verbose_name="¿Necesita movilidad para llegar al evento?",
            ),
        ),
        migrations.AddField(
            model_name="invitado",
            name="pregunta",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name=(
                    "¿Tenés alguna pregunta que te gustaría que la política "
                    "responda? Tené por seguro que se responderá, Antes o "
                    "después del evento."
                ),
            ),
        ),
    ]
