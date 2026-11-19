from django import forms

from .models import Invitado


class InvitadoForm(forms.ModelForm):
    TELEFONO_PREFIJO = "+549"

    class Meta:
        model = Invitado
        fields = [
            "nombre",
            "telefono",
            "vive_en",
            "necesita_movilidad",
            "puede_acercar",
            "lleva_personas",
            "pregunta",
        ]
        labels = {
            "nombre": "Nombre y apellido",
            "telefono": "Nro de teléfono",
            "vive_en": "Localidad",
            "necesita_movilidad": "¿Necesitas movilidad para llegar al evento?",
            "puede_acercar": "¿Podrías acercar a algún vecino?",
            "lleva_personas": "¿Cuántas personas podrías llevar?",
            "pregunta": (
                "¿Tenés alguna pregunta que te gustaría que la política responda? "
                "Tené por seguro que se responderá, Antes o después del evento."
            ),
        }
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Ej: Juan Pérez",
                    "autocomplete": "name",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "placeholder": "+549...",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                }
            ),
            "vive_en": forms.Select(),
            "necesita_movilidad": forms.CheckboxInput(),
            "puede_acercar": forms.CheckboxInput(),
            "lleva_personas": forms.NumberInput(attrs={"min": 1, "value": 1}),
            "pregunta": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Escribí tu pregunta (opcional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lleva_personas"].required = False
        self.fields["telefono"].required = True
        self.fields["pregunta"].required = False
        if not self.is_bound and not self.initial.get("telefono"):
            self.initial["telefono"] = self.TELEFONO_PREFIJO

    def clean_telefono(self):
        telefono = (self.cleaned_data.get("telefono") or "").strip()
        normalizado = telefono.replace(" ", "").replace("-", "")

        if not normalizado.startswith(self.TELEFONO_PREFIJO):
            raise forms.ValidationError(
                f"El número debe comenzar con {self.TELEFONO_PREFIJO}."
            )

        numero = normalizado[len(self.TELEFONO_PREFIJO):]
        if not numero.isdigit() or len(numero) < 8:
            raise forms.ValidationError(
                "Ingresá un número de teléfono válido después del prefijo "
                f"{self.TELEFONO_PREFIJO}."
            )

        return normalizado

    def clean(self):
        cleaned_data = super().clean()
        puede_acercar = cleaned_data.get("puede_acercar")
        lleva_personas = cleaned_data.get("lleva_personas")

        if puede_acercar:
            if not lleva_personas or lleva_personas < 1:
                self.add_error(
                    "lleva_personas",
                    "Indicá cuántas personas podrías llevar.",
                )
        else:
            cleaned_data["lleva_personas"] = 0

        return cleaned_data
