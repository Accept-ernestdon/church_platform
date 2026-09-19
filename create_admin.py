from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import Church, User


app = create_app()


with app.app_context():

    church = db.session.scalar(
        db.select(Church).limit(1)
    )

    if church is None:
        print("No church exists yet. Create a church first.")
    else:
        user = User(
            church_id=church.id,
            name="System Administrator",
            email="admin@example.com",
            password_hash=generate_password_hash("ChangeMe123!"),
            role="Admin",
            is_active=True,
        )

        db.session.add(user)
        db.session.commit()

        print("Admin user created successfully.")
        print("Email: admin@example.com")
        print("Password: ChangeMe123!")