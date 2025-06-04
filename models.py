from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class APIDocumentation(Base):
    __tablename__ = 'api_documentation'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    source_identifier = Column(String(255))
    file_content = Column(JSON)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow)

class Environment(Base):
    __tablename__ = 'environments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    variables = Column(JSON)  # Store key-value pairs as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)

class APIHistory(Base):
    __tablename__ = 'api_history'
    
    id = Column(Integer, primary_key=True)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    request_headers = Column(JSON)
    request_body = Column(Text)
    response_status = Column(Integer)
    response_headers = Column(JSON)
    response_body = Column(Text)
    execution_time = Column(Integer)  # milliseconds
    executed_at = Column(DateTime, default=datetime.utcnow)
    environment_id = Column(Integer)

def get_engine():
    """Get database engine using environment variables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Fallback to individual components
        user = os.getenv('PGUSER', 'postgres')
        password = os.getenv('PGPASSWORD', 'password')
        host = os.getenv('PGHOST', 'localhost')
        port = os.getenv('PGPORT', '5432')
        database = os.getenv('PGDATABASE', 'api_dashboard')
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return create_engine(database_url)

def create_tables():
    """Create all tables in the database"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
