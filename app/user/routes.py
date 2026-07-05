"""User (trekker) blueprint routes.

Regular users browse and book treks, manage their bookings and edit their
profile. All booking rules are delegated to :mod:`app.services.booking_service`.
"""
from datetime import date

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Booking, BookingStatus, Trek, TrekStatus, DifficultyEnum
from app.forms.trek_forms import BookingForm
from app.forms.auth_forms import ProfileForm
from app.utils.decorators import user_required
from app.services import trek_service, booking_service

user_bp = Blueprint("user", __name__)


@user_bp.route("/")
@user_bp.route("/dashboard")
@login_required
@user_required
def dashboard():
    """User overview: upcoming bookings, stats and recommended treks."""
    all_bookings = current_user.bookings

    confirmed = all_bookings.filter_by(status=BookingStatus.CONFIRMED).all()
    upcoming = [b for b in confirmed if b.trek and b.trek.start_date >= date.today()]
    upcoming.sort(key=lambda b: b.trek.start_date)

    stats = {
        "upcoming": len(upcoming),
        "completed": all_bookings.filter_by(status=BookingStatus.COMPLETED).count(),
        "total": all_bookings.count(),
        "cancelled": all_bookings.filter_by(status=BookingStatus.CANCELLED).count(),
    }

    recommended = (
        Trek.query.filter_by(status=TrekStatus.OPEN)
        .filter(Trek.remaining_slots > 0)
        .order_by(Trek.start_date.asc())
        .limit(3)
        .all()
    )

    return render_template(
        "user/dashboard.html",
        stats=stats,
        upcoming=upcoming[:4],
        recommended=recommended,
    )


@user_bp.route("/treks")
@login_required
@user_required
def treks():
    """Browse / search / filter available treks."""
    keyword = request.args.get("keyword", "").strip()
    location = request.args.get("location", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    start_date = request.args.get("start_date", "").strip()
    page = request.args.get("page", 1, type=int)

    parsed_date = None
    if start_date:
        try:
            parsed_date = date.fromisoformat(start_date)
        except ValueError:
            parsed_date = None

    query = trek_service.available_treks(
        keyword=keyword or None,
        location=location or None,
        difficulty=difficulty or None,
        start_date=parsed_date,
    )
    pagination = query.paginate(page=page, per_page=9, error_out=False)

    # IDs of treks the user has already booked (to disable the button).
    booked_ids = {
        b.trek_id
        for b in current_user.bookings.filter_by(status=BookingStatus.CONFIRMED)
    }

    return render_template(
        "user/treks.html",
        pagination=pagination,
        treks=pagination.items,
        keyword=keyword,
        location=location,
        difficulty=difficulty,
        start_date=start_date,
        difficulties=DifficultyEnum.ALL,
        booked_ids=booked_ids,
    )


@user_bp.route("/treks/<int:trek_id>", methods=["GET", "POST"])
@login_required
@user_required
def trek_detail(trek_id):
    """View a trek's details and book it."""
    trek = Trek.query.get_or_404(trek_id)
    form = BookingForm()

    already_booked = booking_service.user_has_active_booking(current_user.id, trek.id)

    if form.validate_on_submit():
        ok, msg = booking_service.create_booking(
            current_user, trek, form.remarks.data
        )
        flash(msg, "success" if ok else "danger")
        if ok:
            return redirect(url_for("user.bookings"))
        return redirect(url_for("user.trek_detail", trek_id=trek.id))

    return render_template(
        "user/trek_detail.html",
        trek=trek,
        form=form,
        already_booked=already_booked,
    )


@user_bp.route("/bookings")
@login_required
@user_required
def bookings():
    """List the user's upcoming bookings and booking history."""
    status = request.args.get("status", "").strip()

    query = current_user.bookings
    if status:
        query = query.filter_by(status=status)

    all_bookings = query.order_by(Booking.booking_date.desc()).all()

    upcoming = [
        b
        for b in all_bookings
        if b.status == BookingStatus.CONFIRMED
        and b.trek
        and b.trek.start_date >= date.today()
    ]
    history = [b for b in all_bookings if b not in upcoming]

    return render_template(
        "user/bookings.html",
        upcoming=upcoming,
        history=history,
        status=status,
        statuses=BookingStatus.ALL,
    )


@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
@user_required
def booking_cancel(booking_id):
    """Cancel one of the user's bookings."""
    booking = Booking.query.get_or_404(booking_id)
    ok, msg = booking_service.cancel_booking(current_user, booking)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("user.bookings"))


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
@user_required
def profile():
    """View and edit the user's profile."""
    form = ProfileForm(original_user=current_user, obj=current_user)

    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.email = form.email.data.strip().lower()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        current_user.bio = form.bio.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("user.profile"))

    return render_template("user/profile.html", form=form)
