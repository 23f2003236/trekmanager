"""Trek lifecycle and query helpers.

Handles creation, updates, deletion and the staff-driven status transitions
(open / close / start / complete). Also provides reusable filtered queries
used by the search screens.
"""
from datetime import date

from sqlalchemy import or_

from app.extensions import db
from app.models import (
    Booking,
    BookingStatus,
    Trek,
    TrekStatus,
)
from app.services.activity_service import log_activity


# --- Creation / mutation -------------------------------------------------
def create_trek(form, actor, image_filename=None) -> Trek:
    """Create a new trek from a validated WTForm."""
    trek = Trek(
        name=form.name.data.strip(),
        location=form.location.data.strip(),
        difficulty=form.difficulty.data,
        description=form.description.data,
        price=form.price.data,
        duration=form.duration.data,
        start_date=form.start_date.data,
        end_date=form.end_date.data,
        slots=form.slots.data,
        remaining_slots=form.slots.data,
        status=form.status.data,
        staff_id=form.staff_id.data or None,
        image=image_filename or "default-trek.jpg",
    )
    db.session.add(trek)
    log_activity(
        f"{actor.full_name} created trek '{trek.name}'",
        actor=actor,
        category="trek",
        icon="bi-plus-circle",
        commit=False,
    )
    db.session.commit()
    return trek


def update_trek(trek: Trek, form, actor, image_filename=None) -> Trek:
    """Update an existing trek, adjusting remaining slots consistently."""
    # Preserve how many are already booked when capacity changes.
    booked = trek.booked_slots

    trek.name = form.name.data.strip()
    trek.location = form.location.data.strip()
    trek.difficulty = form.difficulty.data
    trek.description = form.description.data
    trek.price = form.price.data
    trek.duration = form.duration.data
    trek.start_date = form.start_date.data
    trek.end_date = form.end_date.data
    trek.slots = form.slots.data
    # Keep remaining consistent: capacity minus already booked (never negative).
    trek.remaining_slots = max(form.slots.data - booked, 0)
    trek.status = form.status.data
    trek.staff_id = form.staff_id.data or None
    if image_filename:
        trek.image = image_filename

    log_activity(
        f"{actor.full_name} updated trek '{trek.name}'",
        actor=actor,
        category="trek",
        icon="bi-pencil-square",
        commit=False,
    )
    db.session.commit()
    return trek


def delete_trek(trek: Trek, actor) -> None:
    """Delete a trek and its associated bookings."""
    name = trek.name
    db.session.delete(trek)
    log_activity(
        f"{actor.full_name} deleted trek '{name}'",
        actor=actor,
        category="trek",
        icon="bi-trash",
        commit=False,
    )
    db.session.commit()


def set_trek_status(trek: Trek, new_status: str, actor) -> tuple:
    """Transition a trek to a new lifecycle status (used by staff).

    Returns ``(ok, message)``.
    """
    valid_transitions = {
        TrekStatus.DRAFT: {TrekStatus.OPEN},
        TrekStatus.OPEN: {TrekStatus.CLOSED, TrekStatus.ONGOING},
        TrekStatus.CLOSED: {TrekStatus.OPEN, TrekStatus.ONGOING},
        TrekStatus.ONGOING: {TrekStatus.COMPLETED},
        TrekStatus.COMPLETED: set(),
        TrekStatus.CANCELLED: set(),
    }

    if new_status not in valid_transitions.get(trek.status, set()):
        return False, f"Cannot change status from {trek.status} to {new_status}."

    trek.status = new_status

    # When a trek completes, mark all confirmed bookings as completed.
    if new_status == TrekStatus.COMPLETED:
        for booking in trek.bookings.filter_by(status=BookingStatus.CONFIRMED):
            booking.status = BookingStatus.COMPLETED

    action_map = {
        TrekStatus.OPEN: "opened",
        TrekStatus.CLOSED: "closed",
        TrekStatus.ONGOING: "started",
        TrekStatus.COMPLETED: "completed",
    }
    log_activity(
        f"{actor.full_name} {action_map.get(new_status, 'updated')} trek '{trek.name}'",
        actor=actor,
        category="trek",
        icon="bi-flag",
        commit=False,
    )
    db.session.commit()
    return True, f"Trek '{trek.name}' is now {new_status}."


def update_slots(trek: Trek, new_capacity: int, actor) -> tuple:
    """Staff action to adjust total slot capacity.

    Ensures capacity is not reduced below the number already booked.
    """
    booked = trek.booked_slots
    if new_capacity < booked:
        return False, f"Capacity cannot be less than the {booked} already booked."
    trek.slots = new_capacity
    trek.remaining_slots = new_capacity - booked
    log_activity(
        f"{actor.full_name} set '{trek.name}' capacity to {new_capacity}",
        actor=actor,
        category="trek",
        icon="bi-people",
        commit=False,
    )
    db.session.commit()
    return True, f"Capacity updated to {new_capacity} slots."


# --- Queries -------------------------------------------------------------
def search_treks(keyword=None, location=None, difficulty=None,
                 status=None, start_date=None, staff_id=None):
    """Return a filtered Trek query based on optional criteria."""
    query = Trek.query

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(Trek.name.ilike(like), Trek.location.ilike(like))
        )
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if status:
        query = query.filter(Trek.status == status)
    if start_date:
        query = query.filter(Trek.start_date == start_date)
    if staff_id:
        query = query.filter(Trek.staff_id == staff_id)

    return query.order_by(Trek.start_date.asc())


def available_treks(keyword=None, location=None, difficulty=None, start_date=None):
    """Treks that are currently open and have remaining slots."""
    query = search_treks(
        keyword=keyword,
        location=location,
        difficulty=difficulty,
        start_date=start_date,
        status=TrekStatus.OPEN,
    )
    return query.filter(Trek.remaining_slots > 0)
