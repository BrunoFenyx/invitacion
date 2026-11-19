from django.db import models


class Localidad(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Invitado(models.Model):
    nombre = models.CharField(max_length=75, unique=True)
    telefono = models.CharField(
        "Nro de teléfono",
        max_length=20,
        null=True,
        blank=True,
        unique=True,
    )
    necesita_movilidad = models.BooleanField(
        "¿Necesita movilidad para llegar al evento?",
        default=False,
    )
    puede_acercar = models.BooleanField(
        "¿Puede acercar a algún vecino?",
        default=False,
    )
    lleva_personas = models.PositiveIntegerField(default=0)
    pregunta = models.TextField(
        "¿Tenés alguna pregunta que te gustaría que la política responda? "
        "Tené por seguro que se responderá, Antes o después del evento.",
        blank=True,
        default="",
    )
    vive_en = models.ForeignKey(Localidad, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Invitado"
        verbose_name_plural = "Invitados"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
