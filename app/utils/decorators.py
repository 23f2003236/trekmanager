"""Authorisation decorators.

These wrap view functions to enforce role-based access control. They rely on
Flask-Login's ``current_user`` and abort with an appropriate HTTP status
(or redirect) when access is denied.
"""
from functools import wraps

from flask import abort, redirect, url_for, flash
from flask_login import current_user

from app.models import RoleEnum, StaffStatus


def role_required(*roles):
    """Restrict a view to users whose role is in ``roles``.

    Usage::

        @role_required(RoleEnum.ADMIN)
        def view(): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def admin_required(view_func):
    """Allow only admin accounts."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def staff_required(view_func):
    """Allow only approved staff accounts.

    Pending, rejected or blacklisted staff are redirected with a message
    explaining why they cannot access the dashboard.
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_staff:
            abort(403)
        if current_user.status == StaffStatus.PENDING:
            flash(
                "Your staff account is awaiting admin approval.",
                "warning",
            )
            return redirect(url_for("auth.pending"))
        if current_user.status in (StaffStatus.REJECTED, StaffStatus.BLACKLISTED):
            flash("Your staff account is not active. Contact the administrator.", "danger")
            return redirect(url_for("auth.logout"))
        return view_func(*args, **kwargs)

    return wrapped


def user_required(view_func):
    """Allow only regular (non-blacklisted) user accounts."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_user:
            abort(403)
        if current_user.is_blacklisted:
            flash("Your account has been suspended.", "danger")
            return redirect(url_for("auth.logout"))
        return view_func(*args, **kwargs)

    return wrapped
