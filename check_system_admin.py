from getpass import getpass

from werkzeug.security import check_password_hash

from app import create_app
from app.extensions import db
from app.models.user import User


app = create_app()


with app.app_context():

    print()
    print("=" * 55)
    print("ChurchConnect System Admin Check")
    print("=" * 55)
    print()

    email = input("System Admin email: ").strip().lower()

    user = db.session.scalar(
        db.select(User).where(
            User.email == email
        )
    )

    if user is None:

        print()
        print("RESULT: User was not found.")
        print()

    else:

        print()
        print("User found.")
        print()
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Church ID: {user.church_id}")
        print(f"Role: {user.role}")
        print(f"System Admin: {user.is_system_admin}")
        print(f"Active: {user.is_active}")
        print()

        password = getpass("Enter the password used for this account: ")

        password_correct = check_password_hash(
            user.password_hash,
            password
        )

        print()

        if password_correct:
            print("Password: CORRECT")
        else:
            print("Password: INCORRECT")

        print()

        if (
            user.is_system_admin
            and user.is_active
            and password_correct
        ):
            print("RESULT: System Admin account is valid.")
        else:
            print("RESULT: System Admin account has an issue.")

        print()