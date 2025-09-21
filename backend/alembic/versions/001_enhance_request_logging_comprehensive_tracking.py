"""enhance_request_logging_comprehensive_tracking

Revision ID: 001
Revises: 
Create Date: 2025-09-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add comprehensive request logging table"""
    # Create request_logs table
    op.create_table('request_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('ts', sa.DateTime(), nullable=False),
    sa.Column('method', sa.String(length=16), nullable=False),
    sa.Column('path', sa.String(length=255), nullable=False),
    sa.Column('status_code', sa.Integer(), nullable=False),
    sa.Column('duration_ms', sa.Integer(), nullable=False),
    sa.Column('job_id', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.String(length=64), nullable=True),
    sa.Column('format', sa.String(length=32), nullable=True),
    sa.Column('client_ip', sa.String(length=64), nullable=True),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('file_size', sa.BigInteger(), nullable=True),
    sa.Column('file_type', sa.String(length=64), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('request_data', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
    sa.Column('response_data', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
    sa.Column('extra', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index(op.f('ix_request_logs_ts'), 'request_logs', ['ts'], unique=False)
    op.create_index(op.f('ix_request_logs_path'), 'request_logs', ['path'], unique=False)
    op.create_index(op.f('ix_request_logs_job_id'), 'request_logs', ['job_id'], unique=False)
    op.create_index(op.f('ix_request_logs_user_id'), 'request_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_request_logs_client_ip'), 'request_logs', ['client_ip'], unique=False)


def downgrade():
    """Remove request logging table"""
    op.drop_index(op.f('ix_request_logs_client_ip'), table_name='request_logs')
    op.drop_index(op.f('ix_request_logs_user_id'), table_name='request_logs')
    op.drop_index(op.f('ix_request_logs_job_id'), table_name='request_logs')
    op.drop_index(op.f('ix_request_logs_path'), table_name='request_logs')
    op.drop_index(op.f('ix_request_logs_ts'), table_name='request_logs')
    op.drop_table('request_logs')