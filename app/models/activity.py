"""Activity log model.

Records notable events (bookings, approvals, trek changes, ...) so the
dashboards can show a "Recent Activity" feed.
"""
from datetime import datetime

from app.extensions import db


class Activity(db.Model):
    """A single audit / activity-feed entry."""

    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    actor_name = db.Column(db.String(120))
    action = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), default="general")
    icon = db.Column(db.String(50), default="bi-activity")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Activity {self.action!r}>"
