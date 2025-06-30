from Database.DB import engine, Base
from estructura.models_folder.models_reporte import ReporteError
from estructura.models_folder.models_hotel import Habitacion, Huesped, Reserva
from estructura.models_folder.models_disco import Evento, ClienteDiscoteca, Entrada, Mesa, ReservaMesa, Trago, PedidoTrago
from estructura.models_folder.models_restaurente import Cliente, Ingrediente, Menu, MenuIngrediente, Pedido

def init_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_db()