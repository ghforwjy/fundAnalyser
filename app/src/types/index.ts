// 基金类型
export type FundType = '股票型' | '债券型' | '混合型' | '货币型' | '指数型' | 'QDII' | 'FOF';

// 风险等级
export type RiskLevel = 1 | 2 | 3 | 4 | 5;

// 基金基本信息
export interface FundInfo {
  fund_code: string;
  fund_name: string;
  fund_abbr?: string;
  fund_type: FundType;
  sub_type?: string;
  establish_date?: string;
  manager_company?: string;
  custodian?: string;
  benchmark?: string;
  manage_fee_rate?: number;
  custodian_fee_rate?: number;
  risk_level?: RiskLevel;
  min_purchase_amount?: number;
  status: '正常' | '暂停' | '清盘';
  invest_style?: string;
  invest_scope?: string;
  create_time?: string;
  update_time?: string;
}

// 基金净值
export interface FundNav {
  id?: number;
  fund_code: string;
  nav_date: string;
  unit_nav: number;
  accum_nav?: number;
  daily_return?: number;
  subscribe_status?: string;
  redeem_status?: string;
  dividend?: number;
  create_time?: string;
}

// 基金持仓
export interface FundHolding {
  id?: number;
  fund_code: string;
  report_date: string;
  stock_code: string;
  stock_name: string;
  nav_ratio: number;
  share_num?: number;
  market_value?: number;
}

// 基金经理
export interface FundManager {
  manager_id?: number;
  manager_name: string;
  company?: string;
  gender?: string;
  education?: string;
  tenure_days?: number;
  current_fund_count?: number;
  total_asset?: number;
  best_return?: number;
}

// 基金经理任职历史
export interface ManagerFundHistory {
  id?: number;
  manager_id: number;
  fund_code: string;
  begin_date?: string;
  end_date?: string;
  is_current: boolean;
}

// 数据源配置
export interface DataSource {
  id: string;
  name: string;
  type: 'akshare' | 'tushare' | 'custom';
  status: 'normal' | 'error' | 'disabled';
  is_default: boolean;
  config: {
    token?: string;
    base_url?: string;
    api_key?: string;
    [key: string]: any;
  };
  last_update?: string;
  description?: string;
}

// 数据库表结构
export interface TableSchema {
  table_name: string;
  table_comment?: string;
  columns: ColumnInfo[];
  record_count: number;
  last_update?: string;
}

// 字段信息
export interface ColumnInfo {
  column_name: string;
  data_type: string;
  is_nullable: boolean;
  column_default?: string;
  column_comment?: string;
  is_primary?: boolean;
  is_foreign?: boolean;
}

// 基金统计指标
export interface FundStatistics {
  id?: number;
  fund_code: string;
  calc_date: string;
  period: '1M' | '3M' | '6M' | '1Y' | '3Y' | 'ALL';
  cumulative_return?: number;
  annualized_return?: number;
  max_drawdown?: number;
  volatility?: number;
  sharpe_ratio?: number;
  sortino_ratio?: number;
  calmar_ratio?: number;
  alpha?: number;
  beta?: number;
  info_ratio?: number;
  update_time?: string;
}

// 筛选条件
export interface FilterCondition {
  field: string;
  operator: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte' | 'like' | 'in';
  value: any;
}

// 排序条件
export interface SortCondition {
  field: string;
  direction: 'asc' | 'desc';
}

// 分页参数
export interface PaginationParams {
  page: number;
  page_size: number;
  total?: number;
}

// 分页结果
export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

// 导航项
export interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavItem[];
}

// 图表数据点
export interface ChartDataPoint {
  date: string;
  value: number;
  benchmark?: number;
}

// 调仓变动
export interface HoldingChange {
  stock_code: string;
  stock_name: string;
  current_ratio: number;
  previous_ratio: number;
  change: number;
  change_type: 'added' | 'removed' | 'increased' | 'decreased' | 'unchanged';
}

// 行业分布
export interface IndustryAllocation {
  industry: string;
  ratio: number;
}
