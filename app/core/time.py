"""SQLite stores naive datetimes; every stored value represents UTC."""
from datetime import datetime, timezone

def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
