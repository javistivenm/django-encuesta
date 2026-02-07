# Plan de desarrollo - Encuesta Comedores (MVP)

Este plan traduce los requerimientos del documento funcional a fases ejecutables en este proyecto Django + SQLite.

## Estado general

- [x] Fase 0 completada
- [x] Fase 1 completada
- [x] Fase 2 completada
- [x] Fase 3 completada
- [x] Fase 4 completada
- [x] Fase 5 completada

---

## Fase 0 - Base tecnica

Objetivo: preparar estructura base para empezar el desarrollo funcional.

Checklist:

- [x] Crear app principal `encuestas`
- [x] Registrar app en `INSTALLED_APPS`
- [x] Definir rutas base publicas (tablet) y privadas (portal)
- [x] Configurar vistas placeholder para flujo tablet y portal
- [x] Confirmar autenticacion para area administrativa (`is_staff`)
- [x] Ejecutar `python3 manage.py check`

Entregable:

- Estructura del proyecto lista para construir modulos funcionales.

RF relacionados: RF-12, RF-17.

---

## Fase 1 - Modelo de datos y migraciones

Objetivo: definir entidades minimas para captura y reporteria.

Checklist:

- [x] Modelo `Sede` (nombre, activo)
- [x] Modelo `Comedor` (sede, nombre, ubicacion_referencial, activo)
- [x] Modelo `Turno` (nombre, hora_inicio, hora_fin, activo, modo)
- [x] Modelo `PuntoCaptura` (identificador, comedor, turno_defecto opcional, activo)
- [x] Modelo `ConfiguracionEncuesta` (textos + bandera pregunta abierta)
- [x] Modelo `RespuestaEncuesta` (contexto + respuestas + comentario opcional)
- [x] Validaciones de rangos y escala 1-5
- [x] Crear migraciones
- [x] Ejecutar `python3 manage.py migrate`
- [x] Probar que crea registros sin sobreescribir historicos

Entregable:

- Esquema de base de datos listo para operar MVP.

RF relacionados: RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-07, RF-10, RF-18, RF-19.

---

## Fase 2 - Catalogos operativos (admin)

Objetivo: habilitar configuracion de sedes, comedores, turnos y tablets.

Checklist:

- [x] Registrar modelos en Django Admin
- [x] Crear formularios admin con validaciones clave
- [x] Configurar busqueda/filtros en admin para catalogos
- [x] Verificar alta/edicion/baja logica (activo/inactivo)
- [x] Cargar datos iniciales de prueba

Entregable:

- Portal admin util para operar catalogos del sistema.

RF relacionados: RF-01, RF-02, RF-03, RF-04.

---

## Fase 3 - Flujo de encuesta en tablet

Objetivo: capturar respuestas de forma rapida, simple y continua.

Checklist:

- [x] Pantalla inicial con bienvenida e instrucciones breves
- [x] Formulario touch-friendly con botones grandes (1 a 5)
- [x] Pregunta abierta opcional segun configuracion
- [x] Asociar contexto de captura (sede/comedor/fecha-hora)
- [x] Resolver turno automatico por horario cuando aplique
- [x] Permitir turno manual cuando no aplique horario
- [x] Guardar envio como registro unico
- [x] Mostrar pantalla de agradecimiento
- [x] Retorno automatico al inicio para siguiente usuario

Entregable:

- Flujo completo de encuesta en tablet listo para operacion.

RF relacionados: RF-05, RF-06, RF-07, RF-08, RF-09, RF-10, RF-11, RF-18, RF-19.

---

## Fase 4 - Portal administrativo y reporteria

Objetivo: visualizar resultados, filtrar, analizar y exportar.

Checklist:

- [x] Vista protegida para administradores autenticados
- [x] Filtros por rango de fecha, sede, comedor y turno
- [x] KPI: promedio satisfaccion general
- [x] KPI: promedios por categoria (calidad, variedad, limpieza, tiempo)
- [x] KPI: volumen total de encuestas
- [x] KPI: ranking simple de comedores (mejor/peor promedio)
- [x] Listado de comentarios con filtros
- [x] Exportacion CSV con contexto y respuestas
- [x] (Opcional) Exportacion Excel (diferido, no implementado en MVP)

Entregable:

- Dashboard operativo con filtros e indicadores minimos del MVP.

RF relacionados: RF-12, RF-13, RF-14, RF-15, RF-16, RF-17.

---

## Fase 5 - QA, pruebas y cierre MVP

Objetivo: asegurar calidad, estabilidad y cumplimiento de alcance.

Checklist:

- [x] Tests de modelos y validaciones
- [x] Tests de reglas de turno (automatico/manual)
- [x] Tests de vistas de captura y portal
- [x] Prueba de exportacion CSV
- [x] Prueba de acceso restringido (seguridad admin)
- [x] Prueba en resoluciones tablet (10")
- [x] Ejecutar `python3 manage.py test`
- [x] Ejecutar `python3 manage.py check`

Entregable:

- MVP validado y listo para demo/uso controlado.

RF relacionados: RF-08 a RF-19.

---

## Registro de avance

Usar esta seccion para marcar hitos y notas rapidas.

- Fecha: 2026-02-07
  - Fase: Fase 0 - Base tecnica
  - Estado: [ ] Pendiente  [ ] En progreso  [x] Completada
  - Nota: App `encuestas` creada, rutas base activas y portal protegido con `staff_member_required`.

- Fecha: 2026-02-07
  - Fase: Fase 1 - Modelo de datos y migraciones
  - Estado: [ ] Pendiente  [ ] En progreso  [x] Completada
  - Nota: Modelos creados con validaciones (turnos por horario y escala 1-5), migracion aplicada y verificacion de registros historicos.

- Fecha: 2026-02-07
  - Fase: Fase 2 - Catalogos operativos (admin)
  - Estado: [ ] Pendiente  [ ] En progreso  [x] Completada
  - Nota: Modelos registrados en admin con filtros/busqueda, formularios con validaciones y comando `cargar_datos_demo` ejecutado.

- Fecha: 2026-02-07
  - Fase: Fase 3 - Flujo de encuesta en tablet
  - Estado: [ ] Pendiente  [ ] En progreso  [x] Completada
  - Nota: Flujo de encuesta implementado con turno automatico/manual, pantalla de agradecimiento y retorno automatico al inicio.

- Fecha: 2026-02-07
  - Fase: Fase 4 - Portal administrativo y reporteria
  - Estado: [ ] Pendiente  [ ] En progreso  [x] Completada
  - Nota: Portal con filtros, KPIs, ranking, comentarios y exportacion CSV; se difiere exportacion Excel.

- Fecha: 2026-02-07
  - Fase: Fase 5 - QA, pruebas y cierre MVP
  - Estado: [ ] Pendiente  [ ] En progreso  [x] Completada
  - Nota: Suite de tests ampliada (modelos, flujo tablet, portal, seguridad y CSV) y validaciones finales ejecutadas con exito.
