from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from Database.DB import get_db
from models_folder.models_hotel import Habitacion, Reserva

router = APIRouter()

@router.get("/habitaciones/")
async def get_habitaciones(
    db: Session = Depends(get_db)  # Quitamos la dependencia del current_user
):
    habitaciones = db.query(Habitacion).all()
    return habitaciones

@router.get("/reservas/")
async def get_reservas(
    db: Session = Depends(get_db)  # Quitamos la dependencia del current_user
):
    reservas = db.query(Reserva).all()
    return reservas