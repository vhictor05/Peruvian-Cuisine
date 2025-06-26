from DB import Base, engine
from models_folder.models_hotel import *
from models_folder.models_disco import *
from models_folder.models_restaurente import *
from models_folder.models_reporte import ReporteError

# Crea todas las tablas en main.db
Base.metadata.create_all(bind=engine)