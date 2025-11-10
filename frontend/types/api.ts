export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  ADMIN = 'ADMIN',
  KEITOSAN = 'KEITOSAN',
  TANTOSHA = 'TANTOSHA',
  COORDINATOR = 'COORDINATOR',
  KANRININSHA = 'KANRININSHA',
  EMPLOYEE = 'EMPLOYEE',
  CONTRACT_WORKER = 'CONTRACT_WORKER',
}

export enum CandidateStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  HIRED = 'hired',
}

export enum DocumentType {
  RIREKISHO = 'rirekisho',
  ZAIRYU_CARD = 'zairyu_card',
  LICENSE = 'license',
  CONTRACT = 'contract',
  OTHER = 'other',
}

export enum RequestType {
  YUKYU = 'yukyu',
  HANKYU = 'hankyu',
  IKKIKOKOKU = 'ikkikokoku',
  TAISHA = 'taisha',
}

export enum RequestStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export enum ShiftType {
  ASA = 'asa',
  HIRU = 'hiru',
  YORU = 'yoru',
  OTHER = 'other',
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  search?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: UserRole;
}

export interface UserUpdate {
  email?: string;
  full_name?: string;
  password?: string;
}

export interface Candidate {
  id: number;
  rirekisho_id?: string;
  full_name_roman: string;
  full_name_kanji?: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  phone?: string;
  email?: string;
  address?: string;
  status: CandidateStatus;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface CandidateCreateData {
  full_name_roman: string;
  full_name_kanji?: string;
  date_of_birth?: string;
  gender?: string;
  nationality?: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface CandidateListParams extends PaginationParams {
  status?: CandidateStatus;
  search?: string;
}

export interface Employee {
  id: number;
  employee_id: string;
  full_name_roman: string;
  full_name_kanji?: string;
  date_of_birth?: string;
  email?: string;
  phone?: string;
  factory_id?: number;
  apartment_id?: number;
  hire_date?: string;
  status?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface EmployeeCreateData {
  employee_id: string;
  full_name_roman: string;
  full_name_kanji?: string;
  date_of_birth?: string;
  email?: string;
  phone?: string;
  factory_id?: number;
  apartment_id?: number;
  hire_date?: string;
}

export interface EmployeeListParams extends PaginationParams {
  factory_id?: number;
  status?: string;
  search?: string;
}

export interface Factory {
  id: number;
  name: string;
  name_kanji?: string;
  address?: string;
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  status?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface FactoryCreateData {
  name: string;
  name_kanji?: string;
  address?: string;
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface TimerCard {
  id: number;
  employee_id: number;
  date: string;
  clock_in?: string;
  clock_out?: string;
  break_duration?: number;
  total_hours?: number;
  overtime_hours?: number;
  shift_type?: ShiftType;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface TimerCardCreateData {
  employee_id: number;
  date: string;
  clock_in?: string;
  clock_out?: string;
  break_duration?: number;
  shift_type?: ShiftType;
}

export interface TimerCardListParams extends PaginationParams {
  employee_id?: number;
  date_from?: string;
  date_to?: string;
}

export interface SalaryCalculation {
  id: number;
  employee_id: number;
  period_start: string;
  period_end: string;
  base_salary?: number;
  overtime_pay?: number;
  allowances?: number;
  deductions?: number;
  net_salary?: number;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface SalaryCalculationCreateData {
  employee_id: number;
  period_start: string;
  period_end: string;
  base_salary?: number;
  overtime_pay?: number;
  allowances?: number;
  deductions?: number;
}

export interface SalaryListParams extends PaginationParams {
  employee_id?: number;
  period_start?: string;
  period_end?: string;
}

export interface Request {
  id: number;
  employee_id: number;
  type: RequestType;
  status: RequestStatus;
  start_date: string;
  end_date?: string;
  reason?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

export interface RequestCreateData {
  employee_id: number;
  type: RequestType;
  start_date: string;
  end_date?: string;
  reason?: string;
}

export interface RequestListParams extends PaginationParams {
  employee_id?: number;
  type?: RequestType;
  status?: RequestStatus;
  date_from?: string;
  date_to?: string;
}

export interface DashboardStats {
  total_candidates: number;
  total_employees: number;
  total_factories: number;
  active_requests: number;
  [key: string]: any;
}
