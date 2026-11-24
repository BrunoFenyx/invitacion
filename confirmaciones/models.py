from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
    viaja_con = models.ForeignKey(
        "self",
        verbose_name="Viaja con",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acompanados",
        help_text="Persona que puede acercarlo al evento (si necesita movilidad).",
    )
    orden_necesitan = models.PositiveIntegerField(default=0, editable=False)
    orden_pueden = models.PositiveIntegerField(default=0, editable=False)
    confirmado_en = models.DateTimeField(
        "Fecha de confirmación",
        default=timezone.now,
        editable=False,
    )

    class Meta:
        verbose_name = "Invitado"
        verbose_name_plural = "Invitados"
        ordering = ["nombre"]

    def clean(self):
        super().clean()
        if not self.viaja_con_id:
            return
        if self.viaja_con_id == self.pk:
            raise ValidationError(
                {"viaja_con": "Una persona no puede viajar con sí misma."}
            )
        if not self.viaja_con.puede_acercar:
            raise ValidationError(
                {
                    "viaja_con": (
                        "La persona seleccionada no puede acercar a otros "
                        "al evento."
                    )
                }
            )

    def __str__(self):
        return self.nombre
