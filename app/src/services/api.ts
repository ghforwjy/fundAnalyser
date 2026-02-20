/**
 * API服务 - 连接后端真实接口
 * 已重构为使用fundData skill的数据库
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
  description: string;
  is_active: boolean;
  is_connected: boolean;
  fund_count: number;
  nav_count: number;
  note: string;
}

export interface DataStats {
  total_funds: number;
  total_nav_records: number;
  nav_coverage: number;
  stock_holdings: number;
  total_portfolios: number;
  total_portfolio_funds: number;
}

export const dataSourceApi = {
  // 获取数据源信息
  getAll: () => request<{ success: boolean; data: DataSource[] }>('/datasource'),

  // 获取数据统计
  getStats: () => request<{ success: boolean; data: DataStats }>('/datasource/stats'),
};

// ==================== 数据库管理 API ====================

export interface TableInfo {
  table_name: string;
  index_count: number;
  record_count: number;
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

  // 获取表数据（支持后端搜索和排序）
  getTableData: (params: {
    tableName: string;
    page?: number;
    pageSize?: number;
    search?: string;
    sortField?: string;
    sortDir?: string;
  }) => {
    const queryParams = new URLSearchParams();
    queryParams.append('page', String(params.page || 1));
    queryParams.append('page_size', String(params.pageSize || 20));
    if (params.search) queryParams.append('search', params.search);
    if (params.sortField) queryParams.append('sort_field', params.sortField);
    if (params.sortDir) queryParams.append('sort_dir', params.sortDir);
    return request<{ success: boolean; data: PageResult<any> }>(
      `/db/tables/${params.tableName}/data?${queryParams.toString()}`
    );
  },
};

// ==================== 基金查询 API ====================

export interface FundInfo {
  fund_code: string;
  fund_name: string;
  fund_full_name?: string;
  fund_type: string;
  pinyin_abbr?: string;
  pinyin_full?: string;
  company_name?: string;
  custodian?: string;
  issue_date?: string;
  establish_date?: string;
  establish_scale?: number;
  manage_fee_rate?: number;
  custodian_fee_rate?: number;
  benchmark?: string;
  invest_scope?: string;
  track_target?: string;
  status?: string;
  latest_nav?: number;
  nav_date?: string;
}

export interface FundNav {
  fund_code: string;
  nav_date: string;
  unit_nav: number;
  accum_nav: number;
  daily_return: number;
}

export interface FundHolding {
  stock_code: string;
  stock_name: string;
  hold_ratio: number;
  hold_shares: number;
  hold_value: number;
  quarter: string;
  report_date?: string;
}

export const fundApi = {
  // 获取基金列表
  getList: (params?: {
    page?: number;
    page_size?: number;
    fund_type?: string;
    company_name?: string;
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
    request<{ success: boolean; data: FundInfo }>(`/funds/${fundCode}`),

  // 获取净值历史
  getNavHistory: (fundCode: string, limit?: number, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', String(limit));
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request<{ success: boolean; data: { nav: FundNav[] } }>(`/funds/${fundCode}/nav${query}`);
  },

  // 获取持仓
  getHoldings: (fundCode: string, reportDate?: string, year?: string) => {
    const params = new URLSearchParams();
    if (reportDate) params.append('report_date', reportDate);
    if (year) params.append('year', year);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request<{ success: boolean; data: FundHolding[] }>(`/funds/${fundCode}/holdings${query}`);
  },

  // 获取行业配置
  getIndustryAllocation: (fundCode: string, year?: string) => {
    const params = new URLSearchParams();
    if (year) params.append('year', year);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request<{ success: boolean; data: any[] }>(`/funds/${fundCode}/industry${query}`);
  },

  // 获取业绩表现
  getPerformance: (fundCode: string) =>
    request<{ success: boolean; data: any[] }>(`/funds/${fundCode}/performance`),
};

// ==================== 筛选选项 API ====================

export const filterApi = {
  // 获取基金类型
  getFundTypes: () => request<{ success: boolean; data: string[] }>('/filters/fund-types'),

  // 获取基金公司
  getCompanies: () => request<{ success: boolean; data: string[] }>('/filters/companies'),

  // 获取基金经理
  getManagers: () => request<{ success: boolean; data: string[] }>('/filters/managers'),
};

// ==================== 投资组合 API ====================

export interface FundGroup {
  id: number;
  name: string;
  description: string;
  fund_count: number;
  create_time: string;
  update_time: string;
}

export interface GroupFund {
  id: number;
  portfolio_id: number;
  fund_code: string;
  fund_name: string;
  fund_type: string;
  company_name: string;
  shares?: number;
  buy_date?: string;
  buy_nav?: number;
  amount?: number;
  latest_nav?: number;
  nav_date?: string;
  market_value?: number;
  profit_rate?: number;
  available_cash?: number;      // 可用现金（实时计算：卖出所得 - 买入投入）
  total_buy_amount?: number;    // 总买入金额
  total_sell_amount?: number;   // 总卖出金额
}

export interface PortfolioSummary {
  position_count: number;
  total_cost: number;
  total_market_value: number;
  total_profit: number;
  total_profit_rate: number;
}

// 定投模式
export interface InvestmentMode {
  id: string;
  name: string;
  name_en: string;
  description: string;
  icon: string;
  enabled: boolean;
}

// 基金投资建议
export interface FundInvestmentAdvice {
  fund_code: string;
  fund_name: string;
  base_date: string;
  target_date: string;
  days_diff: number;
  shares_at_base: number;
  nav_at_base: number;
  base_value: number;
  current_shares: number;
  latest_nav: number;
  actual_value: number;
  avg_monthly_return: number;
  target_growth: number;
  target_value: number;
  suggested_invest: number;
  invest_action: string;
  original_holding_value: number;
  original_holding_profit: number;
  market_phase: string;
  algorithm_details: string[];
  error?: string;
}

// 投资组合建议
export interface InvestmentAdvice {
  portfolio_id: number;
  portfolio_name: string;
  mode: string;
  mode_name: string;
  base_date: string;
  target_date: string;
  funds: FundInvestmentAdvice[];
  summary: {
    total_funds: number;
    total_holding_value: number;
    total_suggested_invest: number;
    simulate: boolean;
  };
}

// 交易记录
export interface Transaction {
  id: number;
  portfolio_id: number;
  fund_code: string;
  fund_name: string;
  transaction_type: 'BUY' | 'SELL';
  transaction_date: string;
  shares: number;
  amount: number;
  nav?: number;
  fee?: number;
  notes?: string;
  create_time: string;
}

// 交易请求
export interface TransactionRequest {
  fund_code: string;
  transaction_type: 'BUY' | 'SELL';
  transaction_date: string;
  shares: number;
  amount: number;
  nav?: number;
  fee?: number;
  notes?: string;
}

// 盈亏导入请求
export interface ProfitImportRequest {
  profit_data: Array<{
    fund_code: string;
    fund_name?: string;
    profit_loss: number;  // 盈亏金额（正数表示盈利，负数表示亏损）
    // current_value 由后端自动计算：shares × latest_nav
  }>;
  import_mode: 'overwrite' | 'accumulate';
  import_date?: string;
}

// 现金信息
export interface CashInfo {
  portfolio_id: number;
  portfolio_name: string;
  cash: number;
}

// 止盈参数模板
export interface TakeProfitTemplate {
  id: number;
  name: string;
  description?: string;
  first_threshold: number;
  first_sell_ratio: number;
  step_size: number;
  follow_up_sell_ratio: number;
  enable_cost_control: number;
  target_diluted_cost: number;
  enable_buy_back: number;        // 是否启用波段捡回
  buy_back_threshold: number;     // 捡回阈值
  is_default: number;
  is_system: number;
  create_time?: string;
  update_time?: string;
}

// 基金止盈配置
export interface FundTakeProfitConfig {
  portfolio_id: number;
  fund_code: string;
  fund_name?: string;
  param_source: string;
  template_id?: number;
  template_name?: string;
  first_threshold: number;
  first_sell_ratio: number;
  step_size: number;
  follow_up_sell_ratio: number;
  enable_cost_control: boolean;
  target_diluted_cost: number;
  enable_buy_back: boolean;       // 是否启用波段捡回
  buy_back_threshold: number;     // 捡回阈值
}

// 基金止盈结果
export interface TakeProfitFundResult {
  fund_code: string;
  fund_name: string;
  current_shares: number;
  current_nav: number;
  current_value: number;
  buy_nav: number;
  current_profit_rate: number;
  has_sell_record: boolean;
  last_sell_nav: number | null;
  last_sell_date: string | null;
  diluted_cost: number | null;
  available_cash: number;                    // 可用现金（仅显示参考）
  action: string;                           // SELL / HOLD / STOP / BUY / ERROR
  sell_ratio: number | null;
  sell_shares: number | null;
  sell_amount: number | null;                // 卖出金额
  reason: string;
  param_source: string;
  template_name: string | null;
  algorithm_details: string[];
  // 波段捡回专属字段
  buy_back_shares?: number | null;           // 建议买回的份额
  buy_back_amount?: number | null;           // 预计花费金额
  unrecovered_sells_count?: number;          // 剩余未回收的卖出笔数
  target_sell_nav?: number | null;           // 目标卖出净值（用于计算跌幅）
  decline_rate?: number | null;              // 当前跌幅
}

// 止盈建议
export interface TakeProfitAdvice {
  portfolio_id: number;
  mode: string;
  mode_name: string;
  params: {
    first_threshold: number;
    first_sell_ratio: number;
    step_size: number;
    follow_up_sell_ratio: number;
    enable_cost_control: boolean;
    target_diluted_cost: number;
    enable_buy_back: boolean;           // 是否启用波段捡回
    buy_back_threshold: number;         // 捡回阈值
  };
  funds: TakeProfitFundResult[];
  summary: {
    total_funds: number;
    need_action_count: number;
    hold_count: number;
    stop_count: number;
    buy_back_count: number;             // 建议捡回数量
    error_count: number;
    total_sell_amount: number;          // 预计卖出金额
    total_buy_back_amount: number;      // 预计捡回金额
  };
}

export const portfolioApi = {
  // 分组管理
  getGroups: () => request<{ success: boolean; data: FundGroup[] }>('/portfolio/groups'),

  createGroup: (data: { name: string; description?: string }) =>
    request<{ success: boolean; data: FundGroup }>('/portfolio/groups', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateGroup: (groupId: number, data: { name?: string; description?: string }) =>
    request<{ success: boolean; message: string }>(`/portfolio/groups/${groupId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteGroup: (groupId: number) =>
    request<{ success: boolean; message: string }>(`/portfolio/groups/${groupId}`, {
      method: 'DELETE',
    }),

  // 分组基金操作
  getGroupFunds: (groupId: number, forceRefresh: boolean = false) =>
    request<{ success: boolean; data: GroupFund[]; freshness_summary?: {
      nav_fresh_count: number;
      metrics_fresh_count: number;
      metrics_updated_count: number;
      total_funds: number;
    } }>(`/portfolio/groups/${groupId}/funds?force_refresh=${forceRefresh}`),

  addFundToGroup: (groupId: number, data: {
    fund_code: string;
    fund_name?: string;
    shares?: number;
    buy_date?: string;
    buy_nav?: number;
    amount?: number;
  }) =>
    request<{ success: boolean; message: string }>(`/portfolio/groups/${groupId}/funds`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  removeFundFromGroup: (groupId: number, fundCode: string) =>
    request<{ success: boolean; message: string }>(`/portfolio/groups/${groupId}/funds/${fundCode}`, {
      method: 'DELETE',
    }),

  getFundGroups: (fundCode: string) =>
    request<{ success: boolean; data: FundGroup[] }>(`/portfolio/funds/${fundCode}/groups`),

  // 持仓历史
  getGroupHistory: (groupId: number, limit?: number) =>
    request<{ success: boolean; data: any[] }>(`/portfolio/groups/${groupId}/history?limit=${limit || 100}`),

  // 刷新组合数据
  refreshGroupData: (groupId: number) =>
    request<{
      success: boolean;
      message: string;
      data: {
        updated: number;
        total: number;
      };
    }>(`/portfolio/groups/${groupId}/refresh`, {
      method: 'POST',
    }),

  // 组合汇总
  getPortfolioSummary: (groupId?: number) => {
    const queryParams = groupId !== undefined ? `?group_id=${groupId}` : '';
    return request<{ success: boolean; data: PortfolioSummary }>(`/portfolio/summary${queryParams}`);
  },

  // 图片识别
  recognizeImage: (imageBase64: string) =>
    request<{
      success: boolean;
      data: Array<{
        fundCode: string;
        fundName: string;
        shares: number;
        nav: number;
        amount: number;
      }>;
      message: string;
    }>('/portfolio/recognize-image', {
      method: 'POST',
      body: JSON.stringify({ image_base64: imageBase64 }),
    }),

  // 获取定投模式列表
  getInvestmentModes: () =>
    request<{ success: boolean; data: InvestmentMode[] }>('/portfolio/investment-modes'),

  // 获取投资建议
  getInvestmentAdvice: (groupId: number, mode: string, simulate: boolean = true) =>
    request<{ success: boolean; data: InvestmentAdvice; message?: string }>(
      `/portfolio/groups/${groupId}/investment-advice?mode=${mode}&simulate=${simulate}`,
      { method: 'POST' }
    ),

  // 交易维护
  recordTransaction: (groupId: number, data: TransactionRequest) =>
    request<{ success: boolean; data: any; message?: string }>(`/portfolio/groups/${groupId}/transactions`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getTransactions: (groupId: number, params?: {
    fund_code?: string;
    transaction_type?: 'BUY' | 'SELL';
    start_date?: string;
    end_date?: string;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.fund_code) queryParams.append('fund_code', params.fund_code);
    if (params?.transaction_type) queryParams.append('transaction_type', params.transaction_type);
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return request<{ success: boolean; data: Transaction[] }>(`/portfolio/groups/${groupId}/transactions${query}`);
  },

  // 盈亏导入
  importProfitData: (groupId: number, data: ProfitImportRequest) =>
    request<{ success: boolean; data: any; message?: string }>(`/portfolio/groups/${groupId}/profit-import`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 现金管理
  getCash: (groupId: number) =>
    request<{ success: boolean; data: CashInfo }>(`/portfolio/groups/${groupId}/cash`),

  updateCash: (groupId: number, cash: number) =>
    request<{ success: boolean; data: CashInfo }>(`/portfolio/groups/${groupId}/cash?cash=${cash}`, {
      method: 'PUT',
    }),

  // ==================== 止盈参数模板 ====================

  getTakeProfitTemplates: () =>
    request<{ success: boolean; data: TakeProfitTemplate[] }>('/portfolio/take-profit-templates'),

  getTakeProfitTemplate: (templateId: number) =>
    request<{ success: boolean; data: TakeProfitTemplate }>(`/portfolio/take-profit-templates/${templateId}`),

  createTakeProfitTemplate: (data: {
    name: string;
    description?: string;
    first_threshold?: number;
    first_sell_ratio?: number;
    step_size?: number;
    follow_up_sell_ratio?: number;
    enable_cost_control?: boolean;
    target_diluted_cost?: number;
  }) =>
    request<{ success: boolean; data: { template_id: number }; message?: string }>('/portfolio/take-profit-templates', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTakeProfitTemplate: (templateId: number, data: Partial<{
    name: string;
    description: string;
    first_threshold: number;
    first_sell_ratio: number;
    step_size: number;
    follow_up_sell_ratio: number;
    enable_cost_control: boolean;
    target_diluted_cost: number;
    enable_buy_back: boolean;
    buy_back_threshold: number;
  }>) =>
    request<{ success: boolean; message: string }>(`/portfolio/take-profit-templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteTakeProfitTemplate: (templateId: number) =>
    request<{ success: boolean; message: string }>(`/portfolio/take-profit-templates/${templateId}`, {
      method: 'DELETE',
    }),

  setDefaultTakeProfitTemplate: (templateId: number) =>
    request<{ success: boolean; message: string }>(`/portfolio/take-profit-templates/${templateId}/set-default`, {
      method: 'POST',
    }),

  // ==================== 基金止盈配置 ====================

  getFundTakeProfitConfig: (groupId: number, fundCode: string) =>
    request<{ success: boolean; data: FundTakeProfitConfig }>(`/portfolio/groups/${groupId}/funds/${fundCode}/take-profit-config`),

  setFundTakeProfitConfig: (groupId: number, fundCode: string, data: {
    template_id?: number;
    use_custom?: boolean;
    custom_first_threshold?: number;
    custom_first_sell_ratio?: number;
    custom_step_size?: number;
    custom_follow_up_sell_ratio?: number;
    custom_enable_cost_control?: boolean;
    custom_target_diluted_cost?: number;
  }) =>
    request<{ success: boolean; message: string }>(`/portfolio/groups/${groupId}/funds/${fundCode}/take-profit-config`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  resetFundTakeProfitConfig: (groupId: number, fundCode: string) =>
    request<{ success: boolean; message: string }>(`/portfolio/groups/${groupId}/funds/${fundCode}/take-profit-config`, {
      method: 'DELETE',
    }),

  getPortfolioTakeProfitConfigs: (groupId: number) =>
    request<{ success: boolean; data: FundTakeProfitConfig[] }>(`/portfolio/groups/${groupId}/take-profit-configs`),

  // ==================== 止盈建议 ====================

  getTakeProfitAdvice: (groupId: number) =>
    request<{ success: boolean; data: TakeProfitAdvice; message?: string }>(`/portfolio/groups/${groupId}/take-profit-advice`),

  // ==================== 波段捡回交易 ====================

  executeBuyBackTransaction: (groupId: number, fundCode: string, data: {
    target_sell_transaction_id: number;
    shares: number;
    amount: number;
    nav?: number;
    transaction_date?: string;
    fee?: number;
    notes?: string;
  }) =>
    request<{
      success: boolean;
      message: string;
      data?: {
        success: boolean;
        transaction_type: string;
        fund_code: string;
        fund_name: string;
        shares: number;
        amount: number;
        target_sell_transaction_id: number;
        buy_transaction_id: number;
        new_cash_balance: number;
        transaction_date: string;
      }
    }>(`/portfolio/groups/${groupId}/funds/${fundCode}/buy-back`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// ==================== 标签管理 API ====================

export interface Tag {
  id: number;
  name: string;
  category?: string;
  color?: string;
  create_time?: string;
  update_time?: string;
}

export const tagApi = {
  // 获取所有标签
  getAll: (category?: string) => {
    const queryParams = category ? `?category=${encodeURIComponent(category)}` : '';
    return request<{ success: boolean; data: Tag[] }>(`/funds/tags/all${queryParams}`);
  },

  // 搜索标签
  search: (keyword: string) =>
    request<{ success: boolean; data: Tag[] }>(`/funds/tags/search?keyword=${encodeURIComponent(keyword)}`),

  // 获取标签分类
  getCategories: () =>
    request<{ success: boolean; data: string[] }>(`/funds/tags/categories`),

  // 创建标签
  create: (data: { name: string; category?: string; color?: string }) =>
    request<{ success: boolean; data: Tag; message?: string }>('/funds/tags', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 更新标签
  update: (tagId: number, data: { name?: string; category?: string; color?: string }) =>
    request<{ success: boolean; message: string }>(`/funds/tags/${tagId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // 删除标签
  delete: (tagId: number) =>
    request<{ success: boolean; message: string }>(`/funds/tags/${tagId}`, {
      method: 'DELETE',
    }),

  // 获取基金标签
  getFundTags: (fundCode: string) =>
    request<{ success: boolean; data: Tag[] }>(`/funds/${fundCode}/tags`),

  // 设置基金标签（覆盖式）
  setFundTags: (fundCode: string, tagIds: number[]) =>
    request<{ success: boolean; message: string }>(`/funds/${fundCode}/tags`, {
      method: 'PUT',
      body: JSON.stringify({ tag_ids: tagIds }),
    }),

  // 添加单个标签
  addFundTag: (fundCode: string, tagId: number) =>
    request<{ success: boolean; message: string }>(`/funds/${fundCode}/tags/${tagId}`, {
      method: 'POST',
    }),

  // 移除单个标签
  removeFundTag: (fundCode: string, tagId: number) =>
    request<{ success: boolean; message: string }>(`/funds/${fundCode}/tags/${tagId}`, {
      method: 'DELETE',
    }),
};

export default {
  dataSource: dataSourceApi,
  db: dbApi,
  fund: fundApi,
  filter: filterApi,
  portfolio: portfolioApi,
  tag: tagApi,
};
