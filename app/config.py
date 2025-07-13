import os
from dotenv import load_dotenv

TEST_DB = os.path.abspath('test_temp.db')

load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_PRIMARY_HOST = os.getenv("POSTGRES_PRIMARY_HOST", "primary-db-host")
    POSTGRES_REPLICA_HOST = os.getenv("POSTGRES_REPLICA_HOST", "read-replica-host")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME", "beanbeano_db")
    APP_PORT = os.getenv("APP_PORT", "8000")
    SQLALCHEMY_DATABASE_URI = f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_PRIMARY_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    READING_REPLICAS = os.getenv("READING_REPLICAS", "2")

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{TEST_DB}"
    TESTING = True
    POSTGRES_PRIMARY_HOST = ""
    POSTGRES_REPLICA_BASE = ""
    READ_REPLICAS = "0"