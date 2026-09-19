from datetime import datetime

from app.extensions import db


campaign_group = db.Table(
    "campaign_groups",

    db.Column(
        "campaign_id",
        db.Integer,
        db.ForeignKey("campaigns.id"),
        primary_key=True
    ),

    db.Column(
        "group_id",
        db.Integer,
        db.ForeignKey("groups.id"),
        primary_key=True
    )
)


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    church_id = db.Column(
        db.Integer,
        db.ForeignKey("churches.id"),
        nullable=False
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

    scheduled_at = db.Column(
        db.DateTime,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="draft"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    total_recipients = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    total_sent = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    total_failed = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    sent_at = db.Column(
        db.DateTime,
        nullable=True
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

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    church = db.relationship(
        "Church",
        backref=db.backref("campaigns", lazy=True)
    )

    groups = db.relationship(
        "Group",
        secondary=campaign_group,
        backref=db.backref("campaigns", lazy=True)
    )

    def __repr__(self):
        return f"<Campaign {self.title}>"