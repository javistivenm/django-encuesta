# Manual de operacion MVP - Encuesta Comedores

Esta guia explica como operar y probar el sistema desde dos perfiles:

- Administrador (configura y consulta resultados)
- Usuario de tablet (persona que responde la encuesta)

## 1) Preparacion inicial

Desde la raiz del proyecto:

```bash
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py migrate
```

Crear usuario administrador (si aun no existe):

```bash
python3 manage.py createsuperuser
```

Cargar datos de prueba (recomendado para pruebas rapidas):

```bash
python3 manage.py cargar_datos_demo
```

Generar dataset anual amplio para 2026 (20,000 respuestas):

```bash
python3 manage.py generar_dataset_2026 --total 20000 --seed 2026 --reset-2026
```

Levantar servidor:

```bash
python3 manage.py runserver
```

URLs base:

- Tablet (inicio): `http://127.0.0.1:8000/`
- Portal administrativo: `http://127.0.0.1:8000/portal/`
- Django admin: `http://127.0.0.1:8000/admin/`

## 2) Operacion para Administrador

### 2.1 Ingreso y catalogos

1. Abrir `http://127.0.0.1:8000/admin/`.
2. Iniciar sesion con usuario administrador.
3. Configurar catalogos:
   - `Sedes`
   - `Comedores`
   - `Turnos`
   - `Puntos de captura`
   - `Configuracion de encuesta`

Notas importantes:

- Un `Comedor` siempre pertenece a una `Sede`.
- `Turno` en modo `horario` debe tener hora inicio y fin validas.
- Si la encuesta debe pedir comentario, activar `pregunta_abierta_activa`.

### 2.2 Portal de reporteria

1. Abrir `http://127.0.0.1:8000/portal/`.
2. Si no hay sesion, el sistema redirige a login admin.
3. Usar filtros por:
   - fecha inicio / fecha fin
   - sede
   - comedor
   - turno (incluye opcion "sin turno")

El portal muestra:

- total de encuestas
- promedio de satisfaccion general
- promedios por categoria (calidad, variedad, limpieza, tiempo)
- ranking de comedores
- listado de comentarios

### 2.3 Exportacion

En el portal, usar boton `Exportar CSV`.

- Respeta los filtros actuales.
- Archivo generado: `reporte_encuestas.csv`.

## 3) Operacion para Usuario de tablet (encuestado)

### 3.1 Flujo de captura

1. Abrir `http://127.0.0.1:8000/`.
2. Seleccionar un punto de captura activo (tablet/comedor).
3. Responder preguntas de 1 a 5:
   - satisfaccion general
   - calidad
   - variedad
   - limpieza
   - tiempo de atencion
4. Si esta habilitado, agregar comentario (opcional).
5. Enviar.

Despues del envio:

- se muestra pantalla de agradecimiento
- retorna automaticamente al formulario para el siguiente usuario

### 3.2 Asignacion de turno

El sistema intenta asignar turno asi:

1. Turno automatico por horario (si hay coincidencia)
2. Si no hay coincidencia y existen turnos activos, pide seleccion manual
3. Si aplica, usa turno por defecto del punto de captura

## 4) Plan de prueba recomendado (end-to-end)

1. Cargar datos demo: `python3 manage.py cargar_datos_demo`.
2. Registrar 3-5 encuestas desde la vista tablet.
3. Ir a portal admin y validar que cambian KPIs.
4. Filtrar por sede/comedor/turno y revisar ranking.
5. Verificar listado de comentarios.
6. Exportar CSV y abrir archivo para validar columnas.

## 5) Comandos utiles de verificacion

```bash
python3 manage.py check
python3 manage.py test
```

## 6) Solucion de problemas comunes

- Portal no abre:
  - verificar que el servidor este corriendo
  - verificar login de usuario `is_staff`

- No aparecen puntos en tablet:
  - crear/activar `PuntoCaptura` en admin
  - confirmar que el `Comedor` asociado esta activo

- No guarda encuesta:
  - revisar campos obligatorios 1-5
  - si pide turno manual, seleccionar un turno

- CSV vacio:
  - limpiar filtros o ampliar rango de fechas
