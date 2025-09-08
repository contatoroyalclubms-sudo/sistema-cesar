from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://painel_user:painel123@localhost:5432/paineluniversal")
    secret_key: str = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-aqui")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configurações de Email
    email_host: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    email_port: int = int(os.getenv("EMAIL_PORT", "587"))
    email_user: str = os.getenv("EMAIL_USER", "")
    email_password: str = os.getenv("EMAIL_PASSWORD", "")
    email_from: str = os.getenv("EMAIL_FROM", "")
    email_from_name: str = os.getenv("EMAIL_FROM_NAME", "Sistema Universal")
    email_use_tls: bool = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar campos extras do .env

settings = Settings()

engine = create_engine(
    settings.database_url,
    connect_args={} if "postgresql" in settings.database_url else {"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
