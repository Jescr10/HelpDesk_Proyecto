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
- Pruebas Python locales y CI: ver actualización de resultados al finalizar la verificación.
- Docker no está instalado en la computadora local; su comprobación se ejecuta en el runner de GitHub Actions.

Las capturas de `docs/img/semana16` proceden del ZIP de referencia; no son capturas nuevas de esta actualización.
