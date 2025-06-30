from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(
    prefix="/api/v1/hotel",
    tags=["hotel"]
)

# Agregar rutas del hotel aquí
