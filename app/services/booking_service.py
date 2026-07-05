"""Booking business logic.

Encapsulates all the rules around booking / cancelling treks so the view
functions remain declarative. Every function returns a ``(ok, message)``
tuple where ``ok`` indicates success and ``message`` is a flash-ready string.
"""
from app.extensions import db
from app.models import (
    Booking,
    BookingStatus,
    PaymentStatus,
    Trek,
    TrekStatus,
)
from app.services.activity_service import log_activity


def user_has_active_booking(user_id: int, trek_id: int) -> bool:
    """Return True if the user already has a confirmed booking for the trek."""
    return (
        Booking.query.filter_by(
            user_id=user_id, trek_id=trek_id, status=BookingStatus.CONFIRMED
        ).first()
        is not None
    )


def create_booking(user, trek: Trek, remarks: str = ""):
    """Attempt to book ``trek`` for ``user`` enforcing all business rules.

    Rules enforced:
        * Trek must be OPEN.
        * Trek must have remaining slots (prevents overbooking).
        * A user cannot book the same trek twice while confirmed.
        * Slots are decremented atomically on success.
    """
    if trek.status != TrekStatus.OPEN:
        return False, "This trek is not open for booking right now."

    if trek.remaining_slots <= 0:
        return False, "Sorry, this trek is fully booked."

    if user_has_active_booking(user.id, trek.id):
        return False, "You have already booked this trek."

    booking = Booking(
        user_id=user.id,
        trek_id=trek.id,
        status=BookingStatus.CONFIRMED,
        payment_status=PaymentStatus.PAID,
        remarks=remarks or "",
    )
    # Decrement remaining slots (overbooking prevention).
    trek.remaining_slots -= 1

    db.session.add(booking)
    log_activity(
        f"{user.full_name} booked '{trek.name}'",
        actor=user,
        category="booking",
        icon="bi-bookmark-check",
        commit=False,
    )
    db.session.commit()
    return True, f"Successfully booked '{trek.name}'. See you on the trail!"


def cancel_booking(user, booking: Booking):
    """Cancel a confirmed booking and restore the trek slot."""
    if booking.user_id != user.id:
        return False, "You cannot cancel a booking that isn't yours."

    if booking.status != BookingStatus.CONFIRMED:
        return False, "Only confirmed bookings can be cancelled."

    trek = booking.trek
    booking.status = BookingStatus.CANCELLED
    booking.payment_status = PaymentStatus.REFUNDED

    # Restore a slot but never exceed capacity.
    if trek and trek.remaining_slots < trek.slots:
        trek.remaining_slots += 1

    log_activity(
        f"{user.full_name} cancelled booking for '{trek.name if trek else 'a trek'}'",
        actor=user,
        category="booking",
        icon="bi-x-circle",
        commit=False,
    )
    db.session.commit()
    return True, "Your booking has been cancelled and payment refunded."
