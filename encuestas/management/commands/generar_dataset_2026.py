import random
from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from encuestas.models import Comedor, ConfiguracionEncuesta, PuntoCaptura, RespuestaEncuesta, Sede, Turno


class Command(BaseCommand):
    help = 'Genera un dataset anual de respuestas para 2026 con volumen configurable.'

    def add_arguments(self, parser):
        parser.add_argument('--total', type=int, default=20000, help='Total de respuestas a generar.')
        parser.add_argument('--seed', type=int, default=2026, help='Semilla para generacion reproducible.')
        parser.add_argument(
            '--reset-2026',
            action='store_true',
            help='Elimina respuestas del anio 2026 antes de regenerar.',
        )

    def handle(self, *args, **options):
        total = options['total']
        seed = options['seed']
        reset_2026 = options['reset_2026']

        if total <= 0:
            self.stdout.write(self.style.ERROR('El valor --total debe ser mayor que cero.'))
            return

        random.seed(seed)
        self.stdout.write(f'Generando dataset 2026 con total={total}, seed={seed}...')

        with transaction.atomic():
            if reset_2026:
                eliminadas, _ = RespuestaEncuesta.objects.filter(fecha_hora_registro__year=2026).delete()
                self.stdout.write(f'Respuestas 2026 eliminadas: {eliminadas}')

            turnos = self._asegurar_turnos()
            comedores = self._asegurar_sedes_y_comedores(turnos)
            self._asegurar_configuracion()

            perfiles = self._crear_perfiles_comedor(comedores)
            fechas, pesos_fechas = self._fechas_y_pesos_2026()

            self._generar_respuestas(
                total=total,
                fechas=fechas,
                pesos_fechas=pesos_fechas,
                comedores=comedores,
                perfiles=perfiles,
                turnos=turnos,
            )

        total_2026 = RespuestaEncuesta.objects.filter(fecha_hora_registro__year=2026).count()
        self.stdout.write(self.style.SUCCESS(f'Dataset generado correctamente. Total 2026: {total_2026}'))

    def _asegurar_turnos(self) -> dict[str, Turno]:
        definiciones = {
            'Desayuno': (time(hour=6, minute=30), time(hour=9, minute=30)),
            'Almuerzo': (time(hour=12, minute=0), time(hour=15, minute=0)),
            'Merienda': (time(hour=16, minute=30), time(hour=19, minute=30)),
        }
        turnos: dict[str, Turno] = {}
        for nombre, (hora_inicio, hora_fin) in definiciones.items():
            turno, _ = Turno.objects.update_or_create(
                nombre=nombre,
                defaults={
                    'modo_asignacion': Turno.ModoAsignacion.HORARIO,
                    'hora_inicio': hora_inicio,
                    'hora_fin': hora_fin,
                    'activo': True,
                },
            )
            turnos[nombre] = turno
        return turnos

    def _asegurar_sedes_y_comedores(self, turnos: dict[str, Turno]) -> list[Comedor]:
        sedes_objetivo = [
            'Planta Norte',
            'Planta Sur',
            'Oficinas Centrales',
            'Centro Logistico',
            'Campus Innovacion',
        ]
        sufijos = ['Principal', 'Express', 'Ejecutivo']

        comedores: list[Comedor] = []

        for nombre_sede in sedes_objetivo:
            sede, _ = Sede.objects.get_or_create(nombre=nombre_sede, defaults={'activo': True})
            if not sede.activo:
                sede.activo = True
                sede.save(update_fields=['activo'])

            for sufijo in sufijos:
                nombre_comedor = f'Comedor {sufijo}'
                comedor, _ = Comedor.objects.get_or_create(
                    sede=sede,
                    nombre=nombre_comedor,
                    defaults={
                        'ubicacion_referencial': f'{nombre_sede} - Zona {sufijo}',
                        'activo': True,
                    },
                )
                if not comedor.activo:
                    comedor.activo = True
                    comedor.save(update_fields=['activo'])

                comedores.append(comedor)

        turno_defecto = turnos['Almuerzo']
        for comedor in comedores:
            identificador = self._identificador_punto(comedor)
            PuntoCaptura.objects.get_or_create(
                identificador=identificador,
                defaults={
                    'comedor': comedor,
                    'turno_defecto': turno_defecto,
                    'activo': True,
                },
            )

        return comedores

    def _asegurar_configuracion(self):
        ConfiguracionEncuesta.objects.get_or_create(
            nombre='configuracion_principal',
            defaults={
                'texto_bienvenida': 'Bienvenido a la encuesta de satisfaccion del comedor.',
                'texto_instrucciones': 'Califique del 1 al 5. El comentario es opcional.',
                'texto_agradecimiento': 'Gracias por tu participacion.',
                'pregunta_abierta_activa': True,
            },
        )

    def _identificador_punto(self, comedor: Comedor) -> str:
        base_sede = comedor.sede.nombre.lower().replace(' ', '-')
        base_comedor = comedor.nombre.lower().replace(' ', '-')
        return f'tablet-{base_sede}-{base_comedor}'

    def _crear_perfiles_comedor(self, comedores: list[Comedor]) -> dict[int, dict[str, float]]:
        perfiles: dict[int, dict[str, float]] = {}
        for comedor in comedores:
            base = random.uniform(3.3, 4.6)
            peso = random.uniform(0.8, 1.4)
            perfiles[comedor.id] = {'base': base, 'peso': peso}
        return perfiles

    def _fechas_y_pesos_2026(self) -> tuple[list[date], list[float]]:
        inicio = date(2026, 1, 1)
        fin = date(2026, 12, 31)
        actual = inicio
        fechas: list[date] = []
        pesos: list[float] = []

        while actual <= fin:
            fechas.append(actual)
            if actual.weekday() <= 4:
                pesos.append(1.0)
            elif actual.weekday() == 5:
                pesos.append(0.55)
            else:
                pesos.append(0.4)
            actual += timedelta(days=1)

        return fechas, pesos

    def _generar_respuestas(
        self,
        *,
        total: int,
        fechas: list[date],
        pesos_fechas: list[float],
        comedores: list[Comedor],
        perfiles: dict[int, dict[str, float]],
        turnos: dict[str, Turno],
    ):
        turnos_lista = [turnos['Desayuno'], turnos['Almuerzo'], turnos['Merienda']]
        pesos_turno = [0.26, 0.56, 0.18]

        pesos_comedor = [perfiles[comedor.id]['peso'] for comedor in comedores]

        comentarios_buenos = [
            'Excelente atencion del personal.',
            'Buen sabor y buena temperatura de la comida.',
            'Servicio rapido y ordenado.',
            'Comedor limpio y agradable.',
            'Buena variedad para el almuerzo.',
        ]
        comentarios_mejora = [
            'La fila estuvo larga en este horario.',
            'Falto variedad en el menu de hoy.',
            'Se puede mejorar la temperatura de la comida.',
            'La limpieza puede mejorar en mesas.',
            'Atencion un poco lenta para el volumen.',
        ]

        batch_size = 1000
        objetos: list[RespuestaEncuesta] = []
        fechas_objetivo: list[datetime] = []

        for indice in range(total):
            comedor = random.choices(comedores, weights=pesos_comedor, k=1)[0]
            turno = random.choices(turnos_lista, weights=pesos_turno, k=1)[0]
            fecha = random.choices(fechas, weights=pesos_fechas, k=1)[0]
            fecha_hora = self._fecha_hora_en_turno(fecha, turno)

            perfil = perfiles[comedor.id]['base']
            satisfaccion_general = self._puntaje(perfil + random.gauss(0, 0.65))
            calidad = self._puntaje(perfil + random.gauss(0, 0.75))
            variedad = self._puntaje(perfil - 0.15 + random.gauss(0, 0.85))
            limpieza = self._puntaje(perfil + 0.1 + random.gauss(0, 0.6))
            tiempo_atencion = self._puntaje(perfil - 0.2 + random.gauss(0, 0.8))

            promedio = (
                satisfaccion_general + calidad + variedad + limpieza + tiempo_atencion
            ) / 5
            comentario = self._comentario(promedio, comentarios_buenos, comentarios_mejora)

            objetos.append(
                RespuestaEncuesta(
                    sede=comedor.sede,
                    comedor=comedor,
                    turno=turno,
                    satisfaccion_general=satisfaccion_general,
                    calidad_comida=calidad,
                    variedad_menu=variedad,
                    limpieza_comedor=limpieza,
                    tiempo_atencion_fila=tiempo_atencion,
                    comentario=comentario,
                )
            )
            fechas_objetivo.append(fecha_hora)

            if (indice + 1) % batch_size == 0:
                self._insertar_batch(objetos, fechas_objetivo, batch_size)
                self.stdout.write(f'  Insertadas {indice + 1} / {total} respuestas...')
                objetos = []
                fechas_objetivo = []

        if objetos:
            self._insertar_batch(objetos, fechas_objetivo, batch_size)
            self.stdout.write(f'  Insertadas {total} / {total} respuestas...')

    def _insertar_batch(self, objetos: list[RespuestaEncuesta], fechas_objetivo: list[datetime], batch_size: int):
        creados = RespuestaEncuesta.objects.bulk_create(objetos, batch_size=batch_size)
        for indice, respuesta in enumerate(creados):
            respuesta.fecha_hora_registro = fechas_objetivo[indice]
        RespuestaEncuesta.objects.bulk_update(creados, ['fecha_hora_registro'], batch_size=batch_size)

    def _fecha_hora_en_turno(self, fecha: date, turno: Turno) -> datetime:
        inicio_seg = turno.hora_inicio.hour * 3600 + turno.hora_inicio.minute * 60
        fin_seg = turno.hora_fin.hour * 3600 + turno.hora_fin.minute * 60
        if fin_seg <= inicio_seg:
            fin_seg = inicio_seg + 60
        segundo = random.randint(inicio_seg, fin_seg - 1)
        hora = segundo // 3600
        minuto = (segundo % 3600) // 60
        segundo_final = segundo % 60
        dt_naive = datetime.combine(fecha, time(hour=hora, minute=minuto, second=segundo_final))
        return timezone.make_aware(dt_naive)

    def _puntaje(self, valor: float) -> int:
        redondeado = int(round(valor))
        return max(1, min(5, redondeado))

    def _comentario(
        self,
        promedio: float,
        comentarios_buenos: list[str],
        comentarios_mejora: list[str],
    ) -> str:
        umbral = 0.3
        if promedio <= 2.4:
            umbral = 0.55
        elif promedio <= 3.2:
            umbral = 0.42
        elif promedio >= 4.4:
            umbral = 0.25

        if random.random() > umbral:
            return ''
        if promedio >= 3.6:
            return random.choice(comentarios_buenos)
        return random.choice(comentarios_mejora)
