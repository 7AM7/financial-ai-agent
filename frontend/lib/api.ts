/**
 * API client for the FastAPI backend.
 * Provides type-safe methods for fetching financial data.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions matching backend Pydantic models
export interface MonthlySummary {
  year: number;
  quarter: number;
  month: number;
  year_month: string;
  year_quarter: string;
  month_name: string;
  account_type: string;
  account_count: number;
  total_amount: number;
  avg_amount: number;
  min_amount: number;
  max_amount: number;
}

export interface CategoryPerformance {
  account_category: string;
  account_type: string;
  year: number;
  quarter: number;
  year_quarter: string;
  account_count: number;
  transaction_count: number;
  total_amount: number;
  avg_amount: number;
  min_amount: number;
  max_amount: number;
}

export interface ProfitLoss {
  year: number;
  quarter: number;
  year_quarter: string;
  revenue: number;
  cogs: number;
  expenses: number;
  gross_profit: number;
  net_profit: number;
  profit_margin_percent: number | null;
}

export interface YoYGrowth {
  account_category: string;
  account_type: string;
  current_year: number;
  current_amount: number;
  previous_amount: number;
  absolute_growth: number;
  growth_percent: number | null;
}

export interface TopAccount {
  account_name: string;
  account_type: string;
  account_category: string;
  year: number;
  quarter?: number;
  year_quarter?: string;
  transaction_count: number;
  total_amount: number;
  avg_amount: number;
  rank_in_type_year?: number;
  rank_in_quarter?: number;
}

export interface TrendAnalysis {
  account_type: string;
  year: number;
  month: number;
  year_month: string;
  month_total: number;
  prev_month_total: number | null;
  mom_change: number | null;
  mom_change_percent: number | null;
}

export interface DashboardOverview {
  profit_loss: ProfitLoss[];
  top_expenses: TopAccount[];
  top_revenue: TopAccount[];
  trends: TrendAnalysis[];
}

export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  answer: string;
  sql_query: string | null;
  results: Record<string, unknown>[] | null;
}

// API Client
export const api = {
  /**
   * Get monthly summary data
   */
  async getMonthlySummary(params?: { year?: number; account_type?: string }): Promise<MonthlySummary[]> {
    const queryParams = new URLSearchParams();
    if (params?.year) queryParams.append('year', params.year.toString());
    if (params?.account_type) queryParams.append('account_type', params.account_type);

    const response = await fetch(`${API_BASE_URL}/api/dashboard/monthly-summary?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch monthly summary');
    const data = await response.json();
    return data.data;
  },

  /**
   * Get category performance data
   */
  async getCategoryPerformance(params?: { account_type?: string }): Promise<CategoryPerformance[]> {
    const queryParams = new URLSearchParams();
    if (params?.account_type) queryParams.append('account_type', params.account_type);

    const response = await fetch(`${API_BASE_URL}/api/dashboard/category-performance?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch category performance');
    const data = await response.json();
    return data.data;
  },

  /**
   * Get profit & loss data
   */
  async getProfitLoss(params?: { year?: number }): Promise<ProfitLoss[]> {
    const queryParams = new URLSearchParams();
    if (params?.year) queryParams.append('year', params.year.toString());

    const response = await fetch(`${API_BASE_URL}/api/dashboard/profit-loss?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch profit & loss');
    const data = await response.json();
    return data.data;
  },

  /**
   * Get year-over-year growth metrics
   */
  async getYoYGrowth(params?: { year?: number }): Promise<YoYGrowth[]> {
    const queryParams = new URLSearchParams();
    if (params?.year) queryParams.append('year', params.year.toString());

    const response = await fetch(`${API_BASE_URL}/api/dashboard/yoy-growth?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch YoY growth');
    const data = await response.json();
    return data.data;
  },

  /**
   * Get top accounts
   */
  async getTopAccounts(params?: {
    account_type?: string;
    year?: number;
    period?: 'yearly' | 'quarterly';
    limit?: number;
  }): Promise<TopAccount[]> {
    const queryParams = new URLSearchParams();
    if (params?.account_type) queryParams.append('account_type', params.account_type);
    if (params?.year) queryParams.append('year', params.year.toString());
    if (params?.period) queryParams.append('period', params.period);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const response = await fetch(`${API_BASE_URL}/api/dashboard/top-accounts?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch top accounts');
    const data = await response.json();
    return data.data;
  },

  /**
   * Get trend analysis
   */
  async getTrendAnalysis(params?: { year?: number; account_type?: string }): Promise<TrendAnalysis[]> {
    const queryParams = new URLSearchParams();
    if (params?.year) queryParams.append('year', params.year.toString());
    if (params?.account_type) queryParams.append('account_type', params.account_type);

    const response = await fetch(`${API_BASE_URL}/api/dashboard/trend-analysis?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch trend analysis');
    const data = await response.json();
    return data.data;
  },

  /**
   * Get dashboard overview (all key metrics in one call)
   */
  async getDashboardOverview(): Promise<DashboardOverview> {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/overview`);
    if (!response.ok) throw new Error('Failed to fetch dashboard overview');
    return response.json();
  },

  /**
   * Query financial data using natural language
   */
  async queryFinancialData(question: string): Promise<QueryResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) throw new Error('Failed to query financial data');
    return response.json();
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return response.json();
  },
};
