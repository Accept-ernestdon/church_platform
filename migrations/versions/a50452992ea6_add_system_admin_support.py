from alembic import op
import sqlalchemy as sa


revision = "a50452992ea6"
down_revision = "50becf7d06c5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "is_system_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )

    op.alter_column(
        "users",
        "is_system_admin",
        server_default=None
    )

    op.alter_column(
        "users",
        "church_id",
        existing_type=sa.INTEGER(),
        nullable=True
    )


def downgrade():
    op.alter_column(
        "users",
        "church_id",
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.drop_column(
        "users",
        "is_system_admin"
    )