from estructura.crud.trago_crud import TragoCRUD
from estructura.models_folder.models_disco import Trago
from sqlalchemy.orm import sessionmaker
from Database.DB import engine

if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    db = Session()
    TragoCRUD.inicializar_tragos(db)
    print("Tragos predefinidos inicializados correctamente.")
    db.close()
