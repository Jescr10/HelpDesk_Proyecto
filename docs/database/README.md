# Modelo de datos

SQLite se crea desde los modelos SQLAlchemy. Las fechas se guardan como UTC sin zona para compatibilidad con SQLite; el navegador las presenta en la zona local.

```mermaid
erDiagram
    users ||--o{ tickets : solicita
    users o|--o{ tickets : atiende
    users ||--o{ comments : escribe
    users ||--o{ history : actua
    users ||--o{ articles : publica
    tickets ||--o{ comments : contiene
    tickets ||--o{ history : registra
    users {
      int id PK
      string email UK
      string name
      string role
      string password_hash
    }
    tickets {
      int id PK
      string title
      text description
      string category
      string priority
      string status
      int requester_id FK
      int assignee_id FK
      datetime created_at
      datetime due_at
    }
    comments {
      int id PK
      int ticket_id FK
      int author_id FK
      text body
      datetime created_at
    }
    history {
      int id PK
      int ticket_id FK
      int actor_id FK
      string event_type
      string detail
      datetime created_at
    }
    articles {
      int id PK
      int author_id FK
      string title
      text body
      string category
      datetime created_at
    }
```

Las operaciones sobre tickets guardan el cambio y su evento en una misma transacción. Los solicitantes no pueden leer ni modificar tickets ajenos. Las contraseñas nunca se devuelven en respuestas API.

## Estados

- Abierto → En progreso o Cancelado.
- En progreso → Abierto, Resuelto o Cancelado.
- Resuelto → En progreso o Cerrado.
- Cerrado y Cancelado son finales; no se pueden editar sus datos.
- Se permiten comentarios posteriores al cierre para conservar información adicional.

Resuelto, Cerrado y Cancelado no se cuentan como pendientes ni vencidos. Un responsable debe ser técnico o supervisor.

## Evolución

`create_all` crea tablas faltantes, pero no migra columnas de una base existente. Antes de cambiar modelos persistentes, realiza una copia e incorpora migraciones versionadas (por ejemplo, Alembic). No borres una base con datos reales para aplicar un cambio de esquema.
