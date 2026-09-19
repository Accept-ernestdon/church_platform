from datetime import datetime

from app.extensions import db


class Program(db.Model):
    __tablename__ = "programs"

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
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    day_of_week = db.Column(
        db.String(20),
        nullable=True
    )

    start_time = db.Column(
        db.Time,
        nullable=True
    )

    location = db.Column(
        db.String(150),
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
        backref=db.backref(
            "programs",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Program {self.name}>"