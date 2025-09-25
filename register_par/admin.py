from django.contrib import admin

from .models import Equipos, Disciplinas, Pistas, Arbitros, Participantes, Encuentros, EncuentroEquipo

admin.site.register(Equipos)
admin.site.register(Disciplinas)
admin.site.register(Pistas)
admin.site.register(Arbitros)
admin.site.register(Participantes)
admin.site.register(Encuentros)
admin.site.register(EncuentroEquipo)
