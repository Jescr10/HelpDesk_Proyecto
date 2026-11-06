# ADR 001: completar la arquitectura Python existente

## Decisión

Mantener FastAPI y la separación API → servicios → repositorios → SQLAlchemy presentes en el avance original. Corregir las referencias a módulos inexistentes `app.api.routes` y `app.web`, y servir el frontend desde `app.webs.main`.

La interfaz usa HTML/CSS y JavaScript nativo, sin un proceso de compilación adicional. La misma aplicación sirve la API y los archivos estáticos: no necesita CORS ni servicios externos para una demostración local. SQLite ofrece persistencia sin instalar un servidor de base de datos.

## Seguridad y sesiones

JWT firmado con HS256 y fecha de vencimiento. Cada petición resuelve el usuario desde la base y verifica su rol actual. El navegador guarda el token en sessionStorage, limitado a esa pestaña; salir elimina la copia local (no revoca un token previamente copiado). No se habilita registro público ni se crean cuentas conocidas al arrancar.

Los textos del usuario se escapan antes de insertarlos en HTML. Las entradas tienen límites de tamaño y catálogos cerrados. Los cambios de tickets y sus eventos se confirman de forma atómica. La carga de demostración es explícita e idempotente sobre bases ya inicializadas.

## Límites conocidos

El listado actual carga los tickets completos, incluidos comentarios e historial; para alto volumen conviene paginar y separar las proyecciones de listado/detalle. SQLite está pensado aquí para una instalación pequeña. No se incorpora infraestructura de correo, adjuntos ni despliegue público. Los artículos son públicos en la API por diseño heredado.
