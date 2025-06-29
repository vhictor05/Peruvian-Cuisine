from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from Database.DB import get_db
from models_folder.models_restaurente import Menu, Pedido
from api.dependencies import get_current_user

router = APIRouter()

@router.get("/menus/")
async def get_menus(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    menus = db.query(Menu).all()
    return menus

@router.get("/pedidos/")
async def get_pedidos(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    pedidos = db.query(Pedido).all()
    return pedidos