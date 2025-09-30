from django.db import models
from django.core.exceptions import ValidationError

# Class 'Equipos'.

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
    
# Class 'Disciplinas' (o deportes).

class Disciplinas(models.Model):
    idDis = models.AutoField(primary_key=True)
    nomDis = models.CharField(max_length=50, verbose_name='Nombre de la disciplina:')
    min_equipos = models.PositiveIntegerField(default=2, verbose_name='Mínimo de equipos por encuentro:')
    max_equipos = models.PositiveIntegerField(default=2, verbose_name='Máximo de equipos por encuentro:')
    min_participantes_por_equipo = models.PositiveIntegerField(default=1, verbose_name='Mínimo de participantes por equipo:')
    max_participantes_por_equipo = models.PositiveIntegerField(default=10, verbose_name='Máximo de participantes por equipo:')
    
    class Meta:
        db_table = 'DISCIPLINAS'
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
    
    def __str__(self):
        return self.nomDis
    
    def puede_agregar_mas_equipos(self, encuentro):
        """Verifica si se pueden agregar más equipos al encuentro"""
        return encuentro.equipos.count() < self.max_equipos
    
# Class 'Pistas'.

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
    
# Class 'Árbitros'.

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
    
# Class 'Participantes'.

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
    
# Class 'Encuentros'.

class Encuentros(models.Model):
    idEnc = models.AutoField(primary_key=True)
    idDis = models.ForeignKey(Disciplinas, on_delete=models.CASCADE, verbose_name='Disciplina:')
    finiEnc = models.DateTimeField(verbose_name='Fecha de inicio:')
    ffinEnc = models.DateTimeField(verbose_name='Fecha de fin:')
    idPis = models.ForeignKey(Pistas, on_delete=models.CASCADE, verbose_name='Pista:')
    arbitro = models.ForeignKey(Arbitros, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Árbitro asociado:')
    equipos = models.ManyToManyField(Equipos, through='EncuentroEquipo',verbose_name='Equipos participantes:')
    
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
        """Valida que el encuentro cumple las reglas de su disciplina"""
        super().clean()
        
        # Solo validar si ya tiene disciplina asignada
        if self.idDis and self.pk:  # self.pk significa que ya existe en BD
            equipos_count = self.equipos.count()
            
            # Validar número de equipos
            if not (self.idDis.min_equipos <= equipos_count <= self.idDis.max_equipos):
                raise ValidationError({
                    'equipos': f"Esta disciplina requiere entre {self.idDis.min_equipos} y {self.idDis.max_equipos} equipos. Actual: {equipos_count}"
                })
            
            # Validar participantes por equipo (OPCIONAL - según necesidad)
            for equipo in self.equipos.all():
                participantes_count = equipo.participantes_set.count()
                if participantes_count < self.idDis.min_participantes_por_equipo:
                    raise ValidationError(
                        f"El equipo {equipo.nomEqu} tiene muy pocos participantes "
                        f"({participantes_count}). Mínimo requerido: {self.idDis.min_participantes_por_equipo}"
                    )
    
    def save(self, *args, **kwargs):
        """Ejecuta validación al guardar"""
        self.clean()
        super().save(*args, **kwargs)

    
    
# Class Intermedia 'EncuentroEquipo'.

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