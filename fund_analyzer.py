"""
基金分析工具库 - FundAnalyzer

提供完整的基金分析指标计算方法，包括：
- 收益率计算（累计、年化、区间收益率等）
- 风险指标计算（最大回撤、波动率、VaR等）
- 风险调整收益指标（夏普比率、索提诺比率等）
- 基准比较（Alpha、Beta、跟踪误差等）
- 持仓分析（集中度、行业配置、调仓检测）
- 基金经理评估

作者: Fund Analyst
版本: 1.0.0
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# 数据类定义
# =============================================================================

@dataclass
class FundMetrics:
    """基金指标数据类"""
    # 基本信息
    fund_code: str = ""
    fund_name: str = ""
    analysis_date: datetime = None
    
    # 收益率指标
    total_return: float = 0.0
    total_return_pct: float = 0.0
    annualized_return: float = 0.0
    annualized_return_pct: float = 0.0
    
    # 风险指标
    volatility: float = 0.0
    volatility_pct: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    max_drawdown_start: datetime = None
    max_drawdown_end: datetime = None
    max_drawdown_days: int = 0
    recovery_days: Optional[int] = None
    downside_deviation: float = 0.0
    downside_deviation_pct: float = 0.0
    var_95: float = 0.0
    var_95_pct: float = 0.0
    cvar_95: float = 0.0
    cvar_95_pct: float = 0.0
    
    # 风险调整收益指标
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    treynor_ratio: float = 0.0
    information_ratio: float = 0.0
    
    # 基准比较
    alpha: float = 0.0
    alpha_pct: float = 0.0
    beta: float = 1.0
    tracking_error: float = 0.0
    tracking_error_pct: float = 0.0
    excess_return: float = 0.0
    excess_return_pct: float = 0.0
    r_squared: float = 0.0
    correlation: float = 0.0
    
    # 其他指标
    win_rate: float = 0.0
    win_rate_pct: float = 0.0
    positive_ratio: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'fund_code': self.fund_code,
            'fund_name': self.fund_name,
            'analysis_date': self.analysis_date,
            'total_return': self.total_return,
            'total_return_pct': self.total_return_pct,
            'annualized_return': self.annualized_return,
            'annualized_return_pct': self.annualized_return_pct,
            'volatility': self.volatility,
            'volatility_pct': self.volatility_pct,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_pct': self.max_drawdown_pct,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'treynor_ratio': self.treynor_ratio,
            'information_ratio': self.information_ratio,
            'alpha': self.alpha,
            'beta': self.beta,
            'tracking_error': self.tracking_error,
            'excess_return': self.excess_return,
            'win_rate': self.win_rate
        }


@dataclass
class DrawdownInfo:
    """回撤信息数据类"""
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    start_date: datetime = None
    end_date: datetime = None
    drawdown_days: int = 0
    recovery_date: Optional[datetime] = None
    recovery_days: Optional[int] = None
    drawdown_series: pd.Series = field(default_factory=pd.Series)


@dataclass
class ConcentrationInfo:
    """持仓集中度信息"""
    top3_concentration: float = 0.0
    top3_concentration_pct: float = 0.0
    top5_concentration: float = 0.0
    top5_concentration_pct: float = 0.0
    top10_concentration: float = 0.0
    top10_concentration_pct: float = 0.0
    hhi: float = 0.0
    effective_n: float = 0.0
    total_holdings: int = 0


# =============================================================================
# 基金分析器主类
# =============================================================================

class FundAnalyzer:
    """
    基金分析器主类
    
    使用示例:
        analyzer = FundAnalyzer(risk_free_rate=0.03)
        
        # 计算所有指标
        metrics = analyzer.calculate_all_metrics(nav_series, benchmark_series)
        
        # 生成报告
        report = analyzer.generate_report(nav_series, benchmark_series, "基金名称")
        print(report)
    """
    
    def __init__(self, risk_free_rate: float = 0.03, 
                 periods_per_year: int = 252):
        """
        初始化分析器
        
        参数:
            risk_free_rate: 无风险利率（年化，默认3%）
            periods_per_year: 每年交易日数（默认252）
        """
        self.risk_free_rate = risk_free_rate
        self.periods_per_year = periods_per_year
        self.daily_rf = risk_free_rate / periods_per_year
    
    # =========================================================================
    # 收益率计算方法
    # =========================================================================
    
    def calculate_cumulative_return(self, nav_series: pd.Series, 
                                     dividend_reinvest: bool = True) -> float:
        """
        计算累计收益率
        
        参数:
            nav_series: 基金净值序列（按时间排序）
            dividend_reinvest: 是否考虑分红再投资，默认为True
        
        返回:
            累计收益率（小数形式）
        """
        if len(nav_series) < 2:
            return 0.0
        
        if dividend_reinvest:
            daily_returns = nav_series.pct_change().dropna()
            cumulative_return = (1 + daily_returns).prod() - 1
        else:
            cumulative_return = (nav_series.iloc[-1] / nav_series.iloc[0]) - 1
        
        return cumulative_return
    
    def calculate_cumulative_return_series(self, nav_series: pd.Series) -> pd.Series:
        """
        计算累计收益率序列（用于绘制收益曲线）
        
        参数:
            nav_series: 基金净值序列
        
        返回:
            累计收益率序列
        """
        daily_returns = nav_series.pct_change().fillna(0)
        cumulative_returns = (1 + daily_returns).cumprod() - 1
        return cumulative_returns
    
    def calculate_annualized_return(self, nav_series: pd.Series,
                                     periods_per_year: Optional[int] = None) -> float:
        """
        计算年化收益率
        
        参数:
            nav_series: 基金净值序列
            periods_per_year: 每年周期数（默认使用初始化时的值）
        
        返回:
            年化收益率（小数形式）
        """
        if len(nav_series) < 2:
            return 0.0
        
        periods = periods_per_year or self.periods_per_year
        total_return = self.calculate_cumulative_return(nav_series)
        n_periods = len(nav_series) - 1
        
        return (1 + total_return) ** (periods / n_periods) - 1
    
    def calculate_interval_return(self, nav_series: pd.Series,
                                   start_date=None, end_date=None) -> Dict[str, Any]:
        """
        计算任意时间区间的收益率
        
        参数:
            nav_series: 基金净值序列（带日期索引）
            start_date: 开始日期，默认从第一个数据开始
            end_date: 结束日期，默认到最后一个数据
        
        返回:
            包含区间收益率、年化收益率、区间天数等信息的字典
        """
        # 筛选区间数据
        filtered = nav_series.copy()
        if start_date:
            filtered = filtered[filtered.index >= start_date]
        if end_date:
            filtered = filtered[filtered.index <= end_date]
        
        if len(filtered) < 2:
            return {
                'interval_return': 0.0,
                'annualized_return': 0.0,
                'trading_days': 0,
                'calendar_days': 0,
                'start_nav': 0.0,
                'end_nav': 0.0
            }
        
        interval_return = self.calculate_cumulative_return(filtered)
        trading_days = len(filtered) - 1
        annualized = (1 + interval_return) ** (252 / trading_days) - 1 if trading_days > 0 else 0.0
        calendar_days = (filtered.index[-1] - filtered.index[0]).days
        
        return {
            'interval_return': interval_return,
            'interval_return_pct': interval_return * 100,
            'annualized_return': annualized,
            'annualized_return_pct': annualized * 100,
            'trading_days': trading_days,
            'calendar_days': calendar_days,
            'start_nav': filtered.iloc[0],
            'end_nav': filtered.iloc[-1],
            'start_date': filtered.index[0],
            'end_date': filtered.index[-1]
        }
    
    def calculate_periodic_returns(self, nav_series: pd.Series,
                                    period: str = 'daily') -> pd.Series:
        """
        计算不同周期的收益率
        
        参数:
            nav_series: 基金净值序列（日频，带日期索引）
            period: 目标周期 ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')
        
        返回:
            目标周期的收益率序列
        """
        if period == 'daily':
            return nav_series.pct_change().dropna()
        elif period == 'weekly':
            weekly_nav = nav_series.resample('W-FRI').last().dropna()
            return weekly_nav.pct_change().dropna()
        elif period == 'monthly':
            monthly_nav = nav_series.resample('ME').last().dropna()
            return monthly_nav.pct_change().dropna()
        elif period == 'quarterly':
            quarterly_nav = nav_series.resample('QE').last().dropna()
            return quarterly_nav.pct_change().dropna()
        elif period == 'yearly':
            yearly_nav = nav_series.resample('YE').last().dropna()
            return yearly_nav.pct_change().dropna()
        else:
            raise ValueError(f"不支持的周期类型: {period}")
    
    def calculate_adjusted_nav(self, nav_series: pd.Series,
                                dividend_series: Optional[pd.Series] = None) -> pd.Series:
        """
        计算复权净值（考虑分红再投资）
        
        参数:
            nav_series: 基金净值序列
            dividend_series: 分红序列（分红日索引，分红金额为值），可选
        
        返回:
            复权净值序列
        """
        if dividend_series is None or len(dividend_series) == 0:
            return nav_series
        
        adjusted_nav = nav_series.copy()
        dividend_dates = sorted(dividend_series.index)
        
        for div_date in dividend_dates:
            if div_date in adjusted_nav.index:
                idx = adjusted_nav.index.get_loc(div_date)
                if idx > 0:
                    prev_nav = adjusted_nav.iloc[idx - 1]
                    div_amount = dividend_series[div_date]
                    adjustment_factor = (prev_nav + div_amount) / prev_nav
                    adjusted_nav.iloc[idx:] = adjusted_nav.iloc[idx:] * adjustment_factor
        
        return adjusted_nav
    
    # =========================================================================
    # 风险指标计算方法
    # =========================================================================
    
    def calculate_volatility(self, returns_series: pd.Series,
                              annualize: bool = True,
                              periods_per_year: Optional[int] = None) -> float:
        """
        计算波动率
        
        参数:
            returns_series: 收益率序列
            annualize: 是否年化
            periods_per_year: 每年周期数
        
        返回:
            波动率
        """
        volatility = returns_series.std()
        if annualize:
            periods = periods_per_year or self.periods_per_year
            volatility = volatility * np.sqrt(periods)
        return volatility
    
    def calculate_rolling_volatility(self, returns_series: pd.Series,
                                      window: int = 60,
                                      annualize: bool = True) -> pd.Series:
        """
        计算滚动波动率
        
        参数:
            returns_series: 收益率序列
            window: 滚动窗口
            annualize: 是否年化
        
        返回:
            滚动波动率序列
        """
        rolling_vol = returns_series.rolling(window=window).std()
        if annualize:
            rolling_vol = rolling_vol * np.sqrt(252)
        return rolling_vol
    
    def calculate_max_drawdown(self, nav_series: pd.Series) -> DrawdownInfo:
        """
        计算最大回撤及其相关信息
        
        参数:
            nav_series: 基金净值序列
        
        返回:
            DrawdownInfo对象，包含最大回撤及相关信息
        """
        cumulative = (1 + nav_series.pct_change().fillna(0)).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        end_date = drawdown.idxmin()
        start_date = running_max.loc[:end_date].idxmax()
        drawdown_days = (end_date - start_date).days
        
        # 计算恢复期
        recovery_date = None
        recovery_days = None
        if end_date < cumulative.index[-1]:
            peak_value = running_max.loc[end_date]
            future_values = cumulative.loc[end_date:]
            recovery_points = future_values[future_values >= peak_value]
            if len(recovery_points) > 0:
                recovery_date = recovery_points.index[0]
                recovery_days = (recovery_date - end_date).days
        
        return DrawdownInfo(
            max_drawdown=max_dd,
            max_drawdown_pct=max_dd * 100,
            start_date=start_date,
            end_date=end_date,
            drawdown_days=drawdown_days,
            recovery_date=recovery_date,
            recovery_days=recovery_days,
            drawdown_series=drawdown
        )
    
    def calculate_drawdown_series(self, nav_series: pd.Series) -> pd.Series:
        """
        计算回撤序列（用于绘制回撤曲线）
        
        参数:
            nav_series: 基金净值序列
        
        返回:
            回撤序列
        """
        cumulative = (1 + nav_series.pct_change().fillna(0)).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown
    
    def calculate_downside_deviation(self, returns_series: pd.Series,
                                      target_return: float = 0,
                                      annualize: bool = True) -> float:
        """
        计算下行标准差
        
        参数:
            returns_series: 收益率序列
            target_return: 目标收益率（默认为0）
            annualize: 是否年化
        
        返回:
            下行标准差
        """
        downside_returns = returns_series[returns_series < target_return]
        if len(downside_returns) == 0:
            return 0.0
        
        downside_deviation = np.sqrt(((downside_returns - target_return) ** 2).mean())
        
        if annualize:
            downside_deviation = downside_deviation * np.sqrt(self.periods_per_year)
        
        return downside_deviation
    
    def calculate_var(self, returns_series: pd.Series,
                      confidence_level: float = 0.95,
                      method: str = 'historical',
                      time_horizon: int = 1) -> Dict[str, Any]:
        """
        计算风险价值 (VaR)
        
        参数:
            returns_series: 收益率序列
            confidence_level: 置信水平（如0.95表示95%）
            method: 计算方法 ('historical', 'parametric', 'monte_carlo')
            time_horizon: 时间 horizon（天数）
        
        返回:
            包含VaR值和相关信息的字典
        """
        if method == 'historical':
            var_value = -np.percentile(returns_series.dropna(), (1 - confidence_level) * 100)
        elif method == 'parametric':
            mean = returns_series.mean()
            std = returns_series.std()
            z_score = abs(stats.norm.ppf(1 - confidence_level))
            var_value = -(mean - z_score * std)
        elif method == 'monte_carlo':
            mean = returns_series.mean()
            std = returns_series.std()
            np.random.seed(42)
            simulated_returns = np.random.normal(mean, std, 100000)
            var_value = -np.percentile(simulated_returns, (1 - confidence_level) * 100)
        else:
            raise ValueError(f"不支持的VaR计算方法: {method}")
        
        if time_horizon > 1:
            var_value = var_value * np.sqrt(time_horizon)
        
        annual_var = var_value * np.sqrt(252)
        
        return {
            'var': var_value,
            'var_pct': var_value * 100,
            'confidence_level': confidence_level,
            'method': method,
            'time_horizon': time_horizon,
            'annual_var': annual_var,
            'interpretation': f'在{confidence_level*100}%的置信水平下，单日损失不会超过{var_value*100:.2f}%'
        }
    
    def calculate_cvar(self, returns_series: pd.Series,
                        confidence_level: float = 0.95,
                        method: str = 'historical') -> Dict[str, Any]:
        """
        计算条件风险价值 (CVaR/Expected Shortfall)
        
        参数:
            returns_series: 收益率序列
            confidence_level: 置信水平
            method: 计算方法
        
        返回:
            包含CVaR值的字典
        """
        if method == 'historical':
            var_threshold = np.percentile(returns_series.dropna(), (1 - confidence_level) * 100)
            cvar_value = -returns_series[returns_series <= var_threshold].mean()
        elif method == 'parametric':
            mean = returns_series.mean()
            std = returns_series.std()
            z_score = stats.norm.ppf(1 - confidence_level)
            pdf_z = stats.norm.pdf(z_score)
            cvar_value = -(mean - std * pdf_z / (1 - confidence_level))
        else:
            raise ValueError(f"不支持的CVaR计算方法: {method}")
        
        return {
            'cvar': cvar_value,
            'cvar_pct': cvar_value * 100,
            'confidence_level': confidence_level,
            'method': method,
            'interpretation': f'在损失超过VaR的情况下，平均损失为{cvar_value*100:.2f}%'
        }
    
    # =========================================================================
    # 风险调整收益指标
    # =========================================================================
    
    def calculate_sharpe_ratio(self, nav_series: pd.Series,
                                risk_free_rate: Optional[float] = None) -> float:
        """
        计算夏普比率
        
        参数:
            nav_series: 基金净值序列
            risk_free_rate: 无风险利率（年化，默认使用初始化时的值）
        
        返回:
            夏普比率
        """
        rf = risk_free_rate or self.risk_free_rate
        annual_return = self.calculate_annualized_return(nav_series)
        daily_returns = nav_series.pct_change().dropna()
        annual_vol = self.calculate_volatility(daily_returns)
        
        if annual_vol == 0:
            return 0.0
        
        return (annual_return - rf) / annual_vol
    
    def calculate_rolling_sharpe(self, nav_series: pd.Series,
                                  window: int = 252,
                                  risk_free_rate: Optional[float] = None) -> pd.Series:
        """
        计算滚动夏普比率
        
        参数:
            nav_series: 基金净值序列
            window: 滚动窗口
            risk_free_rate: 无风险利率
        
        返回:
            滚动夏普比率序列
        """
        rf = risk_free_rate or self.risk_free_rate
        daily_returns = nav_series.pct_change().dropna()
        daily_rf = rf / 252
        
        rolling_mean = daily_returns.rolling(window=window).mean()
        rolling_std = daily_returns.rolling(window=window).std()
        rolling_sharpe = (rolling_mean - daily_rf) / rolling_std * np.sqrt(252)
        
        return rolling_sharpe
    
    def calculate_sortino_ratio(self, nav_series: pd.Series,
                                 risk_free_rate: Optional[float] = None,
                                 target_return: float = 0) -> float:
        """
        计算索提诺比率
        
        参数:
            nav_series: 基金净值序列
            risk_free_rate: 无风险利率（年化）
            target_return: 目标收益率（最小可接受收益率）
        
        返回:
            索提诺比率
        """
        rf = risk_free_rate or self.risk_free_rate
        annual_return = self.calculate_annualized_return(nav_series)
        daily_returns = nav_series.pct_change().dropna()
        downside_dev = self.calculate_downside_deviation(daily_returns, target_return)
        
        if downside_dev == 0:
            return np.inf if annual_return > rf else 0.0
        
        return (annual_return - rf) / downside_dev
    
    def calculate_calmar_ratio(self, nav_series: pd.Series,
                                risk_free_rate: Optional[float] = None) -> Dict[str, Any]:
        """
        计算卡玛比率
        
        参数:
            nav_series: 基金净值序列
            risk_free_rate: 无风险利率（年化）
        
        返回:
            包含卡玛比率及相关信息的字典
        """
        rf = risk_free_rate or self.risk_free_rate
        annual_return = self.calculate_annualized_return(nav_series)
        mdd_result = self.calculate_max_drawdown(nav_series)
        max_drawdown = abs(mdd_result.max_drawdown)
        
        if max_drawdown == 0:
            calmar_ratio = np.inf
        else:
            calmar_ratio = (annual_return - rf) / max_drawdown
        
        return {
            'calmar_ratio': calmar_ratio,
            'annual_return': annual_return,
            'max_drawdown': mdd_result.max_drawdown,
            'max_drawdown_pct': mdd_result.max_drawdown_pct,
            'excess_return': annual_return - rf
        }
    
    def calculate_beta(self, fund_returns: pd.Series,
                        market_returns: pd.Series) -> float:
        """
        计算Beta系数
        
        参数:
            fund_returns: 基金收益率序列
            market_returns: 市场收益率序列
        
        返回:
            Beta系数
        """
        aligned = pd.concat([fund_returns, market_returns], axis=1).dropna()
        
        if len(aligned) < 2:
            return 1.0
        
        fund_ret = aligned.iloc[:, 0]
        market_ret = aligned.iloc[:, 1]
        
        covariance = fund_ret.cov(market_ret)
        market_variance = market_ret.var()
        
        if market_variance == 0:
            return 1.0
        
        return covariance / market_variance
    
    def calculate_treynor_ratio(self, nav_series: pd.Series,
                                 benchmark_series: pd.Series,
                                 risk_free_rate: Optional[float] = None) -> Dict[str, Any]:
        """
        计算特雷诺比率
        
        参数:
            nav_series: 基金净值序列
            benchmark_series: 基准指数序列
            risk_free_rate: 无风险利率（年化）
        
        返回:
            包含特雷诺比率及相关信息的字典
        """
        rf = risk_free_rate or self.risk_free_rate
        fund_returns = nav_series.pct_change().dropna()
        benchmark_returns = benchmark_series.pct_change().dropna()
        annual_return = self.calculate_annualized_return(nav_series)
        beta = self.calculate_beta(fund_returns, benchmark_returns)
        
        if beta == 0:
            treynor_ratio = np.inf if annual_return > rf else 0.0
        else:
            treynor_ratio = (annual_return - rf) / beta
        
        return {
            'treynor_ratio': treynor_ratio,
            'beta': beta,
            'annual_return': annual_return,
            'excess_return': annual_return - rf
        }
    
    def calculate_tracking_error(self, fund_returns: pd.Series,
                                  benchmark_returns: pd.Series,
                                  annualize: bool = True) -> float:
        """
        计算跟踪误差
        
        参数:
            fund_returns: 基金收益率序列
            benchmark_returns: 基准收益率序列
            annualize: 是否年化
        
        返回:
            跟踪误差
        """
        aligned = pd.concat([fund_returns, benchmark_returns], axis=1).dropna()
        
        if len(aligned) < 2:
            return 0.0
        
        excess_returns = aligned.iloc[:, 0] - aligned.iloc[:, 1]
        tracking_error = excess_returns.std()
        
        if annualize:
            tracking_error = tracking_error * np.sqrt(252)
        
        return tracking_error
    
    def calculate_information_ratio(self, nav_series: pd.Series,
                                     benchmark_series: pd.Series) -> Dict[str, Any]:
        """
        计算信息比率
        
        参数:
            nav_series: 基金净值序列
            benchmark_series: 基准指数序列
        
        返回:
            包含信息比率及相关信息的字典
        """
        fund_returns = nav_series.pct_change().dropna()
        benchmark_returns = benchmark_series.pct_change().dropna()
        
        fund_annual = self.calculate_annualized_return(nav_series)
        bench_annual = self.calculate_annualized_return(benchmark_series)
        excess_return = fund_annual - bench_annual
        
        tracking_error = self.calculate_tracking_error(fund_returns, benchmark_returns)
        
        if tracking_error == 0:
            information_ratio = np.inf if excess_return > 0 else 0.0
        else:
            information_ratio = excess_return / tracking_error
        
        return {
            'information_ratio': information_ratio,
            'tracking_error': tracking_error,
            'tracking_error_pct': tracking_error * 100,
            'excess_return': excess_return,
            'excess_return_pct': excess_return * 100,
            'fund_annual_return': fund_annual,
            'benchmark_annual_return': bench_annual
        }
    
    # =========================================================================
    # 基准比较方法
    # =========================================================================
    
    def calculate_alpha(self, nav_series: pd.Series,
                        benchmark_series: pd.Series,
                        risk_free_rate: Optional[float] = None) -> Dict[str, Any]:
        """
        计算Alpha
        
        参数:
            nav_series: 基金净值序列
            benchmark_series: 基准指数序列
            risk_free_rate: 无风险利率（年化）
        
        返回:
            包含Alpha、Beta、R²等信息的字典
        """
        rf = risk_free_rate or self.risk_free_rate
        fund_returns = nav_series.pct_change().dropna()
        benchmark_returns = benchmark_series.pct_change().dropna()
        
        aligned = pd.concat([fund_returns, benchmark_returns], axis=1).dropna()
        
        if len(aligned) < 2:
            return {
                'alpha': 0.0,
                'alpha_pct': 0.0,
                'beta': 1.0,
                'r_squared': 0.0,
                'correlation': 0.0
            }
        
        fund_ret = aligned.iloc[:, 0]
        bench_ret = aligned.iloc[:, 1]
        
        beta = self.calculate_beta(fund_ret, bench_ret)
        
        fund_annual = self.calculate_annualized_return(nav_series)
        bench_annual = self.calculate_annualized_return(benchmark_series)
        alpha = fund_annual - rf - beta * (bench_annual - rf)
        
        correlation = fund_ret.corr(bench_ret)
        r_squared = correlation ** 2
        
        return {
            'alpha': alpha,
            'alpha_pct': alpha * 100,
            'beta': beta,
            'r_squared': r_squared,
            'correlation': correlation,
            'fund_annual_return': fund_annual,
            'benchmark_annual_return': bench_annual
        }
    
    def calculate_excess_return(self, nav_series: pd.Series,
                                 benchmark_series: pd.Series,
                                 method: str = 'arithmetic') -> Dict[str, Any]:
        """
        计算超额收益
        
        参数:
            nav_series: 基金净值序列
            benchmark_series: 基准指数序列
            method: 计算方法 ('arithmetic', 'geometric')
        
        返回:
            包含超额收益相关信息的字典
        """
        fund_return = self.calculate_cumulative_return(nav_series)
        benchmark_return = self.calculate_cumulative_return(benchmark_series)
        
        fund_annual = self.calculate_annualized_return(nav_series)
        bench_annual = self.calculate_annualized_return(benchmark_series)
        
        arithmetic_excess = fund_annual - bench_annual
        geometric_excess = (1 + fund_annual) / (1 + bench_annual) - 1
        
        fund_returns = nav_series.pct_change().dropna()
        bench_returns = benchmark_series.pct_change().dropna()
        
        aligned = pd.concat([fund_returns, bench_returns], axis=1).dropna()
        win_rate = (aligned.iloc[:, 0] > aligned.iloc[:, 1]).mean()
        
        return {
            'fund_return': fund_return,
            'benchmark_return': benchmark_return,
            'fund_annual_return': fund_annual,
            'benchmark_annual_return': bench_annual,
            'arithmetic_excess': arithmetic_excess,
            'geometric_excess': geometric_excess,
            'excess_return': arithmetic_excess if method == 'arithmetic' else geometric_excess,
            'excess_return_pct': (arithmetic_excess if method == 'arithmetic' else geometric_excess) * 100,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100
        }
    
    # =========================================================================
    # 综合计算方法
    # =========================================================================
    
    def calculate_all_metrics(self, nav_series: pd.Series,
                              benchmark_series: Optional[pd.Series] = None,
                              fund_code: str = "",
                              fund_name: str = "") -> FundMetrics:
        """
        计算所有指标
        
        参数:
            nav_series: 基金净值序列
            benchmark_series: 基准指数序列（可选）
            fund_code: 基金代码
            fund_name: 基金名称
        
        返回:
            FundMetrics对象，包含所有计算指标
        """
        metrics = FundMetrics()
        metrics.fund_code = fund_code
        metrics.fund_name = fund_name
        metrics.analysis_date = datetime.now()
        
        daily_returns = nav_series.pct_change().dropna()
        
        # 收益率指标
        metrics.total_return = self.calculate_cumulative_return(nav_series)
        metrics.total_return_pct = metrics.total_return * 100
        metrics.annualized_return = self.calculate_annualized_return(nav_series)
        metrics.annualized_return_pct = metrics.annualized_return * 100
        
        # 风险指标
        metrics.volatility = self.calculate_volatility(daily_returns)
        metrics.volatility_pct = metrics.volatility * 100
        
        mdd_result = self.calculate_max_drawdown(nav_series)
        metrics.max_drawdown = mdd_result.max_drawdown
        metrics.max_drawdown_pct = mdd_result.max_drawdown_pct
        metrics.max_drawdown_start = mdd_result.start_date
        metrics.max_drawdown_end = mdd_result.end_date
        metrics.max_drawdown_days = mdd_result.drawdown_days
        metrics.recovery_days = mdd_result.recovery_days
        
        metrics.downside_deviation = self.calculate_downside_deviation(daily_returns)
        metrics.downside_deviation_pct = metrics.downside_deviation * 100
        
        var_result = self.calculate_var(daily_returns)
        metrics.var_95 = var_result['var']
        metrics.var_95_pct = var_result['var_pct']
        
        cvar_result = self.calculate_cvar(daily_returns)
        metrics.cvar_95 = cvar_result['cvar']
        metrics.cvar_95_pct = cvar_result['cvar_pct']
        
        # 风险调整收益指标
        metrics.sharpe_ratio = self.calculate_sharpe_ratio(nav_series)
        metrics.sortino_ratio = self.calculate_sortino_ratio(nav_series)
        
        calmar_result = self.calculate_calmar_ratio(nav_series)
        metrics.calmar_ratio = calmar_result['calmar_ratio']
        
        # 基准比较
        if benchmark_series is not None:
            alpha_result = self.calculate_alpha(nav_series, benchmark_series)
            metrics.alpha = alpha_result['alpha']
            metrics.alpha_pct = alpha_result['alpha_pct']
            metrics.beta = alpha_result['beta']
            metrics.r_squared = alpha_result['r_squared']
            metrics.correlation = alpha_result['correlation']
            
            fund_ret = daily_returns
            bench_ret = benchmark_series.pct_change().dropna()
            metrics.tracking_error = self.calculate_tracking_error(fund_ret, bench_ret)
            metrics.tracking_error_pct = metrics.tracking_error * 100
            
            fund_annual = metrics.annualized_return
            bench_annual = self.calculate_annualized_return(benchmark_series)
            metrics.excess_return = fund_annual - bench_annual
            metrics.excess_return_pct = metrics.excess_return * 100
            
            ir_result = self.calculate_information_ratio(nav_series, benchmark_series)
            metrics.information_ratio = ir_result['information_ratio']
            
            treynor_result = self.calculate_treynor_ratio(nav_series, benchmark_series)
            metrics.treynor_ratio = treynor_result['treynor_ratio']
        
        # 其他指标
        metrics.win_rate = (daily_returns > 0).mean()
        metrics.win_rate_pct = metrics.win_rate * 100
        metrics.positive_ratio = metrics.win_rate
        
        return metrics
    
    def generate_report(self, nav_series: pd.Series,
                        benchmark_series: Optional[pd.Series] = None,
                        fund_name: str = "基金") -> str:
        """
        生成分析报告
        
        参数:
            nav_series: 基金净值序列
            benchmark_series: 基准指数序列（可选）
            fund_name: 基金名称
        
        返回:
            格式化后的分析报告字符串
        """
        metrics = self.calculate_all_metrics(nav_series, benchmark_series)
        
        report = f"""
{'='*70}
{fund_name} 分析报告
分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*70}

【收益率指标】
累计收益率:     {metrics.total_return*100:>10.2f}%
年化收益率:     {metrics.annualized_return*100:>10.2f}%

【风险指标】
年化波动率:     {metrics.volatility*100:>10.2f}%
最大回撤:       {metrics.max_drawdown*100:>10.2f}%
回撤区间:       {metrics.max_drawdown_start.strftime('%Y-%m-%d') if metrics.max_drawdown_start else 'N/A'} - {metrics.max_drawdown_end.strftime('%Y-%m-%d') if metrics.max_drawdown_end else 'N/A'}
回撤持续:       {metrics.max_drawdown_days} 天
下行标准差:     {metrics.downside_deviation*100:>10.2f}%
VaR (95%):      {metrics.var_95*100:>10.2f}%
CVaR (95%):     {metrics.cvar_95*100:>10.2f}%

【风险调整收益】
夏普比率:       {metrics.sharpe_ratio:>10.2f}  ({self._get_sharpe_grade(metrics.sharpe_ratio)})
索提诺比率:     {metrics.sortino_ratio:>10.2f}
卡玛比率:       {metrics.calmar_ratio:>10.2f}
"""
        
        if benchmark_series is not None:
            report += f"""
【基准比较】
Alpha:          {metrics.alpha*100:>10.2f}%
Beta:           {metrics.beta:>10.2f}
跟踪误差:       {metrics.tracking_error*100:>10.2f}%
超额收益:       {metrics.excess_return*100:>10.2f}%
信息比率:       {metrics.information_ratio:>10.2f}
特雷诺比率:     {metrics.treynor_ratio:>10.2f}
R²:             {metrics.r_squared:>10.2f}
相关系数:       {metrics.correlation:>10.2f}
"""
        
        report += f"""
【其他指标】
胜率:           {metrics.win_rate*100:>10.2f}%
{'='*70}
"""
        return report
    
    def _get_sharpe_grade(self, sharpe: float) -> str:
        """根据夏普比率评级"""
        if sharpe >= 2.0:
            return "优秀"
        elif sharpe >= 1.0:
            return "良好"
        elif sharpe >= 0.5:
            return "一般"
        else:
            return "较差"


# =============================================================================
# 持仓分析类
# =============================================================================

class PortfolioAnalyzer:
    """
    持仓分析器
    
    用于分析基金持仓的集中度、行业配置、调仓情况等
    """
    
    @staticmethod
    def calculate_concentration(holdings_df: pd.DataFrame, 
                                 top_n: int = 10) -> ConcentrationInfo:
        """
        计算持仓集中度
        
        参数:
            holdings_df: 持仓数据，包含'stock_code', 'weight'列
            top_n: 前N大重仓股
        
        返回:
            ConcentrationInfo对象
        """
        sorted_h = holdings_df.sort_values('weight', ascending=False)
        
        top3_conc = sorted_h.head(3)['weight'].sum()
        top5_conc = sorted_h.head(5)['weight'].sum()
        top10_conc = sorted_h.head(10)['weight'].sum()
        top_n_conc = sorted_h.head(top_n)['weight'].sum()
        
        hhi = (holdings_df['weight'] ** 2).sum()
        effective_n = 1 / hhi if hhi > 0 else len(holdings_df)
        
        return ConcentrationInfo(
            top3_concentration=top3_conc,
            top3_concentration_pct=top3_conc * 100,
            top5_concentration=top5_conc,
            top5_concentration_pct=top5_conc * 100,
            top10_concentration=top10_conc,
            top10_concentration_pct=top10_conc * 100,
            hhi=hhi,
            effective_n=effective_n,
            total_holdings=len(holdings_df)
        )
    
    @staticmethod
    def analyze_sector_allocation(current_holdings: pd.DataFrame,
                                   previous_holdings: Optional[pd.DataFrame] = None,
                                   sector_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        分析行业配置
        
        参数:
            current_holdings: 当前持仓
            previous_holdings: 上期持仓（可选）
            sector_mapping: 股票代码到行业的映射
        
        返回:
            行业配置分析结果
        """
        if sector_mapping:
            current_holdings = current_holdings.copy()
            current_holdings['sector'] = current_holdings['stock_code'].map(sector_mapping)
        
        current_weights = current_holdings.groupby('sector')['weight'].sum()
        
        result = {
            'current_allocation': current_weights.to_dict(),
            'top_sectors': current_weights.sort_values(ascending=False).head(5).to_dict()
        }
        
        if previous_holdings is not None and sector_mapping:
            previous_holdings = previous_holdings.copy()
            previous_holdings['sector'] = previous_holdings['stock_code'].map(sector_mapping)
            previous_weights = previous_holdings.groupby('sector')['weight'].sum()
            
            all_sectors = set(current_weights.index) | set(previous_weights.index)
            sector_changes = {}
            
            for sector in all_sectors:
                curr_w = current_weights.get(sector, 0)
                prev_w = previous_weights.get(sector, 0)
                sector_changes[sector] = {
                    'current': curr_w,
                    'previous': prev_w,
                    'change': curr_w - prev_w,
                    'change_pct': (curr_w - prev_w) * 100
                }
            
            result['sector_changes'] = sector_changes
            result['increased_sectors'] = {k: v for k, v in sector_changes.items() if v['change'] > 0}
            result['decreased_sectors'] = {k: v for k, v in sector_changes.items() if v['change'] < 0}
        
        return result
    
    @staticmethod
    def detect_position_changes(current: pd.DataFrame,
                                 previous: pd.DataFrame,
                                 change_threshold: float = 0.01) -> Dict[str, Any]:
        """
        检测持仓变化
        
        参数:
            current: 当前持仓
            previous: 上期持仓
            change_threshold: 变化阈值（默认1%）
        
        返回:
            调仓检测结果
        """
        curr_dict = dict(zip(current['stock_code'], current['weight']))
        prev_dict = dict(zip(previous['stock_code'], previous['weight']))
        
        all_stocks = set(curr_dict.keys()) | set(prev_dict.keys())
        
        added, removed, increased, decreased = [], [], [], []
        
        for stock in all_stocks:
            curr_w = curr_dict.get(stock, 0)
            prev_w = prev_dict.get(stock, 0)
            change = curr_w - prev_w
            
            info = {
                'stock_code': stock,
                'current_weight': curr_w,
                'previous_weight': prev_w,
                'change': change,
                'change_pct': change * 100
            }
            
            if prev_w == 0 and curr_w > 0:
                added.append(info)
            elif prev_w > 0 and curr_w == 0:
                removed.append(info)
            elif abs(change) >= change_threshold:
                (increased if change > 0 else decreased).append(info)
        
        total_change = sum(abs(s['change']) for s in added + removed + increased + decreased) / 2
        
        return {
            'added_stocks': added,
            'removed_stocks': removed,
            'increased_stocks': increased,
            'decreased_stocks': decreased,
            'num_added': len(added),
            'num_removed': len(removed),
            'num_increased': len(increased),
            'num_decreased': len(decreased),
            'turnover_ratio': total_change,
            'turnover_ratio_pct': total_change * 100
        }
    
    @staticmethod
    def estimate_turnover_rate(holdings_list: List[pd.DataFrame],
                                dates: List[str],
                                method: str = 'aggregate') -> Dict[str, Any]:
        """
        估算持仓换手率
        
        参数:
            holdings_list: 各期持仓数据列表
            dates: 各期日期列表
            method: 计算方法 ('aggregate', 'average')
        
        返回:
            换手率估算结果
        """
        if len(holdings_list) < 2:
            return {'annual_turnover': 0.0, 'quarterly_turnover': []}
        
        quarterly_turnovers = []
        
        for i in range(1, len(holdings_list)):
            changes = PortfolioAnalyzer.detect_position_changes(
                holdings_list[i], holdings_list[i-1]
            )
            quarterly_turnovers.append({
                'period': f"{dates[i-1]} to {dates[i]}",
                'turnover': changes['turnover_ratio'],
                'turnover_pct': changes['turnover_ratio_pct']
            })
        
        if method == 'aggregate':
            annual_turnover = sum(t['turnover'] for t in quarterly_turnovers) * 2
        else:
            avg_quarterly = np.mean([t['turnover'] for t in quarterly_turnovers])
            annual_turnover = avg_quarterly * 4 * 2
        
        return {
            'annual_turnover': annual_turnover,
            'annual_turnover_pct': annual_turnover * 100,
            'quarterly_turnover': quarterly_turnovers,
            'avg_quarterly_turnover': np.mean([t['turnover'] for t in quarterly_turnovers])
        }


# =============================================================================
# 基金经理评估类
# =============================================================================

class ManagerEvaluator:
    """
    基金经理评估器
    
    用于评估基金经理的任期表现和稳定性
    """
    
    def __init__(self, analyzer: Optional[FundAnalyzer] = None):
        self.analyzer = analyzer or FundAnalyzer()
    
    def evaluate_tenure(self, nav_series: pd.Series,
                        start_date, end_date=None) -> Dict[str, Any]:
        """
        评估基金经理任期表现
        
        参数:
            nav_series: 基金净值序列
            start_date: 上任日期
            end_date: 离任日期（可选，默认至今）
        
        返回:
            任期表现评估结果
        """
        tenure_nav = nav_series[nav_series.index >= start_date]
        if end_date:
            tenure_nav = tenure_nav[tenure_nav.index <= end_date]
        
        if len(tenure_nav) < 2:
            return {}
        
        metrics = self.analyzer.calculate_all_metrics(tenure_nav)
        
        return {
            'start_date': tenure_nav.index[0],
            'end_date': tenure_nav.index[-1],
            'tenure_days': (tenure_nav.index[-1] - tenure_nav.index[0]).days,
            'tenure_years': (tenure_nav.index[-1] - tenure_nav.index[0]).days / 365.25,
            'total_return': metrics.total_return,
            'total_return_pct': metrics.total_return_pct,
            'annualized_return': metrics.annualized_return,
            'annualized_return_pct': metrics.annualized_return_pct,
            'volatility': metrics.volatility,
            'volatility_pct': metrics.volatility_pct,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'max_drawdown_pct': metrics.max_drawdown_pct,
            'calmar_ratio': metrics.calmar_ratio,
            'win_rate': metrics.win_rate,
            'win_rate_pct': metrics.win_rate_pct
        }
    
    def compare_managers(self, nav_series: pd.Series,
                         manager_periods: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        比较不同基金经理的业绩
        
        参数:
            nav_series: 基金净值序列
            manager_periods: 各基金经理任期列表
                [{'name': '经理A', 'start': '2020-01-01', 'end': '2021-12-31'}, ...]
        
        返回:
            各基金经理业绩对比DataFrame
        """
        results = []
        
        for manager in manager_periods:
            result = self.evaluate_tenure(
                nav_series,
                manager['start'],
                manager.get('end')
            )
            result['manager_name'] = manager['name']
            results.append(result)
        
        return pd.DataFrame(results)
    
    def calculate_consistency_score(self, nav_series: pd.Series) -> Dict[str, Any]:
        """
        计算稳定性评分
        
        参数:
            nav_series: 基金净值序列
        
        返回:
            稳定性评分及相关指标
        """
        daily_returns = nav_series.pct_change().dropna()
        
        # 正收益比例
        positive_ratio = (daily_returns > 0).mean()
        
        # 滚动胜率稳定性
        rolling_win = daily_returns.rolling(63).apply(lambda x: (x > 0).mean())
        win_stability = 1 - rolling_win.std() if not pd.isna(rolling_win.std()) else 0
        
        # 波动率稳定性
        rolling_vol = daily_returns.rolling(63).std()
        vol_stability = 1 / (rolling_vol.std() + 1e-6) if not pd.isna(rolling_vol.std()) else 0
        
        # 综合评分
        score = (positive_ratio * 0.4 + win_stability * 0.3 + 
                 min(vol_stability / 10, 1) * 0.3) * 100
        
        return {
            'consistency_score': score,
            'grade': 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D',
            'positive_ratio': positive_ratio,
            'positive_ratio_pct': positive_ratio * 100,
            'win_stability': win_stability,
            'vol_stability': vol_stability
        }


# =============================================================================
# 工具函数
# =============================================================================

def get_risk_level(volatility: float) -> str:
    """根据波动率判断风险等级"""
    if volatility < 0.15:
        return "低风险"
    elif volatility < 0.25:
        return "中等风险"
    else:
        return "高风险"


def get_sharpe_grade(sharpe: float) -> str:
    """根据夏普比率评级"""
    if sharpe >= 2.0:
        return "优秀"
    elif sharpe >= 1.0:
        return "良好"
    elif sharpe >= 0.5:
        return "一般"
    else:
        return "较差"


def format_percentage(value: float, decimals: int = 2) -> str:
    """格式化百分比"""
    return f"{value * 100:.{decimals}f}%"


def get_benchmark_name(benchmark_code: str) -> str:
    """获取基准指数名称"""
    benchmark_names = {
        '000300.SH': '沪深300',
        '000905.SH': '中证500',
        '000906.SH': '中证800',
        '000852.SH': '中证1000',
        'H11001.CSI': '中证全债',
        'CBA00301.CS': '中债总指数',
        'H11025.CSI': '中证货币基金',
        '885001.WI': '偏股混合型基金指数',
        '885000.WI': '普通股票型基金指数',
        'SPX': '标普500',
        'DJI': '道琼斯工业指数',
        'IXIC': '纳斯达克指数'
    }
    return benchmark_names.get(benchmark_code, benchmark_code)


# =============================================================================
# 使用示例
# =============================================================================

if __name__ == "__main__":
    # 创建示例数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    
    # 模拟基金净值（年化收益10%，波动率20%）
    daily_returns = np.random.normal(0.10/252, 0.20/np.sqrt(252), len(dates))
    nav = 1.0 * (1 + daily_returns).cumprod()
    nav_series = pd.Series(nav, index=dates)
    
    # 模拟基准指数
    benchmark_returns = np.random.normal(0.08/252, 0.18/np.sqrt(252), len(dates))
    benchmark = 1.0 * (1 + benchmark_returns).cumprod()
    benchmark_series = pd.Series(benchmark, index=dates)
    
    print("="*70)
    print("基金分析工具库使用示例")
    print("="*70)
    
    # 创建分析器
    analyzer = FundAnalyzer(risk_free_rate=0.03)
    
    # 生成报告
    report = analyzer.generate_report(nav_series, benchmark_series, "示例基金")
    print(report)
    
    # 获取所有指标
    metrics = analyzer.calculate_all_metrics(nav_series, benchmark_series, 
                                              fund_code="000001", 
                                              fund_name="示例基金")
    
    print("\n关键指标摘要:")
    print(f"  夏普比率: {metrics.sharpe_ratio:.2f}")
    print(f"  信息比率: {metrics.information_ratio:.2f}")
    print(f"  最大回撤: {metrics.max_drawdown*100:.2f}%")
    print(f"  年化波动率: {metrics.volatility*100:.2f}%")
    
    # 持仓分析示例
    print("\n" + "="*70)
    print("持仓分析示例")
    print("="*70)
    
    # 模拟持仓数据
    holdings_data = {
        'stock_code': ['000001.SZ', '000002.SZ', '000858.SZ', '600519.SH', '002415.SZ',
                       '000333.SZ', '002594.SZ', '300750.SZ', '601318.SH', '600036.SH'],
        'stock_name': ['平安银行', '万科A', '五粮液', '贵州茅台', '海康威视',
                       '美的集团', '比亚迪', '宁德时代', '中国平安', '招商银行'],
        'weight': [0.08, 0.07, 0.09, 0.12, 0.06, 0.08, 0.10, 0.11, 0.15, 0.14]
    }
    holdings_df = pd.DataFrame(holdings_data)
    
    portfolio_analyzer = PortfolioAnalyzer()
    concentration = portfolio_analyzer.calculate_concentration(holdings_df)
    
    print(f"\n持仓集中度分析:")
    print(f"  前3大重仓股集中度: {concentration.top3_concentration_pct:.2f}%")
    print(f"  前5大重仓股集中度: {concentration.top5_concentration_pct:.2f}%")
    print(f"  前10大重仓股集中度: {concentration.top10_concentration_pct:.2f}%")
    print(f"  赫芬达尔指数(HHI): {concentration.hhi:.4f}")
    print(f"  有效持股数量: {concentration.effective_n:.2f}")
    
    # 基金经理评估示例
    print("\n" + "="*70)
    print("基金经理评估示例")
    print("="*70)
    
    manager_evaluator = ManagerEvaluator(analyzer)
    consistency = manager_evaluator.calculate_consistency_score(nav_series)
    
    print(f"\n稳定性评分:")
    print(f"  综合评分: {consistency['consistency_score']:.2f}")
    print(f"  评级: {consistency['grade']}")
    print(f"  正收益比例: {consistency['positive_ratio_pct']:.2f}%")
