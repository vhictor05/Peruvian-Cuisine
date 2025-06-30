from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(
    prefix="/api/v1/disco",
    tags=["disco"]
)

# Agregar rutas de la discoteca aquí
