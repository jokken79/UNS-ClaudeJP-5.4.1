// ============================================================================
// API Type Definitions
// ============================================================================
// Este archivo contiene todas las definiciones de tipos TypeScript para
// las respuestas de la API del backend.
//
// IMPORTANTE: Mantener sincronizado con los schemas de Pydantic en:
// - backend/app/schemas/candidate.py
// - backend/app/schemas/employee.py
// - backend/app/schemas/factory.py
// - backend/app/schemas/base.py
// - backend/app/schemas/auth.py
// - backend/app/schemas/timer_card.py
// - backend/app/schemas/salary.py
// - backend/app/schemas/request.py
// - backend/app/schemas/dashboard.py
// ============================================================================

// ----------------------------------------------------------------------------
// Generic Types
// ----------------------------------------------------------------------------

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// ----------------------------------------------------------------------------
// Authentication Types
// ----------------------------------------------------------------------------

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
}

export interface UserLogin {
  username: string;
  password: string;
}

// ----------------------------------------------------------------------------
// Candidate Types (100+ fields from backend/app/schemas/candidate.py)
// ----------------------------------------------------------------------------

export interface Candidate {
  // Core identification
  id: number;
  rirekisho_id: string;
  applicant_id: string | null;
  status: string;

  // Reception & Arrival Dates (受付日・来日)
  reception_date: string | null;
  arrival_date: string | null;

  // Basic Information (基本情報)
  full_name_kanji: string | null;
  full_name_kana: string | null;
  full_name_roman: string | null;
  gender: string | null;
  date_of_birth: string | null;
  photo_url: string | null;
  photo_data_url: string | null;
  nationality: string | null;
  marital_status: string | null;
  hire_date: string | null;

  // Address Information (住所情報)
  postal_code: string | null;
  current_address: string | null;
  address: string | null;
  address_banchi: string | null;
  address_building: string | null;
  registered_address: string | null;

  // Contact Information (連絡先)
  phone: string | null;
  mobile: string | null;
  email: string | null;

  // Passport Information (パスポート情報)
  passport_number: string | null;
  passport_expiry: string | null;

  // Residence Card Information (在留カード情報)
  residence_status: string | null;
  residence_expiry: string | null;
  residence_card_number: string | null;

  // Driver's License Information (運転免許情報)
  license_number: string | null;
  license_expiry: string | null;
  car_ownership: string | null;
  voluntary_insurance: string | null;

  // Qualifications & Licenses (資格・免許)
  forklift_license: string | null;
  tama_kake: string | null;
  mobile_crane_under_5t: string | null;
  mobile_crane_over_5t: string | null;
  gas_welding: string | null;

  // Family Members (家族構成) - 5 members
  family_name_1: string | null;
  family_relation_1: string | null;
  family_age_1: number | null;
  family_residence_1: string | null;
  family_separate_address_1: string | null;

  family_name_2: string | null;
  family_relation_2: string | null;
  family_age_2: number | null;
  family_residence_2: string | null;
  family_separate_address_2: string | null;

  family_name_3: string | null;
  family_relation_3: string | null;
  family_age_3: number | null;
  family_residence_3: string | null;
  family_separate_address_3: string | null;

  family_name_4: string | null;
  family_relation_4: string | null;
  family_age_4: number | null;
  family_residence_4: string | null;
  family_separate_address_4: string | null;

  family_name_5: string | null;
  family_relation_5: string | null;
  family_age_5: number | null;
  family_residence_5: string | null;
  family_separate_address_5: string | null;

  // Work History (職歴)
  work_history_company_7: string | null;
  work_history_entry_company_7: string | null;
  work_history_exit_company_7: string | null;

  // Work Experience (経験作業)
  exp_nc_lathe: boolean | null;
  exp_lathe: boolean | null;
  exp_press: boolean | null;
  exp_forklift: boolean | null;
  exp_packing: boolean | null;
  exp_welding: boolean | null;
  exp_car_assembly: boolean | null;
  exp_car_line: boolean | null;
  exp_car_inspection: boolean | null;
  exp_electronic_inspection: boolean | null;
  exp_food_processing: boolean | null;
  exp_casting: boolean | null;
  exp_line_leader: boolean | null;
  exp_painting: boolean | null;
  exp_other: string | null;

  // Lunch/Bento Options (お弁当)
  bento_lunch_dinner: string | null;
  bento_lunch_only: string | null;
  bento_dinner_only: string | null;
  bento_bring_own: string | null;

  // Commute (通勤)
  commute_method: string | null;
  commute_time_oneway: number | null;

  // Interview & Tests (面接・検査)
  interview_result: string | null;
  antigen_test_kit: string | null;
  antigen_test_date: string | null;
  covid_vaccine_status: string | null;

  // Language Skills (語学スキル)
  language_skill_exists: string | null;
  language_skill_1: string | null;
  language_skill_2: string | null;

  // Japanese Language Ability (日本語能力)
  japanese_qualification: string | null;
  japanese_level: string | null;
  jlpt_taken: string | null;
  jlpt_date: string | null;
  jlpt_score: number | null;
  jlpt_scheduled: string | null;

  // Qualifications (有資格)
  qualification_1: string | null;
  qualification_2: string | null;
  qualification_3: string | null;

  // Education (学歴)
  major: string | null;

  // Physical Information (身体情報)
  blood_type: string | null;
  dominant_hand: string | null;
  allergy_exists: string | null;

  // Japanese Ability Details (日本語能力詳細)
  listening_level: string | null;
  speaking_level: string | null;

  // Emergency Contact (緊急連絡先)
  emergency_contact_name: string | null;
  emergency_contact_relation: string | null;
  emergency_contact_phone: string | null;

  // Work Equipment (作業用品)
  safety_shoes: string | null;
  lunch_preference: string | null;
  glasses: string | null;

  // Reading & Writing Ability (読み書き能力)
  read_katakana: string | null;
  read_hiragana: string | null;
  read_kanji: string | null;
  write_katakana: string | null;
  write_hiragana: string | null;
  write_kanji: string | null;

  // Conversation Ability (会話能力)
  can_speak: string | null;
  can_understand: string | null;
  can_read_kana: string | null;
  can_write_kana: string | null;

  // OCR metadata
  ocr_notes: string | null;

  // Approval tracking
  approved_by: number | null;
  approved_at: string | null;

  // Timestamps
  created_at: string;
  updated_at: string | null;
}

export interface CandidateCreateData {
  // Reception & Arrival Dates
  reception_date?: string | null;
  arrival_date?: string | null;

  // Basic Information
  full_name_kanji?: string | null;
  full_name_kana?: string | null;
  full_name_roman?: string | null;
  gender?: string | null;
  date_of_birth?: string | null;
  photo_url?: string | null;
  photo_data_url?: string | null;
  nationality?: string | null;
  marital_status?: string | null;
  hire_date?: string | null;
  applicant_id?: string | null;

  // Address Information
  postal_code?: string | null;
  current_address?: string | null;
  address?: string | null;
  address_banchi?: string | null;
  address_building?: string | null;
  registered_address?: string | null;

  // Contact Information
  phone?: string | null;
  mobile?: string | null;
  email?: string | null;

  // Passport Information
  passport_number?: string | null;
  passport_expiry?: string | null;

  // Residence Card Information
  residence_status?: string | null;
  residence_expiry?: string | null;
  residence_card_number?: string | null;

  // Driver's License Information
  license_number?: string | null;
  license_expiry?: string | null;
  car_ownership?: string | null;
  voluntary_insurance?: string | null;

  // ... (all other fields from Candidate, all optional)
  [key: string]: any;
}

export interface CandidateListParams {
  page?: number;
  page_size?: number;
  status_filter?: string;
  search?: string;
  sort?: string;
}

// ----------------------------------------------------------------------------
// Employee Types (from backend/app/schemas/employee.py)
// ----------------------------------------------------------------------------

export interface Employee {
  // Core identification
  id: number;
  hakenmoto_id: number;
  rirekisho_id: string | null;
  factory_id: string | null;
  factory_name: string | null;
  hakensaki_shain_id: string | null;

  // Basic Information
  full_name_kanji: string;
  full_name_kana: string | null;
  date_of_birth: string | null;
  gender: string | null;
  nationality: string | null;

  // Visa/Residence Information
  zairyu_card_number: string | null;
  zairyu_expire_date: string | null;
  visa_type: string | null;
  visa_renewal_alert: boolean | null;
  visa_alert_days: number | null;

  // Address Information
  address: string | null;
  current_address: string | null;
  address_banchi: string | null;
  address_building: string | null;
  postal_code: string | null;

  // Contact Information
  phone: string | null;
  email: string | null;
  emergency_contact: string | null;
  emergency_phone: string | null;

  // Employment Information
  hire_date: string | null;
  current_hire_date: string | null;
  position: string | null;
  contract_type: string | null;

  // Photos
  photo_url: string | null;
  photo_data_url: string | null;

  // Assignment Information
  assignment_location: string | null;
  assignment_line: string | null;
  job_description: string | null;

  // Financial Information
  jikyu: number;
  jikyu_revision_date: string | null;
  hourly_rate_charged: number | null;
  billing_revision_date: string | null;
  profit_difference: number | null;

  // Social Insurance
  standard_compensation: number | null;
  health_insurance: number | null;
  nursing_insurance: number | null;
  pension_insurance: number | null;
  social_insurance_date: string | null;

  // License and Transportation
  license_type: string | null;
  license_expire_date: string | null;
  commute_method: string | null;
  optional_insurance_expire: string | null;

  // Skills and Qualifications
  japanese_level: string | null;
  career_up_5years: boolean | null;

  // Apartment Information
  apartment_id: number | null;
  apartment_start_date: string | null;
  apartment_move_out_date: string | null;
  apartment_rent: number | null;
  is_corporate_housing: boolean;

  // Paid Leave (Yukyu)
  yukyu_total: number;
  yukyu_used: number;
  yukyu_remaining: number;

  // Status
  current_status: string | null;
  is_active: boolean;
  termination_date: string | null;
  termination_reason: string | null;

  // Additional
  entry_request_date: string | null;
  notes: string | null;

  // Timestamps
  created_at: string;
  updated_at: string | null;
}

export interface EmployeeCreateData {
  rirekisho_id: string;
  factory_id: string;
  hakensaki_shain_id?: string | null;
  hire_date: string;
  jikyu: number;
  position?: string | null;
  contract_type?: string | null;
  apartment_id?: number | null;
  apartment_start_date?: string | null;
  apartment_rent?: number | null;
  is_corporate_housing?: boolean;

  // Basic Information
  full_name_kanji: string;
  full_name_kana?: string | null;
  date_of_birth?: string | null;
  gender?: string | null;
  nationality?: string | null;

  // Address and Contact
  address?: string | null;
  current_address?: string | null;
  address_banchi?: string | null;
  address_building?: string | null;
  phone?: string | null;
  email?: string | null;
  emergency_contact?: string | null;
  emergency_phone?: string | null;

  // Visa
  zairyu_card_number?: string | null;
  zairyu_expire_date?: string | null;
}

export interface EmployeeListParams {
  page?: number;
  page_size?: number;
  contract_type?: string;
  factory_id?: string;
  is_active?: boolean;
  search?: string;
}

// ----------------------------------------------------------------------------
// Factory Types (from backend/app/schemas/factory.py)
// ----------------------------------------------------------------------------

export interface ShiftConfig {
  shift_name: string;
  start_time: string;
  end_time: string;
  break_minutes: number;
}

export interface OvertimeRulesConfig {
  normal_rate_multiplier: number;
  night_rate_multiplier: number;
  holiday_rate_multiplier: number;
  night_start: string;
  night_end: string;
}

export interface BonusesConfig {
  attendance_bonus: number;
  perfect_attendance_bonus: number;
  transportation_allowance: number;
  meal_allowance: number;
  housing_allowance: number;
  other_allowances?: Record<string, any> | null;
}

export interface HolidaysConfig {
  weekly_holidays: string[];
  public_holidays: boolean;
  company_holidays: string[];
}

export interface AttendanceRulesConfig {
  late_penalty: number;
  absence_penalty: number;
  early_leave_penalty: number;
  grace_period_minutes: number;
  require_advance_notice: boolean;
}

export interface FactoryConfig {
  shifts: ShiftConfig[];
  overtime_rules: OvertimeRulesConfig;
  bonuses: BonusesConfig;
  holidays: HolidaysConfig;
  attendance_rules: AttendanceRulesConfig;
}

export interface Factory {
  id: number;
  factory_id: string;
  name: string;
  company_name: string | null;
  plant_name: string | null;
  address: string | null;
  phone: string | null;
  contact_person: string | null;
  config: FactoryConfig | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  employees_count?: number;
  employees?: Employee[];
}

export interface FactoryCreateData {
  factory_id: string;
  name: string;
  company_name?: string | null;
  plant_name?: string | null;
  address?: string | null;
  phone?: string | null;
  contact_person?: string | null;
  config?: FactoryConfig | null;
}

// ----------------------------------------------------------------------------
// Timer Card Types (from backend/app/schemas/timer_card.py)
// ----------------------------------------------------------------------------

export interface TimerCard {
  id: number;
  employee_id: number;
  factory_id: string;
  work_date: string;
  clock_in: string | null;
  clock_out: string | null;
  break_minutes: number;
  shift_type: string | null;
  notes: string | null;
  regular_hours: number;
  overtime_hours: number;
  night_hours: number;
  holiday_hours: number;
  is_approved: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface TimerCardCreateData {
  employee_id: number;
  factory_id: string;
  work_date: string;
  clock_in?: string | null;
  clock_out?: string | null;
  break_minutes?: number;
  shift_type?: string | null;
  notes?: string | null;
}

export interface TimerCardListParams {
  page?: number;
  page_size?: number;
  employee_id?: number;
  factory_id?: string;
  start_date?: string;
  end_date?: string;
  is_approved?: boolean;
}

// ----------------------------------------------------------------------------
// Salary Calculation Types (from backend/app/schemas/salary.py)
// ----------------------------------------------------------------------------

export interface SalaryCalculation {
  id: number;
  employee_id: number;
  month: number;
  year: number;
  total_regular_hours: number;
  total_overtime_hours: number;
  total_night_hours: number;
  total_holiday_hours: number;
  base_salary: number;
  overtime_pay: number;
  night_pay: number;
  holiday_pay: number;
  bonus: number;
  gasoline_allowance: number;
  apartment_deduction: number;
  other_deductions: number;
  gross_salary: number;
  net_salary: number;
  factory_payment: number;
  company_profit: number;
  is_paid: boolean;
  paid_at: string | null;
  created_at: string;
}

export interface SalaryCalculationCreateData {
  employee_id: number;
  month: number;
  year: number;
  bonus?: number;
  gasoline_allowance?: number;
  other_deductions?: number;
  notes?: string | null;
}

export interface SalaryListParams {
  page?: number;
  page_size?: number;
  employee_id?: number;
  month?: number;
  year?: number;
  is_paid?: boolean;
}

// ----------------------------------------------------------------------------
// Request Types (from backend/app/schemas/request.py)
// ----------------------------------------------------------------------------

export interface Request {
  id: number;
  employee_id: number;
  request_type: string;
  start_date: string;
  end_date: string;
  total_days: number | null;
  reason: string | null;
  notes: string | null;
  status: string;
  approved_by: number | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface RequestCreateData {
  employee_id: number;
  request_type: string;
  start_date: string;
  end_date: string;
  total_days?: number | null;
  reason?: string | null;
  notes?: string | null;
}

export interface RequestListParams {
  page?: number;
  page_size?: number;
  employee_id?: number;
  request_type?: string;
  status?: string;
}

// ----------------------------------------------------------------------------
// Dashboard Types (from backend/app/schemas/dashboard.py)
// ----------------------------------------------------------------------------

export interface DashboardStats {
  total_candidates: number;
  pending_candidates: number;
  total_employees: number;
  active_employees: number;
  total_factories: number;
  pending_requests: number;
  pending_timer_cards: number;
  total_salary_current_month: number;
  total_profit_current_month: number;
}

export interface FactoryDashboard {
  factory_id: string;
  factory_name: string;
  total_employees: number;
  active_employees: number;
  current_month_hours: number;
  current_month_salary: number;
  current_month_revenue: number;
  current_month_profit: number;
  profit_margin: number;
}

export interface EmployeeAlert {
  employee_id: number;
  employee_name: string;
  alert_type: string;
  alert_date: string;
  days_until: number;
  message: string;
}

export interface MonthlyTrend {
  month: string;
  total_employees: number;
  total_hours: number;
  total_salary: number;
  total_revenue: number;
  total_profit: number;
}

export interface RecentActivity {
  activity_type: string;
  description: string;
  timestamp: string;
  user: string | null;
}

export interface AdminDashboard {
  stats: DashboardStats;
  factories: FactoryDashboard[];
  alerts: EmployeeAlert[];
  monthly_trends: MonthlyTrend[];
  recent_activities: RecentActivity[];
}

// ----------------------------------------------------------------------------
// Common Response Types
// ----------------------------------------------------------------------------

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface ErrorResponse {
  success: boolean;
  message: string;
  error: string | null;
}
