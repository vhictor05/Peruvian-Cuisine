from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from Database.DB import get_db
from models_folder.models_reporte import ReporteError
from api.dependencies import get_current_user

router = APIRouter()

@router.get("/errores/")
async def get_errores(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        errores = db.query(ReporteError).all()
        return errores
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/errores/")
async def crear_error(
    titulo: str,
    descripcion: str,
    modulo: str,
    urgencia: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        nuevo_error = ReporteError(
            titulo=titulo,
            descripcion=descripcion,
            modulo=modulo,
            urgencia=urgencia,
            reportado_por=current_user,
            estado="Abierto"
        )
        db.add(nuevo_error)
        db.commit()
        db.refresh(nuevo_error)
        return nuevo_error
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))