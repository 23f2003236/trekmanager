"""User model and related enums.

A single ``User`` table stores admins, staff and regular users, distinguished
by the ``role`` column. Staff members additionally carry an approval status.
"""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class RoleEnum:
    """Enumeration of the three user roles."""

    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

    ALL = (ADMIN, STAFF, USER)


class StaffStatus:
    """Approval / moderation status for staff accounts."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLACKLISTED = "blacklisted"


class User(UserMixin, db.Model):
    """Represents an application account (admin, staff or user)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=RoleEnum.USER)

    # Only meaningful for staff accounts; users are always ``approved``.
    status = db.Column(db.String(20), nullable=False, default=StaffStatus.APPROVED)

    # Set to True to block a regular user from logging in.
    is_blacklisted = db.Column(db.Boolean, nullable=False, default=False)

    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships -------------------------------------------------------
    bookings = db.relationship(
        "Booking", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    assigned_treks = db.relationship(
        "Trek", backref="staff", lazy="dynamic", foreign_keys="Trek.staff_id"
    )

    # Password helpers ----------------------------------------------------
    def set_password(self, password: str) -> None:
        """Hash and store the given plaintext password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return True if ``password`` matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    # Convenience predicates ---------------------------------------------
    @property
    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN

    @property
    def is_staff(self) -> bool:
        return self.role == RoleEnum.STAFF

    @property
    def is_user(self) -> bool:
        return self.role == RoleEnum.USER

    @property
    def is_approved_staff(self) -> bool:
        """True only for staff whose account has been approved."""
        return self.is_staff and self.status == StaffStatus.APPROVED

    @property
    def can_login(self) -> bool:
        """Return whether this account is allowed to authenticate."""
        if self.is_blacklisted:
            return False
        if self.is_staff and self.status in (
            StaffStatus.REJECTED,
            StaffStatus.BLACKLISTED,
        ):
            return False
        return True

    @property
    def initials(self) -> str:
        """Two-letter initials used by the avatar widget."""
        parts = (self.full_name or self.username).split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return (self.full_name or self.username)[:2].upper()

    @property
    def status_label(self) -> str:
        """Human-friendly account status for badges."""
        if self.is_blacklisted:
            return "Blacklisted"
        if self.is_staff:
            return self.status.capitalize()
        return "Active"

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<User {self.username} ({self.role})>"
