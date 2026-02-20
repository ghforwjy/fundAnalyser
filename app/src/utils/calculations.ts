/**
 * 投资组合计算工具函数
 * 所有成本、收益计算都使用这里的函数，确保算法一致
 */

/**
 * 计算成本单价
 * @param shares 持有份额
 * @param nav 最新净值
 * @param profit 持有收益/盈利（正数表示盈利，负数表示亏损）
 * @returns 成本单价
 */
export function calculateCostPrice(shares: number, nav: number, profit: number): number {
  if (shares <= 0 || nav <= 0) return 0;
  // 成本 = (份额 * 净值 - 盈利) / 份额
  // 盈利为正时，成本 = (市值 - 盈利) / 份额
  // 盈利为负时，成本 = (市值 - (-亏损)) / 份额 = (市值 + 亏损) / 份额
  const marketValue = shares * nav;
  const cost = marketValue - profit;
  return cost / shares;
}

/**
 * 计算市值
 * @param shares 持有份额
 * @param nav 最新净值
 * @returns 市值
 */
export function calculateMarketValue(shares: number, nav: number): number {
  if (shares <= 0 || nav <= 0) return 0;
  return shares * nav;
}

/**
 * 计算总收益
 * @param shares 持有份额
 * @param nav 最新净值
 * @param costPrice 成本单价
 * @returns 总收益
 */
export function calculateTotalProfit(shares: number, nav: number, costPrice: number): number {
  if (shares <= 0 || nav <= 0 || costPrice <= 0) return 0;
  const marketValue = shares * nav;
  const totalCost = shares * costPrice;
  return marketValue - totalCost;
}

/**
 * 计算收益率
 * @param nav 最新净值
 * @param costPrice 成本单价
 * @returns 收益率（百分比）
 */
export function calculateProfitRate(nav: number, costPrice: number): number {
  if (nav <= 0 || costPrice <= 0) return 0;
  return ((nav - costPrice) / costPrice) * 100;
}
