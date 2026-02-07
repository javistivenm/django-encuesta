from django import forms
from django.contrib import admin

from .models import Comedor, ConfiguracionEncuesta, PuntoCaptura, RespuestaEncuesta, Sede, Turno


class TurnoAdminForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        modo_asignacion = cleaned_data.get('modo_asignacion')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if modo_asignacion == Turno.ModoAsignacion.MANUAL and (hora_inicio or hora_fin):
            if not hora_inicio or not hora_fin:
                raise forms.ValidationError(
                    'Si ingresa horario en modo manual, debe completar inicio y fin.',
                )

        return cleaned_data


class PuntoCapturaAdminForm(forms.ModelForm):
    class Meta:
        model = PuntoCaptura
        fields = '__all__'

    def clean_turno_defecto(self):
        turno = self.cleaned_data.get('turno_defecto')
        if turno and not turno.activo:
            raise forms.ValidationError('El turno por defecto debe estar activo.')
        return turno


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Comedor)
class ComedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sede', 'ubicacion_referencial', 'activo')
    list_filter = ('activo', 'sede')
    search_fields = ('nombre', 'sede__nombre', 'ubicacion_referencial')
    ordering = ('sede__nombre', 'nombre')
    list_select_related = ('sede',)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    form = TurnoAdminForm
    list_display = ('nombre', 'modo_asignacion', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('activo', 'modo_asignacion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(PuntoCaptura)
class PuntoCapturaAdmin(admin.ModelAdmin):
    form = PuntoCapturaAdminForm
    list_display = ('identificador', 'comedor', 'turno_defecto', 'activo')
    list_filter = ('activo', 'comedor__sede', 'comedor', 'turno_defecto')
    search_fields = ('identificador', 'comedor__nombre', 'comedor__sede__nombre')
    ordering = ('identificador',)
    list_select_related = ('comedor', 'comedor__sede', 'turno_defecto')


@admin.register(ConfiguracionEncuesta)
class ConfiguracionEncuestaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pregunta_abierta_activa')
    search_fields = ('nombre',)


@admin.register(RespuestaEncuesta)
class RespuestaEncuestaAdmin(admin.ModelAdmin):
    list_display = (
        'fecha_hora_registro',
        'sede',
        'comedor',
        'turno',
        'satisfaccion_general',
    )
    list_filter = ('sede', 'comedor', 'turno', 'fecha_hora_registro')
    search_fields = ('comentario', 'sede__nombre', 'comedor__nombre')
    ordering = ('-fecha_hora_registro',)
    list_select_related = ('sede', 'comedor', 'turno')
    readonly_fields = ('fecha_hora_registro',)
