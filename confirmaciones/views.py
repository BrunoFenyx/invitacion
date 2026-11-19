from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import InvitadoForm


def confirmacion(request):
    if request.method == "POST":
        form = InvitadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Gracias! Tu confirmación fue registrada.")
            return redirect("confirmaciones:confirmacion")
    else:
        form = InvitadoForm()

    return render(request, "confirmaciones/confirmacion.html", {"form": form})
