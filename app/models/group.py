from datetime import datetime

from app.extensions import db


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    church_id = db.Column(
        db.Integer,
        db.ForeignKey("churches.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    church = db.relationship(
        "Church",
        backref=db.backref("groups", lazy=True)
    )

    def __repr__(self):
        return f"<Group {self.name}>"