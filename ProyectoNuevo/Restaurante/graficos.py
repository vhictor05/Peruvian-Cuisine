import matplotlib.pyplot as plt
from crud.pedido_crud import PedidoCRUD
from crud.menu_crud import MenuCRUD
from crud.ingrediente_crud import IngredienteCRUD

def graficar_ventas_por_fecha(db):
    pedidos = PedidoCRUD.leer_pedidos(db)
    ventas_por_fecha = {}
    
    for pedido in pedidos:
        fecha = pedido.fecha.strftime("%Y-%m-%d")
        if fecha in ventas_por_fecha:
            ventas_por_fecha[fecha] += pedido.total
        else:
            ventas_por_fecha[fecha] = pedido.total

    fechas = list(ventas_por_fecha.keys())
    ventas = list(ventas_por_fecha.values())

    plt.figure(figsize=(10, 6))
    plt.plot(fechas, ventas, marker="o", color="blue", label="Ventas")
    plt.title("Ventas por Fecha")
    plt.xlabel("Fecha")
    plt.ylabel("Total de Ventas ($)")
    plt.grid()
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def graficar_menus_mas_comprados(db):
    pedidos = PedidoCRUD.leer_pedidos(db)
    menu_compras = {}

    for pedido in pedidos:
        for menu in pedido.menus:
            menu_obj = MenuCRUD.get_menu_by_id(db, menu["id"])
            if menu_obj.nombre in menu_compras:
                menu_compras[menu_obj.nombre] += menu["cantidad"]
            else:
                menu_compras[menu_obj.nombre] = menu["cantidad"]

    menus = list(menu_compras.keys())
    cantidades = list(menu_compras.values())

    plt.figure(figsize=(8, 8))
    plt.pie(cantidades, labels=menus, autopct="%1.1f%%", startangle=140)
    plt.title("Distribución de Menús Más Comprados")
    plt.axis("equal")
    plt.show()

def graficar_uso_ingredientes(db):
    pedidos = PedidoCRUD.leer_pedidos(db)
    uso_ingredientes = {}

    for pedido in pedidos:
        for menu in pedido.menus:
            menu_obj = MenuCRUD.get_menu_by_id(db, menu["id"])
            for ing_nombre, cantidad in menu_obj.ing_necesarios.items():
                if ing_nombre in uso_ingredientes:
                    uso_ingredientes[ing_nombre] += cantidad * menu["cantidad"]
                else:
                    uso_ingredientes[ing_nombre] = cantidad * menu["cantidad"]

    ingredientes = list(uso_ingredientes.keys())
    cantidades = list(uso_ingredientes.values())

    plt.figure(figsize=(12, 6))
    plt.bar(ingredientes, cantidades, color="skyblue")
    plt.title("Uso de Ingredientes Basado en Todos los Pedidos")
    plt.xlabel("Ingrediente")
    plt.ylabel("Cantidad Utilizada")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
