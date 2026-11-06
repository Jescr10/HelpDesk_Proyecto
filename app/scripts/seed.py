"""Carga explícita de datos ficticios para demostración local."""
from sqlalchemy import select
from app.core.config import settings
from app.core.database import create_session_factory
from app.core.security import hash_password
from app.models import User, Article
from app.schemas.tickets import TicketIn, AssignIn, StatusIn
from app.services.tickets import TicketService

DEMO_PASSWORD = "HelpDeskDemo2026!"

def seed():
    factory = create_session_factory(settings.database_url)
    with factory() as db:
        if db.scalar(select(User.id).limit(1)):
            print("La base ya contiene usuarios; no se modificó ningún dato.")
            return
        users = []
        for email, name, role in [
            ("admin@example.com", "Administración", "administrator"),
            ("supervisor@example.com", "María López", "supervisor"),
            ("technician@example.com", "Carlos Méndez", "technician"),
            ("requester@example.com", "Ana García", "requester"),
        ]:
            user = User(email=email, name=name, role=role, password_hash=hash_password(DEMO_PASSWORD))
            db.add(user); users.append(user)
        db.commit()
        svc = TicketService(db)
        for i, (title, category, priority, description) in enumerate([
            ("No puedo conectarme a la red de la oficina", "Network", "High", "Desde esta mañana mi equipo no encuentra la red de la oficina. Ya reinicié el equipo."),
            ("Solicitud de instalación de herramienta de diseño", "Software", "Medium", "Necesito instalar la herramienta autorizada para preparar las presentaciones del equipo."),
            ("La impresora del segundo nivel no responde", "Hardware", "Medium", "Los documentos se quedan en la cola de impresión y no aparecen mensajes en el panel."),
            ("Acceso al correo institucional", "Software", "Critical", "La sesión del correo muestra un error de acceso y no puedo recibir mensajes de clientes."),
            ("Configuración de pantalla adicional", "Hardware", "Low", "Necesito ayuda para extender el escritorio a una segunda pantalla en mi estación."),
            ("Consulta sobre el portal de solicitudes", "General", "Low", "Quisiera conocer cómo puedo consultar el seguimiento de mis solicitudes de soporte."),
        ]):
            ticket = svc.create(TicketIn(title=title, category=category, priority=priority, description=description), users[3])
            if i % 2 == 0:
                svc.assign(ticket["id"], AssignIn(assignee_id=users[2].id), users[0])
                svc.change_status(ticket["id"], StatusIn(status="In Progress"), users[2])
            if i == 4:
                svc.change_status(ticket["id"], StatusIn(status="Resolved"), users[2])
        for title, category, body in [
            ("Primeros pasos con tu solicitud de soporte", "General", "1. Selecciona Nuevo ticket.\n2. Escribe un título claro y describe lo que ocurrió.\n3. Elige la categoría y prioridad.\n4. Consulta el estado y responde al técnico desde el detalle del ticket."),
            ("Qué revisar si no tienes conexión a internet", "Network", "Comprueba que el Wi-Fi esté activado y que estés conectado a la red correcta. Si usas cable, revisa ambos extremos. Reinicia el equipo. Si el problema continúa, crea un ticket e indica el mensaje de error."),
            ("Consejos para proteger tu cuenta", "Software", "Usa una contraseña única y activa la verificación en dos pasos cuando esté disponible. Nunca compartas tu contraseña en un ticket. Si recibes un mensaje sospechoso, repórtalo al equipo de soporte."),
        ]:
            db.add(Article(title=title, category=category, body=body, author_id=users[0].id))
        db.commit()
        print("Datos ficticios cargados. Usuarios: admin, supervisor, technician y requester @example.com")
        print("Contraseña de demostración: " + DEMO_PASSWORD)

if __name__ == "__main__":
    seed()
