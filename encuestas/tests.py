from datetime import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Comedor, ConfiguracionEncuesta, PuntoCaptura, RespuestaEncuesta, Sede, Turno


class FlujoTabletTests(TestCase):
    def setUp(self):
        self.sede = Sede.objects.create(nombre='Sede Test')
        self.comedor = Comedor.objects.create(
            sede=self.sede,
            nombre='Comedor Test',
            ubicacion_referencial='Piso 2',
        )
        self.punto = PuntoCaptura.objects.create(identificador='tablet-test-01', comedor=self.comedor)
        ConfiguracionEncuesta.objects.create(nombre='configuracion_principal')

    def _payload(self):
        return {
            'satisfaccion_general': 5,
            'calidad_comida': 4,
            'variedad_menu': 3,
            'limpieza_comedor': 5,
            'tiempo_atencion_fila': 4,
            'comentario': 'Todo bien',
        }

    def test_crea_respuesta_con_turno_automatico(self):
        turno_horario = Turno.objects.create(
            nombre='Turno Full Day',
            modo_asignacion=Turno.ModoAsignacion.HORARIO,
            hora_inicio=time(hour=0, minute=0),
            hora_fin=time(hour=23, minute=59),
        )

        response = self.client.post(
            reverse('encuestas:tablet_encuesta', args=[self.punto.identificador]),
            data=self._payload(),
        )

        self.assertRedirects(
            response,
            reverse('encuestas:tablet_gracias', args=[self.punto.identificador]),
        )
        respuesta = RespuestaEncuesta.objects.get()
        self.assertEqual(respuesta.turno, turno_horario)
        self.assertEqual(respuesta.sede, self.sede)
        self.assertEqual(respuesta.comedor, self.comedor)

    def test_requiere_turno_manual_si_no_hay_horario_automatico(self):
        turno_manual = Turno.objects.create(
            nombre='Turno Manual',
            modo_asignacion=Turno.ModoAsignacion.MANUAL,
        )

        response_sin_turno = self.client.post(
            reverse('encuestas:tablet_encuesta', args=[self.punto.identificador]),
            data=self._payload(),
        )

        self.assertEqual(response_sin_turno.status_code, 200)
        self.assertContains(response_sin_turno, 'Seleccione un turno')
        self.assertEqual(RespuestaEncuesta.objects.count(), 0)

        payload = self._payload()
        payload['turno'] = turno_manual.id
        response_con_turno = self.client.post(
            reverse('encuestas:tablet_encuesta', args=[self.punto.identificador]),
            data=payload,
        )

        self.assertRedirects(
            response_con_turno,
            reverse('encuestas:tablet_gracias', args=[self.punto.identificador]),
        )
        self.assertEqual(RespuestaEncuesta.objects.count(), 1)


class PortalReporteriaTests(TestCase):
    def setUp(self):
        self.sede = Sede.objects.create(nombre='Sede Reportes')
        self.comedor = Comedor.objects.create(
            sede=self.sede,
            nombre='Comedor Reportes',
            ubicacion_referencial='Planta baja',
        )
        self.turno = Turno.objects.create(nombre='Almuerzo', modo_asignacion=Turno.ModoAsignacion.MANUAL)
        RespuestaEncuesta.objects.create(
            sede=self.sede,
            comedor=self.comedor,
            turno=self.turno,
            satisfaccion_general=4,
            calidad_comida=4,
            variedad_menu=3,
            limpieza_comedor=5,
            tiempo_atencion_fila=4,
            comentario='Buen servicio',
        )

        user_model = get_user_model()
        self.staff_user = user_model.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True,
        )

    def test_portal_restringido_para_no_autenticado(self):
        response = self.client.get(reverse('encuestas:portal_inicio'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_portal_muestra_kpis_y_comentarios_para_staff(self):
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('encuestas:portal_inicio'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Encuestas registradas')
        self.assertContains(response, 'Ranking de comedores')
        self.assertContains(response, 'Buen servicio')

    def test_exportacion_csv_respeta_filtros(self):
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('encuestas:portal_exportar_csv'), {'sede': self.sede.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('fecha_hora_registro,sede,comedor,turno', response.content.decode())
        self.assertIn('Sede Reportes', response.content.decode())


class ModelosValidacionTests(TestCase):
    def test_turno_horario_requiere_inicio_y_fin(self):
        turno = Turno(
            nombre='Turno Invalido 1',
            modo_asignacion=Turno.ModoAsignacion.HORARIO,
            hora_inicio=None,
            hora_fin=None,
        )

        with self.assertRaises(ValidationError):
            turno.full_clean()

    def test_turno_horario_rechaza_rango_invalido(self):
        turno = Turno(
            nombre='Turno Invalido 2',
            modo_asignacion=Turno.ModoAsignacion.HORARIO,
            hora_inicio=time(hour=14, minute=0),
            hora_fin=time(hour=13, minute=0),
        )

        with self.assertRaises(ValidationError):
            turno.full_clean()

    def test_respuesta_rechaza_sede_y_comedor_incongruentes(self):
        sede_a = Sede.objects.create(nombre='Sede A')
        sede_b = Sede.objects.create(nombre='Sede B')
        comedor_b = Comedor.objects.create(sede=sede_b, nombre='Comedor B')

        respuesta = RespuestaEncuesta(
            sede=sede_a,
            comedor=comedor_b,
            satisfaccion_general=5,
            calidad_comida=5,
            variedad_menu=5,
            limpieza_comedor=5,
            tiempo_atencion_fila=5,
        )

        with self.assertRaises(ValidationError):
            respuesta.full_clean()

    def test_respuesta_rechaza_valor_fuera_de_escala(self):
        sede = Sede.objects.create(nombre='Sede Escala')
        comedor = Comedor.objects.create(sede=sede, nombre='Comedor Escala')

        respuesta = RespuestaEncuesta(
            sede=sede,
            comedor=comedor,
            satisfaccion_general=6,
            calidad_comida=5,
            variedad_menu=5,
            limpieza_comedor=5,
            tiempo_atencion_fila=5,
        )

        with self.assertRaises(ValidationError):
            respuesta.full_clean()


class TabletResponsiveTests(TestCase):
    def setUp(self):
        self.sede = Sede.objects.create(nombre='Sede UI')
        self.comedor = Comedor.objects.create(sede=self.sede, nombre='Comedor UI')
        self.punto = PuntoCaptura.objects.create(identificador='tablet-ui-01', comedor=self.comedor)
        ConfiguracionEncuesta.objects.create(nombre='configuracion_principal')

    def test_pagina_tablet_incluye_meta_viewport_y_media_queries(self):
        response = self.client.get(reverse('encuestas:tablet_encuesta', args=[self.punto.identificador]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'meta name="viewport"')
        self.assertContains(response, '@media (max-width: 700px)')
