"""Add comprehensive test case fields

Revision ID: 20250831_add_test_case_fields
Revises: 
Create Date: 2025-08-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250831_add_test_case_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to test_cases table
    op.add_column('test_cases', sa.Column('requirement_reference', sa.String(), nullable=True))
    op.add_column('test_cases', sa.Column('module_feature', sa.String(), nullable=True))
    op.add_column('test_cases', sa.Column('version_build', sa.String(), nullable=True))
    op.add_column('test_cases', sa.Column('preconditions', sa.Text(), nullable=True))
    op.add_column('test_cases', sa.Column('actual_result', sa.Text(), nullable=True))
    op.add_column('test_cases', sa.Column('environment', sa.String(), nullable=True))
    op.add_column('test_cases', sa.Column('automation_status', sa.String(), nullable=True))
    op.add_column('test_cases', sa.Column('owner', sa.String(), nullable=True))
    op.add_column('test_cases', sa.Column('linked_defects', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('test_cases', sa.Column('attachments', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Update existing enum values
    # Status enum updates
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'ready'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'pass'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'fail'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'blocked'")
    op.execute("ALTER TYPE status ADD VALUE IF NOT EXISTS 'not_run'")
    
    # TestType enum updates
    op.execute("ALTER TYPE testtype ADD VALUE IF NOT EXISTS 'regression'")
    op.execute("ALTER TYPE testtype ADD VALUE IF NOT EXISTS 'smoke'")
    op.execute("ALTER TYPE testtype ADD VALUE IF NOT EXISTS 'uat'")
    
    # Add new enums
    environment_enum = postgresql.ENUM('dev', 'qa', 'staging', 'prod', name='environmenttype')
    environment_enum.create(op.get_bind())
    
    automation_enum = postgresql.ENUM('manual', 'automated', 'candidate', name='automationstatus')
    automation_enum.create(op.get_bind())

def downgrade():
    # Remove columns
    op.drop_column('test_cases', 'attachments')
    op.drop_column('test_cases', 'linked_defects')
    op.drop_column('test_cases', 'owner')
    op.drop_column('test_cases', 'automation_status')
    op.drop_column('test_cases', 'environment')
    op.drop_column('test_cases', 'actual_result')
    op.drop_column('test_cases', 'preconditions')
    op.drop_column('test_cases', 'version_build')
    op.drop_column('test_cases', 'module_feature')
    op.drop_column('test_cases', 'requirement_reference')
    
    # Drop enums
    environment_enum = postgresql.ENUM('dev', 'qa', 'staging', 'prod', name='environmenttype')
    environment_enum.drop(op.get_bind())
    
    automation_enum = postgresql.ENUM('manual', 'automated', 'candidate', name='automationstatus')
    automation_enum.drop(op.get_bind())