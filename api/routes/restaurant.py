from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.restaurant import Menu, Order, Client, Ingredient

router = APIRouter(
    prefix="/api/v1/restaurant",
    tags=["restaurant"]
)

@router.get("/menu", response_model=List[Menu])
async def get_menu():
    '''Obtiene todo el menú disponible'''
    pass

@router.post("/menu", response_model=Menu)
async def create_menu_item(menu: Menu):
    '''Crea un nuevo ítem en el menú'''
    pass

@router.put("/menu/{item_id}", response_model=Menu)
async def update_menu_item(item_id: int, menu: Menu):
    '''Actualiza un ítem del menú'''
    pass

@router.delete("/menu/{item_id}")
async def delete_menu_item(item_id: int):
    '''Elimina un ítem del menú'''
    pass
