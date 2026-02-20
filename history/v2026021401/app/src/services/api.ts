/**
 * API服务 - 连接后端真实接口
 */

const API_BASE_URL = 'http://localhost:8000/api';

// 通用请求函数
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ==================== 数据源管理 API ====================

export interface DataSource {
  id: number;
  source_name: string;
  source_type: string;
  base_url: string;
  api_key: string;
  is_active: boolean;
  is_connected: boolean;
  last_test_time: string;
  last_test_result: string;
  last_error: string;
  description: string;
  rate_limit: number;
}

export const dataSourceApi = {
  // 获取所有数据源
  getAll: () => request<{ success: boolean; data: DataSource[] }>('/datasource'),

  // 测试数据源连接
  test: (sourceName: string) => 
    request<{ success: boolean; message: string; record_count: number }>(`/datasource/${sourceName}/test`, {
      method: 'POST',
    }),

  // 更新数据源配置
  updateConfig: (sourceName: string, apiKey: string) =>
    request<{ success: boolean; message: string }>(`/datasource/${sourceName}/config`, {
      method: 'POST',
      body: JSON.stringify({ api_key: apiKey }),
    }),
};

// ==================== 数据同步 API ====================

export interface SyncStatus {
  table_name: string;
  data_source: string;
  last_sync_time: string;
  last_sync_date: string;
  last_sync_status: string;
  total_records: number;
  last_update_records: number;
  next_sync_time: string;
  sync_interval: number;
}

export interface UpdateLog {
  id: number;
  table_name: string;
  update_type: string;
  data_source: string;
  start_time: string;
  end_time: string;
  record_count: number;
  success_count: number;
  fail_count: number;
  status: string;
  message: string;
}

export const syncApi = {
  // 获取同步状态
  getStatus: () => request<{ success: boolean; data: SyncStatus[] }>('/sync/status'),

  // 同步基金基本信息
  syncFundBasic: (limit?: number) =>
    request<{ success: boolean; data: any; message: string }>('/sync/fund-basic', {
      method: 'POST',
      body: JSON.stringify({ limit }),
    }),

  // 同步基金净值
  syncFundNav: (fundCodes?: string[]) =>
    request<{ success: boolean; data: any; message: string }>('/sync/fund-nav', {
      method: 'POST',
      body: JSON.stringify({ fund_codes: fundCodes }),
    }),

  // 同步单只基金净值
  syncSingleFundNav: (fundCode: string, days?: number) =>
    request<{ success: boolean; data: any; message: string }>(`/sync/fund-nav/${fundCode}?days=${days || 365}`, {
      method: 'POST',
    }),

  // 获取同步日志
  getLogs: (limit?: number) =>
    request<{ success: boolean; data: UpdateLog[] }>(`/sync/logs?limit=${limit || 50}`),
};

// ==================== 数据库管理 API ====================

export interface TableInfo {
  table_name: string;
  index_count: number;
}

export interface TableDetail {
  table_name: string;
  columns: Array<{
    cid: number;
    name: string;
    type: string;
    notnull: number;
    dflt_value: any;
    pk: number;
  }>;
  indexes: Array<{
    seq: number;
    name: string;
    unique: number;
    origin: string;
    partial: number;
  }>;
  record_count: number;
  foreign_keys: any[];
}

export interface PageResult<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const dbApi = {
  // 获取所有表
  getTables: () => request<{ success: boolean; data: TableInfo[] }>('/db/tables'),

  // 获取表详情
  getTableInfo: (tableName: string) =>
    request<{ success: boolean; data: TableDetail }>(`/db/tables/${tableName}`),

  // 获取表数据
  getTableData: (tableName: string, page?: number, pageSize?: number) =>
    request<{ success: boolean; data: PageResult<any> }>(
      `/db/tables/${tableName}/data?page=${page || 1}&page_size=${pageSize || 50}`
    ),
};

// ==================== 基金查询 API ====================

export interface FundInfo {
  fund_code: string;
  fund_name: string;
  fund_abbr: string;
  fund_type: string;
  sub_type: string;
  establish_date: string;
  manager_company: string;
  custodian: string;
  manager_name: string;
  benchmark: string;
  manage_fee_rate: number;
  custodian_fee_rate: number;
  risk_level: number;
  min_purchase_amount: number;
  subscribe_status: string;
  redeem_status: string;
  status: string;
  latest_nav?: number;
  latest_return?: number;
  nav_date?: string;
}

export interface FundNav {
  fund_code: string;
  trade_date: string;
  unit_nav: number;
  accum_nav: number;
  adj_nav: number;
  daily_return: number;
  subscribe_status: string;
  redeem_status: string;
}

export interface FundHolding {
  stock_code: string;
  stock_name: string;
  nav_ratio: number;
  share_count: number;
  market_value: number;
  rank_num: number;
  sector_name: string;
  change_type: string;
}

export interface FundMetrics {
  total_return: number;
  annualized_return: number;
  return_1m: number;
  return_3m: number;
  return_6m: number;
  return_1y: number;
  volatility: number;
  max_drawdown: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  beta: number;
}

export const fundApi = {
  // 获取基金列表
  getList: (params?: {
    page?: number;
    page_size?: number;
    fund_type?: string;
    manager_company?: string;
    risk_level?: number;
    keyword?: string;
    order_by?: string;
    order_dir?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });
    }
    return request<{ success: boolean; data: PageResult<FundInfo> }>(`/funds?${queryParams.toString()}`);
  },

  // 获取基金详情
  getDetail: (fundCode: string) =>
    request<{ success: boolean; data: { basic_info: FundInfo; latest_nav: FundNav; metrics: any } }>(`/funds/${fundCode}`),

  // 获取净值历史
  getNavHistory: (fundCode: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request<{ success: boolean; data: FundNav[] }>(`/funds/${fundCode}/nav${query}`);
  },

  // 获取持仓
  getHoldings: (fundCode: string, reportDate?: string) => {
    const params = reportDate ? `?report_date=${reportDate}` : '';
    return request<{ success: boolean; data: FundHolding[] }>(`/funds/${fundCode}/holdings${params}`);
  },

  // 获取行业配置
  getIndustryAllocation: (fundCode: string, reportDate?: string) => {
    const params = reportDate ? `?report_date=${reportDate}` : '';
    return request<{ success: boolean; data: any[] }>(`/funds/${fundCode}/industry${params}`);
  },
};

// ==================== 筛选选项 API ====================

export const filterApi = {
  // 获取基金类型
  getFundTypes: () => request<{ success: boolean; data: string[] }>('/filters/fund-types'),

  // 获取基金公司
  getCompanies: () => request<{ success: boolean; data: string[] }>('/filters/companies'),
};

// ==================== 指标计算 API ====================

export const metricsApi = {
  // 计算单只基金指标
  calculate: (fundCode: string, periodType?: string) =>
    request<{ success: boolean; data: any; message: string }>(`/metrics/calculate/${fundCode}?period_type=${periodType || '1Y'}`, {
      method: 'POST',
    }),

  // 批量计算指标
  batchCalculate: (fundCodes?: string[]) =>
    request<{ success: boolean; data: any; message: string }>('/metrics/calculate-batch', {
      method: 'POST',
      body: JSON.stringify(fundCodes || []),
    }),
};

// ==================== 仪表盘 API ====================

export interface DashboardStats {
  fund_stats: {
    total_funds: number;
    type_count: number;
    company_count: number;
  };
  nav_stats: {
    total_records: number;
    covered_funds: number;
    latest_date: string;
  };
  sync_status: {
    total_tables: number;
    synced_tables: number;
  };
  recent_sync: SyncStatus[];
}

export const dashboardApi = {
  // 获取统计数据
  getStats: () => request<{ success: boolean; data: DashboardStats }>('/dashboard/stats'),
};

export default {
  dataSource: dataSourceApi,
  sync: syncApi,
  db: dbApi,
  fund: fundApi,
  filter: filterApi,
  metrics: metricsApi,
  dashboard: dashboardApi,
};
