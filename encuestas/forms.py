from django import forms

from .models import Turno


class EncuestaTabletForm(forms.Form):
    ESCALA_CHOICES = [(valor, str(valor)) for valor in range(1, 6)]

    satisfaccion_general = forms.TypedChoiceField(
        label='Satisfaccion general',
        choices=ESCALA_CHOICES,
        coerce=int,
        widget=forms.RadioSelect,
    )
    calidad_comida = forms.TypedChoiceField(
        label='Calidad de la comida',
        choices=ESCALA_CHOICES,
        coerce=int,
        widget=forms.RadioSelect,
    )
    variedad_menu = forms.TypedChoiceField(
        label='Variedad del menu',
        choices=ESCALA_CHOICES,
        coerce=int,
        widget=forms.RadioSelect,
    )
    limpieza_comedor = forms.TypedChoiceField(
        label='Limpieza del comedor',
        choices=ESCALA_CHOICES,
        coerce=int,
        widget=forms.RadioSelect,
    )
    tiempo_atencion_fila = forms.TypedChoiceField(
        label='Tiempo de atencion/fila',
        choices=ESCALA_CHOICES,
        coerce=int,
        widget=forms.RadioSelect,
    )
    turno = forms.ModelChoiceField(
        label='Turno',
        queryset=Turno.objects.none(),
        required=False,
        empty_label='Seleccione un turno',
    )
    comentario = forms.CharField(
        label='Comentario (opcional)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(
        self,
        *args,
        mostrar_comentario: bool,
        requiere_turno_manual: bool,
        turnos_disponibles,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if not mostrar_comentario:
            self.fields.pop('comentario')

        if requiere_turno_manual:
            self.fields['turno'].required = True
            self.fields['turno'].queryset = turnos_disponibles
        else:
            self.fields.pop('turno')
