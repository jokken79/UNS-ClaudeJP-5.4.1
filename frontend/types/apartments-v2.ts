/**
 * TypeScript types for Apartments V2 API
 * Aligned with backend schemas in: backend/app/schemas/apartment_v2.py
 */

// =============================================================================
// ENUMS
// =============================================================================

export enum RoomType {
  R = 'R',        // Room (1K, 1DK, 1LDK, etc.)
  K = 'K',        // Kitchen
  DK = 'DK',      // Dining Kitchen
  LDK = 'LDK',    // Living Dining Kitchen
  S = 'S',        // Single room
}

export enum ChargeType {
  CLEANING = 'cleaning',
  REPAIR = 'repair',
  DEPOSIT = 'deposit',
  PENALTY = 'penalty',
  OTHER = 'other',
}

export enum AssignmentStatus {
  ACTIVE = 'active',
  ENDED = 'ended',
  CANCELLED = 'cancelled',
}

export enum DeductionStatus {
  PENDING = 'pending',
  PROCESSED = 'processed',
  PAID = 'paid',
  CANCELLED = 'cancelled',
}

export enum ChargeStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  CANCELLED = 'cancelled',
  PAID = 'paid',
}

// =============================================================================
// APARTMENT TYPES
// =============================================================================

export interface ApartmentBase {
  name: string;
  building_name?: string | null;
  room_number?: string | null;
  floor_number?: number | null;
  postal_code?: string | null;
  prefecture?: string | null;
  city?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  room_type?: RoomType | null;
  size_sqm?: number | null;

  // Property type
  property_type?: string | null;

  // Prices
  base_rent: number;
  management_fee?: number;
  deposit?: number;
  key_money?: number;
  default_cleaning_fee?: number;
  parking_spaces?: number | null;
  parking_price_per_unit?: number | null;
  initial_plus?: number | null;

  // Contract
  contract_start_date?: string | null;
  contract_end_date?: string | null;
  landlord_name?: string | null;
  landlord_contact?: string | null;
  real_estate_agency?: string | null;
  emergency_contact?: string | null;

  notes?: string | null;
  status?: string;
}

export interface ApartmentCreate extends ApartmentBase {}

export interface ApartmentUpdate extends Partial<ApartmentBase> {}

export interface ApartmentResponse extends ApartmentBase {
  id: number;
  base_rent: number;
  management_fee: number;
  deposit: number;
  key_money: number;
  default_cleaning_fee: number;
  parking_spaces?: number | null;
  parking_price_per_unit?: number | null;
  initial_plus?: number | null;
  status: string;
  created_at: string;
  updated_at?: string | null;

  // Calculated fields
  full_address?: string | null;
  total_monthly_cost?: number;
  active_assignments?: number;
}

export interface ApartmentWithStats extends ApartmentResponse {
  current_occupancy: number;
  max_occupancy: number;
  occupancy_rate: number;
  is_available: boolean;
  last_assignment_date?: string | null;
  average_stay_duration?: number | null;

  // Factory associations (new)
  region_id?: number | null;
  zone?: string | null;
  factory_associations?: FactoryAssociation[];
  primary_factory?: FactoryInfo | null;
}

// =============================================================================
// FACTORY ASSOCIATION TYPES (NEW)
// =============================================================================

export interface FactoryInfo {
  id: number;
  factory_id: string;
  company_name: string;
  plant_name: string;
  address?: string | null;
}

export interface FactoryAssociation {
  id: number;
  apartment_id: number;
  factory_id: number;
  is_primary: boolean;
  priority: number;
  distance_km?: number | null;
  commute_minutes?: number | null;
  effective_from: string;
  effective_until?: string | null;
  notes?: string | null;
  factory: FactoryInfo;
  employee_count?: number;
}

// =============================================================================
// ASSIGNMENT TYPES
// =============================================================================

export interface AssignmentBase {
  apartment_id: number;
  employee_id: number;
  start_date: string;
  end_date?: string | null;

  // Calculations
  monthly_rent: number;
  days_in_month: number;
  days_occupied: number;
  prorated_rent: number;
  is_prorated: boolean;
  total_deduction: number;

  // Metadata
  contract_type?: string | null;
  notes?: string | null;
  status: AssignmentStatus;
}

export interface AssignmentCreate extends AssignmentBase {}

export interface AssignmentUpdate {
  end_date?: string | null;
  days_occupied?: number;
  prorated_rent?: number;
  total_deduction?: number;
  include_cleaning_fee?: boolean;
  cleaning_fee?: number;
  additional_charges?: Array<{
    charge_type: ChargeType;
    description: string;
    amount: number;
    charge_date: string;
  }>;
  notes?: string | null;
  status?: AssignmentStatus;
}

export interface AssignmentResponse extends AssignmentBase {
  id: number;
  created_at: string;
  updated_at?: string | null;

  // Related data (lazy loaded)
  apartment?: ApartmentResponse;
  employee?: any;
  additional_charges?: AdditionalChargeResponse[];
  deductions?: DeductionResponse[];
}

export interface AssignmentListItem {
  id: number;
  apartment_id: number;
  employee_id: number;
  start_date: string;
  end_date?: string | null;
  status: AssignmentStatus;
  total_deduction: number;
  created_at: string;

  // Related data (summary fields)
  apartment_name: string;
  apartment_code?: string | null;
  employee_name_kanji: string;
  employee_name_kana?: string | null;
}

// =============================================================================
// TRANSFER TYPES
// =============================================================================

export interface TransferRequest {
  employee_id: number;
  current_apartment_id: number;
  new_apartment_id: number;
  transfer_date: string;
  notes?: string | null;
}

export interface TransferResponse {
  ended_assignment: AssignmentResponse;
  new_assignment: AssignmentResponse;
  old_apartment_cost: number;
  new_apartment_cost: number;
  total_monthly_cost: number;
  breakdown: Record<string, any>;
}

// =============================================================================
// CHARGE TYPES
// =============================================================================

export interface AdditionalChargeBase {
  assignment_id: number;
  employee_id: number;
  apartment_id: number;
  charge_type: ChargeType;
  description: string;
  amount: number;
  charge_date: string;
  status: ChargeStatus;
  notes?: string | null;
}

export interface AdditionalChargeCreate extends AdditionalChargeBase {}

export interface AdditionalChargeUpdate {
  description?: string;
  amount?: number;
  status?: ChargeStatus;
  notes?: string | null;
}

export interface AdditionalChargeResponse extends AdditionalChargeBase {
  id: number;
  approved_by?: number | null;
  approved_at?: string | null;
  created_at: string;
  updated_at?: string | null;

  // Related data
  employee_name?: string | null;
  apartment_name?: string | null;
  approver_name?: string | null;
}

// =============================================================================
// DEDUCTION TYPES
// =============================================================================

export interface DeductionBase {
  assignment_id: number;
  employee_id: number;
  apartment_id: number;
  year: number;
  month: number;
  base_rent: number;
  additional_charges: number;
  total_amount: number;
  status: DeductionStatus;
  notes?: string | null;
}

export interface DeductionResponse extends DeductionBase {
  id: number;
  days_in_month: number;
  days_occupied: number;
  was_prorated: boolean;
  created_at: string;
  updated_at?: string | null;

  // Related data
  employee_name?: string | null;
  apartment_name?: string | null;
}

// =============================================================================
// PRORATED CALCULATION TYPES
// =============================================================================

export interface ProratedCalculationRequest {
  monthly_rent: number;
  start_date: string;
  end_date?: string | null;
  year: number;
  month: number;
}

export interface ProratedCalculationResponse {
  monthly_rent: number;
  days_in_month: number;
  days_occupied: number;
  prorated_rent: number;
  daily_rate: number;
  is_prorated: boolean;
  calculation_formula: string;
}

// =============================================================================
// LIST PARAMS
// =============================================================================

export interface ApartmentListParams {
  page?: number;
  page_size?: number;
  status?: string;
  min_rent?: number;
  max_rent?: number;
  prefecture?: string;
  city?: string;
  available_only?: boolean;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';

  // NEW: Factory filtering
  factory_id?: number;
  region_id?: number;
  zone?: string;
  has_factory?: boolean;
}

export interface AssignmentListParams {
  page?: number;
  page_size?: number;
  apartment_id?: number;
  employee_id?: number;
  status?: AssignmentStatus;
  start_date_from?: string;
  start_date_to?: string;
  end_date_from?: string;
  end_date_to?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ChargeListParams {
  page?: number;
  page_size?: number;
  assignment_id?: number;
  employee_id?: number;
  apartment_id?: number;
  charge_type?: ChargeType;
  status?: ChargeStatus;
  date_from?: string;
  date_to?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface DeductionListParams {
  page?: number;
  page_size?: number;
  year?: number;
  month?: number;
  employee_id?: number;
  apartment_id?: number;
  status?: DeductionStatus;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}
