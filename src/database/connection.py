import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

def get_database_url():
    """Get database URL from environment variables with defaults for development."""
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    database = os.getenv('DB_NAME', 'scheduler')
    username = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'postgres')
    
    return f"postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"

def create_db_engine(database_url=None):
    """Create SQLAlchemy engine."""
    if database_url is None:
        database_url = get_database_url()
    
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
    )
    return engine

def create_session_factory(engine):
    """Create session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Global engine and session factory for the application
engine = None
SessionLocal = None

def _get_engine():
    """Get or create the database engine."""
    global engine
    if engine is None:
        engine = create_db_engine()
    return engine

def _get_session_factory():
    """Get or create the session factory."""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = create_session_factory(_get_engine())
    return SessionLocal

def get_db_session():
    """Get database session."""
    session_factory = _get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=_get_engine())