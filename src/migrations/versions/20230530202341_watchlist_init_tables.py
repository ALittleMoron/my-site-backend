"""Watch list init tables.

Revision ID: 395a400af31a
Revises:
Create Date: 2023-05-30 20:23:41.801683

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

from app.core.models.types import datetime as dt_custom_types

revision = '395a400af31a'
down_revision = None
branch_labels = None
depends_on = None
UPDATED_TABLES = {'anime', 'kinopoisk'}


def upgrade() -> None:
    # функция-триггер для обновления updated_at поля.
    op.execute(
        """
            CREATE OR REPLACE FUNCTION update_at_change_column()
                RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = TIMEZONE('utc', CURRENT_TIMESTAMP);
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """,
    )

    # enums
    anime_kind_enum = pg.ENUM(
        'FILM',
        'SERIES',
        'OVA',
        'ONA',
        'SPECIAL',
        'NOT_SET',
        name='anime_lind_enum',
    )
    anime_kind_enum.create(op.get_bind(), checkfirst=True)  # type: ignore
    anime_kind_migration = pg.ENUM(name='anime_lind_enum', create_type=False)

    kinopoisk_kind_enum = pg.ENUM(
        'FILM',
        'SERIES',
        'SHORT_FILM',
        'NOT_SET',
        name='kinopoisk_kind_enum',
    )
    kinopoisk_kind_enum.create(op.get_bind(), checkfirst=True)  # type: ignore
    kinopoisk_kind_migration = pg.ENUM(name='anime_lind_enum', create_type=False)

    watch_list_element_status_enum = pg.ENUM(
        'WATCHED',
        'ABANDONED',
        'POSTPONED',
        'SCHEDULED',
        'REVIEWING',
        name='watch_list_element_status_enum',
    )
    watch_list_element_status_enum.create(op.get_bind(), checkfirst=True)  # type: ignore
    watch_list_element_status_migration = pg.ENUM(
        name='watch_list_element_status_enum',
        create_type=False,
    )

    # tables
    op.create_table(
        'anime',
        sa.Column(  # type: ignore
            'kind',
            anime_kind_migration,
            server_default='NOT_SET',
            nullable=False,
        ),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('native_name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('my_opinion', sa.String(), nullable=True),
        sa.Column('score', sa.SmallInteger(), nullable=True),
        sa.Column('repeat_view_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column(  # type: ignore
            'status',
            watch_list_element_status_migration,
            server_default='SCHEDULED',
            nullable=False,
        ),
        sa.Column(  # type: ignore
            'created_at',
            dt_custom_types.UTCDateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(  # type: ignore
            'updated_at',
            dt_custom_types.UTCDateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.CheckConstraint('score <= 100'),
        sa.CheckConstraint('score >= 0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )
    op.create_table(
        'kinopoisk',
        sa.Column(  # type: ignore
            'kind',
            kinopoisk_kind_migration,
            server_default='NOT_SET',
            nullable=False,
        ),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('native_name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('my_opinion', sa.String(), nullable=True),
        sa.Column('score', sa.SmallInteger(), nullable=True),
        sa.Column('repeat_view_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column(  # type: ignore
            'status',
            watch_list_element_status_migration,
            server_default='SCHEDULED',
            nullable=False,
        ),
        sa.Column(  # type: ignore
            'created_at',
            dt_custom_types.UTCDateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(  # type: ignore
            'updated_at',
            dt_custom_types.UTCDateTime(),
            server_default=sa.text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.CheckConstraint('score <= 100'),
        sa.CheckConstraint('score >= 0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )

    for table_name in UPDATED_TABLES:
        op.execute(
            f"""
                CREATE TRIGGER refresh_updated_at_{table_name} BEFORE UPDATE ON {table_name}
                FOR EACH ROW EXECUTE PROCEDURE update_at_change_column();
            """,
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    # tables
    for table_name in UPDATED_TABLES:
        op.execute(f"DROP TRIGGER refresh_updated_at_{table_name} ON {table_name}")

    op.drop_table('kinopoisk')
    op.drop_table('anime')

    # enums
    anime_kind_migration = pg.ENUM(name='anime_lind_enum', create_type=False)
    anime_kind_migration.drop(op.get_bind(), checkfirst=True)  # type: ignore
    kinopoisk_kind_migration = pg.ENUM(name='anime_lind_enum', create_type=False)
    kinopoisk_kind_migration.drop(op.get_bind(), checkfirst=True)  # type: ignore
    watch_list_element_status_migration = pg.ENUM(
        name='watch_list_element_status_enum',
        create_type=False,
    )
    watch_list_element_status_migration.drop(op.get_bind(), checkfirst=True)  # type: ignore

    # функция-триггер
    op.execute('DROP FUNCTION IF EXISTS update_at_change_column')
    # ### end Alembic commands ###
