from fastapi import Depends
from sqlalchemy.orm import Session
from Database.DB import get_db
from typing import Generator

# Versión simplificada sin autenticación
async def get_current_user():
    return "test_user"  # Retorna un usuario por defecto

def get_db_session() -> Generator[Session, None, None]:
    db = get_db()
    try:
        yield db
    finally:
        db.close()