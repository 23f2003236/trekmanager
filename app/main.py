"""Public / landing blueprint.

Contains the marketing hero landing page and a health check.
"""
from flask import Blueprint, render_template, redirect
from flask_login import current_user

from app.models import Trek, TrekStatus, User, RoleEnum
from app.utils.helpers import dashboard_url_for

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Render the hero landing page (or redirect logged-in users to their dashboard)."""
    if current_user.is_authenticated:
        return redirect(dashboard_url_for(current_user))

    # Feature a few open treks on the landing page.
    featured = (
        Trek.query.filter_by(status=TrekStatus.OPEN)
        .order_by(Trek.start_date.asc())
        .limit(3)
        .all()
    )

    stats = {
        "treks": Trek.query.count(),
        "trekkers": User.query.filter_by(role=RoleEnum.USER).count(),
        "guides": User.query.filter_by(role=RoleEnum.STAFF).count(),
    }
    return render_template("landing.html", featured=featured, stats=stats)
