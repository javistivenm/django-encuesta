from datetime import time

from django.core.management.base import BaseCommand

from encuestas.models import Comedor, ConfiguracionEncuesta, PuntoCaptura, Sede, Turno


class Command(BaseCommand):
    help = 'Carga catalogos iniciales de prueba para sedes, comedores, turnos y tablets.'

    def handle(self, *args, **options):
        sede_norte, _ = Sede.objects.get_or_create(nombre='Planta Norte', defaults={'activo': True})
        sede_central, _ = Sede.objects.get_or_create(
            nombre='Oficinas Centrales',
            defaults={'activo': True},
        )

        comedor_norte, _ = Comedor.objects.get_or_create(
            sede=sede_norte,
            nombre='Comedor Principal Norte',
            defaults={'ubicacion_referencial': 'Edificio A, piso 1', 'activo': True},
        )
        comedor_central, _ = Comedor.objects.get_or_create(
            sede=sede_central,
            nombre='Comedor Central',
            defaults={'ubicacion_referencial': 'Torre Central, piso 2', 'activo': True},
        )

        turno_desayuno, _ = Turno.objects.get_or_create(
            nombre='Desayuno',
            defaults={
                'modo_asignacion': Turno.ModoAsignacion.HORARIO,
                'hora_inicio': time(hour=6, minute=30),
                'hora_fin': time(hour=9, minute=30),
                'activo': True,
            },
        )
        turno_almuerzo, _ = Turno.objects.get_or_create(
            nombre='Almuerzo',
            defaults={
                'modo_asignacion': Turno.ModoAsignacion.HORARIO,
                'hora_inicio': time(hour=12, minute=0),
                'hora_fin': time(hour=15, minute=0),
                'activo': True,
            },
        )

        PuntoCaptura.objects.get_or_create(
            identificador='tablet-norte-01',
            defaults={'comedor': comedor_norte, 'turno_defecto': turno_desayuno, 'activo': True},
        )
        PuntoCaptura.objects.get_or_create(
            identificador='tablet-central-01',
            defaults={'comedor': comedor_central, 'turno_defecto': turno_almuerzo, 'activo': True},
        )

        ConfiguracionEncuesta.objects.get_or_create(
            nombre='configuracion_principal',
            defaults={
                'texto_bienvenida': 'Bienvenido a la encuesta de satisfaccion del comedor.',
                'texto_instrucciones': 'Califique del 1 al 5. El comentario es opcional.',
                'texto_agradecimiento': 'Gracias por tu participacion.',
                'pregunta_abierta_activa': True,
            },
        )

        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados correctamente.'))
