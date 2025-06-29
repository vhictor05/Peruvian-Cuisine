from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Una sola base de datos principal
SQLALCHEMY_DATABASE_URL = "sqlite:////.main.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Declarar base común
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener una sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()