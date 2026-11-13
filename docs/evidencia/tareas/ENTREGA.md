# Lista de tareas por ticket

Fecha de ejecución: 12 de noviembre de 2026. Rama local: `rama-2`.

Módulo (Anexo A): **Control de tareas de soporte técnico / Lista de tareas por ticket**.
Implementado dentro de HelpDesk EDU; conserva la API, autenticación y cliente existentes.
Trabajo y evidencia conservados en la copia local, sin necesidad de repositorio central ni PR.

## Flujo implementado y rúbrica

| Capa | Implementación y evidencia |
| --- | --- |
| Entidad y relación | `TareaTicket`: id, ticket_id, descripcion, completada y fecha_creacion. FK a tickets, relación uno a muchos. |
| Persistencia | Tabla PostgreSQL `ticket_tasks`, ORM y repositorio SQLAlchemy. Las peticiones usan la unidad de trabajo existente. Una prueba confirma el dato y lo recupera en una sesión nueva independiente. |
| Servicio y API | Solo el personal asignado puede agregar/completar. El solicitante consulta únicamente sus tickets; un ticket ajeno devuelve 404. El resto del personal puede consultar conforme al permiso de lectura del sistema, pero no modificar tareas de un ticket no asignado. |
| Pantalla | Sección «Tareas de soporte» en el detalle del ticket: formulario, lista, estado, fecha, contador y porcentaje. Acciones reales contra API, mensajes de éxito/error y recarga desde PostgreSQL. |
| Pruebas | 12 casos nuevos: persistencia, completar, idempotencia, permisos, aislamiento entre tickets, autenticación, entradas inválidas y rechazo en ticket cancelado, sin mutación. |
| Entrega | Este documento, código, salida de pytest, resultado del navegador y tres capturas. |

La aplicación permite asignar técnicos y supervisores; cualquiera de estos puede administrar las tareas **solo si está asignado**. No se agrega un permiso general de administrador. No hay eliminación, edición ni reapertura de tareas: la propuesta exige agregar, listar y completar. Los tickets cerrados/cancelados conservan sus tareas para consulta.

## Rutas

Todas requieren `Authorization: Bearer <token>` y validan permisos en el servicio.

| Método | Ruta | Operación |
| --- | --- | --- |
| GET | `/api/tickets/{ticket_id}/tasks` | Lista ordenada por id. |
| POST | `/api/tickets/{ticket_id}/tasks` | Crea pendiente, cuerpo `{"descripcion":"Revisar conexiones"}`. |
| POST | `/api/tickets/{ticket_id}/tasks/{task_id}/complete` | Completa una tarea del mismo ticket; repetir es idempotente. |

La descripción admite de 1 a 500 caracteres, sin aceptar texto vacío o solo espacios. El cliente no puede imponer id, ticket_id, fecha o estado al crear. Errores: 401 sin autenticación, 403 sin permiso de escritura, 404 sin acceso/al no existir el recurso, 422 entrada inválida o ticket cerrado/cancelado.

## Bases aisladas y reproducción

Se usó el servicio PostgreSQL de Docker en `127.0.0.1:5433`:

- `helpdesk_tasks_test`: base desechable para pytest; las fixtures existentes la recrean.
- `helpdesk_tasks_demo_test`: base separada para la demostración y las capturas; conserva sus datos al volver a preparar la demo.
- La base habitual `helpdesk` no recibió migraciones, pruebas ni tareas de demostración. El servidor habitual del puerto 8000 no se reemplazó.

`docs/database/database.sql` incluye la nueva tabla para bases nuevas. **No ejecutar ese archivo sobre la base habitual existente**: contiene la creación del esquema completo. La aplicación no hace migraciones al arrancar. La instalación en una base habitual existente queda fuera de esta práctica aislada y requeriría una migración aditiva revisada.

Desde la raíz del proyecto en PowerShell, con Docker encendido y `.env` configurado con `TEST_DATABASE_URL`:

```powershell
# Ejecutar toda la suite en helpdesk_tasks_test; falla si no hay PostgreSQL.
.venv\Scripts\python.exe -m dotenv -f .env run -- .venv\Scripts\python.exe -m app.scripts.check_tasks

# Solo las 12 pruebas del módulo.
.venv\Scripts\python.exe -m dotenv -f .env run -- .venv\Scripts\python.exe -m app.scripts.check_tasks tests/test_ticket_tasks.py -q

# Preparar la demo aislada y levantarla en 127.0.0.1:8001.
.venv\Scripts\python.exe -m dotenv -f .env run -- .venv\Scripts\python.exe -m app.scripts.tasks_demo prepare
.venv\Scripts\python.exe -m dotenv -f .env run -- .venv\Scripts\python.exe -m app.scripts.tasks_demo serve
```

Los scripts eligen nombres fijos de bases de prueba a partir de la conexión de `TEST_DATABASE_URL`; no usan su nombre de base original. El usuario de PostgreSQL necesita permiso para crear bases. Si se abre otra consola, entrar primero a la carpeta raíz `HelpDesk_F`. Para detener la demo, `Ctrl+C` en su consola.

Abrir <http://127.0.0.1:8001/app/>. Usuarios **exclusivos de la demo**:

| Rol | Correo | Contraseña de demo |
| --- | --- | --- |
| Técnico | technician@example.com | TareasDemo2026! |
| Solicitante | requester@example.com | TareasDemo2026! |

La contraseña de demo no cambia los accesos de la aplicación habitual. En la ejecución documentada, el ticket **8** tiene tres tareas y una completada. En una demo recién inicializada se puede usar el ticket **2**, asignado al técnico y propiedad de requester@example.com.

## Resultados observados

- Suite completa: **444 passed, 3 skipped, 1 warning**, 66.46 segundos. Incluye 12 pruebas nuevas y las pruebas de JavaScript invocadas por pytest.
- Las tres omisiones corresponden a pruebas preexistentes que requieren `time.tzset`, no disponible en Windows. La advertencia preexistente es la deprecación del uso de httpx en Starlette TestClient.
- No se modificó ninguna prueba preexistente.
- Verificación del comando de entrega, módulo y compatibilidad: **13 passed**, 4.34 segundos.
- Navegador Chrome: formulario crea tres tareas; botón completa una; al recargar permanece 1/3 (33 %); solicitante ve progreso sin botones de escritura. Vista móvil 390 px sin desplazamiento horizontal; sin errores de JavaScript.
- Lectura desde otra sesión: ver `test_create_complete_and_read_from_new_session` en `tests/test_ticket_tasks.py`; crea mediante API, abre una `Session(pg_engine)` independiente, completa mediante API y vuelve a leer desde otra sesión.
- Los casos de rechazo comparan los datos antes y después para demostrar que no cambian.

Salidas: [pytest](pruebas.txt), [navegador](navegador.json).
Capturas: [técnico escritorio](tecnico-desktop.png), [técnico móvil](tecnico-movil.png), [solicitante](solicitante-desktop.png).

## Archivos entregados

Nuevos:

- `app/models/tasks.py`: entidad.
- `app/repositories/tasks.py`: ORM, contrato y repositorio.
- `app/services/tasks.py`: reglas de negocio.
- `app/schemas/tasks.py`: entrada y salida validadas.
- `app/api/routes/tasks.py`: rutas autenticadas.
- `app/scripts/tasks_demo.py`: demostración aislada reproducible.
- `app/scripts/check_tasks.py`: ejecución protegida de pruebas.
- `tests/test_ticket_tasks.py`: pruebas del módulo.
- `docs/evidencia/tareas/`: ficha, resultados y capturas.

Modificados:

- `app/main.py`: registra las rutas.
- `docs/database/database.sql`: tabla y llave foránea para inicialización de bases nuevas.
- `app/web/static/js/api.js`: llamadas autenticadas del cliente y mensaje de permiso.
- `app/web/static/js/pages/ticket.js`: sección de tareas integrada.
- `README.md`: acceso a esta entrega.

No entregar `.env`, `.venv`, bases personales, respaldos ni archivos de credenciales habituales.
