from datetime import datetime
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from .models import Categoria, Transaccion, TransaccionProgramada

# Actions


def duplicar_y_editar(modeladmin, request, queryset):
    for objeto in queryset:
        # Esto asegura que se cree una nueva instancia en lugar de actualizar la existente
        objeto.id = None
        objeto.save()
        return redirect(f"/admin/app/transaccion/{objeto.id}/change/")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'grupo')


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    actions = [duplicar_y_editar]
    list_display = ('id', 'tipo_transaccion', 'categoria',
                    'descripcion', 'cantidad', 'fecha')
    list_filter = ('realizada', 'categoria')
    ordering = ('-fecha',)

    def changelist_view(self, request, extra_context=None):
        if not request.META['QUERY_STRING'] and not 'realizada__exact' in request.GET:
            # Redirigir a la misma página con el filtro aplicado
            return HttpResponseRedirect(request.path + '?realizada__exact=1')

        return super().changelist_view(request, extra_context=extra_context)

    def get_changeform_initial_data(self, request):
        initial_data = super().get_changeform_initial_data(request)
        # Set default value for the "tipo_transaccion" field
        initial_data['tipo_transaccion'] = 'G'
        # Set default value for the "fecha" field to the current date and time
        initial_data['fecha'] = datetime.now()  # type: ignore
        return initial_data


@admin.register(TransaccionProgramada)
class TransaccionProgramadaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cantidad', 'categoria',
                    'inicio', 'final', 'frecuencia')
