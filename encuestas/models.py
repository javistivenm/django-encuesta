from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Sede(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self) -> str:
        return self.nombre


class Comedor(models.Model):
    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, related_name='comedores')
    nombre = models.CharField(max_length=120)
    ubicacion_referencial = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['sede__nombre', 'nombre']
        constraints = [
            models.UniqueConstraint(fields=['sede', 'nombre'], name='unique_comedor_por_sede'),
        ]

    def __str__(self) -> str:
        return f'{self.sede.nombre} - {self.nombre}'


class Turno(models.Model):
    class ModoAsignacion(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        HORARIO = 'horario', 'Por horario'

    nombre = models.CharField(max_length=80, unique=True)
    modo_asignacion = models.CharField(
        max_length=20,
        choices=ModoAsignacion.choices,
        default=ModoAsignacion.HORARIO,
    )
    hora_inicio = models.TimeField(blank=True, null=True)
    hora_fin = models.TimeField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def clean(self) -> None:
        super().clean()
        if self.modo_asignacion == self.ModoAsignacion.HORARIO:
            if not self.hora_inicio or not self.hora_fin:
                raise ValidationError('Los turnos por horario requieren hora de inicio y fin.')
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError('La hora de inicio debe ser menor que la hora de fin.')

    def __str__(self) -> str:
        return self.nombre


class PuntoCaptura(models.Model):
    identificador = models.CharField(max_length=80, unique=True)
    comedor = models.ForeignKey(Comedor, on_delete=models.PROTECT, related_name='puntos_captura')
    turno_defecto = models.ForeignKey(
        Turno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='puntos_captura_por_defecto',
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['identificador']

    def __str__(self) -> str:
        return self.identificador


class ConfiguracionEncuesta(models.Model):
    nombre = models.CharField(max_length=80, default='configuracion_principal', unique=True)
    texto_bienvenida = models.CharField(max_length=255, default='Bienvenido a la encuesta.')
    texto_instrucciones = models.CharField(
        max_length=255,
        default='Seleccione una opcion del 1 al 5 para cada pregunta.',
    )
    texto_agradecimiento = models.CharField(max_length=255, default='Gracias por tu respuesta.')
    pregunta_abierta_activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Configuracion de encuesta'
        verbose_name_plural = 'Configuracion de encuesta'

    def __str__(self) -> str:
        return self.nombre


class RespuestaEncuesta(models.Model):
    escala_validadores = [MinValueValidator(1), MaxValueValidator(5)]

    sede = models.ForeignKey(Sede, on_delete=models.PROTECT, related_name='respuestas')
    comedor = models.ForeignKey(Comedor, on_delete=models.PROTECT, related_name='respuestas')
    turno = models.ForeignKey(
        Turno,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='respuestas',
    )
    fecha_hora_registro = models.DateTimeField(auto_now_add=True)
    satisfaccion_general = models.PositiveSmallIntegerField(validators=escala_validadores)
    calidad_comida = models.PositiveSmallIntegerField(validators=escala_validadores)
    variedad_menu = models.PositiveSmallIntegerField(validators=escala_validadores)
    limpieza_comedor = models.PositiveSmallIntegerField(validators=escala_validadores)
    tiempo_atencion_fila = models.PositiveSmallIntegerField(validators=escala_validadores)
    comentario = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_hora_registro']

    def clean(self) -> None:
        super().clean()
        if self.comedor.sede_id != self.sede_id:
            raise ValidationError('El comedor seleccionado no pertenece a la sede indicada.')

    def __str__(self) -> str:
        return f'Respuesta #{self.pk or "nueva"} - {self.comedor.nombre}'
