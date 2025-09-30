from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Encuentros

@receiver(m2m_changed, sender=Encuentros.equipos.through)
def validar_equipos_encuentro(sender, instance, action, **kwargs):
    """
    Valida CUANDO SE MODIFICAN los equipos de un encuentro
    """
    if action in ["pre_add", "pre_remove"]:
        if instance.idDis:
            nuevos_equipos_count = instance.equipos.count()
            
            if action == "pre_add":
                nuevos_equipos_count += len(kwargs['pk_set'])
            elif action == "pre_remove":
                nuevos_equipos_count -= len(kwargs['pk_set'])
            
            if not (instance.idDis.min_equipos <= nuevos_equipos_count <= instance.idDis.max_equipos):
                raise ValidationError(
                    f"No se pueden tener {nuevos_equipos_count} equipos. "
                    f"Límites: {instance.idDis.min_equipos}-{instance.idDis.max_equipos}"
                )