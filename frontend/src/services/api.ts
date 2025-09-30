/**
 * API Client for VitaNexus Backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Member,
  HealthProfile,
  HealthScore,
  WearableMetric,
  InterventionProgram,
  ProgramEnrollment,
  Rebate,
  PremiumInfo
} from '@/types/member';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(email: string, password: string): Promise<{ access_token: string }> {
    const response = await this.client.post('/auth/login', { email, password });
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    return response.data;
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
  }

  // Members
  async getCurrentMember(): Promise<Member> {
    const response = await this.client.get('/members/me');
    return response.data;
  }

  async getMember(memberId: string): Promise<Member> {
    const response = await this.client.get(`/members/${memberId}`);
    return response.data;
  }

  async updateMember(memberId: string, data: Partial<Member>): Promise<Member> {
    const response = await this.client.patch(`/members/${memberId}`, data);
    return response.data;
  }

  // Health Profile
  async getHealthProfile(memberId: string): Promise<HealthProfile> {
    const response = await this.client.get(`/members/${memberId}/health-profile`);
    return response.data;
  }

  async updateHealthProfile(memberId: string, data: Partial<HealthProfile>): Promise<HealthProfile> {
    const response = await this.client.put(`/members/${memberId}/health-profile`, data);
    return response.data;
  }

  // Health Scoring
  async getCurrentHealthScore(memberId: string): Promise<HealthScore> {
    const response = await this.client.get(`/health-scores/${memberId}`);
    return response.data;
  }

  async calculateHealthScore(memberId: string): Promise<HealthScore> {
    const response = await this.client.post(`/health-scores/${memberId}`);
    return response.data;
  }

  async getHealthScoreHistory(
    memberId: string,
    params?: {
      start_date?: string;
      end_date?: string;
      interval?: 'daily' | 'weekly' | 'monthly';
    }
  ): Promise<{ member_id: string; scores: HealthScore[] }> {
    const response = await this.client.get(`/health-scores/${memberId}/history`, { params });
    return response.data;
  }

  // Wearables
  async getWearableMetrics(
    memberId: string,
    params: {
      start_date: string;
      end_date: string;
      metric_types?: string[];
    }
  ): Promise<{ member_id: string; metrics: WearableMetric[] }> {
    const response = await this.client.get(`/wearables/${memberId}/metrics`, { params });
    return response.data;
  }

  async connectWearable(memberId: string, deviceType: string): Promise<{ authorization_url: string; state: string }> {
    const response = await this.client.post('/wearables/connect', {
      member_id: memberId,
      device_type: deviceType,
      callback_url: `${window.location.origin}/wearables/callback`,
    });
    return response.data;
  }

  // Interventions
  async getAvailablePrograms(memberId?: string): Promise<InterventionProgram[]> {
    const response = await this.client.get('/interventions/programs', {
      params: memberId ? { member_id: memberId } : {},
    });
    return response.data;
  }

  async getInterventionRecommendations(
    memberId: string
  ): Promise<{
    member_id: string;
    recommendations: Array<{
      recommendation_id: string;
      program_id: string;
      program_name: string;
      priority_score: number;
      expected_roi: number;
      recommendation_reason: string;
      status: string;
    }>;
  }> {
    const response = await this.client.get(`/interventions/recommendations/${memberId}`);
    return response.data;
  }

  async enrollInProgram(
    memberId: string,
    programId: string,
    scheduledStartDate?: string
  ): Promise<ProgramEnrollment> {
    const response = await this.client.post('/interventions/enrollments', {
      member_id: memberId,
      program_id: programId,
      scheduled_start_date: scheduledStartDate,
    });
    return response.data;
  }

  async getMyEnrollments(memberId: string): Promise<ProgramEnrollment[]> {
    const response = await this.client.get(`/interventions/enrollments?member_id=${memberId}`);
    return response.data;
  }

  // Financial
  async getPremiumInfo(memberId: string): Promise<PremiumInfo> {
    const response = await this.client.get(`/financial/premiums/${memberId}`);
    return response.data;
  }

  async getRebates(memberId: string): Promise<{ total_rebates_lifetime: number; rebates: Rebate[] }> {
    const response = await this.client.get(`/financial/rebates/${memberId}`);
    return response.data;
  }

  async getCostEstimate(
    memberId: string,
    procedureCodes: string[],
    providerId?: string
  ): Promise<{
    procedure_codes: string[];
    estimated_billed_amount: number;
    estimated_allowed_amount: number;
    estimated_member_cost: number;
    breakdown: {
      deductible: number;
      copay: number;
      coinsurance: number;
    };
  }> {
    const response = await this.client.post('/financial/cost-estimates', {
      member_id: memberId,
      procedure_codes: procedureCodes,
      provider_id: providerId,
    });
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export typed hooks for React Query
export default apiClient;