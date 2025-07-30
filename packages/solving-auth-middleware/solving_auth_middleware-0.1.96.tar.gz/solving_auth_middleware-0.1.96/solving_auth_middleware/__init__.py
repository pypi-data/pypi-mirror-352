from flask import Flask
from .config import Config
from .middleware import requires_permissions
from .enums import UserTypeEnum

__version__ = '0.1.8'

def create_app(config_class=Config):
    """Crée et configure une nouvelle instance de l'application Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)
    return app

__all__ = ['create_app', 'requires_permissions', 'Config', UserTypeEnum]
