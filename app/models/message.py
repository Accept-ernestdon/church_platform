from datetime import datetime

from app.extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    church_id = db.Column(
        db.Integer,
        db.ForeignKey("churches.id"),
        nullable=False
    )

    member_id = db.Column(
        db.Integer,
        db.ForeignKey("members.id"),
        nullable=True
    )

    recipient_phone = db.Column(
        db.String(30),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    channel = db.Column(
        db.String(20),
        nullable=False,
        default="sms"
    )

    source = db.Column(
        db.String(30),
        nullable=False,
        default="manual"
    )

    source_id = db.Column(
        db.Integer,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pending"
    )

    provider_message_id = db.Column(
        db.String(150),
        nullable=True
    )

    failure_reason = db.Column(
        db.Text,
        nullable=True
    )

    sent_at = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    church = db.relationship(
        "Church",
        backref=db.backref(
            "messages",
            lazy=True
        )
    )

    member = db.relationship(
        "Member",
        backref=db.backref(
            "messages",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Message {self.id} {self.status}>"