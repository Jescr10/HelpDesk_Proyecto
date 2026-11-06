# Operación y presentación

## Recorrido sugerido

1. Inicia sesión como solicitante y crea un ticket con título descriptivo.
2. Filtra tus solicitudes, abre el detalle y agrega un comentario.
3. Cierra sesión e ingresa como técnico.
4. Asigna el ticket, pásalo a En progreso y luego a Resuelto.
5. Cierra el ticket; comprueba el historial y los indicadores del resumen.
6. Consulta una guía de la base de conocimiento.
7. Como administrador, crea un usuario desde Equipo y usuarios.

## Arranque

Ejecuta los comandos del README desde la raíz del repositorio. `--reload` es solo para desarrollo. Para detener Uvicorn usa Ctrl+C. Los datos permanecen en `helpdesk.db`.

## Copia de seguridad

Detén el servidor y copia `helpdesk.db` a una ubicación protegida. Para restaurar, detén el servidor y sustituye el archivo solo después de conservar una copia de la base actual. No subas bases con datos de usuarios a GitHub.

## Problemas comunes

- **ModuleNotFoundError:** instala `requirements.lock.txt` con el mismo Python del entorno virtual que inicia Uvicorn.
- **No puedo iniciar sesión:** si es una base nueva de demostración, ejecuta `python -m app.scripts.seed`; si es una instalación real, crea el primer administrador con `python -m app.scripts.create_admin`.
- **Sesión inválida después de reiniciar:** configura una clave `JWT_SECRET` persistente en `.env` y vuelve a iniciar sesión.
- **Puerto ocupado:** ejecuta Uvicorn con `--port 8001` y abre ese puerto.
- **Cambios de modelo no aparecen:** `create_all` no altera tablas existentes. Prepara una migración y conserva un respaldo.

## Repositorios

La rama de entrega es `rama-2` en `Jescr10/HelpDesk_Proyecto`. El remoto local `proyecto` apunta allí; se conserva `origin` para el repositorio anterior `HelpDesk_F`. Para nuevos cambios: `git push proyecto rama-2`.
