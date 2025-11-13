--
-- PostgreSQL database dump
--

\restrict cMFtzOLtAh0fQPxGehhJYdhr17sdctvpYQNxoSvjVJ1zPTnwvtv4AHkVLfoLmHT

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: adminactiontype; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.adminactiontype AS ENUM (
    'PAGE_VISIBILITY_CHANGE',
    'ROLE_PERMISSION_CHANGE',
    'BULK_OPERATION',
    'CONFIG_CHANGE',
    'CACHE_CLEAR',
    'USER_MANAGEMENT',
    'SYSTEM_SETTINGS'
);


ALTER TYPE public.adminactiontype OWNER TO uns_admin;

--
-- Name: apartment_status; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.apartment_status AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'MAINTENANCE',
    'RESERVED'
);


ALTER TYPE public.apartment_status OWNER TO uns_admin;

--
-- Name: assignment_status; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.assignment_status AS ENUM (
    'ACTIVE',
    'ENDED',
    'CANCELLED',
    'TRANSFERRED'
);


ALTER TYPE public.assignment_status OWNER TO uns_admin;

--
-- Name: charge_status; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.charge_status AS ENUM (
    'PENDING',
    'PROCESSED',
    'PAID',
    'CANCELLED'
);


ALTER TYPE public.charge_status OWNER TO uns_admin;

--
-- Name: charge_type; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.charge_type AS ENUM (
    'CLEANING',
    'REPAIR',
    'DEPOSIT',
    'PENALTY',
    'KEY_REPLACEMENT',
    'OTHER'
);


ALTER TYPE public.charge_type OWNER TO uns_admin;

--
-- Name: deduction_status; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.deduction_status AS ENUM (
    'PENDING',
    'PROCESSED',
    'PAID',
    'CANCELLED'
);


ALTER TYPE public.deduction_status OWNER TO uns_admin;

--
-- Name: document_type; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.document_type AS ENUM (
    'RIREKISHO',
    'ZAIRYU_CARD',
    'LICENSE',
    'CONTRACT',
    'OTHER'
);


ALTER TYPE public.document_type OWNER TO uns_admin;

--
-- Name: request_status; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.request_status AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'COMPLETED'
);


ALTER TYPE public.request_status OWNER TO uns_admin;

--
-- Name: request_type; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.request_type AS ENUM (
    'YUKYU',
    'HANKYU',
    'IKKIKOKOKU',
    'TAISHA',
    'NYUUSHA'
);


ALTER TYPE public.request_type OWNER TO uns_admin;

--
-- Name: resourcetype; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.resourcetype AS ENUM (
    'PAGE',
    'ROLE',
    'SYSTEM',
    'USER',
    'PERMISSION'
);


ALTER TYPE public.resourcetype OWNER TO uns_admin;

--
-- Name: room_type; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.room_type AS ENUM (
    'ONE_K',
    'ONE_DK',
    'ONE_LDK',
    'TWO_K',
    'TWO_DK',
    'TWO_LDK',
    'THREE_LDK',
    'STUDIO',
    'OTHER'
);


ALTER TYPE public.room_type OWNER TO uns_admin;

--
-- Name: shift_type; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.shift_type AS ENUM (
    'ASA',
    'HIRU',
    'YORU',
    'OTHER'
);


ALTER TYPE public.shift_type OWNER TO uns_admin;

--
-- Name: user_role; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.user_role AS ENUM (
    'SUPER_ADMIN',
    'ADMIN',
    'KEITOSAN',
    'TANTOSHA',
    'COORDINATOR',
    'KANRININSHA',
    'EMPLOYEE',
    'CONTRACT_WORKER'
);


ALTER TYPE public.user_role OWNER TO uns_admin;

--
-- Name: yukyu_status; Type: TYPE; Schema: public; Owner: uns_admin
--

CREATE TYPE public.yukyu_status AS ENUM (
    'ACTIVE',
    'EXPIRED'
);


ALTER TYPE public.yukyu_status OWNER TO uns_admin;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: additional_charges; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.additional_charges (
    id integer NOT NULL,
    assignment_id integer NOT NULL,
    employee_id integer NOT NULL,
    apartment_id integer NOT NULL,
    charge_type public.charge_type NOT NULL,
    description character varying(500) NOT NULL,
    amount integer NOT NULL,
    charge_date date NOT NULL,
    status public.charge_status NOT NULL,
    approved_by integer,
    approved_at timestamp with time zone,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp without time zone
);


ALTER TABLE public.additional_charges OWNER TO uns_admin;

--
-- Name: additional_charges_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.additional_charges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.additional_charges_id_seq OWNER TO uns_admin;

--
-- Name: additional_charges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.additional_charges_id_seq OWNED BY public.additional_charges.id;


--
-- Name: admin_audit_logs; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.admin_audit_logs (
    id integer NOT NULL,
    admin_user_id integer NOT NULL,
    action_type public.adminactiontype NOT NULL,
    resource_type public.resourcetype NOT NULL,
    resource_key character varying(255),
    previous_value text,
    new_value text,
    ip_address character varying(45),
    user_agent text,
    description text,
    audit_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.admin_audit_logs OWNER TO uns_admin;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.admin_audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_audit_logs_id_seq OWNER TO uns_admin;

--
-- Name: admin_audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.admin_audit_logs_id_seq OWNED BY public.admin_audit_logs.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO uns_admin;

--
-- Name: apartment_assignments; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.apartment_assignments (
    id integer NOT NULL,
    apartment_id integer NOT NULL,
    employee_id integer NOT NULL,
    start_date date NOT NULL,
    end_date date,
    monthly_rent integer NOT NULL,
    days_in_month integer,
    days_occupied integer,
    prorated_rent integer,
    is_prorated boolean,
    total_deduction integer NOT NULL,
    pays_parking boolean NOT NULL,
    contract_type character varying(50),
    status public.assignment_status NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp without time zone,
    CONSTRAINT check_assignment_dates CHECK (((end_date IS NULL) OR (end_date >= start_date))),
    CONSTRAINT check_days_occupied CHECK (((days_occupied > 0) AND (days_occupied <= 31)))
);


ALTER TABLE public.apartment_assignments OWNER TO uns_admin;

--
-- Name: apartment_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.apartment_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.apartment_assignments_id_seq OWNER TO uns_admin;

--
-- Name: apartment_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.apartment_assignments_id_seq OWNED BY public.apartment_assignments.id;


--
-- Name: apartment_factory; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.apartment_factory (
    id integer NOT NULL,
    apartment_id integer NOT NULL,
    factory_id integer NOT NULL,
    is_primary boolean,
    priority integer,
    distance_km numeric(6,2),
    commute_minutes integer,
    effective_from date,
    effective_until date,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.apartment_factory OWNER TO uns_admin;

--
-- Name: apartment_factory_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.apartment_factory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.apartment_factory_id_seq OWNER TO uns_admin;

--
-- Name: apartment_factory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.apartment_factory_id_seq OWNED BY public.apartment_factory.id;


--
-- Name: apartments; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.apartments (
    id integer NOT NULL,
    apartment_code character varying(50),
    name character varying(200) NOT NULL,
    building_name character varying(200),
    room_number character varying(20),
    floor_number integer,
    postal_code character varying(10),
    prefecture character varying(50),
    city character varying(100),
    address text,
    address_line1 character varying(200),
    address_line2 character varying(200),
    region_id integer,
    zone character varying(50),
    room_type public.room_type,
    size_sqm numeric(6,2),
    capacity integer,
    property_type character varying(50),
    base_rent integer NOT NULL,
    monthly_rent integer,
    management_fee integer,
    deposit integer,
    key_money integer,
    default_cleaning_fee integer,
    parking_spaces integer,
    parking_price_per_unit integer,
    initial_plus integer,
    contract_start_date date,
    contract_end_date date,
    landlord_name character varying(200),
    landlord_contact character varying(200),
    real_estate_agency character varying(200),
    emergency_contact character varying(200),
    status public.apartment_status,
    is_available boolean,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp without time zone
);


ALTER TABLE public.apartments OWNER TO uns_admin;

--
-- Name: apartments_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.apartments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.apartments_id_seq OWNER TO uns_admin;

--
-- Name: apartments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.apartments_id_seq OWNED BY public.apartments.id;


--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.audit_log (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    table_name character varying(50),
    record_id integer,
    old_values json,
    new_values json,
    ip_address character varying(50),
    user_agent text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.audit_log OWNER TO uns_admin;

--
-- Name: audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_log_id_seq OWNER TO uns_admin;

--
-- Name: audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.audit_log_id_seq OWNED BY public.audit_log.id;


--
-- Name: candidate_forms; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.candidate_forms (
    id integer NOT NULL,
    candidate_id integer,
    rirekisho_id character varying(20),
    applicant_id character varying(50),
    form_data json NOT NULL,
    photo_data_url text,
    azure_metadata json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.candidate_forms OWNER TO uns_admin;

--
-- Name: candidate_forms_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.candidate_forms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.candidate_forms_id_seq OWNER TO uns_admin;

--
-- Name: candidate_forms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.candidate_forms_id_seq OWNED BY public.candidate_forms.id;


--
-- Name: candidates; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.candidates (
    id integer NOT NULL,
    rirekisho_id character varying(20) NOT NULL,
    reception_date date,
    arrival_date date,
    full_name_kanji character varying(100),
    full_name_kana character varying(100),
    full_name_roman character varying(100),
    gender character varying(10),
    date_of_birth date,
    photo_url character varying(255),
    photo_data_url text,
    nationality character varying(50),
    marital_status character varying(20),
    hire_date date,
    postal_code character varying(10),
    current_address text,
    address text,
    address_banchi character varying(100),
    address_building character varying(100),
    registered_address text,
    phone character varying(20),
    mobile character varying(20),
    passport_number character varying(50),
    passport_expiry date,
    residence_status character varying(50),
    residence_expiry date,
    residence_card_number character varying(50),
    license_number character varying(50),
    license_expiry date,
    car_ownership character varying(10),
    voluntary_insurance character varying(10),
    forklift_license character varying(10),
    tama_kake character varying(10),
    mobile_crane_under_5t character varying(10),
    mobile_crane_over_5t character varying(10),
    gas_welding character varying(10),
    family_name_1 character varying(100),
    family_relation_1 character varying(50),
    family_age_1 integer,
    family_residence_1 character varying(50),
    family_separate_address_1 text,
    family_dependent_1 character varying(50),
    family_name_2 character varying(100),
    family_relation_2 character varying(50),
    family_age_2 integer,
    family_residence_2 character varying(50),
    family_separate_address_2 text,
    family_dependent_2 character varying(50),
    family_name_3 character varying(100),
    family_relation_3 character varying(50),
    family_age_3 integer,
    family_residence_3 character varying(50),
    family_separate_address_3 text,
    family_dependent_3 character varying(50),
    family_name_4 character varying(100),
    family_relation_4 character varying(50),
    family_age_4 integer,
    family_residence_4 character varying(50),
    family_separate_address_4 text,
    family_dependent_4 character varying(50),
    family_name_5 character varying(100),
    family_relation_5 character varying(50),
    family_age_5 integer,
    family_residence_5 character varying(50),
    family_separate_address_5 text,
    family_dependent_5 character varying(50),
    work_history_company_7 character varying(200),
    work_history_entry_company_7 character varying(200),
    work_history_exit_company_7 character varying(200),
    exp_nc_lathe boolean,
    exp_lathe boolean,
    exp_press boolean,
    exp_forklift boolean,
    exp_packing boolean,
    exp_welding boolean,
    exp_car_assembly boolean,
    exp_car_line boolean,
    exp_car_inspection boolean,
    exp_electronic_inspection boolean,
    exp_food_processing boolean,
    exp_casting boolean,
    exp_line_leader boolean,
    exp_painting boolean,
    exp_other text,
    bento_lunch_dinner character varying(10),
    bento_lunch_only character varying(10),
    bento_dinner_only character varying(10),
    bento_bring_own character varying(10),
    lunch_preference character varying(50),
    commute_method character varying(50),
    commute_time_oneway integer,
    interview_result character varying(20),
    antigen_test_kit character varying(20),
    antigen_test_date date,
    covid_vaccine_status character varying(50),
    language_skill_exists character varying(10),
    language_skill_1 character varying(100),
    language_skill_2 character varying(100),
    japanese_qualification character varying(50),
    japanese_level character varying(10),
    jlpt_taken character varying(10),
    jlpt_date date,
    jlpt_score integer,
    jlpt_scheduled character varying(30),
    qualification_1 character varying(100),
    qualification_2 character varying(100),
    qualification_3 character varying(100),
    major character varying(100),
    height double precision,
    weight double precision,
    clothing_size character varying(10),
    waist integer,
    shoe_size double precision,
    blood_type character varying(5),
    vision_right double precision,
    vision_left double precision,
    dominant_hand character varying(10),
    allergy_exists character varying(10),
    glasses character varying(100),
    listening_level character varying(20),
    speaking_level character varying(20),
    emergency_contact_name character varying(100),
    emergency_contact_relation character varying(50),
    emergency_contact_phone character varying(20),
    safety_shoes character varying(10),
    read_katakana character varying(20),
    read_hiragana character varying(20),
    read_kanji character varying(20),
    write_katakana character varying(20),
    write_hiragana character varying(20),
    write_kanji character varying(20),
    can_speak character varying(20),
    can_understand character varying(20),
    can_read_kana character varying(20),
    can_write_kana character varying(20),
    email character varying(100),
    ocr_notes text,
    status character varying(20) DEFAULT 'pending'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    approved_by integer,
    approved_at timestamp with time zone,
    deleted_at timestamp without time zone
);


ALTER TABLE public.candidates OWNER TO uns_admin;

--
-- Name: candidates_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.candidates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.candidates_id_seq OWNER TO uns_admin;

--
-- Name: candidates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.candidates_id_seq OWNED BY public.candidates.id;


--
-- Name: contract_workers; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.contract_workers (
    deleted_at timestamp without time zone,
    id integer NOT NULL,
    hakenmoto_id integer NOT NULL,
    rirekisho_id character varying(20),
    factory_id character varying(200),
    company_name character varying(100),
    plant_name character varying(100),
    hakensaki_shain_id character varying(50),
    full_name_kanji character varying(100) NOT NULL,
    full_name_kana character varying(100),
    photo_url character varying(255),
    photo_data_url text,
    date_of_birth date,
    gender character varying(10),
    nationality character varying(50),
    zairyu_card_number character varying(50),
    zairyu_expire_date date,
    address text,
    phone character varying(20),
    email character varying(100),
    emergency_contact_name character varying(100),
    emergency_contact_phone character varying(20),
    emergency_contact_relationship character varying(50),
    hire_date date,
    current_hire_date date,
    jikyu integer,
    jikyu_revision_date date,
    "position" character varying(100),
    contract_type character varying(50),
    assignment_location character varying(200),
    assignment_line character varying(200),
    job_description text,
    hourly_rate_charged integer,
    billing_revision_date date,
    profit_difference integer,
    standard_compensation integer,
    health_insurance integer,
    nursing_insurance integer,
    pension_insurance integer,
    social_insurance_date date,
    visa_type character varying(50),
    license_type character varying(100),
    license_expire_date date,
    commute_method character varying(50),
    optional_insurance_expire date,
    japanese_level character varying(50),
    career_up_5years boolean,
    entry_request_date date,
    notes text,
    postal_code character varying(10),
    apartment_id integer,
    apartment_start_date date,
    apartment_move_out_date date,
    apartment_rent integer,
    is_corporate_housing boolean NOT NULL,
    housing_subsidy integer,
    is_active boolean,
    termination_date date,
    termination_reason text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.contract_workers OWNER TO uns_admin;

--
-- Name: contract_workers_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.contract_workers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contract_workers_id_seq OWNER TO uns_admin;

--
-- Name: contract_workers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.contract_workers_id_seq OWNED BY public.contract_workers.id;


--
-- Name: contracts; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.contracts (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    contract_type character varying(50) NOT NULL,
    contract_number character varying(50),
    start_date date NOT NULL,
    end_date date,
    pdf_path character varying(500),
    signed boolean,
    signed_at timestamp with time zone,
    signature_data text,
    created_at timestamp with time zone DEFAULT now(),
    deleted_at timestamp without time zone
);


ALTER TABLE public.contracts OWNER TO uns_admin;

--
-- Name: contracts_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.contracts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contracts_id_seq OWNER TO uns_admin;

--
-- Name: contracts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.contracts_id_seq OWNED BY public.contracts.id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.departments OWNER TO uns_admin;

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.departments_id_seq OWNER TO uns_admin;

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: documents; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.documents (
    id integer NOT NULL,
    candidate_id integer,
    employee_id integer,
    document_type public.document_type NOT NULL,
    file_name character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_size integer,
    mime_type character varying(100),
    ocr_data json,
    uploaded_at timestamp with time zone DEFAULT now(),
    uploaded_by integer
);


ALTER TABLE public.documents OWNER TO uns_admin;

--
-- Name: documents_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.documents_id_seq OWNER TO uns_admin;

--
-- Name: documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.documents_id_seq OWNED BY public.documents.id;


--
-- Name: employee_payroll; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.employee_payroll (
    id integer NOT NULL,
    payroll_run_id integer NOT NULL,
    employee_id integer NOT NULL,
    pay_period_start date NOT NULL,
    pay_period_end date NOT NULL,
    regular_hours numeric(5,2),
    overtime_hours numeric(5,2),
    night_shift_hours numeric(5,2),
    holiday_hours numeric(5,2),
    sunday_hours numeric(5,2),
    base_rate numeric(10,2) NOT NULL,
    overtime_rate numeric(10,2) NOT NULL,
    night_shift_rate numeric(10,2) NOT NULL,
    holiday_rate numeric(10,2) NOT NULL,
    base_amount numeric(12,2),
    overtime_amount numeric(12,2),
    night_shift_amount numeric(12,2),
    holiday_amount numeric(12,2),
    gross_amount numeric(12,2),
    income_tax numeric(10,2),
    resident_tax numeric(10,2),
    health_insurance numeric(10,2),
    pension numeric(10,2),
    employment_insurance numeric(10,2),
    total_deductions numeric(12,2),
    net_amount numeric(12,2),
    yukyu_days_approved numeric(4,1),
    yukyu_deduction_jpy numeric(10,2),
    yukyu_request_ids text,
    timer_card_period_id integer,
    payslip_generated boolean,
    payslip_pdf_path character varying(255),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.employee_payroll OWNER TO uns_admin;

--
-- Name: employee_payroll_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.employee_payroll_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employee_payroll_id_seq OWNER TO uns_admin;

--
-- Name: employee_payroll_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.employee_payroll_id_seq OWNED BY public.employee_payroll.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.employees (
    current_address character varying,
    address_banchi character varying,
    address_building character varying,
    workplace_id integer,
    current_region_id integer,
    current_factory_id integer,
    current_department_id integer,
    residence_type_id integer,
    residence_status_id integer,
    residence_address text,
    residence_monthly_cost integer,
    residence_start_date date,
    assigned_regionally_at timestamp with time zone,
    visa_renewal_alert boolean,
    visa_alert_days integer,
    yukyu_total integer,
    yukyu_used integer,
    yukyu_remaining integer,
    current_status character varying(20),
    deleted_at timestamp without time zone,
    id integer NOT NULL,
    hakenmoto_id integer NOT NULL,
    rirekisho_id character varying(20),
    factory_id character varying(200),
    company_name character varying(100),
    plant_name character varying(100),
    hakensaki_shain_id character varying(50),
    full_name_kanji character varying(100) NOT NULL,
    full_name_kana character varying(100),
    photo_url character varying(255),
    photo_data_url text,
    date_of_birth date,
    gender character varying(10),
    nationality character varying(50),
    zairyu_card_number character varying(50),
    zairyu_expire_date date,
    address text,
    phone character varying(20),
    email character varying(100),
    emergency_contact_name character varying(100),
    emergency_contact_phone character varying(20),
    emergency_contact_relationship character varying(50),
    hire_date date,
    current_hire_date date,
    jikyu integer,
    jikyu_revision_date date,
    "position" character varying(100),
    contract_type character varying(50),
    assignment_location character varying(200),
    assignment_line character varying(200),
    job_description text,
    hourly_rate_charged integer,
    billing_revision_date date,
    profit_difference integer,
    standard_compensation integer,
    health_insurance integer,
    nursing_insurance integer,
    pension_insurance integer,
    social_insurance_date date,
    visa_type character varying(50),
    license_type character varying(100),
    license_expire_date date,
    commute_method character varying(50),
    optional_insurance_expire date,
    japanese_level character varying(50),
    career_up_5years boolean,
    entry_request_date date,
    notes text,
    postal_code character varying(10),
    apartment_id integer,
    apartment_start_date date,
    apartment_move_out_date date,
    apartment_rent integer,
    is_corporate_housing boolean NOT NULL,
    housing_subsidy integer,
    is_active boolean,
    termination_date date,
    termination_reason text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.employees OWNER TO uns_admin;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employees_id_seq OWNER TO uns_admin;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: factories; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.factories (
    id integer NOT NULL,
    factory_id character varying(200) NOT NULL,
    company_name character varying(100),
    plant_name character varying(100),
    name character varying(100) NOT NULL,
    address text,
    phone character varying(20),
    contact_person character varying(100),
    config json,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp without time zone
);


ALTER TABLE public.factories OWNER TO uns_admin;

--
-- Name: factories_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.factories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.factories_id_seq OWNER TO uns_admin;

--
-- Name: factories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.factories_id_seq OWNED BY public.factories.id;


--
-- Name: page_visibility; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.page_visibility (
    id integer NOT NULL,
    page_key character varying(100) NOT NULL,
    page_name character varying(100) NOT NULL,
    page_name_en character varying(100),
    is_enabled boolean NOT NULL,
    path character varying(255) NOT NULL,
    description text,
    disabled_message character varying(255),
    last_toggled_by integer,
    last_toggled_at timestamp with time zone,
    updated_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.page_visibility OWNER TO uns_admin;

--
-- Name: page_visibility_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.page_visibility_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.page_visibility_id_seq OWNER TO uns_admin;

--
-- Name: page_visibility_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.page_visibility_id_seq OWNED BY public.page_visibility.id;


--
-- Name: payroll_runs; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.payroll_runs (
    id integer NOT NULL,
    pay_period_start date NOT NULL,
    pay_period_end date NOT NULL,
    status character varying(20),
    total_employees integer,
    total_gross_amount numeric(15,2),
    total_deductions numeric(15,2),
    total_net_amount numeric(15,2),
    created_by character varying(255),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.payroll_runs OWNER TO uns_admin;

--
-- Name: payroll_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.payroll_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payroll_runs_id_seq OWNER TO uns_admin;

--
-- Name: payroll_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.payroll_runs_id_seq OWNED BY public.payroll_runs.id;


--
-- Name: payroll_settings; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.payroll_settings (
    id integer NOT NULL,
    company_id integer,
    overtime_rate numeric(4,2) NOT NULL,
    night_shift_rate numeric(4,2) NOT NULL,
    holiday_rate numeric(4,2) NOT NULL,
    sunday_rate numeric(4,2) NOT NULL,
    standard_hours_per_month numeric(5,2) NOT NULL,
    income_tax_rate numeric(5,2) NOT NULL,
    resident_tax_rate numeric(5,2) NOT NULL,
    health_insurance_rate numeric(5,2) NOT NULL,
    pension_rate numeric(5,2) NOT NULL,
    employment_insurance_rate numeric(5,2) NOT NULL,
    updated_by_id integer,
    updated_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.payroll_settings OWNER TO uns_admin;

--
-- Name: payroll_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.payroll_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.payroll_settings_id_seq OWNER TO uns_admin;

--
-- Name: payroll_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.payroll_settings_id_seq OWNED BY public.payroll_settings.id;


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    token character varying(500) NOT NULL,
    user_id integer NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    revoked boolean,
    revoked_at timestamp with time zone,
    user_agent character varying(500),
    ip_address character varying(45)
);


ALTER TABLE public.refresh_tokens OWNER TO uns_admin;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.refresh_tokens_id_seq OWNER TO uns_admin;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- Name: regions; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.regions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.regions OWNER TO uns_admin;

--
-- Name: regions_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.regions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.regions_id_seq OWNER TO uns_admin;

--
-- Name: regions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.regions_id_seq OWNED BY public.regions.id;


--
-- Name: rent_deductions; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.rent_deductions (
    id integer NOT NULL,
    assignment_id integer NOT NULL,
    employee_id integer NOT NULL,
    apartment_id integer NOT NULL,
    year integer NOT NULL,
    month integer NOT NULL,
    base_rent integer NOT NULL,
    additional_charges integer,
    total_deduction integer NOT NULL,
    status public.deduction_status NOT NULL,
    processed_date date,
    paid_date date,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp without time zone,
    CONSTRAINT check_month_range CHECK (((month >= 1) AND (month <= 12)))
);


ALTER TABLE public.rent_deductions OWNER TO uns_admin;

--
-- Name: rent_deductions_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.rent_deductions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rent_deductions_id_seq OWNER TO uns_admin;

--
-- Name: rent_deductions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.rent_deductions_id_seq OWNED BY public.rent_deductions.id;


--
-- Name: requests; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.requests (
    id integer NOT NULL,
    hakenmoto_id integer,
    candidate_id integer,
    request_type public.request_type NOT NULL,
    status public.request_status,
    start_date date NOT NULL,
    end_date date NOT NULL,
    reason text,
    notes text,
    employee_data jsonb,
    approved_by integer,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.requests OWNER TO uns_admin;

--
-- Name: requests_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.requests_id_seq OWNER TO uns_admin;

--
-- Name: requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.requests_id_seq OWNED BY public.requests.id;


--
-- Name: residence_statuses; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.residence_statuses (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(20),
    description text,
    max_duration_months integer,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.residence_statuses OWNER TO uns_admin;

--
-- Name: residence_statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.residence_statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.residence_statuses_id_seq OWNER TO uns_admin;

--
-- Name: residence_statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.residence_statuses_id_seq OWNED BY public.residence_statuses.id;


--
-- Name: residence_types; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.residence_types (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.residence_types OWNER TO uns_admin;

--
-- Name: residence_types_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.residence_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.residence_types_id_seq OWNER TO uns_admin;

--
-- Name: residence_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.residence_types_id_seq OWNED BY public.residence_types.id;


--
-- Name: role_page_permissions; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.role_page_permissions (
    id integer NOT NULL,
    role_key character varying(50) NOT NULL,
    page_key character varying(100) NOT NULL,
    is_enabled boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.role_page_permissions OWNER TO uns_admin;

--
-- Name: role_page_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.role_page_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.role_page_permissions_id_seq OWNER TO uns_admin;

--
-- Name: role_page_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.role_page_permissions_id_seq OWNED BY public.role_page_permissions.id;


--
-- Name: salary_calculations; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.salary_calculations (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    month integer NOT NULL,
    year integer NOT NULL,
    total_regular_hours numeric(5,2),
    total_overtime_hours numeric(5,2),
    total_night_hours numeric(5,2),
    total_holiday_hours numeric(5,2),
    base_salary integer,
    overtime_pay integer,
    night_pay integer,
    holiday_pay integer,
    bonus integer,
    gasoline_allowance integer,
    apartment_deduction integer,
    other_deductions integer,
    gross_salary integer,
    net_salary integer,
    factory_payment integer,
    company_profit integer,
    is_paid boolean,
    paid_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.salary_calculations OWNER TO uns_admin;

--
-- Name: salary_calculations_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.salary_calculations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.salary_calculations_id_seq OWNER TO uns_admin;

--
-- Name: salary_calculations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.salary_calculations_id_seq OWNED BY public.salary_calculations.id;


--
-- Name: social_insurance_rates; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.social_insurance_rates (
    id integer NOT NULL,
    min_compensation integer NOT NULL,
    max_compensation integer NOT NULL,
    standard_compensation integer NOT NULL,
    health_insurance_total integer,
    health_insurance_employee integer,
    health_insurance_employer integer,
    nursing_insurance_total integer,
    nursing_insurance_employee integer,
    nursing_insurance_employer integer,
    pension_insurance_total integer,
    pension_insurance_employee integer,
    pension_insurance_employer integer,
    effective_date date NOT NULL,
    prefecture character varying(20),
    notes text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.social_insurance_rates OWNER TO uns_admin;

--
-- Name: social_insurance_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.social_insurance_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.social_insurance_rates_id_seq OWNER TO uns_admin;

--
-- Name: social_insurance_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.social_insurance_rates_id_seq OWNED BY public.social_insurance_rates.id;


--
-- Name: staff; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.staff (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    rirekisho_id character varying(20),
    full_name_kanji character varying(100) NOT NULL,
    full_name_kana character varying(100),
    photo_url character varying(255),
    photo_data_url text,
    date_of_birth date,
    gender character varying(10),
    nationality character varying(50),
    address text,
    phone character varying(20),
    email character varying(100),
    emergency_contact_name character varying(100),
    emergency_contact_phone character varying(20),
    emergency_contact_relationship character varying(50),
    postal_code character varying(10),
    hire_date date,
    "position" character varying(100),
    department character varying(100),
    monthly_salary integer,
    health_insurance integer,
    nursing_insurance integer,
    pension_insurance integer,
    social_insurance_date date,
    yukyu_total integer,
    yukyu_used integer,
    is_corporate_housing boolean NOT NULL,
    housing_subsidy integer,
    yukyu_remaining integer,
    is_active boolean,
    termination_date date,
    termination_reason text,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    deleted_at timestamp without time zone
);


ALTER TABLE public.staff OWNER TO uns_admin;

--
-- Name: staff_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.staff_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.staff_id_seq OWNER TO uns_admin;

--
-- Name: staff_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.staff_id_seq OWNED BY public.staff.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.system_settings (
    id integer NOT NULL,
    key character varying(100) NOT NULL,
    value character varying(255),
    description text,
    updated_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.system_settings OWNER TO uns_admin;

--
-- Name: system_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.system_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_settings_id_seq OWNER TO uns_admin;

--
-- Name: system_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.system_settings_id_seq OWNED BY public.system_settings.id;


--
-- Name: timer_cards; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.timer_cards (
    id integer NOT NULL,
    hakenmoto_id integer,
    factory_id character varying(20),
    work_date date NOT NULL,
    shift_type public.shift_type,
    clock_in time without time zone,
    clock_out time without time zone,
    break_minutes integer,
    overtime_minutes integer,
    regular_hours numeric(5,2),
    overtime_hours numeric(5,2),
    night_hours numeric(5,2),
    holiday_hours numeric(5,2),
    notes text,
    is_approved boolean,
    approved_by integer,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.timer_cards OWNER TO uns_admin;

--
-- Name: timer_cards_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.timer_cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.timer_cards_id_seq OWNER TO uns_admin;

--
-- Name: timer_cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.timer_cards_id_seq OWNED BY public.timer_cards.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role public.user_role NOT NULL,
    full_name character varying(100),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO uns_admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO uns_admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: workplaces; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.workplaces (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    workplace_type character varying(50),
    company_name character varying(100),
    location_name character varying(100),
    region_id integer,
    address text,
    description text,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.workplaces OWNER TO uns_admin;

--
-- Name: workplaces_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.workplaces_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workplaces_id_seq OWNER TO uns_admin;

--
-- Name: workplaces_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.workplaces_id_seq OWNED BY public.workplaces.id;


--
-- Name: yukyu_balances; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.yukyu_balances (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    fiscal_year integer NOT NULL,
    assigned_date date NOT NULL,
    months_worked integer NOT NULL,
    days_assigned integer NOT NULL,
    days_carried_over integer NOT NULL,
    days_total integer NOT NULL,
    days_used integer NOT NULL,
    days_remaining integer NOT NULL,
    days_expired integer NOT NULL,
    days_available integer NOT NULL,
    expires_on date NOT NULL,
    status public.yukyu_status NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    notes text
);


ALTER TABLE public.yukyu_balances OWNER TO uns_admin;

--
-- Name: yukyu_balances_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.yukyu_balances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.yukyu_balances_id_seq OWNER TO uns_admin;

--
-- Name: yukyu_balances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.yukyu_balances_id_seq OWNED BY public.yukyu_balances.id;


--
-- Name: yukyu_requests; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.yukyu_requests (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    requested_by_user_id integer NOT NULL,
    factory_id integer,
    request_type public.request_type NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    days_requested numeric(4,1) NOT NULL,
    yukyu_available_at_request integer NOT NULL,
    request_date timestamp with time zone DEFAULT now() NOT NULL,
    status public.request_status NOT NULL,
    approved_by_user_id integer,
    approval_date timestamp with time zone,
    rejection_reason text,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.yukyu_requests OWNER TO uns_admin;

--
-- Name: yukyu_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.yukyu_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.yukyu_requests_id_seq OWNER TO uns_admin;

--
-- Name: yukyu_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.yukyu_requests_id_seq OWNED BY public.yukyu_requests.id;


--
-- Name: yukyu_usage_details; Type: TABLE; Schema: public; Owner: uns_admin
--

CREATE TABLE public.yukyu_usage_details (
    id integer NOT NULL,
    request_id integer NOT NULL,
    balance_id integer NOT NULL,
    usage_date date NOT NULL,
    days_deducted numeric(3,1) NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.yukyu_usage_details OWNER TO uns_admin;

--
-- Name: yukyu_usage_details_id_seq; Type: SEQUENCE; Schema: public; Owner: uns_admin
--

CREATE SEQUENCE public.yukyu_usage_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.yukyu_usage_details_id_seq OWNER TO uns_admin;

--
-- Name: yukyu_usage_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: uns_admin
--

ALTER SEQUENCE public.yukyu_usage_details_id_seq OWNED BY public.yukyu_usage_details.id;


--
-- Name: additional_charges id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.additional_charges ALTER COLUMN id SET DEFAULT nextval('public.additional_charges_id_seq'::regclass);


--
-- Name: admin_audit_logs id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.admin_audit_logs ALTER COLUMN id SET DEFAULT nextval('public.admin_audit_logs_id_seq'::regclass);


--
-- Name: apartment_assignments id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_assignments ALTER COLUMN id SET DEFAULT nextval('public.apartment_assignments_id_seq'::regclass);


--
-- Name: apartment_factory id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_factory ALTER COLUMN id SET DEFAULT nextval('public.apartment_factory_id_seq'::regclass);


--
-- Name: apartments id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartments ALTER COLUMN id SET DEFAULT nextval('public.apartments_id_seq'::regclass);


--
-- Name: audit_log id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.audit_log ALTER COLUMN id SET DEFAULT nextval('public.audit_log_id_seq'::regclass);


--
-- Name: candidate_forms id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.candidate_forms ALTER COLUMN id SET DEFAULT nextval('public.candidate_forms_id_seq'::regclass);


--
-- Name: candidates id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.candidates ALTER COLUMN id SET DEFAULT nextval('public.candidates_id_seq'::regclass);


--
-- Name: contract_workers id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contract_workers ALTER COLUMN id SET DEFAULT nextval('public.contract_workers_id_seq'::regclass);


--
-- Name: contracts id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contracts ALTER COLUMN id SET DEFAULT nextval('public.contracts_id_seq'::regclass);


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: documents id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.documents ALTER COLUMN id SET DEFAULT nextval('public.documents_id_seq'::regclass);


--
-- Name: employee_payroll id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employee_payroll ALTER COLUMN id SET DEFAULT nextval('public.employee_payroll_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: factories id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.factories ALTER COLUMN id SET DEFAULT nextval('public.factories_id_seq'::regclass);


--
-- Name: page_visibility id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.page_visibility ALTER COLUMN id SET DEFAULT nextval('public.page_visibility_id_seq'::regclass);


--
-- Name: payroll_runs id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.payroll_runs ALTER COLUMN id SET DEFAULT nextval('public.payroll_runs_id_seq'::regclass);


--
-- Name: payroll_settings id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.payroll_settings ALTER COLUMN id SET DEFAULT nextval('public.payroll_settings_id_seq'::regclass);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- Name: regions id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.regions ALTER COLUMN id SET DEFAULT nextval('public.regions_id_seq'::regclass);


--
-- Name: rent_deductions id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.rent_deductions ALTER COLUMN id SET DEFAULT nextval('public.rent_deductions_id_seq'::regclass);


--
-- Name: requests id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.requests ALTER COLUMN id SET DEFAULT nextval('public.requests_id_seq'::regclass);


--
-- Name: residence_statuses id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.residence_statuses ALTER COLUMN id SET DEFAULT nextval('public.residence_statuses_id_seq'::regclass);


--
-- Name: residence_types id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.residence_types ALTER COLUMN id SET DEFAULT nextval('public.residence_types_id_seq'::regclass);


--
-- Name: role_page_permissions id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.role_page_permissions ALTER COLUMN id SET DEFAULT nextval('public.role_page_permissions_id_seq'::regclass);


--
-- Name: salary_calculations id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.salary_calculations ALTER COLUMN id SET DEFAULT nextval('public.salary_calculations_id_seq'::regclass);


--
-- Name: social_insurance_rates id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.social_insurance_rates ALTER COLUMN id SET DEFAULT nextval('public.social_insurance_rates_id_seq'::regclass);


--
-- Name: staff id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.staff ALTER COLUMN id SET DEFAULT nextval('public.staff_id_seq'::regclass);


--
-- Name: system_settings id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.system_settings ALTER COLUMN id SET DEFAULT nextval('public.system_settings_id_seq'::regclass);


--
-- Name: timer_cards id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.timer_cards ALTER COLUMN id SET DEFAULT nextval('public.timer_cards_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: workplaces id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.workplaces ALTER COLUMN id SET DEFAULT nextval('public.workplaces_id_seq'::regclass);


--
-- Name: yukyu_balances id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_balances ALTER COLUMN id SET DEFAULT nextval('public.yukyu_balances_id_seq'::regclass);


--
-- Name: yukyu_requests id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_requests ALTER COLUMN id SET DEFAULT nextval('public.yukyu_requests_id_seq'::regclass);


--
-- Name: yukyu_usage_details id; Type: DEFAULT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_usage_details ALTER COLUMN id SET DEFAULT nextval('public.yukyu_usage_details_id_seq'::regclass);


--
-- Name: additional_charges additional_charges_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.additional_charges
    ADD CONSTRAINT additional_charges_pkey PRIMARY KEY (id);


--
-- Name: admin_audit_logs admin_audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: apartment_assignments apartment_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_assignments
    ADD CONSTRAINT apartment_assignments_pkey PRIMARY KEY (id);


--
-- Name: apartment_factory apartment_factory_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_factory
    ADD CONSTRAINT apartment_factory_pkey PRIMARY KEY (id);


--
-- Name: apartments apartments_apartment_code_key; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartments
    ADD CONSTRAINT apartments_apartment_code_key UNIQUE (apartment_code);


--
-- Name: apartments apartments_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartments
    ADD CONSTRAINT apartments_pkey PRIMARY KEY (id);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: candidate_forms candidate_forms_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.candidate_forms
    ADD CONSTRAINT candidate_forms_pkey PRIMARY KEY (id);


--
-- Name: candidates candidates_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT candidates_pkey PRIMARY KEY (id);


--
-- Name: contract_workers contract_workers_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contract_workers
    ADD CONSTRAINT contract_workers_pkey PRIMARY KEY (id);


--
-- Name: contracts contracts_contract_number_key; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_contract_number_key UNIQUE (contract_number);


--
-- Name: contracts contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pkey PRIMARY KEY (id);


--
-- Name: departments departments_name_key; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_name_key UNIQUE (name);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: employee_payroll employee_payroll_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employee_payroll
    ADD CONSTRAINT employee_payroll_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: factories factories_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.factories
    ADD CONSTRAINT factories_pkey PRIMARY KEY (id);


--
-- Name: page_visibility page_visibility_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.page_visibility
    ADD CONSTRAINT page_visibility_pkey PRIMARY KEY (id);


--
-- Name: payroll_runs payroll_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.payroll_runs
    ADD CONSTRAINT payroll_runs_pkey PRIMARY KEY (id);


--
-- Name: payroll_settings payroll_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.payroll_settings
    ADD CONSTRAINT payroll_settings_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: regions regions_name_key; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_name_key UNIQUE (name);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (id);


--
-- Name: rent_deductions rent_deductions_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.rent_deductions
    ADD CONSTRAINT rent_deductions_pkey PRIMARY KEY (id);


--
-- Name: requests requests_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_pkey PRIMARY KEY (id);


--
-- Name: residence_statuses residence_statuses_code_key; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.residence_statuses
    ADD CONSTRAINT residence_statuses_code_key UNIQUE (code);


--
-- Name: residence_statuses residence_statuses_name_key; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.residence_statuses
    ADD CONSTRAINT residence_statuses_name_key UNIQUE (name);


--
-- Name: residence_statuses residence_statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.residence_statuses
    ADD CONSTRAINT residence_statuses_pkey PRIMARY KEY (id);


--
-- Name: residence_types residence_types_name_key; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.residence_types
    ADD CONSTRAINT residence_types_name_key UNIQUE (name);


--
-- Name: residence_types residence_types_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.residence_types
    ADD CONSTRAINT residence_types_pkey PRIMARY KEY (id);


--
-- Name: role_page_permissions role_page_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.role_page_permissions
    ADD CONSTRAINT role_page_permissions_pkey PRIMARY KEY (id);


--
-- Name: salary_calculations salary_calculations_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.salary_calculations
    ADD CONSTRAINT salary_calculations_pkey PRIMARY KEY (id);


--
-- Name: social_insurance_rates social_insurance_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.social_insurance_rates
    ADD CONSTRAINT social_insurance_rates_pkey PRIMARY KEY (id);


--
-- Name: staff staff_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (id);


--
-- Name: timer_cards timer_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.timer_cards
    ADD CONSTRAINT timer_cards_pkey PRIMARY KEY (id);


--
-- Name: rent_deductions uq_assignment_year_month; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.rent_deductions
    ADD CONSTRAINT uq_assignment_year_month UNIQUE (assignment_id, year, month);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: workplaces workplaces_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.workplaces
    ADD CONSTRAINT workplaces_pkey PRIMARY KEY (id);


--
-- Name: yukyu_balances yukyu_balances_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_balances
    ADD CONSTRAINT yukyu_balances_pkey PRIMARY KEY (id);


--
-- Name: yukyu_requests yukyu_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_requests
    ADD CONSTRAINT yukyu_requests_pkey PRIMARY KEY (id);


--
-- Name: yukyu_usage_details yukyu_usage_details_pkey; Type: CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_usage_details
    ADD CONSTRAINT yukyu_usage_details_pkey PRIMARY KEY (id);


--
-- Name: idx_candidate_date_of_birth; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_date_of_birth ON public.candidates USING btree (date_of_birth);


--
-- Name: idx_candidate_email; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_email ON public.candidates USING btree (email);


--
-- Name: idx_candidate_name_birthdate; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_name_birthdate ON public.candidates USING btree (full_name_kanji, date_of_birth);


--
-- Name: idx_candidate_name_kana_trgm; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_name_kana_trgm ON public.candidates USING gin (full_name_kana public.gin_trgm_ops);


--
-- Name: idx_candidate_name_kanji_trgm; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_name_kanji_trgm ON public.candidates USING gin (full_name_kanji public.gin_trgm_ops);


--
-- Name: idx_candidate_name_roman_trgm; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_name_roman_trgm ON public.candidates USING gin (full_name_roman public.gin_trgm_ops);


--
-- Name: idx_candidate_rirekisho_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_rirekisho_id ON public.candidates USING btree (rirekisho_id);


--
-- Name: idx_candidate_status_active; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_candidate_status_active ON public.candidates USING btree (status) WHERE (deleted_at IS NULL);


--
-- Name: idx_employee_factory_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_employee_factory_id ON public.employees USING btree (factory_id);


--
-- Name: idx_employee_hakenmoto_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX idx_employee_hakenmoto_id ON public.employees USING btree (hakenmoto_id);


--
-- Name: idx_employee_name_kanji_trgm; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_employee_name_kanji_trgm ON public.employees USING gin (full_name_kanji public.gin_trgm_ops);


--
-- Name: idx_employee_rirekisho_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX idx_employee_rirekisho_id ON public.employees USING btree (rirekisho_id);


--
-- Name: ix_additional_charges_apartment_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_additional_charges_apartment_id ON public.additional_charges USING btree (apartment_id);


--
-- Name: ix_additional_charges_assignment_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_additional_charges_assignment_id ON public.additional_charges USING btree (assignment_id);


--
-- Name: ix_additional_charges_charge_date; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_additional_charges_charge_date ON public.additional_charges USING btree (charge_date);


--
-- Name: ix_additional_charges_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_additional_charges_deleted_at ON public.additional_charges USING btree (deleted_at);


--
-- Name: ix_additional_charges_employee_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_additional_charges_employee_id ON public.additional_charges USING btree (employee_id);


--
-- Name: ix_additional_charges_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_additional_charges_id ON public.additional_charges USING btree (id);


--
-- Name: ix_admin_audit_logs_action_type; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_admin_audit_logs_action_type ON public.admin_audit_logs USING btree (action_type);


--
-- Name: ix_admin_audit_logs_admin_user_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_admin_audit_logs_admin_user_id ON public.admin_audit_logs USING btree (admin_user_id);


--
-- Name: ix_admin_audit_logs_created_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_admin_audit_logs_created_at ON public.admin_audit_logs USING btree (created_at);


--
-- Name: ix_admin_audit_logs_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_admin_audit_logs_id ON public.admin_audit_logs USING btree (id);


--
-- Name: ix_admin_audit_logs_resource_key; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_admin_audit_logs_resource_key ON public.admin_audit_logs USING btree (resource_key);


--
-- Name: ix_admin_audit_logs_resource_type; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_admin_audit_logs_resource_type ON public.admin_audit_logs USING btree (resource_type);


--
-- Name: ix_apartment_assignments_apartment_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_assignments_apartment_id ON public.apartment_assignments USING btree (apartment_id);


--
-- Name: ix_apartment_assignments_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_assignments_deleted_at ON public.apartment_assignments USING btree (deleted_at);


--
-- Name: ix_apartment_assignments_employee_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_assignments_employee_id ON public.apartment_assignments USING btree (employee_id);


--
-- Name: ix_apartment_assignments_end_date; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_assignments_end_date ON public.apartment_assignments USING btree (end_date);


--
-- Name: ix_apartment_assignments_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_assignments_id ON public.apartment_assignments USING btree (id);


--
-- Name: ix_apartment_assignments_start_date; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_assignments_start_date ON public.apartment_assignments USING btree (start_date);


--
-- Name: ix_apartment_factory_apartment_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_factory_apartment_id ON public.apartment_factory USING btree (apartment_id);


--
-- Name: ix_apartment_factory_factory_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_factory_factory_id ON public.apartment_factory USING btree (factory_id);


--
-- Name: ix_apartment_factory_is_primary; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartment_factory_is_primary ON public.apartment_factory USING btree (is_primary);


--
-- Name: ix_apartments_city; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartments_city ON public.apartments USING btree (city);


--
-- Name: ix_apartments_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartments_deleted_at ON public.apartments USING btree (deleted_at);


--
-- Name: ix_apartments_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartments_id ON public.apartments USING btree (id);


--
-- Name: ix_apartments_name; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartments_name ON public.apartments USING btree (name);


--
-- Name: ix_apartments_prefecture; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartments_prefecture ON public.apartments USING btree (prefecture);


--
-- Name: ix_apartments_region_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartments_region_id ON public.apartments USING btree (region_id);


--
-- Name: ix_apartments_zone; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_apartments_zone ON public.apartments USING btree (zone);


--
-- Name: ix_audit_log_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_audit_log_id ON public.audit_log USING btree (id);


--
-- Name: ix_candidate_forms_applicant_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_candidate_forms_applicant_id ON public.candidate_forms USING btree (applicant_id);


--
-- Name: ix_candidate_forms_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_candidate_forms_id ON public.candidate_forms USING btree (id);


--
-- Name: ix_candidate_forms_rirekisho_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_candidate_forms_rirekisho_id ON public.candidate_forms USING btree (rirekisho_id);


--
-- Name: ix_candidates_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_candidates_deleted_at ON public.candidates USING btree (deleted_at);


--
-- Name: ix_candidates_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_candidates_id ON public.candidates USING btree (id);


--
-- Name: ix_candidates_rirekisho_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_candidates_rirekisho_id ON public.candidates USING btree (rirekisho_id);


--
-- Name: ix_contract_workers_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_contract_workers_deleted_at ON public.contract_workers USING btree (deleted_at);


--
-- Name: ix_contract_workers_hakenmoto_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_contract_workers_hakenmoto_id ON public.contract_workers USING btree (hakenmoto_id);


--
-- Name: ix_contract_workers_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_contract_workers_id ON public.contract_workers USING btree (id);


--
-- Name: ix_contracts_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_contracts_deleted_at ON public.contracts USING btree (deleted_at);


--
-- Name: ix_contracts_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_contracts_id ON public.contracts USING btree (id);


--
-- Name: ix_departments_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_departments_id ON public.departments USING btree (id);


--
-- Name: ix_documents_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_documents_id ON public.documents USING btree (id);


--
-- Name: ix_employee_payroll_employee_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_employee_payroll_employee_id ON public.employee_payroll USING btree (employee_id);


--
-- Name: ix_employee_payroll_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_employee_payroll_id ON public.employee_payroll USING btree (id);


--
-- Name: ix_employee_payroll_payroll_run_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_employee_payroll_payroll_run_id ON public.employee_payroll USING btree (payroll_run_id);


--
-- Name: ix_employees_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_employees_deleted_at ON public.employees USING btree (deleted_at);


--
-- Name: ix_employees_hakenmoto_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_employees_hakenmoto_id ON public.employees USING btree (hakenmoto_id);


--
-- Name: ix_employees_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_employees_id ON public.employees USING btree (id);


--
-- Name: ix_factories_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_factories_deleted_at ON public.factories USING btree (deleted_at);


--
-- Name: ix_factories_factory_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_factories_factory_id ON public.factories USING btree (factory_id);


--
-- Name: ix_factories_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_factories_id ON public.factories USING btree (id);


--
-- Name: ix_page_visibility_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_page_visibility_id ON public.page_visibility USING btree (id);


--
-- Name: ix_page_visibility_page_key; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_page_visibility_page_key ON public.page_visibility USING btree (page_key);


--
-- Name: ix_payroll_runs_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_payroll_runs_id ON public.payroll_runs USING btree (id);


--
-- Name: ix_payroll_runs_pay_period_end; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_payroll_runs_pay_period_end ON public.payroll_runs USING btree (pay_period_end);


--
-- Name: ix_payroll_runs_pay_period_start; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_payroll_runs_pay_period_start ON public.payroll_runs USING btree (pay_period_start);


--
-- Name: ix_payroll_runs_status; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_payroll_runs_status ON public.payroll_runs USING btree (status);


--
-- Name: ix_payroll_settings_company_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_payroll_settings_company_id ON public.payroll_settings USING btree (company_id);


--
-- Name: ix_payroll_settings_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_payroll_settings_id ON public.payroll_settings USING btree (id);


--
-- Name: ix_refresh_tokens_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_refresh_tokens_id ON public.refresh_tokens USING btree (id);


--
-- Name: ix_refresh_tokens_token; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_refresh_tokens_token ON public.refresh_tokens USING btree (token);


--
-- Name: ix_regions_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_regions_id ON public.regions USING btree (id);


--
-- Name: ix_rent_deductions_apartment_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_rent_deductions_apartment_id ON public.rent_deductions USING btree (apartment_id);


--
-- Name: ix_rent_deductions_assignment_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_rent_deductions_assignment_id ON public.rent_deductions USING btree (assignment_id);


--
-- Name: ix_rent_deductions_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_rent_deductions_deleted_at ON public.rent_deductions USING btree (deleted_at);


--
-- Name: ix_rent_deductions_employee_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_rent_deductions_employee_id ON public.rent_deductions USING btree (employee_id);


--
-- Name: ix_rent_deductions_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_rent_deductions_id ON public.rent_deductions USING btree (id);


--
-- Name: ix_rent_deductions_month; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_rent_deductions_month ON public.rent_deductions USING btree (month);


--
-- Name: ix_rent_deductions_year; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_rent_deductions_year ON public.rent_deductions USING btree (year);


--
-- Name: ix_requests_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_requests_id ON public.requests USING btree (id);


--
-- Name: ix_residence_statuses_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_residence_statuses_id ON public.residence_statuses USING btree (id);


--
-- Name: ix_residence_types_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_residence_types_id ON public.residence_types USING btree (id);


--
-- Name: ix_role_page_permissions_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_role_page_permissions_id ON public.role_page_permissions USING btree (id);


--
-- Name: ix_role_page_permissions_page_key; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_role_page_permissions_page_key ON public.role_page_permissions USING btree (page_key);


--
-- Name: ix_role_page_permissions_role_key; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_role_page_permissions_role_key ON public.role_page_permissions USING btree (role_key);


--
-- Name: ix_salary_calculations_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_salary_calculations_id ON public.salary_calculations USING btree (id);


--
-- Name: ix_social_insurance_rates_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_social_insurance_rates_id ON public.social_insurance_rates USING btree (id);


--
-- Name: ix_staff_deleted_at; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_staff_deleted_at ON public.staff USING btree (deleted_at);


--
-- Name: ix_staff_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_staff_id ON public.staff USING btree (id);


--
-- Name: ix_staff_staff_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_staff_staff_id ON public.staff USING btree (staff_id);


--
-- Name: ix_system_settings_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_system_settings_id ON public.system_settings USING btree (id);


--
-- Name: ix_system_settings_key; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_system_settings_key ON public.system_settings USING btree (key);


--
-- Name: ix_timer_cards_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_timer_cards_id ON public.timer_cards USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_workplaces_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_workplaces_id ON public.workplaces USING btree (id);


--
-- Name: ix_workplaces_name; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE UNIQUE INDEX ix_workplaces_name ON public.workplaces USING btree (name);


--
-- Name: ix_yukyu_balances_employee_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_balances_employee_id ON public.yukyu_balances USING btree (employee_id);


--
-- Name: ix_yukyu_balances_fiscal_year; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_balances_fiscal_year ON public.yukyu_balances USING btree (fiscal_year);


--
-- Name: ix_yukyu_balances_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_balances_id ON public.yukyu_balances USING btree (id);


--
-- Name: ix_yukyu_requests_employee_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_requests_employee_id ON public.yukyu_requests USING btree (employee_id);


--
-- Name: ix_yukyu_requests_factory_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_requests_factory_id ON public.yukyu_requests USING btree (factory_id);


--
-- Name: ix_yukyu_requests_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_requests_id ON public.yukyu_requests USING btree (id);


--
-- Name: ix_yukyu_requests_status; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_requests_status ON public.yukyu_requests USING btree (status);


--
-- Name: ix_yukyu_usage_details_balance_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_usage_details_balance_id ON public.yukyu_usage_details USING btree (balance_id);


--
-- Name: ix_yukyu_usage_details_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_usage_details_id ON public.yukyu_usage_details USING btree (id);


--
-- Name: ix_yukyu_usage_details_request_id; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_usage_details_request_id ON public.yukyu_usage_details USING btree (request_id);


--
-- Name: ix_yukyu_usage_details_usage_date; Type: INDEX; Schema: public; Owner: uns_admin
--

CREATE INDEX ix_yukyu_usage_details_usage_date ON public.yukyu_usage_details USING btree (usage_date);


--
-- Name: additional_charges additional_charges_apartment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.additional_charges
    ADD CONSTRAINT additional_charges_apartment_id_fkey FOREIGN KEY (apartment_id) REFERENCES public.apartments(id);


--
-- Name: additional_charges additional_charges_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.additional_charges
    ADD CONSTRAINT additional_charges_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: additional_charges additional_charges_assignment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.additional_charges
    ADD CONSTRAINT additional_charges_assignment_id_fkey FOREIGN KEY (assignment_id) REFERENCES public.apartment_assignments(id) ON DELETE CASCADE;


--
-- Name: additional_charges additional_charges_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.additional_charges
    ADD CONSTRAINT additional_charges_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: admin_audit_logs admin_audit_logs_admin_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.admin_audit_logs
    ADD CONSTRAINT admin_audit_logs_admin_user_id_fkey FOREIGN KEY (admin_user_id) REFERENCES public.users(id);


--
-- Name: apartment_assignments apartment_assignments_apartment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_assignments
    ADD CONSTRAINT apartment_assignments_apartment_id_fkey FOREIGN KEY (apartment_id) REFERENCES public.apartments(id) ON DELETE CASCADE;


--
-- Name: apartment_assignments apartment_assignments_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_assignments
    ADD CONSTRAINT apartment_assignments_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: apartment_factory apartment_factory_apartment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_factory
    ADD CONSTRAINT apartment_factory_apartment_id_fkey FOREIGN KEY (apartment_id) REFERENCES public.apartments(id) ON DELETE CASCADE;


--
-- Name: apartment_factory apartment_factory_factory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartment_factory
    ADD CONSTRAINT apartment_factory_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES public.factories(id) ON DELETE CASCADE;


--
-- Name: apartments apartments_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.apartments
    ADD CONSTRAINT apartments_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: audit_log audit_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: candidate_forms candidate_forms_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.candidate_forms
    ADD CONSTRAINT candidate_forms_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id) ON DELETE SET NULL;


--
-- Name: candidates candidates_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT candidates_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: contract_workers contract_workers_apartment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contract_workers
    ADD CONSTRAINT contract_workers_apartment_id_fkey FOREIGN KEY (apartment_id) REFERENCES public.apartments(id);


--
-- Name: contract_workers contract_workers_factory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contract_workers
    ADD CONSTRAINT contract_workers_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- Name: contract_workers contract_workers_rirekisho_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contract_workers
    ADD CONSTRAINT contract_workers_rirekisho_id_fkey FOREIGN KEY (rirekisho_id) REFERENCES public.candidates(rirekisho_id);


--
-- Name: contracts contracts_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: documents documents_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id) ON DELETE CASCADE;


--
-- Name: documents documents_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: documents documents_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: employee_payroll employee_payroll_payroll_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employee_payroll
    ADD CONSTRAINT employee_payroll_payroll_run_id_fkey FOREIGN KEY (payroll_run_id) REFERENCES public.payroll_runs(id);


--
-- Name: employees employees_apartment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_apartment_id_fkey FOREIGN KEY (apartment_id) REFERENCES public.apartments(id);


--
-- Name: employees employees_current_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_current_department_id_fkey FOREIGN KEY (current_department_id) REFERENCES public.departments(id);


--
-- Name: employees employees_current_factory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_current_factory_id_fkey FOREIGN KEY (current_factory_id) REFERENCES public.factories(id);


--
-- Name: employees employees_current_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_current_region_id_fkey FOREIGN KEY (current_region_id) REFERENCES public.regions(id);


--
-- Name: employees employees_factory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES public.factories(factory_id);


--
-- Name: employees employees_residence_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_residence_status_id_fkey FOREIGN KEY (residence_status_id) REFERENCES public.residence_statuses(id);


--
-- Name: employees employees_residence_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_residence_type_id_fkey FOREIGN KEY (residence_type_id) REFERENCES public.residence_types(id);


--
-- Name: employees employees_rirekisho_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_rirekisho_id_fkey FOREIGN KEY (rirekisho_id) REFERENCES public.candidates(rirekisho_id);


--
-- Name: employees employees_workplace_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_workplace_id_fkey FOREIGN KEY (workplace_id) REFERENCES public.workplaces(id);


--
-- Name: page_visibility page_visibility_last_toggled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.page_visibility
    ADD CONSTRAINT page_visibility_last_toggled_by_fkey FOREIGN KEY (last_toggled_by) REFERENCES public.users(id);


--
-- Name: payroll_settings payroll_settings_updated_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.payroll_settings
    ADD CONSTRAINT payroll_settings_updated_by_id_fkey FOREIGN KEY (updated_by_id) REFERENCES public.users(id);


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: rent_deductions rent_deductions_apartment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.rent_deductions
    ADD CONSTRAINT rent_deductions_apartment_id_fkey FOREIGN KEY (apartment_id) REFERENCES public.apartments(id);


--
-- Name: rent_deductions rent_deductions_assignment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.rent_deductions
    ADD CONSTRAINT rent_deductions_assignment_id_fkey FOREIGN KEY (assignment_id) REFERENCES public.apartment_assignments(id) ON DELETE CASCADE;


--
-- Name: rent_deductions rent_deductions_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.rent_deductions
    ADD CONSTRAINT rent_deductions_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: requests requests_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: requests requests_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id) ON DELETE SET NULL;


--
-- Name: requests requests_hakenmoto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.requests
    ADD CONSTRAINT requests_hakenmoto_id_fkey FOREIGN KEY (hakenmoto_id) REFERENCES public.employees(hakenmoto_id) ON DELETE CASCADE;


--
-- Name: salary_calculations salary_calculations_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.salary_calculations
    ADD CONSTRAINT salary_calculations_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: staff staff_rirekisho_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.staff
    ADD CONSTRAINT staff_rirekisho_id_fkey FOREIGN KEY (rirekisho_id) REFERENCES public.candidates(rirekisho_id);


--
-- Name: timer_cards timer_cards_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.timer_cards
    ADD CONSTRAINT timer_cards_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: timer_cards timer_cards_hakenmoto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.timer_cards
    ADD CONSTRAINT timer_cards_hakenmoto_id_fkey FOREIGN KEY (hakenmoto_id) REFERENCES public.employees(hakenmoto_id) ON DELETE CASCADE;


--
-- Name: workplaces workplaces_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.workplaces
    ADD CONSTRAINT workplaces_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: yukyu_balances yukyu_balances_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_balances
    ADD CONSTRAINT yukyu_balances_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: yukyu_requests yukyu_requests_approved_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_requests
    ADD CONSTRAINT yukyu_requests_approved_by_user_id_fkey FOREIGN KEY (approved_by_user_id) REFERENCES public.users(id);


--
-- Name: yukyu_requests yukyu_requests_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_requests
    ADD CONSTRAINT yukyu_requests_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: yukyu_requests yukyu_requests_factory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_requests
    ADD CONSTRAINT yukyu_requests_factory_id_fkey FOREIGN KEY (factory_id) REFERENCES public.factories(id);


--
-- Name: yukyu_requests yukyu_requests_requested_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_requests
    ADD CONSTRAINT yukyu_requests_requested_by_user_id_fkey FOREIGN KEY (requested_by_user_id) REFERENCES public.users(id);


--
-- Name: yukyu_usage_details yukyu_usage_details_balance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_usage_details
    ADD CONSTRAINT yukyu_usage_details_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES public.yukyu_balances(id) ON DELETE CASCADE;


--
-- Name: yukyu_usage_details yukyu_usage_details_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: uns_admin
--

ALTER TABLE ONLY public.yukyu_usage_details
    ADD CONSTRAINT yukyu_usage_details_request_id_fkey FOREIGN KEY (request_id) REFERENCES public.yukyu_requests(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict cMFtzOLtAh0fQPxGehhJYdhr17sdctvpYQNxoSvjVJ1zPTnwvtv4AHkVLfoLmHT

