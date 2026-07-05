"""
Application entry point.

Running ``python run.py`` creates the application, initialises the database
(creating tables and seeding default data on first run) and starts the
development server.
"""
import os

from app import create_app, db
from app.services.seed_service import seed_database

# Create the Flask application instance using the environment-selected config.
app = create_app(os.environ.get("FLASK_CONFIG", "default"))


def bootstrap():
    """Create database tables and seed default data if the DB is empty."""
    with app.app_context():
        # Ensure the instance folder exists for the SQLite file.
        os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
        db.create_all()
        seed_database()


if __name__ == "__main__":
    bootstrap()
    # host=0.0.0.0 makes the server reachable from other devices on the LAN,
    # which is handy for testing the responsive layout on a phone/tablet.
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", True))
