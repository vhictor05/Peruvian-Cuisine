from abc import ABC, abstractmethod
from typing import List
from tkinter import messagebox
from datetime import datetime

# =================== INVENTORY OBSERVER PATTERN ===================

class InventorySubject:
    """Subject/Observable para cambios en el inventario"""

    def __init__(self):
        self._observers: List['InventoryObserver'] = []
        self._inventory_data = {}

    def attach(self, observer: 'InventoryObserver'):
        """Registra un observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: 'InventoryObserver'):
        """Desregistra un observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_inventory_change(self, ingredient_name: str, old_quantity: float, new_quantity: float):
        """Notifica a todos los observers sobre cambios en el inventario"""
        for observer in self._observers:
            observer.update_inventory(ingredient_name, old_quantity, new_quantity)


class InventoryObserver(ABC):
    """Interfaz Observer para cambios en inventario"""

    @abstractmethod
    def update_inventory(self, ingredient_name: str, old_quantity: float, new_quantity: float):
        pass


class StockAlertObserver(InventoryObserver):
    """Observer que muestra alertas de stock bajo"""

    def __init__(self, low_stock_threshold=5):
        self.low_stock_threshold = low_stock_threshold

    def update_inventory(self, ingredient_name: str, old_quantity: float, new_quantity: float):
        """Muestra alertas cuando el stock está bajo"""
        if new_quantity < self.low_stock_threshold and new_quantity >= 0:
            messagebox.showwarning(
                "⚠️ Stock Bajo",
                f"¡Atención! El ingrediente '{ingredient_name}' tiene stock bajo:\n"
                f"Cantidad actual: {new_quantity}\n"
                f"Se recomienda reabastecer pronto."
            )
        elif new_quantity < 0:
            messagebox.showerror(
                "❌ Stock Agotado",
                f"¡ERROR! El ingrediente '{ingredient_name}' tiene stock negativo:\n"
                f"Cantidad actual: {new_quantity}"
            )


class PanelRefreshObserver(InventoryObserver):
    """Observer que actualiza paneles cuando cambia el inventario"""

    def __init__(self):
        self.panels = []

    def add_panel(self, panel):
        """Agrega un panel para actualizar"""
        if hasattr(panel, 'refresh_list'):
            self.panels.append(panel)

    def update_inventory(self, ingredient_name: str, old_quantity: float, new_quantity: float):
        """Actualiza todos los paneles registrados"""
        for panel in self.panels:
            try:
                panel.refresh_list()
            except Exception as e:
                print(f"Error actualizando panel: {e}")


class InventoryUpdateObserver(InventoryObserver):
    """Descuenta ingredientes automáticamente cuando cambia el inventario"""

    def __init__(self, db):
        self.db = db

    def update_inventory(self, ingredient_name: str, old_quantity: float, new_quantity: float):
        print(f"[Descuento automático] '{ingredient_name}' actualizado de {old_quantity} → {new_quantity}")


# =================== ORDER OBSERVER PATTERN ===================

class OrderSubject:
    """Subject/Observable para eventos de pedidos"""

    def __init__(self):
        self._observers: List['OrderObserver'] = []

    def attach(self, observer: 'OrderObserver'):
        """Registra un observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: 'OrderObserver'):
        """Desregistra un observer"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_new_order(self, pedido):
        """Notifica sobre un nuevo pedido"""
        for observer in self._observers:
            observer.on_new_order(pedido)


class OrderObserver(ABC):
    """Interfaz Observer para eventos de pedidos"""

    @abstractmethod
    def on_new_order(self, pedido):
        pass


class KitchenNotificationObserver(OrderObserver):
    """Observer que maneja notificaciones de cocina"""

    def on_new_order(self, pedido):
        """Notifica a la cocina sobre un nuevo pedido"""
        messagebox.showinfo(
            "🍳 Nuevo Pedido para Cocina",
            f"Nuevo pedido #{pedido.id} recibido"
        )


class AuditLogObserver(InventoryObserver, OrderObserver):
    """Registra logs de acciones del sistema"""

    def update_inventory(self, ingredient_name: str, old_quantity: float, new_quantity: float):
        log = f"[AUDIT] Inventario actualizado - {ingredient_name}: {old_quantity} → {new_quantity} @ {datetime.now()}"
        print(log)

    def on_new_order(self, pedido):
        log = f"[AUDIT] Pedido creado - ID: {pedido.id} @ {datetime.now()}"
        print(log)


# =================== OBSERVER MANAGER ===================

class ObserverManager:
    """Gestor centralizado de todos los observers del sistema"""

    def __init__(self, db):
        self.db = db

        # Crear subjects
        self.inventory_subject = InventorySubject()
        self.order_subject = OrderSubject()

        # Crear observers básicos
        self.stock_alert_observer = StockAlertObserver()
        self.panel_refresh_observer = PanelRefreshObserver()
        self.inventory_update_observer = InventoryUpdateObserver(db)
        self.kitchen_observer = KitchenNotificationObserver()
        self.audit_observer = AuditLogObserver()

        # Registrar observers básicos
        self.inventory_subject.attach(self.stock_alert_observer)
        self.inventory_subject.attach(self.panel_refresh_observer)
        self.inventory_subject.attach(self.inventory_update_observer)
        self.inventory_subject.attach(self.audit_observer)

        self.order_subject.attach(self.kitchen_observer)
        self.order_subject.attach(self.audit_observer)

    def notify_inventory_change(self, ingredient_name: str, old_quantity: float, new_quantity: float):
        """Notifica cambios en el inventario"""
        self.inventory_subject.notify_inventory_change(ingredient_name, old_quantity, new_quantity)

    def notify_new_order(self, pedido):
        """Notifica un nuevo pedido"""
        self.order_subject.notify_new_order(pedido)
