/**
 * 数据库字段中文名映射配置
 * 用于数据管理页面的表结构显示
 */

// 通用字段映射（跨表通用）
const commonFieldLabels: Record<string, string> = {
  // ID相关
  id: 'ID',
  cid: '列ID',
  
  // 基金基本信息
  fund_code: '基金代码',
  fund_name: '基金名称',
  fund_full_name: '基金全称',
  fund_type: '基金类型',
  
  // 拼音
  pinyin_abbr: '拼音缩写',
  pinyin_full: '拼音全称',
  
  // 公司信息
  company_name: '基金公司',
  custodian: '托管银行',
  manager_name: '基金经理',
  
  // 日期
  establish_date: '成立日期',
  issue_date: '发行日期',
  nav_date: '净值日期',
  report_date: '报告日期',
  record_date: '记录日期',
  split_date: '拆分日期',
  ex_dividend_date: '除息日',
  payment_date: '分红发放日',
  next_open_date: '下次开放日',
  rank_date: '排行日期',
  transaction_date: '交易日期',
  create_time: '创建时间',
  update_time: '更新时间',
  calc_start_date: '计算开始日期',
  calc_end_date: '计算结束日期',
  data_start_date: '数据开始日期',
  data_end_date: '数据结束日期',
  confirmed_date: '确认日期',
  buy_date: '买入日期',
  
  // 净值相关
  unit_nav: '单位净值',
  accum_nav: '累计净值',
  latest_nav: '最新净值',
  buy_nav: '买入净值',
  nav: '净值',
  
  // 收益相关
  daily_return: '日收益率',
  return_1w: '近一周收益',
  return_1m: '近一月收益',
  return_3m: '近三月收益',
  return_6m: '近六月收益',
  return_1y: '近一年收益',
  return_2y: '近两年收益',
  return_3y: '近三年收益',
  return_this_year: '今年以来收益',
  return_since_inception: '成立以来收益',
  period_return: '期间收益',
  best_return: '最佳收益',
  
  // 规模与金额
  establish_scale: '成立规模',
  total_scale: '管理规模',
  manage_scale: '管理规模',
  market_value: '市值',
  hold_value: '持仓市值',
  hold_shares: '持仓股数',
  shares: '份额',
  amount: '金额',
  min_purchase: '最低申购额',
  daily_limit: '日限额',
  cash: '现金',
  
  // 费率
  manage_fee_rate: '管理费率',
  custodian_fee_rate: '托管费率',
  fee_rate: '费率',
  fee: '手续费',
  
  // 评级
  rating_5star_count: '五星评级数',
  rating_sh: '上海证券评级',
  rating_zs: '招商证券评级',
  rating_ja: '济安金信评级',
  rating_morningstar: '晨星评级',
  rating_tx: '天相评级',
  
  // 风险指标
  risk_return_ratio: '风险收益比',
  risk_resistance: '抗风险能力',
  annual_volatility: '年化波动率',
  annual_volatility_1y: '近一年年化波动率',
  sharpe_ratio: '夏普比率',
  sharpe_ratio_1y: '近一年夏普比率',
  max_drawdown: '最大回撤',
  max_drawdown_1y: '近一年最大回撤',
  
  // 排名
  rank_in_category: '同类排名',
  rank_category: '排名分类',
  
  // 持仓
  stock_code: '股票代码',
  stock_name: '股票名称',
  bond_code: '债券代码',
  bond_name: '债券名称',
  hold_ratio: '持仓比例',
  
  // 行业
  industry_name: '行业名称',
  allocation_ratio: '配置比例',
  
  // 分红拆分
  dividend_per_share: '每股分红',
  split_ratio: '拆分比例',
  split_type: '拆分类型',
  year: '年份',
  quarter: '季度',
  
  // 状态
  status: '状态',
  subscribe_status: '申购状态',
  redeem_status: '赎回状态',
  
  // 其他
  benchmark: '业绩基准',
  invest_scope: '投资范围',
  track_target: '跟踪标的',
  data_source: '数据来源',
  period: '周期',
  performance_type: '业绩类型',
  asset_type: '资产类型',
  description: '描述',
  notes: '备注',
  name: '名称',
  
  // 持仓历史
  shares_change: '份额变动',
  
  // 交易
  transaction_type: '交易类型',
  portfolio_id: '组合ID',
  
  // 指标更新时间
  metrics_update_time: '指标更新时间',
  
  // 交易相关
  trading_days: '交易日数',
  
  // 指数基准
  index_code: '指数代码',
  index_name: '指数名称',
  market_phase: '市场阶段',
  avg_monthly_return: '月均收益',
  monthly_return_std: '月收益标准差',
  sample_months: '样本月数',
  phase_name: '阶段名称',
  is_current: '是否当前',
  is_trade_day: '是否交易日',
  trade_date: '交易日期',
  
  // 表元数据
  table_name: '表名',
  last_sync_time: '最后同步时间',
  record_count: '记录数',
  last_sync_status: '同步状态',
  last_error: '最后错误',
  
  // 数据库字段属性
  type: '数据类型',
  notnull: '非空',
  dflt_value: '默认值',
  pk: '主键',
  unique: '唯一',
  origin: '来源',
  partial: '部分',
  seq: '序号',
  
  // 持仓收益
  profit_loss: '盈亏金额',
  profit_rate: '收益率',
  total_profit: '总收益',
  total_cost: '总成本',
  total_market_value: '总市值',
  current_value: '当前市值',
  cost_nav: '成本净值',
  import_date: '导入日期',
  import_source: '导入来源',
  
  // 基金经理
  tenure_days: '任职天数',
  fund_count: '基金数量',
  manager_count: '经理人数',
};

// 表特定的字段映射（当与通用映射冲突时使用）
const tableSpecificFieldLabels: Record<string, Record<string, string>> = {
  portfolio: {
    name: '组合名称',
    description: '组合描述',
  },
  portfolio_fund: {
    name: '基金名称',
  },
  fund_company: {
    name: '公司名称',
    description: '公司描述',
  },
  fund_manager: {
    name: '经理姓名',
  },
  index_benchmark: {
    name: '指数名称',
  },
  market_phase_record: {
    name: '阶段名称',
  },
};

/**
 * 获取字段的中文名
 * @param fieldName 字段英文名
 * @param tableName 表名（可选，用于表特定映射）
 * @returns 字段中文名
 */
export function getFieldLabel(fieldName: string, tableName?: string): string {
  // 优先使用表特定映射
  if (tableName && tableSpecificFieldLabels[tableName]?.[fieldName]) {
    return tableSpecificFieldLabels[tableName][fieldName];
  }
  
  // 使用通用映射
  return commonFieldLabels[fieldName] || fieldName;
}

/**
 * 获取表的中文名
 * @param tableName 表英文名
 * @returns 表中文名
 */
export function getTableLabel(tableName: string): string {
  const tableLabels: Record<string, string> = {
    fund_info: '基金基本信息',
    fund_nav: '基金净值',
    fund_stock_holding: '股票持仓',
    fund_bond_holding: '债券持仓',
    fund_industry_allocation: '行业配置',
    fund_risk_metrics: '风险指标',
    fund_performance: '业绩表现',
    fund_rating: '基金评级',
    fund_manager: '基金经理',
    fund_company: '基金公司',
    fund_dividend: '基金分红',
    fund_split: '基金拆分',
    fund_rank: '基金排行',
    fund_purchase_status: '申购状态',
    fund_asset_allocation: '资产配置',
    portfolio: '投资组合',
    portfolio_fund: '组合持仓基金',
    holding_history: '持仓历史',
    portfolio_transaction: '交易记录',
    fund_data_meta: '数据元信息',
    trade_calendar: '交易日历',
    index_benchmark: '指数基准',
    market_phase_record: '市场阶段记录',
  };
  
  return tableLabels[tableName] || tableName;
}

export default {
  getFieldLabel,
  getTableLabel,
  commonFieldLabels,
  tableSpecificFieldLabels,
};
