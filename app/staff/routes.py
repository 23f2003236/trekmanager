"""Staff blueprint routes.

Approved staff manage the treks assigned to them: adjusting capacity,
opening / closing / starting / completing treks and viewing participants.
Staff can never touch treks that are not assigned to them.
"""
from datetime import date

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
)
from flask_login import login_required, current_user

from app.models import Booking, BookingStatus, Trek, TrekStatus
from app.forms.trek_forms import SlotsForm
from app.utils.decorators import staff_required
from app.services import trek_service
from app.services.activity_service import recent_activities

staff_bp = Blueprint("staff", __name__)


def _owned_trek_or_404(trek_id):
    """Return the trek if assigned to the current staff, else 403/404."""
    trek = Trek.query.get_or_404(trek_id)
    if trek.staff_id != current_user.id:
        # Not assigned to this guide -> forbidden.
        abort(403)
    return trek


@staff_bp.route("/")
@staff_bp.route("/dashboard")
@login_required
@staff_required
def dashboard():
    """Staff overview: assigned, today's and upcoming treks."""
    assigned = current_user.assigned_treks
    today = date.today()

    todays = assigned.filter(Trek.start_date == today).all()
    upcoming = (
        assigned.filter(Trek.start_date > today)
        .order_by(Trek.start_date.asc())
        .all()
    )
    ongoing = assigned.filter_by(status=TrekStatus.ONGOING).all()

    total_assigned = assigned.count()
    total_participants = 0
    for trek in assigned.all():
        total_participants += trek.booked_slots

    stats = {
        "assigned": total_assigned,
        "today": len(todays),
        "upcoming": len(upcoming),
        "participants": total_participants,
        "completed": assigned.filter_by(status=TrekStatus.COMPLETED).count(),
    }

    return render_template(
        "staff/dashboard.html",
        stats=stats,
        todays=todays,
        upcoming=upcoming[:5],
        ongoing=ongoing,
        activities=recent_activities(6),
    )


@staff_bp.route("/treks")
@login_required
@staff_required
def treks():
    """List / search treks assigned to the current staff member."""
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "").strip()

    query = current_user.assigned_treks
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            Trek.name.ilike(like) | Trek.location.ilike(like)
        )
    if status:
        query = query.filter(Trek.status == status)

    trek_list = query.order_by(Trek.start_date.asc()).all()
    return render_template(
        "staff/treks.html",
        treks=trek_list,
        keyword=keyword,
        status=status,
        statuses=TrekStatus.ALL,
    )


@staff_bp.route("/treks/<int:trek_id>", methods=["GET", "POST"])
@login_required
@staff_required
def trek_detail(trek_id):
    """View an assigned trek, its participants and manage its slots."""
    trek = _owned_trek_or_404(trek_id)
    form = SlotsForm()

    if form.validate_on_submit():
        ok, msg = trek_service.update_slots(trek, form.slots.data, current_user)
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("staff.trek_detail", trek_id=trek.id))

    if request.method == "GET":
        form.slots.data = trek.slots

    participants = trek.bookings.filter(
        Booking.status != BookingStatus.CANCELLED
    ).all()

    return render_template(
        "staff/trek_detail.html",
        trek=trek,
        form=form,
        participants=participants,
    )


@staff_bp.route("/treks/<int:trek_id>/status", methods=["POST"])
@login_required
@staff_required
def trek_status(trek_id):
    """Transition an assigned trek's lifecycle status."""
    trek = _owned_trek_or_404(trek_id)
    action = request.form.get("action")

    mapping = {
        "open": TrekStatus.OPEN,
        "close": TrekStatus.CLOSED,
        "start": TrekStatus.ONGOING,
        "complete": TrekStatus.COMPLETED,
    }
    if action not in mapping:
        abort(400)

    ok, msg = trek_service.set_trek_status(trek, mapping[action], current_user)
    flash(msg, "success" if ok else "danger")
    return redirect(request.referrer or url_for("staff.trek_detail", trek_id=trek.id))
