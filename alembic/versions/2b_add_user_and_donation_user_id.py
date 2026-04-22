"""Таблица user и связь пожертвований с пользователем.

Идентификатор ревизии: 2b
Предыдущая ревизия: 1a
Дата создания: 2025-04-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '2b'
down_revision = '1a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('hashed_password', sa.String(length=1024), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    with op.batch_alter_table('donation', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('user_id', sa.Integer(), nullable=False),
        )
        batch_op.create_foreign_key(
            'fk_donation_user_id_user',
            'user',
            ['user_id'],
            ['id'],
        )


def downgrade():
    with op.batch_alter_table('donation', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_donation_user_id_user',
            type_='foreignkey',
        )
        batch_op.drop_column('user_id')

    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
