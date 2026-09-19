from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import (
    current_user,
    login_required
)

from werkzeug.security import generate_password_hash

from app.admin.decorators import system_admin_required
from app.extensions import db
from app.models.church import Church
from app.models.user import User
from app.models.member import Member
from app.models.message import Message


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

@admin_bp.route("/")
@login_required
@system_admin_required
def dashboard():

    search = request.args.get(
        "search",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    church_query = db.select(Church)

    if search:

        search_pattern = f"%{search}%"

        church_query = church_query.where(
            db.or_(
                Church.name.ilike(search_pattern),
                Church.location.ilike(search_pattern),
                Church.email.ilike(search_pattern),
                Church.phone.ilike(search_pattern)
            )
        )

    if status == "active":

        church_query = church_query.where(
            Church.is_active.is_(True)
        )

    elif status == "inactive":

        church_query = church_query.where(
            Church.is_active.is_(False)
        )

    churches = db.session.scalars(
        church_query.order_by(
            Church.created_at.desc()
        )
    ).all()

    church_rows = []

    for church in churches:

        administrator_count = db.session.scalar(
            db.select(
                db.func.count(User.id)
            ).where(
                User.church_id == church.id,
                User.is_system_admin.is_(False)
            )
        ) or 0

        member_count = db.session.scalar(
            db.select(
                db.func.count(Member.id)
            ).where(
                Member.church_id == church.id
            )
        ) or 0

        church_rows.append(
            {
                "church": church,
                "administrator_count": administrator_count,
                "member_count": member_count
            }
        )

    total_churches = db.session.scalar(
        db.select(
            db.func.count(Church.id)
        )
    ) or 0

    active_churches = db.session.scalar(
        db.select(
            db.func.count(Church.id)
        ).where(
            Church.is_active.is_(True)
        )
    ) or 0

    inactive_churches = db.session.scalar(
        db.select(
            db.func.count(Church.id)
        ).where(
            Church.is_active.is_(False)
        )
    ) or 0

    total_administrators = db.session.scalar(
        db.select(
            db.func.count(User.id)
        ).where(
            User.is_system_admin.is_(False)
        )
    ) or 0

    active_administrators = db.session.scalar(
        db.select(
            db.func.count(User.id)
        ).where(
            User.is_system_admin.is_(False),
            User.is_active.is_(True)
        )
    ) or 0

    inactive_administrators = db.session.scalar(
        db.select(
            db.func.count(User.id)
        ).where(
            User.is_system_admin.is_(False),
            User.is_active.is_(False)
        )
    ) or 0

    total_members = db.session.scalar(
        db.select(
            db.func.count(Member.id)
        )
    ) or 0

    active_members = db.session.scalar(
        db.select(
            db.func.count(Member.id)
        ).where(
            Member.is_active.is_(True)
        )
    ) or 0

    total_messages = db.session.scalar(
        db.select(
            db.func.count(Message.id)
        )
    ) or 0

    sent_messages = db.session.scalar(
        db.select(
            db.func.count(Message.id)
        ).where(
            Message.status == "sent"
        )
    ) or 0

    recent_administrators = db.session.scalars(
        db.select(User)
        .where(
            User.is_system_admin.is_(False)
        )
        .order_by(
            User.created_at.desc()
        )
        .limit(5)
    ).all()

    return render_template(
        "admin/dashboard.html",
        churches=churches,
        church_rows=church_rows,
        total_churches=total_churches,
        active_churches=active_churches,
        inactive_churches=inactive_churches,
        total_administrators=total_administrators,
        active_administrators=active_administrators,
        inactive_administrators=inactive_administrators,
        total_members=total_members,
        active_members=active_members,
        total_messages=total_messages,
        sent_messages=sent_messages,
        recent_administrators=recent_administrators,
        search=search,
        selected_status=status
    )


@admin_bp.route("/administrators")
@login_required
@system_admin_required
def administrators():

    search = request.args.get(
        "search",
        ""
    ).strip()

    church_id = request.args.get(
        "church_id",
        type=int
    )

    status = request.args.get(
        "status",
        ""
    ).strip()

    query = db.select(User).where(
        User.is_system_admin.is_(False)
    )

    if search:

        search_pattern = f"%{search}%"

        query = query.where(
            db.or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    if church_id:

        query = query.where(
            User.church_id == church_id
        )

    if status == "active":

        query = query.where(
            User.is_active.is_(True)
        )

    elif status == "inactive":

        query = query.where(
            User.is_active.is_(False)
        )

    administrators = db.session.scalars(
        query.order_by(
            User.created_at.desc()
        )
    ).all()

    churches = db.session.scalars(
        db.select(Church)
        .order_by(
            Church.name.asc()
        )
    ).all()

    total_administrators = db.session.scalar(
        db.select(
            db.func.count(User.id)
        ).where(
            User.is_system_admin.is_(False)
        )
    ) or 0

    active_administrators = db.session.scalar(
        db.select(
            db.func.count(User.id)
        ).where(
            User.is_system_admin.is_(False),
            User.is_active.is_(True)
        )
    ) or 0

    inactive_administrators = db.session.scalar(
        db.select(
            db.func.count(User.id)
        ).where(
            User.is_system_admin.is_(False),
            User.is_active.is_(False)
        )
    ) or 0

    return render_template(
        "admin/administrators.html",
        administrators=administrators,
        churches=churches,
        total_administrators=total_administrators,
        active_administrators=active_administrators,
        inactive_administrators=inactive_administrators,
        search=search,
        selected_church_id=church_id,
        selected_status=status
    )


@admin_bp.route(
    "/churches/add",
    methods=["GET", "POST"]
)
@login_required
@system_admin_required
def add_church():

    if request.method == "POST":

        church_name = request.form.get(
            "church_name",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        church_email = request.form.get(
            "church_email",
            ""
        ).strip().lower()

        admin_name = request.form.get(
            "admin_name",
            ""
        ).strip()

        admin_email = request.form.get(
            "admin_email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not church_name:

            flash(
                "Church name is required.",
                "error"
            )

            return render_template(
                "admin/add_church.html"
            )

        if not admin_name:

            flash(
                "Administrator name is required.",
                "error"
            )

            return render_template(
                "admin/add_church.html"
            )

        if not admin_email:

            flash(
                "Administrator email is required.",
                "error"
            )

            return render_template(
                "admin/add_church.html"
            )

        if not password:

            flash(
                "Password is required.",
                "error"
            )

            return render_template(
                "admin/add_church.html"
            )

        if len(password) < 8:

            flash(
                "Password must be at least 8 characters long.",
                "error"
            )

            return render_template(
                "admin/add_church.html"
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "admin/add_church.html"
            )

        if church_email:

            existing_church = db.session.scalar(
                db.select(Church).where(
                    Church.email == church_email
                )
            )

            if existing_church:

                flash(
                    "A church with that email address already exists.",
                    "error"
                )

                return render_template(
                    "admin/add_church.html"
                )

        existing_user = db.session.scalar(
            db.select(User).where(
                User.email == admin_email
            )
        )

        if existing_user:

            flash(
                "A user with that email already exists.",
                "error"
            )

            return render_template(
                "admin/add_church.html"
            )

        church = Church(
            name=church_name,
            location=location,
            phone=phone,
            email=church_email,
            is_active=True
        )

        db.session.add(church)

        db.session.flush()

        church_admin = User(
            church_id=church.id,
            name=admin_name,
            email=admin_email,
            password_hash=generate_password_hash(
                password
            ),
            role="Admin",
            is_system_admin=False,
            is_active=True
        )

        db.session.add(church_admin)

        db.session.commit()

        flash(
            "Church and administrator account created successfully.",
            "success"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    return render_template(
        "admin/add_church.html"
    )

@admin_bp.route(
    "/churches/<int:church_id>"
)
@login_required
@system_admin_required
def manage_church(church_id):

    church = db.session.get(
        Church,
        church_id
    )

    if church is None:

        flash(
            "Church could not be found.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    administrators = db.session.scalars(
        db.select(User).where(
            User.church_id == church.id,
            User.is_system_admin.is_(False)
        ).order_by(
            User.created_at.asc()
        )
    ).all()

    return render_template(
        "admin/manage_church.html",
        church=church,
        administrators=administrators
    )


@admin_bp.route(
    "/churches/<int:church_id>/administrators/add",
    methods=["GET", "POST"]
)
@login_required
@system_admin_required
def add_administrator(church_id):

    church = db.session.get(
        Church,
        church_id
    )

    if church is None:

        flash(
            "Church could not be found.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if not church.is_active:

        flash(
            "Administrators cannot be added to an inactive church.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        role = request.form.get(
            "role",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        allowed_roles = [
            "Admin",
            "Manager",
            "Staff"
        ]

        if not name:

            flash(
                "Administrator name is required.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        if not email:

            flash(
                "Administrator email is required.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        if "@" not in email or "." not in email.split("@")[-1]:

            flash(
                "Please enter a valid administrator email address.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        if not role:

            flash(
                "Administrator role is required.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        if role not in allowed_roles:

            flash(
                "Invalid administrator role.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        if not password:

            flash(
                "Password is required.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        if len(password) < 8:

            flash(
                "Password must be at least 8 characters long.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        existing_user = db.session.scalar(
            db.select(User).where(
                User.email == email
            )
        )

        if existing_user:

            flash(
                "A user with that email already exists.",
                "error"
            )

            return render_template(
                "admin/add_administrator.html",
                church=church
            )

        administrator = User(
            church_id=church.id,
            name=name,
            email=email,
            password_hash=generate_password_hash(
                password
            ),
            role=role,
            is_system_admin=False,
            is_active=True
        )

        db.session.add(administrator)

        db.session.commit()

        flash(
            "Administrator account created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    return render_template(
        "admin/add_administrator.html",
        church=church
    )

@admin_bp.route(
    "/churches/<int:church_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@system_admin_required
def edit_church(church_id):

    church = db.session.get(
        Church,
        church_id
    )

    if church is None:

        flash(
            "Church could not be found.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    if request.method == "POST":

        church_name = request.form.get(
            "church_name",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        church_email = request.form.get(
            "church_email",
            ""
        ).strip().lower()

        if not church_name:

            flash(
                "Church name is required.",
                "error"
            )

            return render_template(
                "admin/edit_church.html",
                church=church
            )

        if church_email:

            existing_church = db.session.scalar(
                db.select(Church).where(
                    Church.email == church_email,
                    Church.id != church.id
                )
            )

            if existing_church:

                flash(
                    "Another church is already using that email address.",
                    "error"
                )

                return render_template(
                    "admin/edit_church.html",
                    church=church
                )

        church.name = church_name
        church.location = location
        church.phone = phone
        church.email = church_email

        db.session.commit()

        flash(
            "Church information updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    return render_template(
        "admin/edit_church.html",
        church=church
    )

@admin_bp.route(
    "/churches/<int:church_id>/administrators/<int:user_id>/edit",
    methods=["GET", "POST"]
)
@login_required
@system_admin_required
def edit_administrator(
    church_id,
    user_id
):

    church = db.session.get(
        Church,
        church_id
    )

    if church is None:

        flash(
            "Church could not be found.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    administrator = db.session.get(
        User,
        user_id
    )

    if administrator is None:

        flash(
            "Administrator could not be found.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.church_id != church.id:

        flash(
            "Administrator does not belong to this church.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.is_system_admin:

        flash(
            "System Admin accounts cannot be managed here.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        role = request.form.get(
            "role",
            ""
        ).strip()

        allowed_roles = [
            "Admin",
            "Manager",
            "Staff"
        ]

        if not name:

            flash(
                "Administrator name is required.",
                "error"
            )

            return render_template(
                "admin/edit_administrator.html",
                church=church,
                administrator=administrator
            )

        if not email:

            flash(
                "Administrator email is required.",
                "error"
            )

            return render_template(
                "admin/edit_administrator.html",
                church=church,
                administrator=administrator
            )

        if not role:

            flash(
                "Administrator role is required.",
                "error"
            )

            return render_template(
                "admin/edit_administrator.html",
                church=church,
                administrator=administrator
            )

        if role not in allowed_roles:

            flash(
                "Invalid administrator role.",
                "error"
            )

            return render_template(
                "admin/edit_administrator.html",
                church=church,
                administrator=administrator
            )

        existing_user = db.session.scalar(
            db.select(User).where(
                User.email == email,
                User.id != administrator.id
            )
        )

        if existing_user:

            flash(
                "Another user is already using that email address.",
                "error"
            )

            return render_template(
                "admin/edit_administrator.html",
                church=church,
                administrator=administrator
            )

        administrator.name = name
        administrator.email = email
        administrator.role = role

        db.session.commit()

        flash(
            "Administrator information updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    return render_template(
        "admin/edit_administrator.html",
        church=church,
        administrator=administrator
    )

@admin_bp.route(
    "/churches/<int:church_id>/toggle",
    methods=["POST"]
)
@login_required
@system_admin_required
def toggle_church(church_id):

    church = db.session.get(
        Church,
        church_id
    )

    if church is None:

        flash(
            "Church could not be found.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    church.is_active = not church.is_active

    db.session.commit()

    if church.is_active:

        flash(
            f"{church.name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{church.name} has been deactivated.",
            "success"
        )

    return redirect(
        url_for(
            "admin.manage_church",
            church_id=church.id
        )
    )


@admin_bp.route(
    "/churches/<int:church_id>/administrators/<int:user_id>/toggle",
    methods=["POST"]
)
@login_required
@system_admin_required
def toggle_administrator(
    church_id,
    user_id
):

    church = db.session.get(
        Church,
        church_id
    )

    if church is None:

        flash(
            "Church could not be found.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    administrator = db.session.get(
        User,
        user_id
    )

    if administrator is None:

        flash(
            "Administrator could not be found.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.church_id != church.id:

        flash(
            "Administrator does not belong to this church.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.is_system_admin:

        flash(
            "System Admin accounts cannot be managed here.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.id == current_user.id:

        flash(
            "You cannot deactivate your own administrator account.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    administrator.is_active = not administrator.is_active

    db.session.commit()

    if administrator.is_active:

        flash(
            f"{administrator.name} has been activated.",
            "success"
        )

    else:

        flash(
            f"{administrator.name} has been deactivated.",
            "success"
        )

    return redirect(
        url_for(
            "admin.manage_church",
            church_id=church.id
        )
    )

@admin_bp.route(
    "/churches/<int:church_id>/administrators/<int:user_id>/reset-password",
    methods=["POST"]
)
@login_required
@system_admin_required
def reset_administrator_password(
    church_id,
    user_id
):

    church = db.session.get(
        Church,
        church_id
    )

    if church is None:

        flash(
            "Church could not be found.",
            "error"
        )

        return redirect(
            url_for("admin.dashboard")
        )

    administrator = db.session.get(
        User,
        user_id
    )

    if administrator is None:

        flash(
            "Administrator could not be found.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.church_id != church.id:

        flash(
            "Administrator does not belong to this church.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.is_system_admin:

        flash(
            "System Admin accounts cannot be managed here.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if administrator.id == current_user.id:

        flash(
            "You cannot reset your own password through this route.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    new_password = request.form.get(
        "new_password",
        ""
    ).strip()

    confirm_password = request.form.get(
        "confirm_password",
        ""
    ).strip()

    if not new_password:

        flash(
            "New password is required.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if len(new_password) < 8:

        flash(
            "Password must be at least 8 characters long.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    if new_password != confirm_password:

        flash(
            "Passwords do not match.",
            "error"
        )

        return redirect(
            url_for(
                "admin.manage_church",
                church_id=church.id
            )
        )

    administrator.password_hash = generate_password_hash(
        new_password
    )

    db.session.commit()

    flash(
        f"Password for {administrator.name} was reset successfully.",
        "success"
    )

    return redirect(
        url_for(
            "admin.manage_church",
            church_id=church.id
        )
    )