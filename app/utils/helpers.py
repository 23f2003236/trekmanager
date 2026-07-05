"""Small reusable helper functions used across blueprints."""
from flask import url_for
from flask_login import current_user


def dashboard_url_for(user) -> str:
    """Return the correct dashboard URL for a given user based on role."""
    if user is None or not user.is_authenticated:
        return url_for("main.index")
    if user.is_admin:
        return url_for("admin.dashboard")
    if user.is_staff:
        return url_for("staff.dashboard")
    return url_for("user.dashboard")


def current_dashboard_url() -> str:
    """Convenience wrapper around :func:`dashboard_url_for` for the current user."""
    return dashboard_url_for(current_user)


def paginate_query(query, page: int, per_page: int = 9):
    """Paginate a SQLAlchemy query returning a Pagination object."""
    return query.paginate(page=page, per_page=per_page, error_out=False)
