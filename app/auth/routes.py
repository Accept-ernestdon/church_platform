from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)

from werkzeug.security import check_password_hash

from app.extensions import db
from app.models.user import User
from app.models.church import Church


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.before_app_request
def check_active_church():

    if not current_user.is_authenticated:
        return None

    if current_user.is_system_admin:
        return None

    church = db.session.get(
        Church,
        current_user.church_id
    )

    if church is None:

        logout_user()

        flash(
            "Your church account could not be found.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    if not church.is_active:

        logout_user()

        flash(
            "Your church account has been deactivated.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = db.session.scalar(
            db.select(User).where(
                User.email == email
            )
        )

        if user is None:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        if not user.is_active:

            flash(
                "Your account has been deactivated.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        if not check_password_hash(
            user.password_hash,
            password
        ):

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        if user.is_system_admin:

            login_user(user)

            return redirect(
                url_for("admin.dashboard")
            )

        church = db.session.get(
            Church,
            user.church_id
        )

        if church is None:

            flash(
                "Your church account could not be found.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        if not church.is_active:

            flash(
                "Your church account has been deactivated.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        login_user(user)

        return redirect(
            url_for("dashboard.home")
        )

    return render_template(
        "auth/login.html"
    )


@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("auth.login")
    )