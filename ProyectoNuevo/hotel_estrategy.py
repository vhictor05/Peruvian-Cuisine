from abc import ABC, abstractmethod

class EstrategiaPrecio(ABC):
    @abstractmethod
    def calcular_precio(self, base: float) -> float:
        pass

class PrecioNormal(EstrategiaPrecio):
    def calcular_precio(self, base: float) -> float:
        return base

class PrecioConDescuento(EstrategiaPrecio):
    def calcular_precio(self, base: float) -> float:
        return base * 0.8

class PrecioConIVA(EstrategiaPrecio):
    def calcular_precio(self, base: float) -> float:
        return base * 1.19


# === CONTEXTO ===
class CalculadoraPrecio:
    def __init__(self, estrategia: EstrategiaPrecio):
        self.estrategia = estrategia

    def calcular(self, base: float) -> float:
        return self.estrategia.calcular_precio(base)

# === FACTORY ===
class PrecioStrategyFactory:
    @staticmethod
    def obtener_estrategia(nombre: str) -> EstrategiaPrecio:
        estrategias = {
            "Normal": PrecioNormal(),
            "Con Descuento": PrecioConDescuento(),
            "Con IVA": PrecioConIVA()
        }
        if nombre not in estrategias:
            raise ValueError(f"Estrategia de precio '{nombre}' no soportada")
        return estrategias[nombre]
