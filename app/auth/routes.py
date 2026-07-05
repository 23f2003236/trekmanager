"""Authentication routes: login, register, logout, pending screen."""
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models import User, RoleEnum, StaffStatus
from app.forms.auth_forms import LoginForm, RegisterForm
from app.services.activity_service import log_activity
from app.utils.helpers import dashboard_url_for

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an existing user and redirect to their dashboard."""
    if current_user.is_authenticated:
        return redirect(dashboard_url_for(current_user))

    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data.strip()
        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier.lower())
        ).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", form=form)

        # Enforce blacklist / staff-status rules at login.
        if user.is_blacklisted:
            flash("Your account has been suspended. Please contact support.", "danger")
            return render_template("auth/login.html", form=form)

        if user.is_staff and user.status == StaffStatus.REJECTED:
            flash("Your staff application was rejected.", "danger")
            return render_template("auth/login.html", form=form)

        if user.is_staff and user.status == StaffStatus.BLACKLISTED:
            flash("Your staff account has been blacklisted.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember.data)

        # Pending staff are logged in but sent to the waiting screen.
        if user.is_staff and user.status == StaffStatus.PENDING:
            return redirect(url_for("auth.pending"))

        flash(f"Welcome back, {user.full_name.split()[0]}!", "success")
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(dashboard_url_for(user))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user or staff member.

    Users are immediately active; staff start in the ``pending`` state and
    must be approved by an admin before they can access the staff dashboard.
    """
    if current_user.is_authenticated:
        return redirect(dashboard_url_for(current_user))

    form = RegisterForm()
    if form.validate_on_submit():
        role = form.role.data if form.role.data in (RoleEnum.USER, RoleEnum.STAFF) else RoleEnum.USER
        status = StaffStatus.PENDING if role == RoleEnum.STAFF else StaffStatus.APPROVED

        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data.strip() if form.phone.data else None,
            role=role,
            status=status,
        )
        user.set_password(form.password.data)
        db.session.add(user)

        log_activity(
            f"{user.full_name} registered as {role}",
            actor=user,
            category="auth",
            icon="bi-person-plus",
            commit=False,
        )
        db.session.commit()

        if role == RoleEnum.STAFF:
            flash(
                "Account created! Your guide application is pending admin approval.",
                "info",
            )
        else:
            flash("Account created successfully. You can now sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/pending")
@login_required
def pending():
    """Waiting screen shown to staff whose account is not yet approved."""
    if not current_user.is_staff:
        return redirect(dashboard_url_for(current_user))
    if current_user.status == StaffStatus.APPROVED:
        return redirect(url_for("staff.dashboard"))
    return render_template("auth/pending.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log the current user out."""
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
