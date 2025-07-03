import os
from dotenv import load_dotenv

TEST_DB = os.path.abspath('test_temp.db')

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://user:pass@localhost:5432/coffee_db"

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{TEST_DB}'
    TESTING = True
