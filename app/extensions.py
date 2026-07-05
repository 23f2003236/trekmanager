"""
Central place where Flask extensions are instantiated.

Keeping the extension objects here (separate from the app factory) avoids
circular imports: models and blueprints import from this module, while the
factory in ``app/__init__.py`` initialises them against the app instance.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# ORM / database handle.
db = SQLAlchemy()

# Login / session manager.
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to continue."
login_manager.login_message_category = "warning"
