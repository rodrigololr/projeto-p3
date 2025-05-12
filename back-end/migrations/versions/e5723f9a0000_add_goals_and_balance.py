"""add goals and balance

Revision ID: e5723f9a0000
Revises: 776f32e0bc45
Create Date: 2025-05-12 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'e5723f9a0000'
down_revision = '776f32e0bc45'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # Verificar e adicionar total_balance na tabela users
    if 'total_balance' not in [col['name'] for col in inspector.get_columns('users')]:
        op.add_column('users', sa.Column('total_balance', sa.Float(), server_default='0.0', nullable=False))

    # Verificar e adicionar tag na tabela expenses
    if 'tag' not in [col['name'] for col in inspector.get_columns('expenses')]:
        op.add_column('expenses', sa.Column('tag', sa.String(), nullable=True))

    # Verificar se a tabela goals já existe
    if not inspector.has_table('goals'):
        op.create_table('goals',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('tag', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    # Remover as colunas adicionadas
    if 'total_balance' in [col['name'] for col in inspector.get_columns('users')]:
        op.drop_column('users', 'total_balance')
    if 'tag' in [col['name'] for col in inspector.get_columns('expenses')]:
        op.drop_column('expenses', 'tag')
    if inspector.has_table('goals'):
        op.drop_table('goals')