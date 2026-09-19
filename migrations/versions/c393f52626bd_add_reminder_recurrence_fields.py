"""add reminder recurrence fields

Revision ID: c393f52626bd
Revises: 2d009951eb56
Create Date: 2026-09-11
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c393f52626bd"
down_revision = "2d009951eb56"
branch_labels = None
depends_on = None


def upgrade():
    # ---------------------------------------------------------
    # Add recurrence fields with temporary defaults.
    #
    # The existing reminder must receive valid values while
    # these new NOT NULL columns are being added.
    # ---------------------------------------------------------

    op.add_column(
        "reminders",
        sa.Column(
            "recurrence_type",
            sa.String(length=20),
            nullable=False,
            server_default="one_time"
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "recurrence_interval",
            sa.Integer(),
            nullable=False,
            server_default="1"
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "recurrence_day_of_week",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "recurrence_day_of_month",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "recurrence_month",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "recurrence_end_date",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "next_run_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "last_run_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )

    op.add_column(
        "reminders",
        sa.Column(
            "total_sent",
            sa.Integer(),
            nullable=False,
            server_default="0"
        )
    )

    # ---------------------------------------------------------
    # Remove the temporary database defaults.
    #
    # The application model already provides the appropriate
    # defaults for newly-created reminders.
    # ---------------------------------------------------------

    op.alter_column(
        "reminders",
        "recurrence_type",
        server_default=None
    )

    op.alter_column(
        "reminders",
        "recurrence_interval",
        server_default=None
    )

    op.alter_column(
        "reminders",
        "is_active",
        server_default=None
    )

    op.alter_column(
        "reminders",
        "total_sent",
        server_default=None
    )


def downgrade():

    op.drop_column(
        "reminders",
        "total_sent"
    )

    op.drop_column(
        "reminders",
        "is_active"
    )

    op.drop_column(
        "reminders",
        "last_run_at"
    )

    op.drop_column(
        "reminders",
        "next_run_at"
    )

    op.drop_column(
        "reminders",
        "recurrence_end_date"
    )

    op.drop_column(
        "reminders",
        "recurrence_month"
    )

    op.drop_column(
        "reminders",
        "recurrence_day_of_month"
    )

    op.drop_column(
        "reminders",
        "recurrence_day_of_week"
    )

    op.drop_column(
        "reminders",
        "recurrence_interval"
    )

    op.drop_column(
        "reminders",
        "recurrence_type"
    )