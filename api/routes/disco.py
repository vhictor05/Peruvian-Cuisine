from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from Database.DB import get_db
from models_folder.models_disco import Evento, Entrada
from api.dependencies import get_current_user

router = APIRouter()

@router.get("/eventos/")
async def get_eventos(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    eventos = db.query(Evento).all()
    return eventos

@router.get("/entradas/")
async def get_entradas(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    entradas = db.query(Entrada).all()
    return entradas