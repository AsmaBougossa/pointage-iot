import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Configuration de base — lue depuis les variables d'environnement (.env)."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 8  # 8h

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:@localhost:3306/pointage_iot"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    FACE_RECOGNITION_TOLERANCE = float(os.getenv("FACE_RECOGNITION_TOLERANCE", 0.5))
    CAMERA_DEFAULT_SOURCE = os.getenv("CAMERA_DEFAULT_SOURCE", "0")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    ENCODINGS_FOLDER = os.path.join(BASE_DIR, "app", "static", "encodings")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "TEST_DATABASE_URL", "mysql+pymysql://root:@localhost:3306/pointage_iot_test"
    )


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
