from getpass import getpass

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()


with app.app_context():

    print()
    print("=" * 55)
    print("ChurchConnect System Admin Setup")
    print("=" * 55)
    print()

    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()

    if not name:
        print()
        print("Admin name is required.")
        raise SystemExit

    if not email:
        print()
        print("Admin email is required.")
        raise SystemExit

    existing_user = db.session.scalar(
        db.select(User).where(
            User.email == email
        )
    )

    if existing_user:

        print()
        print("A user with this email already exists.")
        print("Please use a different email address.")
        raise SystemExit

    password = getpass("Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if not password:
        print()
        print("Password is required.")
        raise SystemExit

    if password != confirm_password:

        print()
        print("Passwords do not match.")
        raise SystemExit

    admin = User(
        church_id=None,
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role="System Admin",
        is_system_admin=True,
        is_active=True
    )

    db.session.add(admin)
    db.session.commit()

    print()
    print("=" * 55)
    print("System Admin created successfully.")
    print("=" * 55)
    print()
    print(f"Name: {admin.name}")
    print(f"Email: {admin.email}")
    print(f"Role: {admin.role}")
    print(f"System Admin: {admin.is_system_admin}")
    print()