"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-04-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable UUID generation
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # appointment_types
    op.create_table(
        'appointment_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('default_duration_minutes', sa.Integer, nullable=False, server_default='30'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # professionals
    op.create_table(
        'professionals',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('specialty', sa.String(100), nullable=False),
        sa.Column('specialty_slug', sa.String(100), nullable=False),
        sa.Column('external_id', sa.String(100), nullable=True),
        sa.Column('provider', sa.String(50), nullable=False, server_default='local'),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('name', 'specialty', name='uq_professional_name_specialty'),
    )
    
    # appointments
    op.create_table(
        'appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('patient_name', sa.String(200), nullable=False),
        sa.Column('patient_phone', sa.String(20), nullable=False),
        sa.Column('patient_email', sa.String(200), nullable=True),
        sa.Column('professional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('professionals.id'), nullable=True),
        sa.Column('professional_name', sa.String(200), nullable=True),
        sa.Column('appointment_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('appointment_types.id'), nullable=True),
        sa.Column('specialty', sa.String(100), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer, nullable=False),
        sa.Column('status', sa.String(30), nullable=False, server_default='scheduled'),
        sa.Column('source', sa.String(30), nullable=False, server_default='lia'),
        sa.Column('convenio_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('convenio_name', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('patient_notes', sa.Text, nullable=True),
        sa.Column('external_id', sa.String(200), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # appointments indexes
    op.create_index('ix_appointments_scheduled_at', 'appointments', ['scheduled_at'])
    op.create_index('ix_appointments_patient_phone', 'appointments', ['patient_phone'])
    op.create_index('ix_appointments_status_scheduled_at', 'appointments', ['status', 'scheduled_at'])
    op.create_index('ix_appointments_professional_scheduled', 'appointments', ['professional_id', 'scheduled_at'])
    op.create_index('ix_appointments_external_id', 'appointments', ['external_id'])
    
    # availability_blocks
    op.create_table(
        'availability_blocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('professional_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('professionals.id'), nullable=True),
        sa.Column('specialty', sa.String(100), nullable=True),
        sa.Column('start_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(200), nullable=True),
        sa.Column('recurring', sa.String(20), nullable=False, server_default='none'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # availability_blocks index
    op.create_index('ix_availability_professional_start_end', 'availability_blocks', 
                    ['professional_id', 'start_at', 'end_at'])
    
    # scheduling_settings
    op.create_table(
        'scheduling_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('weekday_opening', sa.Time, nullable=False, server_default='08:00:00'),
        sa.Column('weekday_closing', sa.Time, nullable=False, server_default='17:00:00'),
        sa.Column('saturday_opening', sa.Time, nullable=False, server_default='08:00:00'),
        sa.Column('saturday_closing', sa.Time, nullable=False, server_default='12:00:00'),
        sa.Column('sunday_closed', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('holidays_closed', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('buffer_minutes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('max_advance_days', sa.Integer, nullable=False, server_default='60'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    
    # provider_routes
    op.create_table(
        'provider_routes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('specialty_slug', sa.String(100), nullable=False, unique=True),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('provider_routes')
    op.drop_table('scheduling_settings')
    op.drop_index('ix_availability_professional_start_end', 'availability_blocks')
    op.drop_table('availability_blocks')
    op.drop_index('ix_appointments_external_id', 'appointments')
    op.drop_index('ix_appointments_professional_scheduled', 'appointments')
    op.drop_index('ix_appointments_status_scheduled_at', 'appointments')
    op.drop_index('ix_appointments_patient_phone', 'appointments')
    op.drop_index('ix_appointments_scheduled_at', 'appointments')
    op.drop_table('appointments')
    op.drop_table('professionals')
    op.drop_table('appointment_types')
