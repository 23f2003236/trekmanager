"""Trek model and related enums."""
from datetime import datetime, date

from app.extensions import db


class TrekStatus:
    """Lifecycle status of a trek."""

    DRAFT = "draft"          # created, not yet open for booking
    OPEN = "open"            # accepting bookings
    CLOSED = "closed"        # bookings closed, not started
    ONGOING = "ongoing"      # trek in progress
    COMPLETED = "completed"  # finished
    CANCELLED = "cancelled"  # called off

    ALL = (DRAFT, OPEN, CLOSED, ONGOING, COMPLETED, CANCELLED)


class DifficultyEnum:
    """Difficulty grading for a trek."""

    EASY = "Easy"
    MODERATE = "Moderate"
    HARD = "Hard"
    EXTREME = "Extreme"

    ALL = (EASY, MODERATE, HARD, EXTREME)


class Trek(db.Model):
    """A trekking expedition that users can book."""

    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    location = db.Column(db.String(150), nullable=False, index=True)
    difficulty = db.Column(db.String(20), nullable=False, default=DifficultyEnum.MODERATE)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, default=0.0)
    duration = db.Column(db.Integer, nullable=False, default=1)  # in days

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    slots = db.Column(db.Integer, nullable=False, default=0)
    remaining_slots = db.Column(db.Integer, nullable=False, default=0)

    image = db.Column(db.String(255))  # filename in static/images
    status = db.Column(db.String(20), nullable=False, default=TrekStatus.DRAFT)

    staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships -------------------------------------------------------
    bookings = db.relationship(
        "Booking", backref="trek", lazy="dynamic", cascade="all, delete-orphan"
    )

    # Derived properties --------------------------------------------------
    @property
    def booked_slots(self) -> int:
        """Number of slots currently taken."""
        return max(self.slots - self.remaining_slots, 0)

    @property
    def fill_percent(self) -> int:
        """Percentage of capacity booked (for progress bars)."""
        if not self.slots:
            return 0
        return int(round((self.booked_slots / self.slots) * 100))

    @property
    def is_bookable(self) -> bool:
        """True when a user is allowed to book this trek."""
        return self.status == TrekStatus.OPEN and self.remaining_slots > 0

    @property
    def is_today(self) -> bool:
        """True when the trek starts today."""
        return self.start_date == date.today()

    @property
    def is_upcoming(self) -> bool:
        """True when the trek starts in the future."""
        return self.start_date > date.today()

    @property
    def image_url(self) -> str:
        """Filename to render; falls back to a default placeholder."""
        return self.image or "default-trek.jpg"

    @property
    def difficulty_class(self) -> str:
        """CSS badge modifier based on difficulty."""
        return {
            DifficultyEnum.EASY: "badge-easy",
            DifficultyEnum.MODERATE: "badge-moderate",
            DifficultyEnum.HARD: "badge-hard",
            DifficultyEnum.EXTREME: "badge-extreme",
        }.get(self.difficulty, "badge-moderate")

    @property
    def status_class(self) -> str:
        """CSS badge modifier based on status."""
        return {
            TrekStatus.DRAFT: "badge-status-draft",
            TrekStatus.OPEN: "badge-status-open",
            TrekStatus.CLOSED: "badge-status-closed",
            TrekStatus.ONGOING: "badge-status-ongoing",
            TrekStatus.COMPLETED: "badge-status-completed",
            TrekStatus.CANCELLED: "badge-status-cancelled",
        }.get(self.status, "badge-status-draft")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Trek {self.name} @ {self.location}>"
