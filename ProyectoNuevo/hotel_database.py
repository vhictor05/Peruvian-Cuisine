from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./hotel.db"  # Nueva base de datos

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Agregar una función para eliminar las tablas y recrearlas
def recreate_db():
    # Eliminar las tablas existentes
    Base.metadata.drop_all(bind=engine)
    
    # Crear las tablas nuevas con la nueva configuración de relaciones
    Base.metadata.create_all(bind=engine)
