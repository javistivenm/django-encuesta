# Guia rapida de validacion UI (MVP Encuesta Comedores)

Duracion estimada: 10 a 15 minutos.

## 0) Precondiciones

- Servidor corriendo:

```bash
source .venv/bin/activate
python3 manage.py runserver
```

- Dataset 2026 cargado:

```bash
python3 manage.py generar_dataset_2026 --total 20000 --seed 2026 --reset-2026
```

- Usuario administrador disponible.

## 1) Validacion de vista tablet (3-4 min)

1. Abrir `http://127.0.0.1:8000/`.
2. Verificar pantalla de bienvenida y lista de puntos de captura.
3. Seleccionar un punto de captura.
4. Verificar formulario con 5 preguntas (escala 1 a 5).
5. Si aplica, verificar selector de turno.
6. Ingresar comentario (opcional) y enviar.
7. Validar pantalla de agradecimiento y retorno automatico al formulario.

Resultado esperado:

- Flujo continuo funcional para siguiente encuestado.

## 2) Validacion portal administrativo (3 min)

1. Abrir `http://127.0.0.1:8000/portal/`.
2. Iniciar sesion con usuario admin si se solicita.
3. Verificar que se muestran:
   - total de encuestas
   - promedio de satisfaccion general
   - promedios por categoria
   - ranking de comedores
   - listado de comentarios

Resultado esperado:

- El dashboard carga sin errores y con datos.

## 3) Validacion de filtros (4 min)

Probar estos casos en `http://127.0.0.1:8000/portal/`:

1. Fecha:
   - `fecha_inicio=2026-01-01`
   - `fecha_fin=2026-03-31`
   - Esperado: menor volumen que el anio completo.

2. Sede:
   - seleccionar una sede.
   - Esperado: KPIs, ranking y comentarios se ajustan.

3. Comedor:
   - seleccionar un comedor especifico.
   - Esperado: datos restringidos a ese comedor.

4. Turno:
   - probar `Almuerzo` y luego `Desayuno`.
   - Esperado: cambia volumen y promedios.

## 4) Validacion de exportacion CSV (2 min)

1. Aplicar filtros en el portal.
2. Clic en `Exportar CSV`.
3. Abrir `reporte_encuestas.csv`.

Validar columnas:

- `fecha_hora_registro`
- `sede`
- `comedor`
- `turno`
- `satisfaccion_general`
- `calidad_comida`
- `variedad_menu`
- `limpieza_comedor`
- `tiempo_atencion_fila`
- `comentario`

Resultado esperado:

- El archivo respeta filtros y contiene datos coherentes.

## 5) Smoke test final (1 min)

1. Registrar una encuesta nueva en `http://127.0.0.1:8000/`.
2. Refrescar `http://127.0.0.1:8000/portal/`.

Resultado esperado:

- El total de encuestas incrementa y el registro aparece en reporteria/comentarios (si incluyo comentario).
