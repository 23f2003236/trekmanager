"""Activity-feed service.

Provides a single helper to record an activity entry and a helper to fetch
the most recent entries for the dashboards.
"""
from app.extensions import db
from app.models import Activity


def log_activity(action: str, actor=None, category: str = "general",
                 icon: str = "bi-activity", commit: bool = True) -> Activity:
    """Create and persist an :class:`Activity` record.

    Args:
        action: Human readable description of the event.
        actor: The ``User`` who performed the action (optional).
        category: Grouping label such as ``booking`` or ``trek``.
        icon: Bootstrap icon class shown next to the entry.
        commit: Whether to commit immediately. Set False to batch commits.
    """
    activity = Activity(
        actor_id=getattr(actor, "id", None),
        actor_name=getattr(actor, "full_name", None) or getattr(actor, "username", "System"),
        action=action,
        category=category,
        icon=icon,
    )
    db.session.add(activity)
    if commit:
        db.session.commit()
    return activity


def recent_activities(limit: int = 8):
    """Return the ``limit`` most recent activities, newest first."""
    return (
        Activity.query.order_by(Activity.created_at.desc()).limit(limit).all()
    )
