"""Add page visibility and system settings tables

Revision ID: 001
Revises:
Create Date: 2025-11-03 22:15:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create system_settings table
    op.create_table('system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=True)

    # Create page_visibility table
    op.create_table('page_visibility',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_key', sa.String(length=100), nullable=False),
        sa.Column('page_name', sa.String(length=100), nullable=False),
        sa.Column('page_name_en', sa.String(length=100), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('disabled_message', sa.String(length=255), nullable=True),
        sa.Column('last_toggled_by', sa.Integer(), nullable=True),
        sa.Column('last_toggled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['last_toggled_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_page_visibility_page_key'), 'page_visibility', ['page_key'], unique=True)

    # Insert default system settings
    op.bulk_insert(
        sa.table('system_settings',
            sa.column('key', sa.String),
            sa.column('value', sa.String),
            sa.column('description', sa.Text)
        ),
        [
            {
                'key': 'maintenance_mode',
                'value': 'false',
                'description': 'Enable/disable maintenance mode for all users'
            },
            {
                'key': 'admin_panel_enabled',
                'value': 'true',
                'description': 'Enable/disable admin panel access'
            },
            {
                'key': 'max_file_upload_size',
                'value': '10485760',
                'description': 'Maximum file upload size in bytes (10MB)'
            },
            {
                'key': 'session_timeout',
                'value': '3600',
                'description': 'User session timeout in seconds (1 hour)'
            }
        ]
    )

    # Insert default page visibility settings
    op.bulk_insert(
        sa.table('page_visibility',
            sa.column('page_key', sa.String),
            sa.column('page_name', sa.String),
            sa.column('page_name_en', sa.String),
            sa.column('is_enabled', sa.Boolean),
            sa.column('path', sa.String),
            sa.column('description', sa.Text),
            sa.column('disabled_message', sa.String)
        ),
        [
            # Dashboard & Core
            {
                'page_key': 'dashboard',
                'page_name': 'ダッシュボード',
                'page_name_en': 'Dashboard',
                'is_enabled': True,
                'path': '/dashboard',
                'description': 'Main dashboard with statistics and overview',
                'disabled_message': 'ダッシュボードは準備中です。しばらくお待ちください。'
            },
            {
                'page_key': 'candidates',
                'page_name': '候補者管理',
                'page_name_en': 'Candidates',
                'is_enabled': True,
                'path': '/candidates',
                'description': 'Manage job candidates and applications',
                'disabled_message': '候補者管理は準備中です。しばらくお待ちください。'
            },
            {
                'page_key': 'employees',
                'page_name': '従業員管理',
                'page_name_en': 'Employees',
                'is_enabled': True,
                'path': '/employees',
                'description': 'Manage dispatched employees',
                'disabled_message': '従業員管理は準備中です。しばらくお待ちください。'
            },
            {
                'page_key': 'factories',
                'page_name': '工場管理',
                'page_name_en': 'Factories',
                'is_enabled': True,
                'path': '/factories',
                'description': 'Manage client factories and work sites',
                'disabled_message': '工場管理は準備中です。しばらくお待ちください。'
            },
            {
                'page_key': 'apartments',
                'page_name': '住宅管理',
                'page_name_en': 'Apartments',
                'is_enabled': True,
                'path': '/apartments',
                'description': 'Manage employee housing and apartments',
                'disabled_message': '住宅管理は準備中です。しばらくお待ちください。'
            },
            {
                'page_key': 'timercards',
                'page_name': 'タイムカード',
                'page_name_en': 'Time Cards',
                'is_enabled': True,
                'path': '/timercards',
                'description': 'Attendance tracking and time management',
                'disabled_message': 'タイムカードは準備中です。しばらくお待ちください。'
            },
            {
                'page_key': 'salary',
                'page_name': '給与管理',
                'page_name_en': 'Salary',
                'is_enabled': True,
                'path': '/salary',
                'description': 'Payroll calculations and salary management',
                'disabled_message': '給与管理は準備中です。しばらくお待ちください。'
            },
            {
                'page_key': 'requests',
                'page_name': '申請管理',
                'page_name_en': 'Requests',
                'is_enabled': True,
                'path': '/requests',
                'description': 'Leave requests and workflow management',
                'disabled_message': '申請管理は準備中です。しばらくお待ちください。'
            },
            # Reports & Analytics
            {
                'page_key': 'reports',
                'page_name': 'レポート',
                'page_name_en': 'Reports',
                'is_enabled': True,
                'path': '/reports',
                'description': 'Analytics and reporting dashboard',
                'disabled_message': 'レポートは準備中です。しばらくお待ちください。'
            },
            # Additional Pages
            {
                'page_key': 'design-system',
                'page_name': 'デザインシステム',
                'page_name_en': 'Design System',
                'is_enabled': True,
                'path': '/design-system',
                'description': 'UI components and design system showcase',
                'disabled_message': 'デザインシステムは準備中です。'
            },
            {
                'page_key': 'examples-forms',
                'page_name': 'フォーム例',
                'page_name_en': 'Examples - Forms',
                'is_enabled': True,
                'path': '/examples/forms',
                'description': 'Example forms and input components',
                'disabled_message': 'フォーム例は準備中です。'
            },
            {
                'page_key': 'support',
                'page_name': 'サポート',
                'page_name_en': 'Support',
                'is_enabled': True,
                'path': '/support',
                'description': 'Help and support documentation',
                'disabled_message': 'サポートは準備中です。'
            },
            {
                'page_key': 'help',
                'page_name': 'ヘルプ',
                'page_name_en': 'Help',
                'is_enabled': True,
                'path': '/help',
                'description': 'User help and guides',
                'disabled_message': 'ヘルプは準備中です。'
            },
            {
                'page_key': 'privacy',
                'page_name': 'プライバシーポリシー',
                'page_name_en': 'Privacy Policy',
                'is_enabled': True,
                'path': '/privacy',
                'description': 'Privacy policy and data handling',
                'disabled_message': 'プライバシーポリシーは準備中です。'
            },
            {
                'page_key': 'terms',
                'page_name': '利用規約',
                'page_name_en': 'Terms of Service',
                'is_enabled': True,
                'path': '/terms',
                'description': 'Terms and conditions of use',
                'disabled_message': '利用規約は準備中です。'
            }
        ]
    )


def downgrade():
    op.drop_table('page_visibility')
    op.drop_table('system_settings')
