"""Admin blueprint routes.

Provides the admin dashboard, trek CRUD, staff moderation, user moderation,
booking management, reports and cross-entity search.
"""
import os
import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    abort,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import (
    Activity,
    Booking,
    BookingStatus,
    RoleEnum,
    StaffStatus,
    Trek,
    TrekStatus,
    User,
)
from app.forms.trek_forms import TrekForm
from app.utils.decorators import admin_required
from app.services import trek_service
from app.services.activity_service import log_activity, recent_activities

admin_bp = Blueprint("admin", __name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _staff_choices():
    """Return (id, label) choices of staff for the assign-guide dropdown."""
    staff = User.query.filter_by(role=RoleEnum.STAFF, status=StaffStatus.APPROVED).all()
    choices = [(0, "— Unassigned —")]
    choices += [(s.id, f"{s.full_name} (@{s.username})") for s in staff]
    return choices


def _save_image(file_storage):
    """Persist an uploaded image and return its stored filename (or None)."""
    if not file_storage or not file_storage.filename:
        return None
    ext = os.path.splitext(secure_filename(file_storage.filename))[1].lower()
    filename = f"trek-{uuid.uuid4().hex[:12]}{ext}"
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, filename))
    return filename


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@admin_bp.route("/")
@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Render the admin overview dashboard with headline statistics."""
    stats = {
        "total_treks": Trek.query.count(),
        "total_users": User.query.filter_by(role=RoleEnum.USER).count(),
        "total_staff": User.query.filter_by(role=RoleEnum.STAFF).count(),
        "pending_staff": User.query.filter_by(
            role=RoleEnum.STAFF, status=StaffStatus.PENDING
        ).count(),
        "total_bookings": Booking.query.filter_by(status=BookingStatus.CONFIRMED).count(),
        "completed_treks": Trek.query.filter_by(status=TrekStatus.COMPLETED).count(),
        "open_treks": Trek.query.filter_by(status=TrekStatus.OPEN).count(),
        "revenue": db.session.query(db.func.coalesce(db.func.sum(Trek.price), 0))
        .select_from(Booking)
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Booking.status != BookingStatus.CANCELLED)
        .scalar(),
    }

    upcoming = (
        Trek.query.filter(Trek.status.in_([TrekStatus.OPEN, TrekStatus.CLOSED]))
        .order_by(Trek.start_date.asc())
        .limit(5)
        .all()
    )
    pending_staff_list = (
        User.query.filter_by(role=RoleEnum.STAFF, status=StaffStatus.PENDING)
        .order_by(User.created_at.desc())
        .all()
    )

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        upcoming=upcoming,
        pending_staff_list=pending_staff_list,
        activities=recent_activities(8),
    )


# ---------------------------------------------------------------------------
# Trek management
# ---------------------------------------------------------------------------
@admin_bp.route("/treks")
@login_required
@admin_required
def treks():
    """List / search all treks."""
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    page = request.args.get("page", 1, type=int)

    query = trek_service.search_treks(
        keyword=keyword or None,
        status=status or None,
        difficulty=difficulty or None,
    )
    pagination = query.paginate(page=page, per_page=8, error_out=False)

    return render_template(
        "admin/treks.html",
        pagination=pagination,
        treks=pagination.items,
        keyword=keyword,
        status=status,
        difficulty=difficulty,
        statuses=TrekStatus.ALL,
    )


@admin_bp.route("/treks/new", methods=["GET", "POST"])
@login_required
@admin_required
def trek_create():
    """Create a new trek."""
    form = TrekForm()
    form.staff_id.choices = _staff_choices()

    if form.validate_on_submit():
        image_filename = _save_image(form.image.data)
        trek = trek_service.create_trek(form, current_user, image_filename)
        flash(f"Trek '{trek.name}' created successfully.", "success")
        return redirect(url_for("admin.treks"))

    return render_template("admin/trek_form.html", form=form, title="Create Trek")


@admin_bp.route("/treks/<int:trek_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def trek_edit(trek_id):
    """Edit an existing trek."""
    trek = Trek.query.get_or_404(trek_id)
    form = TrekForm(obj=trek)
    form.staff_id.choices = _staff_choices()

    if request.method == "GET":
        form.staff_id.data = trek.staff_id or 0

    if form.validate_on_submit():
        image_filename = _save_image(form.image.data)
        trek_service.update_trek(trek, form, current_user, image_filename)
        flash(f"Trek '{trek.name}' updated.", "success")
        return redirect(url_for("admin.treks"))

    return render_template(
        "admin/trek_form.html", form=form, title="Edit Trek", trek=trek
    )


@admin_bp.route("/treks/<int:trek_id>/delete", methods=["POST"])
@login_required
@admin_required
def trek_delete(trek_id):
    """Delete a trek."""
    trek = Trek.query.get_or_404(trek_id)
    trek_service.delete_trek(trek, current_user)
    flash("Trek deleted.", "info")
    return redirect(url_for("admin.treks"))


@admin_bp.route("/treks/<int:trek_id>")
@login_required
@admin_required
def trek_detail(trek_id):
    """View a single trek with its participant list."""
    trek = Trek.query.get_or_404(trek_id)
    bookings = trek.bookings.filter(Booking.status != BookingStatus.CANCELLED).all()
    return render_template("admin/trek_detail.html", trek=trek, bookings=bookings)


# ---------------------------------------------------------------------------
# Staff management
# ---------------------------------------------------------------------------
@admin_bp.route("/staff")
@login_required
@admin_required
def staff():
    """List / search staff accounts."""
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()

    query = User.query.filter_by(role=RoleEnum.STAFF)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            db.or_(
                User.full_name.ilike(like),
                User.username.ilike(like),
                User.email.ilike(like),
            )
        )
    if status:
        query = query.filter(User.status == status)

    staff_list = query.order_by(User.created_at.desc()).all()
    return render_template(
        "admin/staff.html",
        staff_list=staff_list,
        keyword=keyword,
        status=status,
        statuses=[StaffStatus.PENDING, StaffStatus.APPROVED,
                  StaffStatus.REJECTED, StaffStatus.BLACKLISTED],
    )


@admin_bp.route("/staff/<int:staff_id>/action", methods=["POST"])
@login_required
@admin_required
def staff_action(staff_id):
    """Approve / reject / blacklist / reinstate a staff member."""
    member = User.query.filter_by(id=staff_id, role=RoleEnum.STAFF).first_or_404()
    action = request.form.get("action")

    mapping = {
        "approve": (StaffStatus.APPROVED, "approved", "bi-check-circle"),
        "reject": (StaffStatus.REJECTED, "rejected", "bi-x-circle"),
        "blacklist": (StaffStatus.BLACKLISTED, "blacklisted", "bi-slash-circle"),
        "reinstate": (StaffStatus.APPROVED, "reinstated", "bi-arrow-counterclockwise"),
    }
    if action not in mapping:
        abort(400)

    new_status, verb, icon = mapping[action]
    member.status = new_status
    log_activity(
        f"{current_user.full_name} {verb} staff '{member.full_name}'",
        actor=current_user,
        category="staff",
        icon=icon,
        commit=False,
    )
    db.session.commit()
    flash(f"Staff member {member.full_name} {verb}.", "success")
    return redirect(request.referrer or url_for("admin.staff"))


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------
@admin_bp.route("/users")
@login_required
@admin_required
def users():
    """List / search regular users."""
    keyword = request.args.get("keyword", "").strip()
    query = User.query.filter_by(role=RoleEnum.USER)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            db.or_(
                User.full_name.ilike(like),
                User.username.ilike(like),
                User.email.ilike(like),
            )
        )
    user_list = query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", user_list=user_list, keyword=keyword)


@admin_bp.route("/users/<int:user_id>/blacklist", methods=["POST"])
@login_required
@admin_required
def user_blacklist(user_id):
    """Toggle the blacklist flag on a regular user."""
    member = User.query.filter_by(id=user_id, role=RoleEnum.USER).first_or_404()
    member.is_blacklisted = not member.is_blacklisted
    verb = "blacklisted" if member.is_blacklisted else "reinstated"
    log_activity(
        f"{current_user.full_name} {verb} user '{member.full_name}'",
        actor=current_user,
        category="user",
        icon="bi-slash-circle" if member.is_blacklisted else "bi-check-circle",
        commit=False,
    )
    db.session.commit()
    flash(f"User {member.full_name} {verb}.", "success")
    return redirect(request.referrer or url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>")
@login_required
@admin_required
def user_detail(user_id):
    """View a single user's profile and booking history."""
    member = User.query.get_or_404(user_id)
    bookings = member.bookings.order_by(Booking.booking_date.desc()).all()
    return render_template("admin/user_detail.html", member=member, bookings=bookings)


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------
@admin_bp.route("/bookings")
@login_required
@admin_required
def bookings():
    """List / search all bookings across the platform."""
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()

    query = Booking.query.join(User, Booking.user_id == User.id).join(
        Trek, Booking.trek_id == Trek.id
    )
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            db.or_(User.full_name.ilike(like), Trek.name.ilike(like))
        )
    if status:
        query = query.filter(Booking.status == status)

    booking_list = query.order_by(Booking.booking_date.desc()).all()
    return render_template(
        "admin/bookings.html",
        booking_list=booking_list,
        keyword=keyword,
        status=status,
        statuses=BookingStatus.ALL,
    )


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    """Aggregate reports: booking history, completed treks, staff/user activity."""
    completed_treks = (
        Trek.query.filter_by(status=TrekStatus.COMPLETED)
        .order_by(Trek.end_date.desc())
        .all()
    )

    # Staff activity: how many treks each staff member is running.
    staff_activity = []
    for s in User.query.filter_by(role=RoleEnum.STAFF, status=StaffStatus.APPROVED).all():
        assigned = s.assigned_treks.count()
        completed = s.assigned_treks.filter_by(status=TrekStatus.COMPLETED).count()
        staff_activity.append({"staff": s, "assigned": assigned, "completed": completed})

    # User activity: bookings per user.
    user_activity = []
    for u in User.query.filter_by(role=RoleEnum.USER).all():
        total = u.bookings.count()
        active = u.bookings.filter_by(status=BookingStatus.CONFIRMED).count()
        if total:
            user_activity.append({"user": u, "total": total, "active": active})
    user_activity.sort(key=lambda x: x["total"], reverse=True)

    recent_bookings = (
        Booking.query.order_by(Booking.booking_date.desc()).limit(15).all()
    )

    return render_template(
        "admin/reports.html",
        completed_treks=completed_treks,
        staff_activity=staff_activity,
        user_activity=user_activity,
        recent_bookings=recent_bookings,
    )


# ---------------------------------------------------------------------------
# Global search
# ---------------------------------------------------------------------------
@admin_bp.route("/search")
@login_required
@admin_required
def search():
    """Cross-entity search across treks, users, staff and bookings."""
    q = request.args.get("q", "").strip()
    results = {"treks": [], "users": [], "staff": [], "bookings": []}

    if q:
        like = f"%{q}%"
        results["treks"] = Trek.query.filter(
            db.or_(Trek.name.ilike(like), Trek.location.ilike(like))
        ).all()
        results["users"] = User.query.filter(
            User.role == RoleEnum.USER,
            db.or_(
                User.full_name.ilike(like),
                User.username.ilike(like),
                User.email.ilike(like),
            ),
        ).all()
        results["staff"] = User.query.filter(
            User.role == RoleEnum.STAFF,
            db.or_(
                User.full_name.ilike(like),
                User.username.ilike(like),
                User.email.ilike(like),
            ),
        ).all()
        results["bookings"] = (
            Booking.query.join(Trek, Booking.trek_id == Trek.id)
            .filter(Trek.name.ilike(like))
            .all()
        )

    total = sum(len(v) for v in results.values())
    return render_template("admin/search.html", q=q, results=results, total=total)
