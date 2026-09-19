from datetime import datetime

from app.extensions import db
from app.models.member_group import member_group


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    church_id = db.Column(
        db.Integer,
        db.ForeignKey("churches.id"),
        nullable=False
    )

    groups = db.relationship(
        "Group",
        secondary=member_group,
        backref=db.backref("members", lazy=True)
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    sms_opt_in = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    whatsapp_opt_in = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    church = db.relationship(
        "Church",
        backref=db.backref("members", lazy=True)
    )

    def __repr__(self):
        return f"<Member {self.name}>"