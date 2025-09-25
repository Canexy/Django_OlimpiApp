from django.db import models

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
    
    class Meta:
        db_table = 'DISCIPLINAS'
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
    
    def __str__(self):
        return self.nomDis
    
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