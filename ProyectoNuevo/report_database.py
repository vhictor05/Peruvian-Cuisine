from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración específica para reportes
SQLALCHEMY_DATABASE_URL = "sqlite:///./reportes.db"  # Base de datos dedicada

# Motor de la base de datos
report_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

# Sesión específica para reportes
ReportSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=report_engine
)

# Base para modelos de reportes
ReportBase = declarative_base()

def get_report_db():
    """
    Provee una conexión a la base de datos de reportes
    """
    db = ReportSessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_report_db():
    """
    Inicializa la base de datos de reportes
    """
    from models_folder.models_reporte import ReporteError
    ReportBase.metadata.create_all(bind=report_engine)