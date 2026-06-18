import os
import secrets

class Config:
    # B8 FIX: Never use a hardcoded default secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # Render provides postgres:// but SQLAlchemy 2.x requires postgresql://
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///../instance/app.db')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,     # Verify connections before use
        "pool_recycle": 300,        # Recycle connections every 5 minutes
    }

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size

    # Rate limiting defaults
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')

    # CORS — B7 FIX: whitelist specific origins, not wildcard
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/aat_db')

    def __init__(self):
        # In production, SECRET_KEY MUST be set via environment variable
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("No SECRET_KEY set for production environment!")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    GEMINI_API_KEY = None  # Disable Gemini in tests
