import axios from 'axios';

import { useAuthStore } from '@/stores/auth-store';
import type {
  AuthResponse,
  User,
  Candidate,
  CandidateCreateData,
  CandidateUpdateData,
  CandidateListParams,
  PaginatedResponse,
  Employee,
  EmployeeCreateData,
  EmployeeListParams,
  Factory,
  FactoryCreateData,
  TimerCard,
  TimerCardCreateData,
  TimerCardListParams,
  SalaryCalculation,
  SalaryCalculationCreateData,
  SalaryListParams,
  Request,
  RequestCreateData,
  RequestListParams,
  DashboardStats,
} from '@/types/api';

import type {
  ApartmentResponse,
  ApartmentWithStats,
  ApartmentCreate,
  ApartmentUpdate,
  ApartmentListParams,
  AssignmentResponse,
  AssignmentListItem,
  AssignmentCreate,
  AssignmentUpdate,
  AssignmentListParams,
  TransferRequest,
  TransferResponse,
  AdditionalChargeResponse,
  AdditionalChargeCreate,
  AdditionalChargeUpdate,
  ChargeListParams,
  DeductionResponse,
  DeductionListParams,
  ProratedCalculationRequest,
  ProratedCalculationResponse,
} from '@/types/apartments-v2';

// Normalize base URL to ensure it includes `/api` and no trailing slash
const normalizeBaseUrl = (url: string): string => {
  if (!url) return 'http://localhost:8000/api';
  const trimmed = url.replace(/\/+$/, '');
  return trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`;
};

const API_BASE_URL = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,  // 30 seconds for OCR operations
});

const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  return useAuthStore.getState().token;
};

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: any) => {
    const token = getAuthToken();

    // Only add token if not already provided in the request config
    if (token && !config.headers?.authorization) {
      config.headers = config.headers ?? {};
      config.headers.authorization = `Bearer ${token}`;
    }

    // Ajustar baseURL para SSR si se define un endpoint interno (Docker, etc.)
    if (typeof window === 'undefined') {
      const internal = process.env.INTERNAL_API_URL;
      if (internal) {
        config.baseURL = normalizeBaseUrl(internal);
      } else {
        // Por defecto, mantén la misma base URL normalizada
        config.baseURL = API_BASE_URL;
      }
    }

    return config;
  },
  (error: unknown) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response: any) => response,
  async (error: any) => {
    // Log detallado para depurar errores de red y respuesta
    if (error.response) {
      console.error('Response error:', error.response.status);
    } else if (error.request) {
      const url = (() => {
        try {
          const base = error.config?.baseURL ?? '';
          const path = error.config?.url ?? '';
          return `${base}${path}`;
        } catch {
          return undefined;
        }
      })();
      console.error('Network error:', error.message, '| code:', error.code, '| url:', url);
    }

    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth services
export const authService = {
  login: async (username: string, password: string): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.set('username', username);
    formData.set('password', password);

    const response = await api.post<AuthResponse>('/auth/login/', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  logout: (): void => {
    useAuthStore.getState().logout();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  },

  getCurrentUser: async (token?: string): Promise<User> => {
    const config = token ? {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    } : {};
    const response = await api.get<User>('/auth/me/', config);
    return response.data;
  }
};

// Employee services
export const employeeService = {
  getEmployees: async (params?: EmployeeListParams): Promise<PaginatedResponse<Employee>> => {
    const response = await api.get<PaginatedResponse<Employee>>('/employees/', { params });
    return response.data;
  },

  getEmployee: async <T = Employee>(id: string | number): Promise<T> => {
    const response = await api.get<T>(`/employees/${id}/`);
    return response.data;
  },

  createEmployee: async (data: EmployeeCreateData): Promise<Employee> => {
    const response = await api.post<Employee>('/employees/', data);
    return response.data;
  },

  updateEmployee: async (id: string | number, data: Partial<EmployeeCreateData>): Promise<Employee> => {
    const response = await api.put<Employee>(`/employees/${id}/`, data);
    return response.data;
  },

  deleteEmployee: async (id: string | number): Promise<void> => {
    await api.delete(`/employees/${id}/`);
  },

  getAvailableForApartment: async (params?: EmployeeListParams): Promise<PaginatedResponse<Employee>> => {
    const response = await api.get<PaginatedResponse<Employee>>('/employees/available-for-apartment', { params });
    return response.data;
  }
};

// Candidate services
export const candidateService = {
  getCandidates: async (params?: CandidateListParams): Promise<PaginatedResponse<Candidate>> => {
    const response = await api.get<PaginatedResponse<Candidate>>('/candidates/', { params });
    return response.data;
  },

  getCandidate: async (id: string | number): Promise<Candidate> => {
    const response = await api.get<Candidate>(`/candidates/${id}/`);
    return response.data;
  },

  createCandidate: async (data: CandidateCreateData): Promise<Candidate> => {
    const response = await api.post<Candidate>('/candidates/', data);
    return response.data;
  },

  updateCandidate: async (id: string | number, data: CandidateUpdateData): Promise<Candidate> => {
    const response = await api.put<Candidate>(`/candidates/${id}/`, data);
    return response.data;
  },

  deleteCandidate: async (id: string | number): Promise<void> => {
    await api.delete(`/candidates/${id}/`);
  },

  approveCandidate: async (id: string | number): Promise<Candidate> => {
    const response = await api.post<Candidate>(`/candidates/${id}/approve/`);
    return response.data;
  },

  rejectCandidate: async (id: string | number, reason: string): Promise<Candidate> => {
    const response = await api.post<Candidate>(`/candidates/${id}/reject/`, { reason });
    return response.data;
  }
};

// Factory services
export const factoryService = {
  getFactories: async (params?: Record<string, unknown>): Promise<Factory[]> => {
    const response = await api.get<Factory[]>('/factories/', { params });
    return response.data;
  },

  getFactory: async (id: string | number): Promise<Factory> => {
    const response = await api.get<Factory>(`/factories/${id}/`);
    return response.data;
  },

  createFactory: async (data: FactoryCreateData): Promise<Factory> => {
    const response = await api.post<Factory>('/factories/', data);
    return response.data;
  },

  updateFactory: async (id: string | number, data: Partial<FactoryCreateData>): Promise<Factory> => {
    const response = await api.put<Factory>(`/factories/${id}/`, data);
    return response.data;
  },

  deleteFactory: async (id: string | number): Promise<void> => {
    await api.delete(`/factories/${id}/`);
  }
};

// Timer Card services
export const timerCardService = {
  getTimerCards: async <T = TimerCard[]>(params?: TimerCardListParams): Promise<T> => {
    const response = await api.get<T>('/timer-cards/', { params });
    return response.data;
  },

  getTimerCard: async <T = TimerCard>(id: string | number): Promise<T> => {
    const response = await api.get<T>(`/timer-cards/${id}/`);
    return response.data;
  },

  createTimerCard: async (data: TimerCardCreateData): Promise<TimerCard> => {
    const response = await api.post<TimerCard>('/timer-cards/', data);
    return response.data;
  },

  updateTimerCard: async (id: string | number, data: Partial<TimerCardCreateData>): Promise<TimerCard> => {
    const response = await api.put<TimerCard>(`/timer-cards/${id}/`, data);
    return response.data;
  },

  deleteTimerCard: async (id: string | number): Promise<void> => {
    await api.delete(`/timer-cards/${id}/`);
  },

  // OCR Upload services
  uploadTimerCardPDF: async (formData: FormData): Promise<any> => {
    const response = await api.post('/timer-cards/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  createBulkTimerCards: async (records: any[]): Promise<any> => {
    const response = await api.post('/timer-cards/bulk/', { records });
    return response.data;
  }
};

// Salary services
export const salaryService = {
  getSalaries: async <T = SalaryCalculation[]>(params?: SalaryListParams): Promise<T> => {
    const response = await api.get<T>('/salary/', { params });
    return response.data;
  },

  getSalary: async <T = SalaryCalculation>(id: string | number): Promise<T> => {
    const response = await api.get<T>(`/salary/${id}/`);
    return response.data;
  },

  calculateSalary: async (data: SalaryCalculationCreateData): Promise<SalaryCalculation> => {
    const response = await api.post<SalaryCalculation>('/salary/calculate/', data);
    return response.data;
  }
};

// Request services
export const requestService = {
  getRequests: async <T = Request[]>(params?: RequestListParams): Promise<T> => {
    const response = await api.get<T>('/requests/', { params });
    return response.data;
  },

  getRequest: async <T = Request>(id: string | number): Promise<T> => {
    const response = await api.get<T>(`/requests/${id}/`);
    return response.data;
  },

  createRequest: async (data: RequestCreateData): Promise<Request> => {
    const response = await api.post<Request>('/requests/', data);
    return response.data;
  },

  approveRequest: async (id: string | number): Promise<Request> => {
    const response = await api.post<Request>(`/requests/${id}/approve/`);
    return response.data;
  },

  rejectRequest: async (id: string | number, reason: string): Promise<Request> => {
    const response = await api.post<Request>(`/requests/${id}/reject/`, { reason });
    return response.data;
  }
};

// Dashboard services
export const dashboardService = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get<DashboardStats>('/dashboard/stats/');
    return response.data;
  },

  getRecentActivity: async (): Promise<unknown> => {
    const response = await api.get('/dashboard/recent-activity/');
    return response.data;
  }
};

// =============================================================================
// APARTMENTS V2 SERVICES
// =============================================================================

export const apartmentsV2Service = {
  // -----------------------------------------------------------------------------
  // APARTMENTS
  // -----------------------------------------------------------------------------

  /**
   * List apartments with filters and pagination
   */
  listApartments: async (params?: ApartmentListParams): Promise<PaginatedResponse<ApartmentWithStats>> => {
    const response = await api.get<PaginatedResponse<ApartmentWithStats>>('/apartments-v2/apartments', { params });
    return response.data;
  },

  /**
   * Get apartment by ID with stats
   */
  getApartment: async (id: number): Promise<ApartmentWithStats> => {
    const response = await api.get<ApartmentWithStats>(`/apartments-v2/apartments/${id}`);
    return response.data;
  },

  /**
   * Create new apartment
   */
  createApartment: async (data: ApartmentCreate): Promise<ApartmentResponse> => {
    const response = await api.post<ApartmentResponse>('/apartments-v2/apartments', data);
    return response.data;
  },

  /**
   * Update existing apartment
   */
  updateApartment: async (id: number, data: ApartmentUpdate): Promise<ApartmentResponse> => {
    const response = await api.put<ApartmentResponse>(`/apartments-v2/apartments/${id}`, data);
    return response.data;
  },

  /**
   * Soft delete apartment
   */
  deleteApartment: async (id: number): Promise<void> => {
    await api.delete(`/apartments-v2/apartments/${id}`);
  },

  // -----------------------------------------------------------------------------
  // ASSIGNMENTS
  // -----------------------------------------------------------------------------

  /**
   * List assignments with filters and pagination
   */
  listAssignments: async (params?: AssignmentListParams): Promise<PaginatedResponse<AssignmentListItem>> => {
    const response = await api.get<PaginatedResponse<AssignmentListItem>>('/apartments-v2/assignments', { params });
    return response.data;
  },

  /**
   * Get assignment by ID with full details
   */
  getAssignment: async (id: number): Promise<AssignmentResponse> => {
    const response = await api.get<AssignmentResponse>(`/apartments-v2/assignments/${id}`);
    return response.data;
  },

  /**
   * Create new assignment
   */
  createAssignment: async (data: AssignmentCreate): Promise<AssignmentResponse> => {
    const response = await api.post<AssignmentResponse>('/apartments-v2/assignments', data);
    return response.data;
  },

  /**
   * Update/end assignment
   */
  updateAssignment: async (id: number, data: AssignmentUpdate): Promise<AssignmentResponse> => {
    const response = await api.put<AssignmentResponse>(`/apartments-v2/assignments/${id}`, data);
    return response.data;
  },

  /**
   * End assignment (convenience method)
   */
  endAssignment: async (
    id: number,
    data: {
      end_date: string;
      include_cleaning_fee?: boolean;
      cleaning_fee?: number;
      additional_charges?: Array<{
        charge_type: string;
        description: string;
        amount: number;
        charge_date: string;
      }>;
    }
  ): Promise<AssignmentResponse> => {
    const response = await api.put<AssignmentResponse>(`/apartments-v2/assignments/${id}/end`, data);
    return response.data;
  },

  /**
   * Get active assignment for employee
   */
  getActiveAssignmentByEmployee: async (employeeId: number): Promise<AssignmentResponse | null> => {
    const response = await api.get<AssignmentResponse | null>(
      `/apartments-v2/assignments/employee/${employeeId}/active`
    );
    return response.data;
  },

  /**
   * Get active assignments for apartment
   */
  getActiveAssignmentsByApartment: async (apartmentId: number): Promise<AssignmentResponse[]> => {
    const response = await api.get<AssignmentResponse[]>(
      `/apartments-v2/assignments/apartment/${apartmentId}/active`
    );
    return response.data;
  },

  // -----------------------------------------------------------------------------
  // TRANSFERS
  // -----------------------------------------------------------------------------

  /**
   * Transfer employee between apartments
   */
  transferEmployee: async (data: TransferRequest): Promise<TransferResponse> => {
    const response = await api.post<TransferResponse>('/apartments-v2/assignments/transfer', data);
    return response.data;
  },

  // -----------------------------------------------------------------------------
  // ADDITIONAL CHARGES
  // -----------------------------------------------------------------------------

  /**
   * List additional charges
   */
  listCharges: async (params?: ChargeListParams): Promise<PaginatedResponse<AdditionalChargeResponse>> => {
    const response = await api.get<PaginatedResponse<AdditionalChargeResponse>>('/apartments-v2/charges', { params });
    return response.data;
  },

  /**
   * Get charge by ID
   */
  getCharge: async (id: number): Promise<AdditionalChargeResponse> => {
    const response = await api.get<AdditionalChargeResponse>(`/apartments-v2/charges/${id}`);
    return response.data;
  },

  /**
   * Create additional charge
   */
  createCharge: async (data: AdditionalChargeCreate): Promise<AdditionalChargeResponse> => {
    const response = await api.post<AdditionalChargeResponse>('/apartments-v2/charges', data);
    return response.data;
  },

  /**
   * Update additional charge
   */
  updateCharge: async (id: number, data: AdditionalChargeUpdate): Promise<AdditionalChargeResponse> => {
    const response = await api.put<AdditionalChargeResponse>(`/apartments-v2/charges/${id}`, data);
    return response.data;
  },

  /**
   * Approve charge (admin only)
   */
  approveCharge: async (id: number): Promise<AdditionalChargeResponse> => {
    const response = await api.put<AdditionalChargeResponse>(`/apartments-v2/charges/${id}/approve`);
    return response.data;
  },

  /**
   * Delete charge (soft delete)
   */
  deleteCharge: async (id: number): Promise<void> => {
    await api.delete(`/apartments-v2/charges/${id}`);
  },

  // -----------------------------------------------------------------------------
  // DEDUCTIONS
  // -----------------------------------------------------------------------------

  /**
   * List rent deductions
   */
  listDeductions: async (params?: DeductionListParams): Promise<PaginatedResponse<DeductionResponse>> => {
    const response = await api.get<PaginatedResponse<DeductionResponse>>('/apartments-v2/deductions', { params });
    return response.data;
  },

  /**
   * Get deductions for specific year/month
   */
  getDeductionsByPeriod: async (year: number, month: number): Promise<DeductionResponse[]> => {
    const response = await api.get<DeductionResponse[]>(`/apartments-v2/deductions/${year}/${month}`);
    return response.data;
  },

  /**
   * Generate deductions for specific month
   */
  generateDeductions: async (year: number, month: number): Promise<{ created: number; skipped: number }> => {
    const response = await api.post<{ created: number; skipped: number }>(
      '/apartments-v2/deductions/generate',
      { year, month }
    );
    return response.data;
  },

  /**
   * Export deductions to CSV
   */
  exportDeductions: async (year: number, month: number): Promise<Blob> => {
    const response = await api.get(`/apartments-v2/deductions/export/${year}/${month}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // -----------------------------------------------------------------------------
  // CALCULATIONS
  // -----------------------------------------------------------------------------

  /**
   * Calculate prorated rent
   */
  calculateProratedRent: async (data: ProratedCalculationRequest): Promise<ProratedCalculationResponse> => {
    const response = await api.post<ProratedCalculationResponse>('/apartments-v2/calculate/prorated', data);
    return response.data;
  },

  /**
   * Calculate transfer cost (preview)
   */
  calculateTransferCost: async (data: TransferRequest): Promise<{
    old_apartment_cost: number;
    new_apartment_cost: number;
    total_monthly_cost: number;
    breakdown: Record<string, any>;
  }> => {
    const response = await api.post('/apartments-v2/calculate/transfer', data);
    return response.data;
  },
};

export default api;
