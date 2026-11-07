# Validación de la actualización de rama-2

Fecha: 6 de noviembre de 2026.

## Fuente y correspondencia

Se importó `developer.zip` como referencia de implementación de las semanas 7 a 17. Los módulos reemplazados de la versión SQLite siguen recuperables en el historial Git. La copia local `HelpDesk_Proyecto/`, el archivo SQLite y los entornos locales no se publican ni se eliminan.

| Requisito de referencia | Implementación |
| --- | --- |
| Dominio, relaciones y excepciones | `app/models`, `app/domain` |
| Repositorios y unidad de trabajo | `app/repositories`, `app/core/database.py` |
| PostgreSQL 16 y pgvector | `docs/database`, `docker-compose.yml` |
| API autenticada y permisos | `app/api/routes`, `app/api/dependencies.py` |
| Observer, Facade e inyección | `app/domain/events.py`, `app/services/helpdesk.py`, `app/core/services.py` |
| Cliente web y avisos | `app/web/static` |
| Despliegue, salud y respaldo | `Dockerfile`, `app/scripts/db_backup.py`, `/api/health` |

## Ajustes sobre la referencia

- Dependencia `tzdata` para que las zonas IANA funcionen en Windows.
- Tiempo de conexión PostgreSQL limitado a 3 segundos para evitar esperas indefinidas con la base apagada.
- Respaldos privados con ACL de Windows antes de escribir datos (en Linux se mantiene `0600`).
- Pruebas de Node con salida TAP explícita; las pruebas POSIX de `tzset` se ejecutan en Linux.
- Paquete `tests` explícito para evitar colisiones de importación con otros paquetes instalados.
- README con repositorio correcto, rama de entrega y pasos para PowerShell.
- CI con PostgreSQL + pgvector, JavaScript, suite completa y comprobación Docker.
- `REQUIRE_TEST_DATABASE=1` hace fallar CI si PostgreSQL no responde, en vez de presentar pruebas omitidas como éxito.

## Evidencia

- JavaScript: 22 pruebas aprobadas localmente.
- Windows / Python 3.13: **253 aprobadas**, 3 omitidas por requerir `time.tzset` de POSIX; 179 de integración excluidas de la ejecución local sin PostgreSQL.
- GitHub Actions / Linux / PostgreSQL 16 + pgvector: **435 aprobadas**, sin omisiones. Incluye autenticación, roles, persistencia, transacciones, avisos, cliente web y recuperación ante fallos.
- Docker: imagen construida, servicios saludables, `/api/health` con 200 y `{"status":"ok"}`, y `/app/` servido correctamente.
- Respaldo real `pg_dump` y restauración `pg_restore` completados en el proyecto desechable `helpdesk-ci`; salud de la aplicación verificada después de restaurar.
- [Ejecución exitosa en GitHub Actions](https://github.com/Jescr10/HelpDesk_Proyecto/actions/runs/42330813846), código verificado en `6bbc2db`. Los cambios posteriores de esta entrega solo documentan el resultado y corrigen un ejemplo de comando.
- Advertencia no bloqueante: Starlette avisa que su integración con `httpx` está deprecada; se conservan las versiones del lock de referencia para esta entrega.
- Docker no está instalado en la computadora local; su comprobación se ejecuta en el runner de GitHub Actions.

Las capturas de `docs/img/semana16` proceden del ZIP de referencia; no son capturas nuevas de esta actualización.
