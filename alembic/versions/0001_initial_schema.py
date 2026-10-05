"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-30 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create departments table
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('head_of_department', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_code'), 'departments', ['code'], unique=True)
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    op.create_index(op.f('ix_departments_name'), 'departments', ['name'], unique=True)

    # 2. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=150), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('roll_number', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('ix_users_roll_number'), 'users', ['roll_number'], unique=False)

    # 3. Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('venue', sa.String(length=200), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('registration_deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('organizer_id', sa.Integer(), nullable=False),
        sa.Column('banner_url', sa.String(length=500), nullable=True),
        sa.Column('is_certificate_provided', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(op.f('ix_events_start_time'), 'events', ['start_time'], unique=False)
    op.create_index(op.f('ix_events_status'), 'events', ['status'], unique=False)
    op.create_index(op.f('ix_events_title'), 'events', ['title'], unique=False)

    # 4. Create event_registrations table
    op.create_table(
        'event_registrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('registered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cancellation_reason', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'student_id', name='uq_event_student_registration')
    )
    op.create_index(op.f('ix_event_registrations_event_id'), 'event_registrations', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_registrations_id'), 'event_registrations', ['id'], unique=False)
    op.create_index(op.f('ix_event_registrations_status'), 'event_registrations', ['status'], unique=False)
    op.create_index(op.f('ix_event_registrations_student_id'), 'event_registrations', ['student_id'], unique=False)

    # 5. Create attendances table
    op.create_table(
        'attendances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('registration_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('marked_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('marked_by_id', sa.Integer(), nullable=True),
        sa.Column('check_in_code', sa.String(length=64), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['marked_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['registration_id'], ['event_registrations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'student_id', name='uq_event_student_attendance')
    )
    op.create_index(op.f('ix_attendances_event_id'), 'attendances', ['event_id'], unique=False)
    op.create_index(op.f('ix_attendances_id'), 'attendances', ['id'], unique=False)
    op.create_index(op.f('ix_attendances_status'), 'attendances', ['status'], unique=False)
    op.create_index(op.f('ix_attendances_student_id'), 'attendances', ['student_id'], unique=False)

    # 6. Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('related_event_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['related_event_id'], ['events.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_is_read'), 'notifications', ['is_read'], unique=False)
    op.create_index(op.f('ix_notifications_notification_type'), 'notifications', ['notification_type'], unique=False)
    op.create_index(op.f('ix_notifications_recipient_id'), 'notifications', ['recipient_id'], unique=False)

    # 7. Create event_feedbacks table
    op.create_table(
        'event_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'student_id', name='uq_event_student_feedback'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range')
    )
    op.create_index(op.f('ix_event_feedbacks_event_id'), 'event_feedbacks', ['event_id'], unique=False)
    op.create_index(op.f('ix_event_feedbacks_id'), 'event_feedbacks', ['id'], unique=False)
    op.create_index(op.f('ix_event_feedbacks_student_id'), 'event_feedbacks', ['student_id'], unique=False)

    # 8. Create certificates table
    op.create_table(
        'certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('certificate_code', sa.String(length=100), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('issue_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('issued_by_id', sa.Integer(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['issued_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'student_id', name='uq_event_student_certificate')
    )
    op.create_index(op.f('ix_certificates_certificate_code'), 'certificates', ['certificate_code'], unique=True)
    op.create_index(op.f('ix_certificates_event_id'), 'certificates', ['event_id'], unique=False)
    op.create_index(op.f('ix_certificates_id'), 'certificates', ['id'], unique=False)
    op.create_index(op.f('ix_certificates_student_id'), 'certificates', ['student_id'], unique=False)


def downgrade() -> None:
    op.drop_table('certificates')
    op.drop_table('event_feedbacks')
    op.drop_table('notifications')
    op.drop_table('attendances')
    op.drop_table('event_registrations')
    op.drop_table('events')
    op.drop_table('users')
    op.drop_table('departments')
