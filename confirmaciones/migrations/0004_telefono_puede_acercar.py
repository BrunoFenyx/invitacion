from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("confirmaciones", "0003_zonas_iniciales"),
    ]

    operations = [
        migrations.RenameField(
            model_name="invitado",
            old_name="movilidad",
            new_name="puede_llegar",
        ),
        migrations.RenameField(
            model_name="invitado",
            old_name="celular",
            new_name="telefono",
        ),
        migrations.AlterField(
            model_name="invitado",
            name="telefono",
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                unique=True,
                verbose_name="Nro de teléfono",
            ),
        ),
        migrations.AlterField(
            model_name="invitado",
            name="puede_llegar",
            field=models.BooleanField(
                default=False,
                verbose_name="¿Puede llegar al evento?",
            ),
        ),
        migrations.AddField(
            model_name="invitado",
            name="puede_acercar",
            field=models.BooleanField(
                default=False,
                verbose_name="¿Puede acercar a algún vecino?",
            ),
        ),
    ]
