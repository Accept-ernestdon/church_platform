from app.extensions import db


member_group = db.Table(
    "member_group",

    db.Column(
        "member_id",
        db.Integer,
        db.ForeignKey("members.id", ondelete="CASCADE"),
        primary_key=True
    ),

    db.Column(
        "group_id",
        db.Integer,
        db.ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True
    )
)