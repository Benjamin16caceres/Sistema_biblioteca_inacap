from django.contrib import admin
from .models import Sala, Reserva

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad', 'estado', 'habilitada']
    list_filter = ['estado', 'habilitada']
    list_editable = ['estado', 'habilitada']
    search_fields = ['nombre']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['sala', 'rut', 'fecha_inicio', 'fecha_termino']
    list_filter = ['sala', 'fecha_inicio']
    search_fields = ['rut', 'sala__nombre']
    readonly_fields = ['fecha_inicio']