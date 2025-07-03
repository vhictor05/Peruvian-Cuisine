import sys
from pathlib import Path

# Agregar el directorio padre al path para encontrar 'Database'
current_dir = Path(__file__).parent
project_dir = current_dir.parent
sys.path.append(str(project_dir))


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base de datos principal
SQLALCHEMY_DATABASE_URL = "sqlite:///./main.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Base declarativa única
Base = declarative_base()

# Sesión única
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alias para mantener compatibilidad con el código existente
get_report_db = get_db
init_report_db = lambda: Base.metadata.create_all(bind=engine)