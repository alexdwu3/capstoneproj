import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/castingagency')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
