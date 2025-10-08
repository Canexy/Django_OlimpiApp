from django.db import models
from django.core.exceptions import ValidationError

class Equipos(models.Model):
    OPCIONES_SN = [
        ('S', 'Sí'),
        ('N', 'No'),
    ]
    
    idEqu = models.AutoField(primary_key=True)
    nomEqu = models.CharField(max_length=25, verbose_name='Nombre del equipo:')
    oliEqu = models.CharField(max_length=1, choices=OPCIONES_SN, verbose_name='¿Es olímpico?')
    
    class Meta:
        db_table = 'EQUIPOS'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        constraints = [
            models.CheckConstraint(
                check=models.Q(oliEqu__in=['S', 'N']),
                name='check_oliEqu'
            )
        ]
    
    def __str__(self):
        return self.nomEqu
    
class Disciplinas(models.Model):
    idDis = models.AutoField(primary_key=True)
    nomDis = models.CharField(max_length=50, verbose_name='Nombre de la disciplina:')
    min_equipos = models.PositiveIntegerField(default=1, verbose_name='Mínimo de equipos por encuentro:')
    max_equipos = models.PositiveIntegerField(default=10, verbose_name='Máximo de equipos por encuentro:')
    min_participantes_por_equipo = models.PositiveIntegerField(default=1, verbose_name='Mínimo de participantes por equipo:')
    max_participantes_por_equipo = models.PositiveIntegerField(default=10, verbose_name='Máximo de participantes por equipo:')
    
    class Meta:
        db_table = 'DISCIPLINAS'
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
    
    def __str__(self):
        return self.nomDis
    
class Pistas(models.Model):
    OPCIONES_SN = [
        ('S', 'Sí'),
        ('N', 'No'),
    ]
    
    idPis = models.AutoField(primary_key=True)
    nomPis = models.CharField(max_length=25, verbose_name='Nombre de la pista:')
    cubPis = models.CharField(max_length=1, choices=OPCIONES_SN, verbose_name='¿Está cubierta?')
    
    class Meta:
        db_table = 'PISTAS'
        verbose_name = 'Pista'
        verbose_name_plural = 'Pistas'
        constraints = [
            models.CheckConstraint(
                check=models.Q(cubPis__in=['S', 'N']),
                name='check_cubPis'
            )
        ]
    
    def __str__(self):
        return self.nomPis

class Arbitros(models.Model):
    idArb = models.AutoField(primary_key=True)
    nomArb = models.CharField(max_length=50, verbose_name='Nombre completo:')
    telArb = models.CharField(max_length=9, verbose_name='Teléfono de contacto:')
    conArb = models.EmailField(max_length=75, verbose_name='Correo de contacto:')
    
    class Meta:
        db_table = 'ARBITROS'
        verbose_name = 'Árbitro'
        verbose_name_plural = 'Árbitros'
    
    def __str__(self):
        return self.nomArb

class Participantes(models.Model):
    idPar = models.AutoField(primary_key=True)
    nomPar = models.CharField(max_length=75, verbose_name='Nombre completo:')
    fecPar = models.DateField(verbose_name='Fecha de nacimiento:')
    curPar = models.CharField(max_length=5, verbose_name='Curso:')
    telPar = models.CharField(max_length=9, verbose_name='Teléfono de contacto:')
    conPar = models.EmailField(max_length=75, verbose_name='Correo de contacto:')
    equipo = models.ForeignKey(Equipos, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Equipo al que pertenece')

    class Meta:
        db_table = 'PARTICIPANTES'
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'
    
    def __str__(self):
        return f"{self.nomPar} ({self.curPar})"

class Encuentros(models.Model):
    idEnc = models.AutoField(primary_key=True)
    idDis = models.ForeignKey(Disciplinas, on_delete=models.CASCADE, verbose_name='Disciplina:')
    finiEnc = models.DateTimeField(verbose_name='Fecha de inicio:')
    ffinEnc = models.DateTimeField(verbose_name='Fecha de fin:')
    idPis = models.ForeignKey(Pistas, on_delete=models.CASCADE, verbose_name='Pista:')
    arbitro = models.ForeignKey(Arbitros, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Árbitro asociado:')
    equipos = models.ManyToManyField(Equipos, through='EncuentroEquipo', verbose_name='Equipos participantes:')
    
    class Meta:
        db_table = 'ENCUENTROS'
        verbose_name = 'Encuentro'
        verbose_name_plural = 'Encuentros'
        constraints = [
            models.CheckConstraint(
                check=models.Q(ffinEnc__gt=models.F('finiEnc')),
                name='check_fechas_encuentro'
            )
        ]
    
    def __str__(self):
        return f"Encuentro {self.idEnc} - {self.idDis}"
    
    def clean(self):
        """Solo validación básica de campos directos"""
        super().clean()
        
        if self.finiEnc and self.ffinEnc and self.ffinEnc <= self.finiEnc:
            raise ValidationError({
                'ffinEnc': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
    
    def es_valido_para_disciplina(self):
        """
        Valida si el encuentro cumple todas las reglas de su disciplina
        Retorna: (booleano, lista_de_errores)
        """
        errors = []
        
        if not self.idDis:
            return False, ["No tiene disciplina asignada"]
        
        # Validar número de equipos
        equipos_count = self.equipos.count()
        if not (self.idDis.min_equipos <= equipos_count <= self.idDis.max_equipos):
            errors.append(
                f"Requiere entre {self.idDis.min_equipos} y {self.idDis.max_equipos} equipos. "
                f"Tiene {equipos_count}."
            )
        
        # Validar participantes por equipo
        if equipos_count > 0:
            from django.db.models import Count
            equipos_con_conteo = self.equipos.annotate(
                num_participantes=Count('participantes')
            )
            for equipo in equipos_con_conteo:
                if equipo.num_participantes < self.idDis.min_participantes_por_equipo:
                    errors.append(
                        f"El equipo '{equipo.nomEqu}' tiene {equipo.num_participantes} participantes. "
                        f"Mínimo: {self.idDis.min_participantes_por_equipo}"
                    )
        
        return len(errors) == 0, errors

class EncuentroEquipo(models.Model):
    ROLES_EQUIPO = [
        ('L', 'Local'),
        ('V', 'Visitante'),
    ]
    
    encuentro = models.ForeignKey(Encuentros, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipos, on_delete=models.CASCADE)
    rol = models.CharField(max_length=1, choices=ROLES_EQUIPO, verbose_name='Rol del equipo:')
    
    class Meta:
        db_table = 'ENCUENTRO_EQUIPO'
        unique_together = ('encuentro', 'equipo')
        verbose_name = 'Equipo del Encuentro'
        verbose_name_plural = 'Equipos de Encuentros'