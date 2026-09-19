from datetime import datetime

from app.extensions import db


reminder_group = db.Table(
    "reminder_groups",

    db.Column(
        "reminder_id",
        db.Integer,
        db.ForeignKey("reminders.id"),
        primary_key=True
    ),

    db.Column(
        "group_id",
        db.Integer,
        db.ForeignKey("groups.id"),
        primary_key=True
    )
)


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    church_id = db.Column(
        db.Integer,
        db.ForeignKey("churches.id"),
        nullable=False
    )

    program_id = db.Column(
        db.Integer,
        db.ForeignKey("programs.id"),
        nullable=True
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    audience_type = db.Column(
        db.String(30),
        nullable=False,
        default="all"
    )

    channel = db.Column(
        db.String(20),
        nullable=False,
        default="sms"
    )

    # ---------------------------------------------------------
    # Scheduling
    # ---------------------------------------------------------

    scheduled_at = db.Column(
        db.DateTime,
        nullable=False
    )

    recurrence_type = db.Column(
        db.String(20),
        nullable=False,
        default="one_time"
    )

    recurrence_interval = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    recurrence_day_of_week = db.Column(
        db.Integer,
        nullable=True
    )

    recurrence_day_of_month = db.Column(
        db.Integer,
        nullable=True
    )

    recurrence_month = db.Column(
        db.Integer,
        nullable=True
    )

    recurrence_end_date = db.Column(
        db.DateTime,
        nullable=True
    )

    next_run_at = db.Column(
        db.DateTime,
        nullable=True
    )

    last_run_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    status = db.Column(
        db.String(20),
        nullable=False,
        default="scheduled"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    sent_at = db.Column(
        db.DateTime,
        nullable=True
    )

    total_sent = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    failure_reason = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    church = db.relationship(
        "Church",
        backref=db.backref(
            "reminders",
            lazy=True
        )
    )

    program = db.relationship(
        "Program",
        backref=db.backref(
            "reminders",
            lazy=True
        )
    )

    groups = db.relationship(
        "Group",
        secondary=reminder_group,
        backref=db.backref(
            "reminders",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Reminder {self.title}>"