"""admin table.

Revision ID: 9e9ff391bff4
Revises: 395a400af31a
Create Date: 2023-08-04 14:21:54.896307

"""
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from app.core.models.types import datetime as dt_custom_types

# revision identifiers, used by Alembic.
revision = '9e9ff391bff4'
down_revision = '395a400af31a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'admins',
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column(
            'password',
            sqlalchemy_utils.types.password.PasswordType(max_length=1137),
            nullable=False,
        ),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column(
            'created_at',
            dt_custom_types.UTCDateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            dt_custom_types.UTCDateTime(timezone=True),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )


def downgrade() -> None:
    op.drop_table('admins')
