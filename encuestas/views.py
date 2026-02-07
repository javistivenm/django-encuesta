import csv
from datetime import date

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import EncuestaTabletForm
from .models import Comedor, ConfiguracionEncuesta, PuntoCaptura, RespuestaEncuesta, Sede, Turno


def tablet_inicio(request: HttpRequest) -> HttpResponse:
    configuracion = _obtener_configuracion_encuesta()
    puntos = PuntoCaptura.objects.filter(activo=True).select_related('comedor', 'comedor__sede')
    contexto = {
        'configuracion': configuracion,
        'puntos': puntos,
    }
    return render(request, 'encuestas/tablet_inicio.html', contexto)


def tablet_encuesta(request: HttpRequest, identificador: str) -> HttpResponse:
    punto = get_object_or_404(
        PuntoCaptura.objects.select_related('comedor', 'comedor__sede', 'turno_defecto'),
        identificador=identificador,
        activo=True,
    )
    configuracion = _obtener_configuracion_encuesta()
    turno_automatico = _obtener_turno_automatico()
    turnos_disponibles = Turno.objects.filter(activo=True).order_by('nombre')
    requiere_turno_manual = turno_automatico is None and turnos_disponibles.exists()

    if request.method == 'POST':
        formulario = EncuestaTabletForm(
            request.POST,
            mostrar_comentario=configuracion.pregunta_abierta_activa,
            requiere_turno_manual=requiere_turno_manual,
            turnos_disponibles=turnos_disponibles,
        )
        if formulario.is_valid():
            turno_asignado = turno_automatico
            if requiere_turno_manual:
                turno_asignado = formulario.cleaned_data.get('turno')
            if not turno_asignado and punto.turno_defecto and punto.turno_defecto.activo:
                turno_asignado = punto.turno_defecto

            RespuestaEncuesta.objects.create(
                sede=punto.comedor.sede,
                comedor=punto.comedor,
                turno=turno_asignado,
                satisfaccion_general=formulario.cleaned_data['satisfaccion_general'],
                calidad_comida=formulario.cleaned_data['calidad_comida'],
                variedad_menu=formulario.cleaned_data['variedad_menu'],
                limpieza_comedor=formulario.cleaned_data['limpieza_comedor'],
                tiempo_atencion_fila=formulario.cleaned_data['tiempo_atencion_fila'],
                comentario=formulario.cleaned_data.get('comentario', ''),
            )
            return redirect('encuestas:tablet_gracias', identificador=identificador)
    else:
        formulario = EncuestaTabletForm(
            mostrar_comentario=configuracion.pregunta_abierta_activa,
            requiere_turno_manual=requiere_turno_manual,
            turnos_disponibles=turnos_disponibles,
        )

    contexto = {
        'configuracion': configuracion,
        'formulario': formulario,
        'punto': punto,
        'requiere_turno_manual': requiere_turno_manual,
        'turno_automatico': turno_automatico,
    }
    return render(request, 'encuestas/tablet_encuesta.html', contexto)


def tablet_gracias(request: HttpRequest, identificador: str) -> HttpResponse:
    punto = get_object_or_404(PuntoCaptura, identificador=identificador, activo=True)
    configuracion = _obtener_configuracion_encuesta()
    contexto = {
        'configuracion': configuracion,
        'punto': punto,
        'retorno_url': reverse('encuestas:tablet_encuesta', args=[identificador]),
    }
    return render(request, 'encuestas/tablet_gracias.html', contexto)


@staff_member_required
def portal_inicio(request: HttpRequest) -> HttpResponse:
    respuestas = _filtrar_respuestas(request)
    promedios = respuestas.aggregate(
        promedio_satisfaccion_general=Avg('satisfaccion_general'),
        promedio_calidad=Avg('calidad_comida'),
        promedio_variedad=Avg('variedad_menu'),
        promedio_limpieza=Avg('limpieza_comedor'),
        promedio_tiempo=Avg('tiempo_atencion_fila'),
    )
    ranking_comedores = (
        respuestas.values('comedor__nombre', 'comedor__sede__nombre')
        .annotate(promedio=Avg('satisfaccion_general'), total=Count('id'))
        .order_by('-promedio', '-total', 'comedor__nombre')
    )
    comentarios = (
        respuestas.exclude(comentario='')
        .select_related('sede', 'comedor', 'turno')
        .order_by('-fecha_hora_registro')
    )

    contexto = {
        'respuestas_total': respuestas.count(),
        'promedios': promedios,
        'ranking_comedores': ranking_comedores,
        'comentarios': comentarios,
        'filtros': {
            'fecha_inicio': request.GET.get('fecha_inicio', ''),
            'fecha_fin': request.GET.get('fecha_fin', ''),
            'sede_id': request.GET.get('sede', ''),
            'comedor_id': request.GET.get('comedor', ''),
            'turno_id': request.GET.get('turno', ''),
        },
        'sedes': Sede.objects.filter(activo=True).order_by('nombre'),
        'comedores': Comedor.objects.filter(activo=True).select_related('sede').order_by('sede__nombre', 'nombre'),
        'turnos': Turno.objects.filter(activo=True).order_by('nombre'),
        'querystring': request.GET.urlencode(),
    }
    return render(request, 'encuestas/portal_inicio.html', contexto)


@staff_member_required
def portal_exportar_csv(request: HttpRequest) -> HttpResponse:
    respuestas = _filtrar_respuestas(request).select_related('sede', 'comedor', 'turno')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_encuestas.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            'fecha_hora_registro',
            'sede',
            'comedor',
            'turno',
            'satisfaccion_general',
            'calidad_comida',
            'variedad_menu',
            'limpieza_comedor',
            'tiempo_atencion_fila',
            'comentario',
        ]
    )
    for respuesta in respuestas:
        writer.writerow(
            [
                timezone.localtime(respuesta.fecha_hora_registro).strftime('%Y-%m-%d %H:%M:%S'),
                respuesta.sede.nombre,
                respuesta.comedor.nombre,
                respuesta.turno.nombre if respuesta.turno else '',
                respuesta.satisfaccion_general,
                respuesta.calidad_comida,
                respuesta.variedad_menu,
                respuesta.limpieza_comedor,
                respuesta.tiempo_atencion_fila,
                respuesta.comentario,
            ]
        )
    return response


def _obtener_configuracion_encuesta() -> ConfiguracionEncuesta:
    configuracion, _ = ConfiguracionEncuesta.objects.get_or_create(nombre='configuracion_principal')
    return configuracion


def _obtener_turno_automatico() -> Turno | None:
    hora_actual = timezone.localtime().time()
    return (
        Turno.objects.filter(
            activo=True,
            modo_asignacion=Turno.ModoAsignacion.HORARIO,
            hora_inicio__lte=hora_actual,
            hora_fin__gt=hora_actual,
        )
        .order_by('hora_inicio')
        .first()
    )


def _filtrar_respuestas(request: HttpRequest):
    respuestas = RespuestaEncuesta.objects.all().select_related('sede', 'comedor', 'turno')

    sede_id = request.GET.get('sede')
    comedor_id = request.GET.get('comedor')
    turno_id = request.GET.get('turno')
    fecha_inicio = _parsear_fecha(request.GET.get('fecha_inicio'))
    fecha_fin = _parsear_fecha(request.GET.get('fecha_fin'))

    if sede_id:
        respuestas = respuestas.filter(sede_id=sede_id)
    if comedor_id:
        respuestas = respuestas.filter(comedor_id=comedor_id)
    if turno_id:
        if turno_id == 'sin_turno':
            respuestas = respuestas.filter(turno__isnull=True)
        else:
            respuestas = respuestas.filter(turno_id=turno_id)
    if fecha_inicio:
        respuestas = respuestas.filter(fecha_hora_registro__date__gte=fecha_inicio)
    if fecha_fin:
        respuestas = respuestas.filter(fecha_hora_registro__date__lte=fecha_fin)

    return respuestas


def _parsear_fecha(valor: str | None) -> date | None:
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None
