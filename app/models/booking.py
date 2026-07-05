"""Booking model and related enums."""
from datetime import datetime

from app.extensions import db


class BookingStatus:
    """Status of a booking."""

    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

    ALL = (CONFIRMED, CANCELLED, COMPLETED)


class PaymentStatus:
    """Payment state of a booking."""

    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"

    ALL = (PENDING, PAID, REFUNDED)


class Booking(db.Model):
    """A user's reservation for a specific trek."""

    __tablename__ = "bookings"

    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default=BookingStatus.CONFIRMED)
    payment_status = db.Column(
        db.String(20), nullable=False, default=PaymentStatus.PAID
    )
    remarks = db.Column(db.String(255))

    @property
    def status_class(self) -> str:
        """CSS badge modifier based on booking status."""
        return {
            BookingStatus.CONFIRMED: "badge-status-open",
            BookingStatus.CANCELLED: "badge-status-cancelled",
            BookingStatus.COMPLETED: "badge-status-completed",
        }.get(self.status, "badge-status-draft")

    @property
    def payment_class(self) -> str:
        """CSS badge modifier based on payment status."""
        return {
            PaymentStatus.PAID: "badge-status-completed",
            PaymentStatus.PENDING: "badge-status-closed",
            PaymentStatus.REFUNDED: "badge-status-ongoing",
        }.get(self.payment_status, "badge-status-draft")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Booking #{self.booking_id} user={self.user_id} trek={self.trek_id}>"
