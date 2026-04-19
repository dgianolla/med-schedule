"""add patients, convenios tables and alter appointments

Revision ID: 002_patients_convenios
Revises: 001_initial
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002_patients_convenios'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # patients
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False, unique=True),
        sa.Column('email', sa.String(200), nullable=True),
        sa.Column('document', sa.String(30), nullable=True),
        sa.Column('birth_date', sa.Date, nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index('ix_patients_phone', 'patients', ['phone'])
    op.create_index('ix_patients_document', 'patients', ['document'])

    # convenios
    op.create_table(
        'convenios',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=True, unique=True),
        sa.Column('active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('contact', sa.String(200), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # alter appointments: add patient_id FK and medical_notes
    op.add_column('appointments', sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_appointments_patient_id',
        'appointments', 'patients',
        ['patient_id'], ['id'],
    )
    op.create_index('ix_appointments_patient_id', 'appointments', ['patient_id'])

    op.add_column('appointments', sa.Column('medical_notes', sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column('appointments', 'medical_notes')
    op.drop_index('ix_appointments_patient_id', 'appointments')
    op.drop_constraint('fk_appointments_patient_id', 'appointments', type_='foreignkey')
    op.drop_column('appointments', 'patient_id')
    op.drop_table('convenios')
    op.drop_index('ix_patients_document', 'patients')
    op.drop_index('ix_patients_phone', 'patients')
    op.drop_table('patients')
