from app import create_app
from app.extensions import db
from app.models import Church, Group


app = create_app()

with app.app_context():

    church = db.session.scalar(
        db.select(Church).where(
            Church.name == "Grace Community Church"
        )
    )

    if church is None:
        print("Grace Community Church was not found.")
    else:

        default_groups = [
            ("Men", "Men's ministry"),
            ("Women", "Women's ministry"),
            ("Youth", "Youth ministry"),
            ("Children", "Children's ministry"),
            ("Choir", "Church choir"),
        ]

        for name, description in default_groups:

            existing_group = db.session.scalar(
                db.select(Group).where(
                    Group.church_id == church.id,
                    Group.name == name
                )
            )

            if existing_group is None:
                group = Group(
                    church_id=church.id,
                    name=name,
                    description=description,
                    is_active=True
                )

                db.session.add(group)

        db.session.commit()

        print("Default groups created successfully.")