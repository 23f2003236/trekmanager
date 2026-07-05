"""
Application factory.

Builds and configures the Flask application, registers extensions,
blueprints, template helpers and error handlers.
"""
from datetime import datetime

from flask import Flask, render_template

from config import config_by_name
from app.extensions import db, login_manager


def create_app(config_name: str = "default") -> Flask:
    """Create and configure a Flask application instance.

    Args:
        config_name: Key into ``config_by_name`` selecting a configuration.

    Returns:
        A fully configured :class:`flask.Flask` instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # --- Initialise extensions -------------------------------------------
    db.init_app(app)
    login_manager.init_app(app)

    # Import models so they are registered with SQLAlchemy metadata.
    from app.models import user as user_model  # noqa: F401
    from app.models import trek as trek_model  # noqa: F401
    from app.models import booking as booking_model  # noqa: F401
    from app.models import activity as activity_model  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id: str):
        """Flask-Login callback to reload a user from the session."""
        return user_model.User.query.get(int(user_id))

    # --- Register blueprints ---------------------------------------------
    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.staff.routes import staff_bp
    from app.user.routes import user_bp
    from app.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(staff_bp, url_prefix="/staff")
    app.register_blueprint(user_bp, url_prefix="/user")

    # --- Template context / filters --------------------------------------
    register_template_helpers(app)

    # --- Error handlers ---------------------------------------------------
    register_error_handlers(app)

    return app


def register_template_helpers(app: Flask) -> None:
    """Inject globals and register Jinja filters used across templates."""

    @app.context_processor
    def inject_globals():
        return {
            "current_year": datetime.utcnow().year,
            "app_name": "TrekVault",
        }

    @app.template_filter("date_pretty")
    def date_pretty(value):
        """Render a date/datetime as ``05 Jul 2026``."""
        if not value:
            return "—"
        return value.strftime("%d %b %Y")

    @app.template_filter("datetime_pretty")
    def datetime_pretty(value):
        """Render a datetime as ``05 Jul 2026, 14:30``."""
        if not value:
            return "—"
        return value.strftime("%d %b %Y, %H:%M")

    @app.template_filter("currency")
    def currency(value):
        """Render a number as an INR currency string."""
        try:
            return "₹{:,.0f}".format(float(value))
        except (TypeError, ValueError):
            return "₹0"


def register_error_handlers(app: Flask) -> None:
    """Register custom error pages for common HTTP errors."""

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500
