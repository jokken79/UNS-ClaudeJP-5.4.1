"""add_more_missing_columns_to_candidates

Revision ID: 3c20e838905b
Revises: 7b5286821f25
Create Date: 2025-10-19 02:35:06.737278

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


def _column_exists(table_name: str, column_name: str) -> bool:
    """Return True if a column already exists on the target table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _add_column_if_missing(table_name: str, name: str, type_: sa.types.TypeEngine, **kwargs) -> None:
    if not _column_exists(table_name, name):
        op.add_column(table_name, sa.Column(name, type_, **kwargs))


def _drop_column_if_exists(table_name: str, name: str) -> None:
    if _column_exists(table_name, name):
        op.drop_column(table_name, name)


# revision identifiers, used by Alembic.
revision: str = '3c20e838905b'
down_revision: Union[str, None] = '7b5286821f25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the missing columns to candidates table if they are not already present
    definitions = [
        ("marital_status", sa.String(length=20), {"nullable": True}),
        ("hire_date", sa.Date(), {"nullable": True}),
        ("current_address", sa.Text(), {"nullable": True}),
        ("address_banchi", sa.String(length=100), {"nullable": True}),
        ("address_building", sa.String(length=100), {"nullable": True}),
        ("building_name", sa.String(length=100), {"nullable": True}),
        ("registered_address", sa.Text(), {"nullable": True}),
        ("passport_number", sa.String(length=50), {"nullable": True}),
        ("passport_expiry", sa.Date(), {"nullable": True}),
        ("residence_status", sa.String(length=50), {"nullable": True}),
        ("residence_expiry", sa.Date(), {"nullable": True}),
        ("license_number", sa.String(length=50), {"nullable": True}),
        ("license_expiry", sa.Date(), {"nullable": True}),
        ("car_ownership", sa.String(length=10), {"nullable": True}),
        ("voluntary_insurance", sa.String(length=10), {"nullable": True}),
        ("forklift_license", sa.String(length=10), {"nullable": True}),
        ("tama_kake", sa.String(length=10), {"nullable": True}),
        ("mobile_crane_under_5t", sa.String(length=10), {"nullable": True}),
        ("mobile_crane_over_5t", sa.String(length=10), {"nullable": True}),
        ("gas_welding", sa.String(length=10), {"nullable": True}),
        ("family_name_1", sa.String(length=100), {"nullable": True}),
        ("family_relation_1", sa.String(length=50), {"nullable": True}),
        ("family_age_1", sa.Integer(), {"nullable": True}),
        ("family_residence_1", sa.String(length=50), {"nullable": True}),
        ("family_separate_address_1", sa.Text(), {"nullable": True}),
        ("family_name_2", sa.String(length=100), {"nullable": True}),
        ("family_relation_2", sa.String(length=50), {"nullable": True}),
        ("family_age_2", sa.Integer(), {"nullable": True}),
        ("family_residence_2", sa.String(length=50), {"nullable": True}),
        ("family_separate_address_2", sa.Text(), {"nullable": True}),
        ("family_name_3", sa.String(length=100), {"nullable": True}),
        ("family_relation_3", sa.String(length=50), {"nullable": True}),
        ("family_age_3", sa.Integer(), {"nullable": True}),
        ("family_residence_3", sa.String(length=50), {"nullable": True}),
        ("family_separate_address_3", sa.Text(), {"nullable": True}),
        ("family_name_4", sa.String(length=100), {"nullable": True}),
        ("family_relation_4", sa.String(length=50), {"nullable": True}),
        ("family_age_4", sa.Integer(), {"nullable": True}),
        ("family_residence_4", sa.String(length=50), {"nullable": True}),
        ("family_separate_address_4", sa.Text(), {"nullable": True}),
        ("family_name_5", sa.String(length=100), {"nullable": True}),
        ("family_relation_5", sa.String(length=50), {"nullable": True}),
        ("family_age_5", sa.Integer(), {"nullable": True}),
        ("family_residence_5", sa.String(length=50), {"nullable": True}),
        ("family_separate_address_5", sa.Text(), {"nullable": True}),
        ("work_history_company_7", sa.String(length=200), {"nullable": True}),
        ("work_history_entry_company_7", sa.String(length=200), {"nullable": True}),
        ("work_history_exit_company_7", sa.String(length=200), {"nullable": True}),
        ("exp_nc_lathe", sa.Boolean(), {"nullable": True}),
        ("exp_lathe", sa.Boolean(), {"nullable": True}),
        ("exp_press", sa.Boolean(), {"nullable": True}),
        ("exp_forklift", sa.Boolean(), {"nullable": True}),
        ("exp_packing", sa.Boolean(), {"nullable": True}),
        ("exp_welding", sa.Boolean(), {"nullable": True}),
        ("exp_car_assembly", sa.Boolean(), {"nullable": True}),
        ("exp_car_line", sa.Boolean(), {"nullable": True}),
        ("exp_car_inspection", sa.Boolean(), {"nullable": True}),
        ("exp_electronic_inspection", sa.Boolean(), {"nullable": True}),
        ("exp_food_processing", sa.Boolean(), {"nullable": True}),
        ("exp_casting", sa.Boolean(), {"nullable": True}),
        ("exp_line_leader", sa.Boolean(), {"nullable": True}),
        ("exp_painting", sa.Boolean(), {"nullable": True}),
        ("exp_other", sa.Text(), {"nullable": True}),
        ("bento_lunch_dinner", sa.String(length=10), {"nullable": True}),
        ("bento_lunch_only", sa.String(length=10), {"nullable": True}),
        ("bento_dinner_only", sa.String(length=10), {"nullable": True}),
        ("bento_bring_own", sa.String(length=10), {"nullable": True}),
        ("commute_method", sa.String(length=50), {"nullable": True}),
        ("commute_time_oneway", sa.Integer(), {"nullable": True}),
        ("interview_result", sa.String(length=20), {"nullable": True}),
        ("antigen_test_kit", sa.String(length=20), {"nullable": True}),
        ("antigen_test_date", sa.Date(), {"nullable": True}),
        ("covid_vaccine_status", sa.String(length=50), {"nullable": True}),
        ("language_skill_exists", sa.String(length=10), {"nullable": True}),
        ("language_skill_1", sa.String(length=100), {"nullable": True}),
        ("language_skill_2", sa.String(length=100), {"nullable": True}),
        ("japanese_qualification", sa.String(length=50), {"nullable": True}),
        ("jlpt_taken", sa.String(length=10), {"nullable": True}),
        ("jlpt_date", sa.Date(), {"nullable": True}),
        ("jlpt_score", sa.Integer(), {"nullable": True}),
        ("jlpt_scheduled", sa.String(length=10), {"nullable": True}),
        ("qualification_1", sa.String(length=100), {"nullable": True}),
        ("qualification_2", sa.String(length=100), {"nullable": True}),
        ("qualification_3", sa.String(length=100), {"nullable": True}),
        ("major", sa.String(length=100), {"nullable": True}),
        ("blood_type", sa.String(length=5), {"nullable": True}),
        ("dominant_hand", sa.String(length=10), {"nullable": True}),
        ("allergy_exists", sa.String(length=10), {"nullable": True}),
        ("listening_level", sa.String(length=20), {"nullable": True}),
        ("speaking_level", sa.String(length=20), {"nullable": True}),
        ("emergency_contact_name", sa.String(length=100), {"nullable": True}),
        ("emergency_contact_relation", sa.String(length=50), {"nullable": True}),
        ("emergency_contact_phone", sa.String(length=20), {"nullable": True}),
        ("safety_shoes", sa.String(length=10), {"nullable": True}),
        ("read_katakana", sa.String(length=20), {"nullable": True}),
        ("read_hiragana", sa.String(length=20), {"nullable": True}),
        ("read_kanji", sa.String(length=20), {"nullable": True}),
        ("write_katakana", sa.String(length=20), {"nullable": True}),
        ("write_hiragana", sa.String(length=20), {"nullable": True}),
        ("write_kanji", sa.String(length=20), {"nullable": True}),
        ("can_speak", sa.String(length=20), {"nullable": True}),
        ("can_understand", sa.String(length=20), {"nullable": True}),
        ("can_read_kana", sa.String(length=20), {"nullable": True}),
        ("can_write_kana", sa.String(length=20), {"nullable": True}),
    ]

    for name, type_, kwargs in definitions:
        _add_column_if_missing("candidates", name, type_, **kwargs)


def downgrade() -> None:
    # Remove the columns if they exist
    columns = [
        "can_write_kana",
        "can_read_kana",
        "can_understand",
        "can_speak",
        "write_kanji",
        "write_hiragana",
        "write_katakana",
        "read_kanji",
        "read_hiragana",
        "read_katakana",
        "safety_shoes",
        "emergency_contact_phone",
        "emergency_contact_relation",
        "emergency_contact_name",
        "speaking_level",
        "listening_level",
        "allergy_exists",
        "dominant_hand",
        "blood_type",
        "major",
        "qualification_3",
        "qualification_2",
        "qualification_1",
        "jlpt_scheduled",
        "jlpt_score",
        "jlpt_date",
        "jlpt_taken",
        "japanese_qualification",
        "language_skill_2",
        "language_skill_1",
        "language_skill_exists",
        "covid_vaccine_status",
        "antigen_test_date",
        "antigen_test_kit",
        "interview_result",
        "commute_time_oneway",
        "commute_method",
        "bento_bring_own",
        "bento_dinner_only",
        "bento_lunch_only",
        "bento_lunch_dinner",
        "exp_other",
        "exp_painting",
        "exp_line_leader",
        "exp_casting",
        "exp_food_processing",
        "exp_electronic_inspection",
        "exp_car_inspection",
        "exp_car_line",
        "exp_car_assembly",
        "exp_welding",
        "exp_packing",
        "exp_forklift",
        "exp_press",
        "exp_lathe",
        "exp_nc_lathe",
        "work_history_exit_company_7",
        "work_history_entry_company_7",
        "work_history_company_7",
        "family_separate_address_5",
        "family_residence_5",
        "family_age_5",
        "family_relation_5",
        "family_name_5",
        "family_separate_address_4",
        "family_residence_4",
        "family_age_4",
        "family_relation_4",
        "family_name_4",
        "family_separate_address_3",
        "family_residence_3",
        "family_age_3",
        "family_relation_3",
        "family_name_3",
        "family_separate_address_2",
        "family_residence_2",
        "family_age_2",
        "family_relation_2",
        "family_name_2",
        "family_separate_address_1",
        "family_residence_1",
        "family_age_1",
        "family_relation_1",
        "family_name_1",
        "gas_welding",
        "mobile_crane_over_5t",
        "mobile_crane_under_5t",
        "tama_kake",
        "forklift_license",
        "voluntary_insurance",
        "car_ownership",
        "license_expiry",
        "license_number",
        "residence_expiry",
        "residence_status",
        "passport_expiry",
        "passport_number",
        "registered_address",
        "building_name",
        "address_building",
        "address_banchi",
        "current_address",
        "hire_date",
        "marital_status",
    ]

    for name in columns:
        _drop_column_if_exists("candidates", name)
