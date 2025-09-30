from django.contrib import admin
from .models import Equipos, Disciplinas, Pistas, Arbitros, Participantes, Encuentros, EncuentroEquipo

admin.site.register(Equipos)
admin.site.register(Disciplinas)
admin.site.register(Pistas)
admin.site.register(Arbitros)
admin.site.register(Participantes)

class EncuentroEquipoInline(admin.TabularInline):
    model = EncuentroEquipo
    extra = 2  # Muestra 2 slots por defecto.
    # max_num = 10  # Límite visual.

@admin.register(Encuentros)
class EncuentrosAdmin(admin.ModelAdmin):
    inlines = [EncuentroEquipoInline]