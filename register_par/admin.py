from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Equipos, Disciplinas, Pistas, Arbitros, Participantes, Encuentros, EncuentroEquipo

admin.site.register(Equipos)
admin.site.register(Disciplinas)
admin.site.register(Pistas)
admin.site.register(Arbitros)
admin.site.register(Participantes)

class EncuentroEquipoFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """Valida reglas de negocio sin depender del objeto guardado"""
        super().clean()
        
        if any(self.errors):
            return
            
        if hasattr(self, 'instance') and hasattr(self.instance, 'idDis') and self.instance.idDis:
            disciplina = self.instance.idDis
            
            # Contar equipos que no se eliminan
            equipos_count = 0
            equipos_instances = []
            
            for form in self.forms:
                if (not form.cleaned_data.get('DELETE', False) and 
                    form.cleaned_data.get('equipo')):
                    equipos_count += 1
                    equipos_instances.append(form.cleaned_data['equipo'])
            
            # Validar número de equipos
            if not (disciplina.min_equipos <= equipos_count <= disciplina.max_equipos):
                raise ValidationError(
                    f"Esta disciplina requiere entre {disciplina.min_equipos} y {disciplina.max_equipos} equipos. "
                    f"Tiene {equipos_count} equipos."
                )
            
            # Validar participantes por equipo
            if equipos_count > 0:
                from django.db.models import Count
                equipos_con_ids = [equipo.idEqu for equipo in equipos_instances]
                equipos_con_conteo = Equipos.objects.filter(idEqu__in=equipos_con_ids).annotate(
                    num_participantes=Count('participantes')
                )
                
                for equipo in equipos_con_conteo:
                    if equipo.num_participantes < disciplina.min_participantes_por_equipo:
                        raise ValidationError(
                            f"El equipo '{equipo.nomEqu}' tiene {equipo.num_participantes} participantes. "
                            f"Mínimo requerido: {disciplina.min_participantes_por_equipo}"
                        )

class EncuentroEquipoInline(admin.TabularInline):
    model = EncuentroEquipo
    formset = EncuentroEquipoFormSet
    extra = 1
    min_num = 1

@admin.register(Encuentros)
class EncuentrosAdmin(admin.ModelAdmin):
    inlines = [EncuentroEquipoInline]
    list_display = ['idEnc', 'idDis', 'finiEnc', 'ffinEnc', 'idPis', 'arbitro']
    list_filter = ['idDis', 'idPis', 'finiEnc']

"""
FORM SET: EncuentroEquipoFormSet

FINALIDAD:
Validar las reglas de negocio ANTES de que el encuentro se guarde,
mostrando errores en el formulario como validaciones nativas de Django.

QUÉ VALIDA:
1. Número de equipos dentro del rango permitido por la disciplina
2. Que cada equipo tenga suficientes participantes
3. Previene completamente el guardado de encuentros inválidos

CUÁNDO SE EJECUTA:
Durante la validación del formulario del admin, antes del guardado.
"""