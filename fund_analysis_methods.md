# 基金分析指标计算方法完整指南

## 目录
1. [基金收益率计算方法](#1-基金收益率计算方法)
2. [基金风险指标计算](#2-基金风险指标计算)
3. [风险调整收益指标](#3-风险调整收益指标)
4. [基金业绩比较基准](#4-基金业绩比较基准)
5. [基金持仓分析方法](#5-基金持仓分析方法)
6. [基金经理评估](#6-基金经理评估)
7. [完整Python实现](#7-完整python实现)

---

## 1. 基金收益率计算方法

### 1.1 累计收益率 (Cumulative Return)

#### 计算公式

**简单累计收益率（不考虑分红再投资）：**
$$R_{cumulative} = \frac{NAV_{end} - NAV_{start}}{NAV_{start}} \times 100\%$$

**考虑分红再投资的累计收益率：**
$$R_{cumulative} = \left(\prod_{t=1}^{n}(1 + r_t)\right) - 1$$

其中，$r_t$ 为第t期的收益率

#### Python实现

```python
import numpy as np
import pandas as pd

def calculate_cumulative_return(nav_series, dividend_reinvest=True):
    """
    计算累计收益率
    
    参数:
        nav_series: pd.Series, 基金净值序列（按时间排序）
        dividend_reinvest: bool, 是否考虑分红再投资，默认为True
    
    返回:
        float: 累计收益率（小数形式）
    """
    if len(nav_series) < 2:
        return 0.0
    
    if dividend_reinvest:
        # 计算日收益率后累乘
        daily_returns = nav_series.pct_change().dropna()
        cumulative_return = (1 + daily_returns).prod() - 1
    else:
        # 简单收益率
        cumulative_return = (nav_series.iloc[-1] / nav_series.iloc[0]) - 1
    
    return cumulative_return


def calculate_cumulative_return_series(nav_series):
    """
    计算累计收益率序列（用于绘制收益曲线）
    
    参数:
        nav_series: pd.Series, 基金净值序列
    
    返回:
        pd.Series: 累计收益率序列
    """
    daily_returns = nav_series.pct_change().fillna(0)
    cumulative_returns = (1 + daily_returns).cumprod() - 1
    return cumulative_returns
```

#### 结果解读
- **正值**：表示投资盈利
- **负值**：表示投资亏损
- **比较基准**：通常与同期市场指数或同类基金比较

---

### 1.2 年化收益率 (Annualized Return)

#### 计算公式

**通用年化收益率公式：**
$$R_{annualized} = (1 + R_{total})^{\frac{252}{n}} - 1$$

其中：
- $R_{total}$：总收益率
- $n$：实际交易日数
- 252：一年中的交易日数

**不同时间周期的年化：**

| 周期 | 年化公式 |
|------|----------|
| 日收益率 | $R_{annual} = (1 + r_{daily})^{252} - 1$ |
| 周收益率 | $R_{annual} = (1 + r_{weekly})^{52} - 1$ |
| 月收益率 | $R_{annual} = (1 + r_{monthly})^{12} - 1$ |
| 季收益率 | $R_{annual} = (1 + r_{quarterly})^{4} - 1$ |

#### Python实现

```python
def calculate_annualized_return(nav_series, periods_per_year=252):
    """
    计算年化收益率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        periods_per_year: int, 每年周期数（日:252, 周:52, 月:12）
    
    返回:
        float: 年化收益率（小数形式）
    """
    if len(nav_series) < 2:
        return 0.0
    
    total_return = calculate_cumulative_return(nav_series)
    n_periods = len(nav_series) - 1
    
    # 年化计算
    annualized_return = (1 + total_return) ** (periods_per_year / n_periods) - 1
    
    return annualized_return


def calculate_annualized_return_from_periodic(periodic_returns, period='daily'):
    """
    从周期性收益率计算年化收益率
    
    参数:
        periodic_returns: pd.Series, 周期性收益率序列
        period: str, 周期类型 ('daily', 'weekly', 'monthly', 'quarterly')
    
    返回:
        float: 年化收益率
    """
    period_mapping = {
        'daily': 252,
        'weekly': 52,
        'monthly': 12,
        'quarterly': 4,
        'yearly': 1
    }
    
    periods_per_year = period_mapping.get(period, 252)
    
    # 计算平均周期收益率
    mean_periodic_return = periodic_returns.mean()
    
    # 年化
    annualized_return = (1 + mean_periodic_return) ** periods_per_year - 1
    
    return annualized_return
```

#### 结果解读
- **> 10%**：表现优秀
- **5%-10%**：表现良好
- **0%-5%**：表现一般
- **< 0%**：亏损

---

### 1.3 区间收益率计算

#### 计算公式

$$R_{interval} = \frac{NAV_{end} - NAV_{start}}{NAV_{start}}$$

#### Python实现

```python
def calculate_interval_return(nav_series, start_date=None, end_date=None):
    """
    计算任意时间区间的收益率
    
    参数:
        nav_series: pd.Series, 基金净值序列（带日期索引）
        start_date: str/datetime, 开始日期，默认从第一个数据开始
        end_date: str/datetime, 结束日期，默认到最后一个数据
    
    返回:
        dict: 包含区间收益率、年化收益率、区间天数等信息
    """
    # 筛选区间数据
    if start_date:
        nav_series = nav_series[nav_series.index >= start_date]
    if end_date:
        nav_series = nav_series[nav_series.index <= end_date]
    
    if len(nav_series) < 2:
        return {
            'interval_return': 0.0,
            'annualized_return': 0.0,
            'trading_days': 0,
            'calendar_days': 0
        }
    
    # 计算区间收益率
    interval_return = calculate_cumulative_return(nav_series)
    
    # 计算年化收益率
    trading_days = len(nav_series) - 1
    annualized_return = (1 + interval_return) ** (252 / trading_days) - 1 if trading_days > 0 else 0.0
    
    # 计算日历天数
    calendar_days = (nav_series.index[-1] - nav_series.index[0]).days
    
    return {
        'interval_return': interval_return,
        'annualized_return': annualized_return,
        'trading_days': trading_days,
        'calendar_days': calendar_days,
        'start_nav': nav_series.iloc[0],
        'end_nav': nav_series.iloc[-1]
    }


def calculate_rolling_returns(nav_series, window=252):
    """
    计算滚动收益率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        window: int, 滚动窗口大小（默认252个交易日，约1年）
    
    返回:
        pd.Series: 滚动收益率序列
    """
    rolling_returns = nav_series.pct_change(window).dropna()
    return rolling_returns
```

---

### 1.4 不同周期收益率计算

#### Python实现

```python
def calculate_periodic_returns(nav_series, period='daily'):
    """
    计算不同周期的收益率
    
    参数:
        nav_series: pd.Series, 基金净值序列（日频，带日期索引）
        period: str, 目标周期 ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')
    
    返回:
        pd.Series: 目标周期的收益率序列
    """
    # 重采样到目标周期
    if period == 'daily':
        return nav_series.pct_change().dropna()
    
    elif period == 'weekly':
        # 按周重采样，取周五的数据
        weekly_nav = nav_series.resample('W-FRI').last().dropna()
        return weekly_nav.pct_change().dropna()
    
    elif period == 'monthly':
        # 按月重采样，取月末数据
        monthly_nav = nav_series.resample('ME').last().dropna()
        return monthly_nav.pct_change().dropna()
    
    elif period == 'quarterly':
        # 按季重采样，取季末数据
        quarterly_nav = nav_series.resample('QE').last().dropna()
        return quarterly_nav.pct_change().dropna()
    
    elif period == 'yearly':
        # 按年重采样，取年末数据
        yearly_nav = nav_series.resample('YE').last().dropna()
        return yearly_nav.pct_change().dropna()
    
    else:
        raise ValueError(f"不支持的周期类型: {period}")


def calculate_multi_period_returns(nav_series):
    """
    计算多周期收益率汇总
    
    参数:
        nav_series: pd.Series, 基金净值序列
    
    返回:
        dict: 各周期收益率
    """
    results = {}
    
    # 日收益率
    results['daily'] = calculate_periodic_returns(nav_series, 'daily')
    
    # 周收益率
    results['weekly'] = calculate_periodic_returns(nav_series, 'weekly')
    
    # 月收益率
    results['monthly'] = calculate_periodic_returns(nav_series, 'monthly')
    
    # 季收益率
    results['quarterly'] = calculate_periodic_returns(nav_series, 'quarterly')
    
    # 年收益率
    results['yearly'] = calculate_periodic_returns(nav_series, 'yearly')
    
    return results
```

---

### 1.5 考虑分红再投资的收益率

#### 计算公式

**复权净值计算：**
$$NAV_{adjusted,t} = NAV_{adjusted,t-1} \times (1 + r_t)$$

其中：
- 分红日：$r_t = \frac{NAV_t + D_t - NAV_{t-1}}{NAV_{t-1}}$
- $D_t$ 为分红金额

#### Python实现

```python
def calculate_adjusted_nav(nav_series, dividend_series=None):
    """
    计算复权净值（考虑分红再投资）
    
    参数:
        nav_series: pd.Series, 基金净值序列
        dividend_series: pd.Series, 分红序列（分红日索引，分红金额为值），可选
    
    返回:
        pd.Series: 复权净值序列
    """
    if dividend_series is None or len(dividend_series) == 0:
        # 无分红数据，返回原始净值
        return nav_series
    
    # 创建复权净值序列
    adjusted_nav = nav_series.copy()
    
    # 按日期排序
    dividend_dates = sorted(dividend_series.index)
    
    for div_date in dividend_dates:
        if div_date in adjusted_nav.index:
            # 找到分红日前后的净值
            idx = adjusted_nav.index.get_loc(div_date)
            if idx > 0:
                prev_nav = adjusted_nav.iloc[idx - 1]
                div_amount = dividend_series[div_date]
                
                # 计算复权因子
                adjustment_factor = (prev_nav + div_amount) / prev_nav
                
                # 调整分红日及之后的所有净值
                adjusted_nav.iloc[idx:] = adjusted_nav.iloc[idx:] * adjustment_factor
    
    return adjusted_nav


def calculate_total_return(nav_series, dividend_series=None):
    """
    计算总收益率（考虑分红）
    
    参数:
        nav_series: pd.Series, 基金净值序列
        dividend_series: pd.Series, 分红序列
    
    返回:
        dict: 包含总收益率、分红收益率、净值增长率
    """
    # 计算复权净值
    adjusted_nav = calculate_adjusted_nav(nav_series, dividend_series)
    
    # 总收益率（基于复权净值）
    total_return = calculate_cumulative_return(adjusted_nav)
    
    # 净值增长率（不考虑分红）
    nav_growth = calculate_cumulative_return(nav_series)
    
    # 分红贡献的收益率
    dividend_return = total_return - nav_growth
    
    return {
        'total_return': total_return,
        'nav_growth': nav_growth,
        'dividend_return': dividend_return,
        'dividend_contribution': dividend_return / total_return if total_return != 0 else 0
    }
```

---

## 2. 基金风险指标计算

### 2.1 最大回撤 (Maximum Drawdown)

#### 计算公式

$$MDD = \max_{t \in [0,T]}\left(\frac{P_{peak} - P_t}{P_{peak}}\right)$$

其中：
- $P_{peak}$：区间内的历史最高点
- $P_t$：当前点净值

#### Python实现

```python
def calculate_max_drawdown(nav_series):
    """
    计算最大回撤及其相关信息
    
    参数:
        nav_series: pd.Series, 基金净值序列
    
    返回:
        dict: 包含最大回撤、回撤开始日期、回撤结束日期、回撤持续天数
    """
    # 计算累计收益曲线
    cumulative = (1 + nav_series.pct_change().fillna(0)).cumprod()
    
    # 计算历史最高点
    running_max = cumulative.expanding().max()
    
    # 计算回撤
    drawdown = (cumulative - running_max) / running_max
    
    # 最大回撤
    max_drawdown = drawdown.min()
    
    # 找到最大回撤的结束日期
    max_dd_end_date = drawdown.idxmin()
    
    # 找到回撤开始日期（最高点日期）
    max_dd_start_date = running_max.loc[:max_dd_end_date].idxmax()
    
    # 计算回撤持续天数
    drawdown_days = (max_dd_end_date - max_dd_start_date).days
    
    # 计算回撤恢复期（如果有）
    recovery_days = None
    if max_dd_end_date < cumulative.index[-1]:
        # 寻找恢复日期（净值回到或超过回撤前高点）
        peak_value = running_max.loc[max_dd_end_date]
        future_values = cumulative.loc[max_dd_end_date:]
        recovery_points = future_values[future_values >= peak_value]
        if len(recovery_points) > 0:
            recovery_date = recovery_points.index[0]
            recovery_days = (recovery_date - max_dd_end_date).days
    
    return {
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_drawdown * 100,
        'start_date': max_dd_start_date,
        'end_date': max_dd_end_date,
        'drawdown_days': drawdown_days,
        'recovery_days': recovery_days,
        'drawdown_series': drawdown
    }


def calculate_drawdown_series(nav_series):
    """
    计算回撤序列（用于绘制回撤曲线）
    
    参数:
        nav_series: pd.Series, 基金净值序列
    
    返回:
        pd.Series: 回撤序列
    """
    cumulative = (1 + nav_series.pct_change().fillna(0)).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown


def calculate_calmar_ratio(nav_series, annualized_return=None):
    """
    计算卡玛比率（年化收益率/最大回撤）
    
    参数:
        nav_series: pd.Series, 基金净值序列
        annualized_return: float, 年化收益率（可选，不传入则自动计算）
    
    返回:
        float: 卡玛比率
    """
    if annualized_return is None:
        annualized_return = calculate_annualized_return(nav_series)
    
    max_dd = calculate_max_drawdown(nav_series)['max_drawdown']
    
    if max_dd == 0:
        return np.inf
    
    calmar_ratio = annualized_return / abs(max_dd)
    return calmar_ratio
```

#### 结果解读
- **< 10%**：风险控制优秀
- **10%-20%**：风险控制良好
- **20%-30%**：风险较高
- **> 30%**：风险很高

---

### 2.2 波动率 (Volatility)

#### 计算公式

**样本标准差：**
$$\sigma = \sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(r_i - \bar{r})^2}$$

**年化波动率：**
$$\sigma_{annual} = \sigma_{daily} \times \sqrt{252}$$

#### Python实现

```python
def calculate_volatility(returns_series, annualize=True, periods_per_year=252):
    """
    计算波动率
    
    参数:
        returns_series: pd.Series, 收益率序列
        annualize: bool, 是否年化
        periods_per_year: int, 每年周期数
    
    返回:
        float: 波动率
    """
    # 计算标准差
    volatility = returns_series.std()
    
    if annualize:
        volatility = volatility * np.sqrt(periods_per_year)
    
    return volatility


def calculate_rolling_volatility(returns_series, window=60, annualize=True):
    """
    计算滚动波动率
    
    参数:
        returns_series: pd.Series, 收益率序列
        window: int, 滚动窗口
        annualize: bool, 是否年化
    
    返回:
        pd.Series: 滚动波动率序列
    """
    rolling_vol = returns_series.rolling(window=window).std()
    
    if annualize:
        rolling_vol = rolling_vol * np.sqrt(252)
    
    return rolling_vol


def calculate_volatility_adjusted_return(nav_series, risk_free_rate=0.03):
    """
    计算风险调整后的收益指标
    
    参数:
        nav_series: pd.Series, 基金净值序列
        risk_free_rate: float, 无风险利率（年化）
    
    返回:
        dict: 包含波动率、年化收益率、夏普比率等
    """
    daily_returns = nav_series.pct_change().dropna()
    
    # 年化波动率
    annual_volatility = calculate_volatility(daily_returns, annualize=True)
    
    # 年化收益率
    annual_return = calculate_annualized_return(nav_series)
    
    # 日无风险利率
    daily_rf = risk_free_rate / 252
    
    # 夏普比率
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility != 0 else 0
    
    return {
        'annual_volatility': annual_volatility,
        'annual_return': annual_return,
        'sharpe_ratio': sharpe_ratio,
        'return_volatility_ratio': annual_return / annual_volatility if annual_volatility != 0 else 0
    }
```

#### 结果解读
- **< 15%**：低风险
- **15%-25%**：中等风险
- **> 25%**：高风险

---

### 2.3 下行标准差 (Downside Deviation)

#### 计算公式

$$\sigma_{down} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}\min(r_i - r_{target}, 0)^2}$$

其中，$r_{target}$ 通常取0或无风险利率

#### Python实现

```python
def calculate_downside_deviation(returns_series, target_return=0, annualize=True):
    """
    计算下行标准差
    
    参数:
        returns_series: pd.Series, 收益率序列
        target_return: float, 目标收益率（默认为0）
        annualize: bool, 是否年化
    
    返回:
        float: 下行标准差
    """
    # 计算下行偏差
    downside_returns = returns_series[returns_series < target_return]
    
    if len(downside_returns) == 0:
        return 0.0
    
    # 计算下行标准差
    downside_deviation = np.sqrt(((downside_returns - target_return) ** 2).mean())
    
    if annualize:
        downside_deviation = downside_deviation * np.sqrt(252)
    
    return downside_deviation


def calculate_sortino_ratio(nav_series, risk_free_rate=0.03, target_return=0):
    """
    计算索提诺比率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        risk_free_rate: float, 无风险利率（年化）
        target_return: float, 目标收益率
    
    返回:
        float: 索提诺比率
    """
    daily_returns = nav_series.pct_change().dropna()
    
    # 年化收益率
    annual_return = calculate_annualized_return(nav_series)
    
    # 下行标准差
    downside_dev = calculate_downside_deviation(daily_returns, target_return, annualize=True)
    
    if downside_dev == 0:
        return np.inf
    
    sortino_ratio = (annual_return - risk_free_rate) / downside_dev
    
    return sortino_ratio
```

---

### 2.4 风险价值 (VaR - Value at Risk)

#### 计算公式

**历史模拟法：**
$$VaR_{\alpha} = -\text{Percentile}(returns, \alpha \times 100\%)$$

**参数法（正态分布假设）：**
$$VaR_{\alpha} = -(\mu + z_{\alpha} \times \sigma)$$

其中：
- $\alpha$：置信水平（如95%）
- $z_{\alpha}$：标准正态分布的分位数

#### Python实现

```python
def calculate_var(returns_series, confidence_level=0.95, method='historical', 
                  time_horizon=1, annualize=True):
    """
    计算风险价值 (VaR)
    
    参数:
        returns_series: pd.Series, 收益率序列
        confidence_level: float, 置信水平（如0.95表示95%）
        method: str, 计算方法 ('historical', 'parametric', 'monte_carlo')
        time_horizon: int, 时间 horizon（天数）
        annualize: bool, 是否年化
    
    返回:
        dict: 包含VaR值和相关信息
    """
    if method == 'historical':
        # 历史模拟法
        var_value = -np.percentile(returns_series.dropna(), (1 - confidence_level) * 100)
    
    elif method == 'parametric':
        # 参数法（假设正态分布）
        mean = returns_series.mean()
        std = returns_series.std()
        z_score = abs(np.percentile(np.random.standard_normal(1000000), (1 - confidence_level) * 100))
        var_value = -(mean - z_score * std)
    
    elif method == 'monte_carlo':
        # 蒙特卡洛模拟法
        mean = returns_series.mean()
        std = returns_series.std()
        
        # 生成模拟收益率
        np.random.seed(42)
        simulated_returns = np.random.normal(mean, std, 100000)
        var_value = -np.percentile(simulated_returns, (1 - confidence_level) * 100)
    
    else:
        raise ValueError(f"不支持的VaR计算方法: {method}")
    
    # 调整时间 horizon
    if time_horizon > 1:
        var_value = var_value * np.sqrt(time_horizon)
    
    # 年化
    if annualize:
        annual_var = var_value * np.sqrt(252)
    else:
        annual_var = None
    
    return {
        'var': var_value,
        'var_pct': var_value * 100,
        'confidence_level': confidence_level,
        'method': method,
        'time_horizon': time_horizon,
        'annual_var': annual_var,
        'interpretation': f'在{confidence_level*100}%的置信水平下，单日损失不会超过{var_value*100:.2f}%'
    }


def calculate_cvar(returns_series, confidence_level=0.95, method='historical'):
    """
    计算条件风险价值 (CVaR/Expected Shortfall)
    
    参数:
        returns_series: pd.Series, 收益率序列
        confidence_level: float, 置信水平
        method: str, 计算方法
    
    返回:
        dict: 包含CVaR值
    """
    if method == 'historical':
        # 历史模拟法
        var_threshold = np.percentile(returns_series.dropna(), (1 - confidence_level) * 100)
        cvar_value = -returns_series[returns_series <= var_threshold].mean()
    
    elif method == 'parametric':
        # 参数法（假设正态分布）
        from scipy import stats
        mean = returns_series.mean()
        std = returns_series.std()
        z_score = stats.norm.ppf(1 - confidence_level)
        
        # CVaR = -μ + σ * φ(z) / (1-α)
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
```

---

## 3. 风险调整收益指标

### 3.1 夏普比率 (Sharpe Ratio)

#### 计算公式

$$Sharpe = \frac{R_p - R_f}{\sigma_p}$$

其中：
- $R_p$：投资组合年化收益率
- $R_f$：无风险利率（年化）
- $\sigma_p$：投资组合年化波动率

#### Python实现

```python
def calculate_sharpe_ratio(nav_series, risk_free_rate=0.03, periods_per_year=252):
    """
    计算夏普比率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        risk_free_rate: float, 无风险利率（年化，默认3%）
        periods_per_year: int, 每年周期数
    
    返回:
        float: 夏普比率
    """
    daily_returns = nav_series.pct_change().dropna()
    
    # 年化收益率
    annual_return = calculate_annualized_return(nav_series, periods_per_year)
    
    # 年化波动率
    annual_volatility = calculate_volatility(daily_returns, annualize=True, periods_per_year=periods_per_year)
    
    if annual_volatility == 0:
        return 0.0
    
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    
    return sharpe_ratio


def calculate_rolling_sharpe(nav_series, window=252, risk_free_rate=0.03):
    """
    计算滚动夏普比率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        window: int, 滚动窗口
        risk_free_rate: float, 无风险利率
    
    返回:
        pd.Series: 滚动夏普比率序列
    """
    daily_returns = nav_series.pct_change().dropna()
    daily_rf = risk_free_rate / 252
    
    # 滚动平均收益率
    rolling_mean = daily_returns.rolling(window=window).mean()
    
    # 滚动标准差
    rolling_std = daily_returns.rolling(window=window).std()
    
    # 滚动夏普比率（年化）
    rolling_sharpe = (rolling_mean - daily_rf) / rolling_std * np.sqrt(252)
    
    return rolling_sharpe
```

#### 结果解读
- **> 2.0**：非常优秀
- **1.0-2.0**：良好
- **0.5-1.0**：一般
- **< 0.5**：较差

---

### 3.2 索提诺比率 (Sortino Ratio)

#### 计算公式

$$Sortino = \frac{R_p - R_f}{\sigma_d}$$

其中：
- $\sigma_d$：下行标准差

#### Python实现

```python
def calculate_sortino_ratio(nav_series, risk_free_rate=0.03, target_return=0, 
                            periods_per_year=252):
    """
    计算索提诺比率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        risk_free_rate: float, 无风险利率（年化）
        target_return: float, 目标收益率（最小可接受收益率）
        periods_per_year: int, 每年周期数
    
    返回:
        float: 索提诺比率
    """
    daily_returns = nav_series.pct_change().dropna()
    
    # 年化收益率
    annual_return = calculate_annualized_return(nav_series, periods_per_year)
    
    # 下行标准差（年化）
    downside_dev = calculate_downside_deviation(daily_returns, target_return, annualize=True)
    
    if downside_dev == 0:
        return np.inf if annual_return > risk_free_rate else 0.0
    
    sortino_ratio = (annual_return - risk_free_rate) / downside_dev
    
    return sortino_ratio
```

#### 结果解读
- **> 2.0**：非常优秀
- **1.0-2.0**：良好
- **0.5-1.0**：一般
- **< 0.5**：较差

---

### 3.3 卡玛比率 (Calmar Ratio)

#### 计算公式

$$Calmar = \frac{R_p}{|MDD|}$$

其中：
- $MDD$：最大回撤

#### Python实现

```python
def calculate_calmar_ratio(nav_series, risk_free_rate=0.03, periods_per_year=252):
    """
    计算卡玛比率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        risk_free_rate: float, 无风险利率（年化，可选）
        periods_per_year: int, 每年周期数
    
    返回:
        dict: 包含卡玛比率及相关信息
    """
    # 年化收益率
    annual_return = calculate_annualized_return(nav_series, periods_per_year)
    
    # 最大回撤
    mdd_result = calculate_max_drawdown(nav_series)
    max_drawdown = abs(mdd_result['max_drawdown'])
    
    if max_drawdown == 0:
        calmar_ratio = np.inf
    else:
        calmar_ratio = (annual_return - risk_free_rate) / max_drawdown
    
    return {
        'calmar_ratio': calmar_ratio,
        'annual_return': annual_return,
        'max_drawdown': -max_drawdown,
        'max_drawdown_pct': -max_drawdown * 100,
        'excess_return': annual_return - risk_free_rate
    }
```

#### 结果解读
- **> 3.0**：非常优秀
- **2.0-3.0**：良好
- **1.0-2.0**：一般
- **< 1.0**：较差

---

### 3.4 特雷诺比率 (Treynor Ratio)

#### 计算公式

$$Treynor = \frac{R_p - R_f}{\beta_p}$$

其中：
- $\beta_p$：投资组合的Beta系数

#### Python实现

```python
def calculate_beta(stock_returns, market_returns):
    """
    计算Beta系数
    
    参数:
        stock_returns: pd.Series, 股票/基金收益率序列
        market_returns: pd.Series, 市场收益率序列
    
    返回:
        float: Beta系数
    """
    # 对齐数据
    aligned_data = pd.concat([stock_returns, market_returns], axis=1).dropna()
    
    if len(aligned_data) < 2:
        return 1.0
    
    stock_ret = aligned_data.iloc[:, 0]
    market_ret = aligned_data.iloc[:, 1]
    
    # 计算协方差和市场方差
    covariance = stock_ret.cov(market_ret)
    market_variance = market_ret.var()
    
    if market_variance == 0:
        return 1.0
    
    beta = covariance / market_variance
    
    return beta


def calculate_treynor_ratio(nav_series, benchmark_series, risk_free_rate=0.03):
    """
    计算特雷诺比率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        benchmark_series: pd.Series, 基准指数序列
        risk_free_rate: float, 无风险利率（年化）
    
    返回:
        dict: 包含特雷诺比率及相关信息
    """
    # 计算收益率
    fund_returns = nav_series.pct_change().dropna()
    benchmark_returns = benchmark_series.pct_change().dropna()
    
    # 年化收益率
    annual_return = calculate_annualized_return(nav_series)
    
    # 计算Beta
    beta = calculate_beta(fund_returns, benchmark_returns)
    
    if beta == 0:
        treynor_ratio = np.inf if annual_return > risk_free_rate else 0.0
    else:
        treynor_ratio = (annual_return - risk_free_rate) / beta
    
    return {
        'treynor_ratio': treynor_ratio,
        'beta': beta,
        'annual_return': annual_return,
        'excess_return': annual_return - risk_free_rate
    }
```

#### 结果解读
- **> 0.1**：优秀
- **0.05-0.1**：良好
- **0-0.05**：一般
- **< 0**：较差

---

### 3.5 信息比率 (Information Ratio)

#### 计算公式

$$IR = \frac{R_p - R_b}{\sigma_{tracking}}$$

其中：
- $R_b$：基准收益率
- $\sigma_{tracking}$：跟踪误差（超额收益的标准差）

#### Python实现

```python
def calculate_tracking_error(fund_returns, benchmark_returns, annualize=True):
    """
    计算跟踪误差
    
    参数:
        fund_returns: pd.Series, 基金收益率序列
        benchmark_returns: pd.Series, 基准收益率序列
        annualize: bool, 是否年化
    
    返回:
        float: 跟踪误差
    """
    # 对齐数据
    aligned_data = pd.concat([fund_returns, benchmark_returns], axis=1).dropna()
    
    if len(aligned_data) < 2:
        return 0.0
    
    fund_ret = aligned_data.iloc[:, 0]
    bench_ret = aligned_data.iloc[:, 1]
    
    # 计算超额收益
    excess_returns = fund_ret - bench_ret
    
    # 计算跟踪误差（超额收益的标准差）
    tracking_error = excess_returns.std()
    
    if annualize:
        tracking_error = tracking_error * np.sqrt(252)
    
    return tracking_error


def calculate_information_ratio(nav_series, benchmark_series):
    """
    计算信息比率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        benchmark_series: pd.Series, 基准指数序列
    
    返回:
        dict: 包含信息比率及相关信息
    """
    # 计算收益率
    fund_returns = nav_series.pct_change().dropna()
    benchmark_returns = benchmark_series.pct_change().dropna()
    
    # 对齐数据
    aligned_data = pd.concat([fund_returns, benchmark_returns], axis=1).dropna()
    
    if len(aligned_data) < 2:
        return {
            'information_ratio': 0.0,
            'tracking_error': 0.0,
            'excess_return': 0.0
        }
    
    fund_ret = aligned_data.iloc[:, 0]
    bench_ret = aligned_data.iloc[:, 1]
    
    # 计算年化收益率
    fund_annual_return = calculate_annualized_return(nav_series.loc[fund_ret.index])
    bench_annual_return = calculate_annualized_return(benchmark_series.loc[bench_ret.index])
    
    # 年化超额收益
    excess_return = fund_annual_return - bench_annual_return
    
    # 跟踪误差
    tracking_error = calculate_tracking_error(fund_ret, bench_ret, annualize=True)
    
    if tracking_error == 0:
        information_ratio = np.inf if excess_return > 0 else 0.0
    else:
        information_ratio = excess_return / tracking_error
    
    return {
        'information_ratio': information_ratio,
        'tracking_error': tracking_error,
        'excess_return': excess_return,
        'fund_annual_return': fund_annual_return,
        'benchmark_annual_return': bench_annual_return
    }
```

#### 结果解读
- **> 1.0**：非常优秀
- **0.5-1.0**：良好
- **0-0.5**：一般
- **< 0**：较差（跑输基准）

---

## 4. 基金业绩比较基准

### 4.1 常见业绩比较基准指数

| 指数名称 | 指数代码 | 适用基金类型 | 特点 |
|----------|----------|--------------|------|
| 沪深300 | 000300.SH | 大盘股票型基金 | A股核心资产代表 |
| 中证500 | 000905.SH | 中盘股票型基金 | 中小盘成长风格 |
| 中证800 | 000906.SH | 全市场股票型基金 | 大中小盘综合 |
| 中证1000 | 000852.SH | 小盘股票型基金 | 小市值股票 |
| 中证全债 | H11001.CSI | 债券型基金 | 全市场债券 |
| 中债总指数 | CBA00301.CS | 债券型基金 | 利率债为主 |
| 中证货币基金 | H11025.CSI | 货币基金 | 货币市场 |
| 偏股混合型基金指数 | 885001.WI | 偏股混合基金 | 同类基金比较 |
| 普通股票型基金指数 | 885000.WI | 股票型基金 | 同类基金比较 |

### 4.2 基准数据获取方法

#### Python实现

```python
import akshare as ak
import yfinance as yf

def get_benchmark_data(benchmark_code, start_date=None, end_date=None):
    """
    获取基准指数数据
    
    参数:
        benchmark_code: str, 指数代码（如'000300.SH'）
        start_date: str, 开始日期（YYYY-MM-DD）
        end_date: str, 结束日期（YYYY-MM-DD）
    
    返回:
        pd.DataFrame: 包含日期和收盘价的DataFrame
    """
    try:
        # 使用akshare获取A股指数数据
        if benchmark_code.endswith('.SH') or benchmark_code.endswith('.SZ'):
            # 去除后缀
            code = benchmark_code.split('.')[0]
            df = ak.index_zh_a_hist(symbol=code, period="daily", 
                                    start_date=start_date, end_date=end_date)
            df['date'] = pd.to_datetime(df['日期'])
            df = df.rename(columns={'收盘': 'close'})
            return df[['date', 'close']].set_index('date')['close']
        
        # 使用yfinance获取国际指数
        else:
            ticker = benchmark_code
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            return df['Close']
    
    except Exception as e:
        print(f"获取基准数据失败: {e}")
        return None


def get_multiple_benchmarks(benchmark_codes, start_date=None, end_date=None):
    """
    获取多个基准指数数据
    
    参数:
        benchmark_codes: list, 指数代码列表
        start_date: str, 开始日期
        end_date: str, 结束日期
    
    返回:
        pd.DataFrame: 各基准指数的收盘价
    """
    data = {}
    for code in benchmark_codes:
        series = get_benchmark_data(code, start_date, end_date)
        if series is not None:
            data[code] = series
    
    return pd.DataFrame(data)
```

### 4.3 超额收益计算

#### Python实现

```python
def calculate_excess_return(nav_series, benchmark_series, method='arithmetic'):
    """
    计算超额收益
    
    参数:
        nav_series: pd.Series, 基金净值序列
        benchmark_series: pd.Series, 基准指数序列
        method: str, 计算方法 ('arithmetic', 'geometric')
    
    返回:
        dict: 包含超额收益相关信息
    """
    # 计算累计收益率
    fund_return = calculate_cumulative_return(nav_series)
    benchmark_return = calculate_cumulative_return(benchmark_series)
    
    # 计算年化收益率
    fund_annual = calculate_annualized_return(nav_series)
    benchmark_annual = calculate_annualized_return(benchmark_series)
    
    # 算术超额收益
    arithmetic_excess = fund_annual - benchmark_annual
    
    # 几何超额收益
    geometric_excess = (1 + fund_annual) / (1 + benchmark_annual) - 1
    
    # 胜率（跑赢基准的交易日比例）
    fund_returns = nav_series.pct_change().dropna()
    bench_returns = benchmark_series.pct_change().dropna()
    
    aligned = pd.concat([fund_returns, bench_returns], axis=1).dropna()
    win_rate = (aligned.iloc[:, 0] > aligned.iloc[:, 1]).mean()
    
    return {
        'fund_return': fund_return,
        'benchmark_return': benchmark_return,
        'fund_annual_return': fund_annual,
        'benchmark_annual_return': benchmark_annual,
        'arithmetic_excess': arithmetic_excess,
        'geometric_excess': geometric_excess,
        'excess_return': arithmetic_excess if method == 'arithmetic' else geometric_excess,
        'win_rate': win_rate,
        'win_rate_pct': win_rate * 100
    }


def calculate_alpha_beta(nav_series, benchmark_series, risk_free_rate=0.03):
    """
    计算Alpha和Beta
    
    参数:
        nav_series: pd.Series, 基金净值序列
        benchmark_series: pd.Series, 基准指数序列
        risk_free_rate: float, 无风险利率（年化）
    
    返回:
        dict: 包含Alpha、Beta、R²等信息
    """
    fund_returns = nav_series.pct_change().dropna()
    benchmark_returns = benchmark_series.pct_change().dropna()
    
    # 对齐数据
    aligned = pd.concat([fund_returns, benchmark_returns], axis=1).dropna()
    
    if len(aligned) < 2:
        return {
            'alpha': 0.0,
            'beta': 1.0,
            'r_squared': 0.0
        }
    
    fund_ret = aligned.iloc[:, 0]
    bench_ret = aligned.iloc[:, 1]
    
    # 计算Beta
    beta = calculate_beta(fund_ret, bench_ret)
    
    # 计算Alpha（年化）
    fund_annual = calculate_annualized_return(nav_series)
    bench_annual = calculate_annualized_return(benchmark_series)
    alpha = fund_annual - risk_free_rate - beta * (bench_annual - risk_free_rate)
    
    # 计算R²
    correlation = fund_ret.corr(bench_ret)
    r_squared = correlation ** 2
    
    return {
        'alpha': alpha,
        'alpha_annual': alpha,
        'beta': beta,
        'r_squared': r_squared,
        'correlation': correlation,
        'fund_annual_return': fund_annual,
        'benchmark_annual_return': bench_annual
    }
```

---

## 5. 基金持仓分析方法

### 5.1 持仓集中度计算

#### 计算公式

**前N大重仓股集中度：**
$$Concentration_{topN} = \sum_{i=1}^{N}w_i \times 100\%$$

其中，$w_i$ 为第i大重仓股的持仓权重

**赫芬达尔指数（HHI）：**
$$HHI = \sum_{i=1}^{n}w_i^2$$

#### Python实现

```python
def calculate_concentration(holdings_df, top_n=10):
    """
    计算持仓集中度
    
    参数:
        holdings_df: pd.DataFrame, 持仓数据，包含'stock_code', 'stock_name', 'weight'列
        top_n: int, 前N大重仓股
    
    返回:
        dict: 集中度指标
    """
    # 按权重排序
    sorted_holdings = holdings_df.sort_values('weight', ascending=False)
    
    # 前N大重仓股集中度
    top_n_concentration = sorted_holdings.head(top_n)['weight'].sum()
    
    # 赫芬达尔指数
    hhi = (holdings_df['weight'] ** 2).sum()
    
    # 有效持股数量（HHI的倒数）
    effective_n = 1 / hhi if hhi > 0 else len(holdings_df)
    
    # 前3、前5、前10集中度
    top3_conc = sorted_holdings.head(3)['weight'].sum()
    top5_conc = sorted_holdings.head(5)['weight'].sum()
    top10_conc = sorted_holdings.head(10)['weight'].sum()
    
    return {
        'top3_concentration': top3_conc,
        'top3_concentration_pct': top3_conc * 100,
        'top5_concentration': top5_conc,
        'top5_concentration_pct': top5_conc * 100,
        'top10_concentration': top10_conc,
        'top10_concentration_pct': top10_conc * 100,
        f'top{top_n}_concentration': top_n_concentration,
        f'top{top_n}_concentration_pct': top_n_concentration * 100,
        'hhi': hhi,
        'effective_n': effective_n,
        'total_holdings': len(holdings_df)
    }


def calculate_sector_concentration(sector_weights):
    """
    计算行业集中度
    
    参数:
        sector_weights: pd.Series, 行业权重（行业名称为索引）
    
    返回:
        dict: 行业集中度指标
    """
    # 按权重排序
    sorted_sectors = sector_weights.sort_values(ascending=False)
    
    # 前3大行业集中度
    top3_sector_conc = sorted_sectors.head(3).sum()
    
    # 前5大行业集中度
    top5_sector_conc = sorted_sectors.head(5).sum()
    
    # 行业赫芬达尔指数
    sector_hhi = (sector_weights ** 2).sum()
    
    # 行业数量
    num_sectors = len(sector_weights[sector_weights > 0])
    
    return {
        'top3_sector_concentration': top3_sector_conc,
        'top3_sector_concentration_pct': top3_sector_conc * 100,
        'top5_sector_concentration': top5_sector_conc,
        'top5_sector_concentration_pct': top5_sector_conc * 100,
        'sector_hhi': sector_hhi,
        'num_sectors': num_sectors,
        'sector_weights': sorted_sectors.to_dict()
    }
```

---

### 5.2 行业配置分析

#### Python实现

```python
def analyze_sector_allocation(current_holdings, previous_holdings=None, 
                               sector_mapping=None):
    """
    分析行业配置
    
    参数:
        current_holdings: pd.DataFrame, 当前持仓，包含'stock_code', 'weight'列
        previous_holdings: pd.DataFrame, 上期持仓（可选，用于计算变化）
        sector_mapping: dict, 股票代码到行业的映射
    
    返回:
        dict: 行业配置分析结果
    """
    # 添加行业信息
    if sector_mapping:
        current_holdings = current_holdings.copy()
        current_holdings['sector'] = current_holdings['stock_code'].map(sector_mapping)
    
    # 按行业汇总权重
    current_sector_weights = current_holdings.groupby('sector')['weight'].sum()
    
    result = {
        'current_allocation': current_sector_weights.to_dict(),
        'top_sectors': current_sector_weights.sort_values(ascending=False).head(5).to_dict()
    }
    
    # 如果有上期数据，计算变化
    if previous_holdings is not None:
        if sector_mapping:
            previous_holdings = previous_holdings.copy()
            previous_holdings['sector'] = previous_holdings['stock_code'].map(sector_mapping)
        
        previous_sector_weights = previous_holdings.groupby('sector')['weight'].sum()
        
        # 合并当前和上期数据
        all_sectors = set(current_sector_weights.index) | set(previous_sector_weights.index)
        sector_changes = {}
        
        for sector in all_sectors:
            current_w = current_sector_weights.get(sector, 0)
            previous_w = previous_sector_weights.get(sector, 0)
            sector_changes[sector] = {
                'current': current_w,
                'previous': previous_w,
                'change': current_w - previous_w,
                'change_pct': (current_w - previous_w) * 100
            }
        
        result['sector_changes'] = sector_changes
        
        # 识别增配和减配的行业
        increased_sectors = {k: v for k, v in sector_changes.items() if v['change'] > 0}
        decreased_sectors = {k: v for k, v in sector_changes.items() if v['change'] < 0}
        
        result['increased_sectors'] = increased_sectors
        result['decreased_sectors'] = decreased_sectors
    
    return result


def calculate_sector_deviation(fund_sector_weights, benchmark_sector_weights):
    """
    计算行业配置偏离度（相对于基准）
    
    参数:
        fund_sector_weights: pd.Series, 基金行业权重
        benchmark_sector_weights: pd.Series, 基准行业权重
    
    返回:
        dict: 行业偏离分析
    """
    # 合并数据
    all_sectors = set(fund_sector_weights.index) | set(benchmark_sector_weights.index)
    
    deviations = {}
    for sector in all_sectors:
        fund_w = fund_sector_weights.get(sector, 0)
        bench_w = benchmark_sector_weights.get(sector, 0)
        deviation = fund_w - bench_w
        deviations[sector] = {
            'fund_weight': fund_w,
            'benchmark_weight': bench_w,
            'deviation': deviation,
            'deviation_pct': deviation * 100,
            'relative_weight': fund_w / bench_w if bench_w > 0 else np.inf
        }
    
    # 计算总偏离度（绝对值之和的一半）
    total_deviation = sum(abs(d['deviation']) for d in deviations.values()) / 2
    
    # 超配和低配的行业
    overweight_sectors = {k: v for k, v in deviations.items() if v['deviation'] > 0}
    underweight_sectors = {k: v for k, v in deviations.items() if v['deviation'] < 0}
    
    return {
        'total_deviation': total_deviation,
        'total_deviation_pct': total_deviation * 100,
        'sector_deviations': deviations,
        'overweight_sectors': overweight_sectors,
        'underweight_sectors': underweight_sectors
    }
```

---

### 5.3 调仓检测方法

#### Python实现

```python
def detect_position_changes(current_holdings, previous_holdings, 
                            change_threshold=0.01):
    """
    检测持仓变化
    
    参数:
        current_holdings: pd.DataFrame, 当前持仓
        previous_holdings: pd.DataFrame, 上期持仓
        change_threshold: float, 变化阈值（默认1%）
    
    返回:
        dict: 调仓检测结果
    """
    # 合并持仓数据
    current_dict = dict(zip(current_holdings['stock_code'], current_holdings['weight']))
    previous_dict = dict(zip(previous_holdings['stock_code'], previous_holdings['weight']))
    
    all_stocks = set(current_dict.keys()) | set(previous_dict.keys())
    
    added_stocks = []  # 新增持仓
    removed_stocks = []  # 移除持仓
    increased_stocks = []  # 加仓
    decreased_stocks = []  # 减仓
    unchanged_stocks = []  # 持仓不变
    
    for stock in all_stocks:
        current_w = current_dict.get(stock, 0)
        previous_w = previous_dict.get(stock, 0)
        change = current_w - previous_w
        
        stock_info = {
            'stock_code': stock,
            'current_weight': current_w,
            'previous_weight': previous_w,
            'change': change,
            'change_pct': change * 100
        }
        
        if previous_w == 0 and current_w > 0:
            added_stocks.append(stock_info)
        elif previous_w > 0 and current_w == 0:
            removed_stocks.append(stock_info)
        elif abs(change) >= change_threshold:
            if change > 0:
                increased_stocks.append(stock_info)
            else:
                decreased_stocks.append(stock_info)
        else:
            unchanged_stocks.append(stock_info)
    
    # 计算调仓幅度
    total_change = sum(abs(s['change']) for s in added_stocks + removed_stocks + 
                       increased_stocks + decreased_stocks) / 2
    
    return {
        'added_stocks': added_stocks,
        'removed_stocks': removed_stocks,
        'increased_stocks': increased_stocks,
        'decreased_stocks': decreased_stocks,
        'unchanged_stocks': unchanged_stocks,
        'num_added': len(added_stocks),
        'num_removed': len(removed_stocks),
        'num_increased': len(increased_stocks),
        'num_decreased': len(decreased_stocks),
        'turnover_ratio': total_change,
        'turnover_ratio_pct': total_change * 100
    }


def estimate_turnover_rate(holdings_list, dates, method='aggregate'):
    """
    估算持仓换手率
    
    参数:
        holdings_list: list of pd.DataFrame, 各期持仓数据
        dates: list, 各期日期
        method: str, 计算方法 ('aggregate', 'average')
    
    返回:
        dict: 换手率估算结果
    """
    if len(holdings_list) < 2:
        return {'annual_turnover': 0.0, 'quarterly_turnover': []}
    
    quarterly_turnovers = []
    
    for i in range(1, len(holdings_list)):
        changes = detect_position_changes(holdings_list[i], holdings_list[i-1])
        quarterly_turnovers.append({
            'period': f"{dates[i-1]} to {dates[i]}",
            'turnover': changes['turnover_ratio'],
            'turnover_pct': changes['turnover_ratio_pct']
        })
    
    # 年化换手率
    if method == 'aggregate':
        # 汇总法：假设4个季度
        annual_turnover = sum(t['turnover'] for t in quarterly_turnovers) * 2  # 买入+卖出
    else:
        # 平均法
        avg_quarterly = np.mean([t['turnover'] for t in quarterly_turnovers])
        annual_turnover = avg_quarterly * 4 * 2
    
    return {
        'annual_turnover': annual_turnover,
        'annual_turnover_pct': annual_turnover * 100,
        'quarterly_turnover': quarterly_turnovers,
        'avg_quarterly_turnover': np.mean([t['turnover'] for t in quarterly_turnovers])
    }
```

---

### 5.4 持仓换手率估算

#### Python实现

```python
def calculate_portfolio_turnover(nav_series, returns_series=None, 
                                  use_flow_method=False):
    """
    计算组合换手率
    
    参数:
        nav_series: pd.Series, 基金净值序列
        returns_series: pd.Series, 基金收益率序列（可选）
        use_flow_method: bool, 是否使用资金流向法
    
    返回:
        dict: 换手率相关指标
    """
    if returns_series is None:
        returns_series = nav_series.pct_change().dropna()
    
    if use_flow_method:
        # 基于资金流向的换手率估算
        # 需要申购赎回数据，这里简化处理
        daily_turnover = returns_series.abs().mean()
    else:
        # 基于净值变化的估算
        daily_turnover = returns_series.abs().mean()
    
    # 年化换手率（假设每个交易日都有交易）
    annual_turnover = daily_turnover * 252
    
    # 调整因子（考虑到基金并非每日全仓调仓）
    adjustment_factor = 0.5  # 假设平均持仓周期为2天
    adjusted_annual_turnover = annual_turnover * adjustment_factor
    
    return {
        'daily_turnover': daily_turnover,
        'daily_turnover_pct': daily_turnover * 100,
        'annual_turnover': annual_turnover,
        'annual_turnover_pct': annual_turnover * 100,
        'adjusted_annual_turnover': adjusted_annual_turnover,
        'adjusted_annual_turnover_pct': adjusted_annual_turnover * 100
    }


def analyze_trading_activity(nav_series, volume_threshold=0.02):
    """
    分析交易活跃度
    
    参数:
        nav_series: pd.Series, 基金净值序列
        volume_threshold: float, 交易活跃度阈值
    
    返回:
        dict: 交易活跃度分析
    """
    daily_returns = nav_series.pct_change().dropna()
    
    # 计算日收益率的绝对值
    abs_returns = daily_returns.abs()
    
    # 高活跃度交易日（收益率变化超过阈值）
    high_activity_days = abs_returns[abs_returns > volume_threshold]
    
    # 低活跃度交易日
    low_activity_days = abs_returns[abs_returns <= volume_threshold]
    
    return {
        'avg_daily_change': abs_returns.mean(),
        'avg_daily_change_pct': abs_returns.mean() * 100,
        'max_daily_change': abs_returns.max(),
        'max_daily_change_pct': abs_returns.max() * 100,
        'high_activity_days': len(high_activity_days),
        'high_activity_ratio': len(high_activity_days) / len(abs_returns),
        'low_activity_days': len(low_activity_days),
        'activity_score': abs_returns.mean() * 100  # 活跃度评分
    }
```

---

## 6. 基金经理评估

### 6.1 基金经理任期收益计算

#### Python实现

```python
def calculate_manager_tenure_return(nav_series, manager_start_date, 
                                     manager_end_date=None):
    """
    计算基金经理任期收益
    
    参数:
        nav_series: pd.Series, 基金净值序列
        manager_start_date: str/datetime, 基金经理上任日期
        manager_end_date: str/datetime, 基金经理离任日期（可选，默认至今）
    
    返回:
        dict: 任期收益相关信息
    """
    # 筛选任期内的数据
    tenure_nav = nav_series[nav_series.index >= manager_start_date]
    
    if manager_end_date:
        tenure_nav = tenure_nav[tenure_nav.index <= manager_end_date]
    
    if len(tenure_nav) < 2:
        return {
            'tenure_return': 0.0,
            'annualized_return': 0.0,
            'tenure_days': 0
        }
    
    # 计算任期收益
    tenure_return = calculate_cumulative_return(tenure_nav)
    
    # 计算年化收益
    annualized_return = calculate_annualized_return(tenure_nav)
    
    # 计算任期天数
    tenure_days = (tenure_nav.index[-1] - tenure_nav.index[0]).days
    
    # 计算风险指标
    volatility = calculate_volatility(tenure_nav.pct_change().dropna(), annualize=True)
    sharpe = calculate_sharpe_ratio(tenure_nav)
    max_dd = calculate_max_drawdown(tenure_nav)
    
    return {
        'start_date': tenure_nav.index[0],
        'end_date': tenure_nav.index[-1],
        'tenure_days': tenure_days,
        'tenure_years': tenure_days / 365.25,
        'start_nav': tenure_nav.iloc[0],
        'end_nav': tenure_nav.iloc[-1],
        'tenure_return': tenure_return,
        'tenure_return_pct': tenure_return * 100,
        'annualized_return': annualized_return,
        'annualized_return_pct': annualized_return * 100,
        'volatility': volatility,
        'volatility_pct': volatility * 100,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd['max_drawdown'],
        'max_drawdown_pct': max_dd['max_drawdown_pct'],
        'calmar_ratio': calculate_calmar_ratio(tenure_nav, annualized_return)
    }


def compare_managers(nav_series, manager_periods):
    """
    比较不同基金经理的业绩
    
    参数:
        nav_series: pd.Series, 基金净值序列
        manager_periods: list of dict, 各基金经理任期 [{'name': '经理A', 'start': '2020-01-01', 'end': '2021-12-31'}, ...]
    
    返回:
        pd.DataFrame: 各基金经理业绩对比
    """
    results = []
    
    for manager in manager_periods:
        result = calculate_manager_tenure_return(
            nav_series, 
            manager['start'], 
            manager.get('end')
        )
        result['manager_name'] = manager['name']
        results.append(result)
    
    return pd.DataFrame(results)
```

---

### 6.2 基金经理稳定性评估

#### Python实现

```python
def calculate_return_consistency(returns_series, window=63):
    """
    计算收益稳定性（滚动窗口胜率）
    
    参数:
        returns_series: pd.Series, 收益率序列
        window: int, 滚动窗口（默认63个交易日，约3个月）
    
    返回:
        dict: 稳定性指标
    """
    # 正收益比例
    positive_ratio = (returns_series > 0).mean()
    
    # 滚动胜率
    rolling_positive = returns_series.rolling(window=window).apply(
        lambda x: (x > 0).mean()
    )
    
    # 胜率稳定性（滚动胜率的标准差）
    win_rate_stability = rolling_positive.std()
    
    # 收益一致性（连续正收益/负收益的统计）
    positive_streaks = []
    negative_streaks = []
    current_streak = 1
    current_sign = returns_series.iloc[0] > 0
    
    for ret in returns_series.iloc[1:]:
        if (ret > 0) == current_sign:
            current_streak += 1
        else:
            if current_sign:
                positive_streaks.append(current_streak)
            else:
                negative_streaks.append(current_streak)
            current_streak = 1
            current_sign = ret > 0
    
    avg_positive_streak = np.mean(positive_streaks) if positive_streaks else 0
    avg_negative_streak = np.mean(negative_streaks) if negative_streaks else 0
    
    return {
        'positive_ratio': positive_ratio,
        'positive_ratio_pct': positive_ratio * 100,
        'avg_win_rate': rolling_positive.mean(),
        'win_rate_stability': win_rate_stability,
        'avg_positive_streak': avg_positive_streak,
        'avg_negative_streak': avg_negative_streak,
        'max_positive_streak': max(positive_streaks) if positive_streaks else 0,
        'max_negative_streak': max(negative_streaks) if negative_streaks else 0
    }


def evaluate_manager_stability(nav_series, benchmark_series=None):
    """
    综合评估基金经理稳定性
    
    参数:
        nav_series: pd.Series, 基金净值序列
        benchmark_series: pd.Series, 基准指数序列（可选）
    
    返回:
        dict: 稳定性评估结果
    """
    daily_returns = nav_series.pct_change().dropna()
    
    # 收益稳定性
    return_consistency = calculate_return_consistency(daily_returns)
    
    # 波动率稳定性
    rolling_vol = calculate_rolling_volatility(daily_returns, window=63)
    vol_stability = 1 / (rolling_vol.std() + 1e-6)  # 波动越小越稳定
    
    # 最大回撤恢复能力
    mdd_result = calculate_max_drawdown(nav_series)
    recovery_score = 1 / (mdd_result['recovery_days'] + 1) if mdd_result['recovery_days'] else 0
    
    # 相对基准稳定性（如果有基准）
    relative_stability = None
    if benchmark_series is not None:
        excess_returns = daily_returns - benchmark_series.pct_change().dropna()
        relative_stability = {
            'excess_positive_ratio': (excess_returns > 0).mean(),
            'excess_volatility': excess_returns.std() * np.sqrt(252),
            'tracking_error': calculate_tracking_error(daily_returns, 
                                                        benchmark_series.pct_change().dropna())
        }
    
    # 综合稳定性评分（0-100）
    stability_score = (
        return_consistency['positive_ratio'] * 30 +
        (1 - min(return_consistency['win_rate_stability'] * 10, 1)) * 20 +
        min(vol_stability / 10, 1) * 20 +
        min(recovery_score * 100, 1) * 30
    )
    
    return {
        'stability_score': stability_score,
        'stability_grade': 'A' if stability_score >= 80 else 'B' if stability_score >= 60 else 'C' if stability_score >= 40 else 'D',
        'return_consistency': return_consistency,
        'volatility_stability': vol_stability,
        'recovery_score': recovery_score,
        'relative_stability': relative_stability
    }
```

---

## 7. 完整Python实现

以下是封装了所有计算方法的完整Python类，方便集成到基金数据库系统中。

### 7.1 核心分析类

```python
"""
基金分析工具库 - FundAnalysisToolkit

提供完整的基金分析指标计算方法，包括：
- 收益率计算
- 风险指标计算
- 风险调整收益指标
- 基准比较
- 持仓分析
- 基金经理评估

作者: Fund Analyst
版本: 1.0.0
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


@dataclass
class FundMetrics:
    """基金指标数据类"""
    # 收益率指标
    total_return: float = 0.0
    annualized_return: float = 0.0
    
    # 风险指标
    volatility: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_start: datetime = None
    max_drawdown_end: datetime = None
    downside_deviation: float = 0.0
    var_95: float = 0.0
    cvar_95: float = 0.0
    
    # 风险调整收益指标
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    treynor_ratio: float = 0.0
    information_ratio: float = 0.0
    
    # 基准比较
    alpha: float = 0.0
    beta: float = 1.0
    tracking_error: float = 0.0
    excess_return: float = 0.0
    
    # 其他
    win_rate: float = 0.0
    positive_ratio: float = 0.0


class FundAnalyzer:
    """
    基金分析器主类
    
    使用示例:
        analyzer = FundAnalyzer(risk_free_rate=0.03)
        metrics = analyzer.calculate_all_metrics(nav_series, benchmark_series)
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
    
    # ==================== 收益率计算 ====================
    
    def calculate_cumulative_return(self, nav_series: pd.Series) -> float:
        """计算累计收益率"""
        if len(nav_series) < 2:
            return 0.0
        daily_returns = nav_series.pct_change().dropna()
        return (1 + daily_returns).prod() - 1
    
    def calculate_annualized_return(self, nav_series: pd.Series) -> float:
        """计算年化收益率"""
        if len(nav_series) < 2:
            return 0.0
        total_return = self.calculate_cumulative_return(nav_series)
        n_periods = len(nav_series) - 1
        return (1 + total_return) ** (self.periods_per_year / n_periods) - 1
    
    def calculate_interval_return(self, nav_series: pd.Series, 
                                   start_date=None, end_date=None) -> Dict:
        """计算区间收益率"""
        if start_date:
            nav_series = nav_series[nav_series.index >= start_date]
        if end_date:
            nav_series = nav_series[nav_series.index <= end_date]
        
        if len(nav_series) < 2:
            return {'interval_return': 0.0, 'annualized_return': 0.0}
        
        interval_return = self.calculate_cumulative_return(nav_series)
        trading_days = len(nav_series) - 1
        annualized = (1 + interval_return) ** (252 / trading_days) - 1
        
        return {
            'interval_return': interval_return,
            'annualized_return': annualized,
            'trading_days': trading_days,
            'calendar_days': (nav_series.index[-1] - nav_series.index[0]).days
        }
    
    # ==================== 风险指标 ====================
    
    def calculate_volatility(self, returns_series: pd.Series, 
                              annualize: bool = True) -> float:
        """计算波动率"""
        vol = returns_series.std()
        if annualize:
            vol = vol * np.sqrt(self.periods_per_year)
        return vol
    
    def calculate_max_drawdown(self, nav_series: pd.Series) -> Dict:
        """计算最大回撤"""
        cumulative = (1 + nav_series.pct_change().fillna(0)).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = drawdown.min()
        end_date = drawdown.idxmin()
        start_date = running_max.loc[:end_date].idxmax()
        
        return {
            'max_drawdown': max_dd,
            'max_drawdown_pct': max_dd * 100,
            'start_date': start_date,
            'end_date': end_date,
            'drawdown_days': (end_date - start_date).days,
            'drawdown_series': drawdown
        }
    
    def calculate_downside_deviation(self, returns_series: pd.Series,
                                      target_return: float = 0) -> float:
        """计算下行标准差"""
        downside = returns_series[returns_series < target_return]
        if len(downside) == 0:
            return 0.0
        dd = np.sqrt(((downside - target_return) ** 2).mean())
        return dd * np.sqrt(self.periods_per_year)
    
    def calculate_var(self, returns_series: pd.Series, 
                      confidence: float = 0.95) -> Dict:
        """计算VaR"""
        var_val = -np.percentile(returns_series.dropna(), (1 - confidence) * 100)
        return {
            'var': var_val,
            'var_pct': var_val * 100,
            'confidence': confidence
        }
    
    def calculate_cvar(self, returns_series: pd.Series,
                        confidence: float = 0.95) -> Dict:
        """计算CVaR"""
        var_threshold = np.percentile(returns_series.dropna(), (1 - confidence) * 100)
        cvar_val = -returns_series[returns_series <= var_threshold].mean()
        return {
            'cvar': cvar_val,
            'cvar_pct': cvar_val * 100,
            'confidence': confidence
        }
    
    # ==================== 风险调整收益 ====================
    
    def calculate_sharpe_ratio(self, nav_series: pd.Series) -> float:
        """计算夏普比率"""
        annual_return = self.calculate_annualized_return(nav_series)
        daily_returns = nav_series.pct_change().dropna()
        annual_vol = self.calculate_volatility(daily_returns)
        if annual_vol == 0:
            return 0.0
        return (annual_return - self.risk_free_rate) / annual_vol
    
    def calculate_sortino_ratio(self, nav_series: pd.Series) -> float:
        """计算索提诺比率"""
        annual_return = self.calculate_annualized_return(nav_series)
        daily_returns = nav_series.pct_change().dropna()
        downside_dev = self.calculate_downside_deviation(daily_returns)
        if downside_dev == 0:
            return np.inf if annual_return > self.risk_free_rate else 0.0
        return (annual_return - self.risk_free_rate) / downside_dev
    
    def calculate_calmar_ratio(self, nav_series: pd.Series) -> float:
        """计算卡玛比率"""
        annual_return = self.calculate_annualized_return(nav_series)
        max_dd = self.calculate_max_drawdown(nav_series)['max_drawdown']
        if max_dd == 0:
            return np.inf
        return (annual_return - self.risk_free_rate) / abs(max_dd)
    
    def calculate_beta(self, fund_returns: pd.Series, 
                        market_returns: pd.Series) -> float:
        """计算Beta"""
        aligned = pd.concat([fund_returns, market_returns], axis=1).dropna()
        if len(aligned) < 2:
            return 1.0
        cov = aligned.iloc[:, 0].cov(aligned.iloc[:, 1])
        var = aligned.iloc[:, 1].var()
        return cov / var if var != 0 else 1.0
    
    def calculate_treynor_ratio(self, nav_series: pd.Series,
                                 benchmark_series: pd.Series) -> Dict:
        """计算特雷诺比率"""
        fund_ret = nav_series.pct_change().dropna()
        bench_ret = benchmark_series.pct_change().dropna()
        annual_return = self.calculate_annualized_return(nav_series)
        beta = self.calculate_beta(fund_ret, bench_ret)
        if beta == 0:
            treynor = np.inf if annual_return > self.risk_free_rate else 0.0
        else:
            treynor = (annual_return - self.risk_free_rate) / beta
        return {
            'treynor_ratio': treynor,
            'beta': beta,
            'annual_return': annual_return
        }
    
    def calculate_tracking_error(self, fund_returns: pd.Series,
                                  benchmark_returns: pd.Series) -> float:
        """计算跟踪误差"""
        aligned = pd.concat([fund_returns, benchmark_returns], axis=1).dropna()
        if len(aligned) < 2:
            return 0.0
        excess = aligned.iloc[:, 0] - aligned.iloc[:, 1]
        return excess.std() * np.sqrt(self.periods_per_year)
    
    def calculate_information_ratio(self, nav_series: pd.Series,
                                     benchmark_series: pd.Series) -> Dict:
        """计算信息比率"""
        fund_ret = nav_series.pct_change().dropna()
        bench_ret = benchmark_series.pct_change().dropna()
        
        fund_annual = self.calculate_annualized_return(nav_series)
        bench_annual = self.calculate_annualized_return(benchmark_series)
        excess = fund_annual - bench_annual
        te = self.calculate_tracking_error(fund_ret, bench_ret)
        
        if te == 0:
            ir = np.inf if excess > 0 else 0.0
        else:
            ir = excess / te
        
        return {
            'information_ratio': ir,
            'tracking_error': te,
            'excess_return': excess
        }
    
    # ==================== 基准比较 ====================
    
    def calculate_alpha(self, nav_series: pd.Series,
                        benchmark_series: pd.Series) -> Dict:
        """计算Alpha"""
        fund_ret = nav_series.pct_change().dropna()
        bench_ret = benchmark_series.pct_change().dropna()
        
        fund_annual = self.calculate_annualized_return(nav_series)
        bench_annual = self.calculate_annualized_return(benchmark_series)
        beta = self.calculate_beta(fund_ret, bench_ret)
        
        alpha = fund_annual - self.risk_free_rate - beta * (bench_annual - self.risk_free_rate)
        
        aligned = pd.concat([fund_ret, bench_ret], axis=1).dropna()
        correlation = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
        
        return {
            'alpha': alpha,
            'alpha_annual': alpha,
            'beta': beta,
            'r_squared': correlation ** 2,
            'correlation': correlation
        }
    
    # ==================== 综合计算 ====================
    
    def calculate_all_metrics(self, nav_series: pd.Series,
                              benchmark_series: pd.Series = None) -> FundMetrics:
        """计算所有指标"""
        metrics = FundMetrics()
        
        daily_returns = nav_series.pct_change().dropna()
        
        # 收益率
        metrics.total_return = self.calculate_cumulative_return(nav_series)
        metrics.annualized_return = self.calculate_annualized_return(nav_series)
        
        # 风险指标
        metrics.volatility = self.calculate_volatility(daily_returns)
        mdd_result = self.calculate_max_drawdown(nav_series)
        metrics.max_drawdown = mdd_result['max_drawdown']
        metrics.max_drawdown_start = mdd_result['start_date']
        metrics.max_drawdown_end = mdd_result['end_date']
        metrics.downside_deviation = self.calculate_downside_deviation(daily_returns)
        metrics.var_95 = self.calculate_var(daily_returns)['var']
        metrics.cvar_95 = self.calculate_cvar(daily_returns)['cvar']
        
        # 风险调整收益
        metrics.sharpe_ratio = self.calculate_sharpe_ratio(nav_series)
        metrics.sortino_ratio = self.calculate_sortino_ratio(nav_series)
        metrics.calmar_ratio = self.calculate_calmar_ratio(nav_series)
        
        # 基准比较
        if benchmark_series is not None:
            alpha_result = self.calculate_alpha(nav_series, benchmark_series)
            metrics.alpha = alpha_result['alpha']
            metrics.beta = alpha_result['beta']
            
            fund_ret = daily_returns
            bench_ret = benchmark_series.pct_change().dropna()
            metrics.tracking_error = self.calculate_tracking_error(fund_ret, bench_ret)
            
            fund_annual = metrics.annualized_return
            bench_annual = self.calculate_annualized_return(benchmark_series)
            metrics.excess_return = fund_annual - bench_annual
            
            ir_result = self.calculate_information_ratio(nav_series, benchmark_series)
            metrics.information_ratio = ir_result['information_ratio']
            
            treynor_result = self.calculate_treynor_ratio(nav_series, benchmark_series)
            metrics.treynor_ratio = treynor_result['treynor_ratio']
        
        # 其他
        metrics.win_rate = (daily_returns > 0).mean()
        metrics.positive_ratio = metrics.win_rate
        
        return metrics
    
    def generate_report(self, nav_series: pd.Series,
                        benchmark_series: pd.Series = None,
                        fund_name: str = "基金") -> str:
        """生成分析报告"""
        metrics = self.calculate_all_metrics(nav_series, benchmark_series)
        
        report = f"""
{'='*60}
{fund_name} 分析报告
{'='*60}

【收益率指标】
累计收益率:     {metrics.total_return*100:>10.2f}%
年化收益率:     {metrics.annualized_return*100:>10.2f}%

【风险指标】
年化波动率:     {metrics.volatility*100:>10.2f}%
最大回撤:       {metrics.max_drawdown*100:>10.2f}%
下行标准差:     {metrics.downside_deviation*100:>10.2f}%
VaR (95%):      {metrics.var_95*100:>10.2f}%
CVaR (95%):     {metrics.cvar_95*100:>10.2f}%

【风险调整收益】
夏普比率:       {metrics.sharpe_ratio:>10.2f}
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
"""
        
        report += f"""
【其他指标】
胜率:           {metrics.win_rate*100:>10.2f}%
{'='*60}
"""
        return report


# ==================== 持仓分析类 ====================

class PortfolioAnalyzer:
    """持仓分析器"""
    
    @staticmethod
    def calculate_concentration(holdings_df: pd.DataFrame, top_n: int = 10) -> Dict:
        """计算持仓集中度"""
        sorted_h = holdings_df.sort_values('weight', ascending=False)
        
        top_n_conc = sorted_h.head(top_n)['weight'].sum()
        hhi = (holdings_df['weight'] ** 2).sum()
        
        return {
            'top3_concentration': sorted_h.head(3)['weight'].sum(),
            'top5_concentration': sorted_h.head(5)['weight'].sum(),
            'top10_concentration': sorted_h.head(10)['weight'].sum(),
            f'top{top_n}_concentration': top_n_conc,
            'hhi': hhi,
            'effective_n': 1 / hhi if hhi > 0 else len(holdings_df)
        }
    
    @staticmethod
    def detect_position_changes(current: pd.DataFrame, previous: pd.DataFrame,
                                 threshold: float = 0.01) -> Dict:
        """检测持仓变化"""
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
            elif abs(change) >= threshold:
                (increased if change > 0 else decreased).append(info)
        
        total_change = sum(abs(s['change']) for s in added + removed + increased + decreased) / 2
        
        return {
            'added_stocks': added,
            'removed_stocks': removed,
            'increased_stocks': increased,
            'decreased_stocks': decreased,
            'turnover_ratio': total_change,
            'turnover_ratio_pct': total_change * 100
        }


# ==================== 基金经理评估类 ====================

class ManagerEvaluator:
    """基金经理评估器"""
    
    def __init__(self, analyzer: FundAnalyzer = None):
        self.analyzer = analyzer or FundAnalyzer()
    
    def evaluate_tenure(self, nav_series: pd.Series,
                        start_date, end_date=None) -> Dict:
        """评估基金经理任期表现"""
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
            'total_return': metrics.total_return,
            'annualized_return': metrics.annualized_return,
            'volatility': metrics.volatility,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'calmar_ratio': metrics.calmar_ratio,
            'win_rate': metrics.win_rate
        }
    
    def calculate_consistency_score(self, nav_series: pd.Series) -> Dict:
        """计算稳定性评分"""
        daily_returns = nav_series.pct_change().dropna()
        
        # 正收益比例
        positive_ratio = (daily_returns > 0).mean()
        
        # 滚动胜率稳定性
        rolling_win = daily_returns.rolling(63).apply(lambda x: (x > 0).mean())
        win_stability = 1 - rolling_win.std()
        
        # 波动率稳定性
        rolling_vol = daily_returns.rolling(63).std()
        vol_stability = 1 / (rolling_vol.std() + 1e-6)
        
        # 综合评分
        score = (positive_ratio * 0.4 + win_stability * 0.3 + 
                 min(vol_stability / 10, 1) * 0.3) * 100
        
        return {
            'consistency_score': score,
            'grade': 'A' if score >= 80 else 'B' if score >= 60 else 'C' if score >= 40 else 'D',
            'positive_ratio': positive_ratio,
            'win_stability': win_stability,
            'vol_stability': vol_stability
        }


# ==================== 工具函数 ====================

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


# ==================== 使用示例 ====================

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
    
    # 创建分析器
    analyzer = FundAnalyzer(risk_free_rate=0.03)
    
    # 生成报告
    report = analyzer.generate_report(nav_series, benchmark_series, "示例基金")
    print(report)
    
    # 获取所有指标
    metrics = analyzer.calculate_all_metrics(nav_series, benchmark_series)
    print(f"\n夏普比率: {metrics.sharpe_ratio:.2f}")
    print(f"信息比率: {metrics.information_ratio:.2f}")
```

---

## 8. 数据来源建议

### 8.1 免费数据源

| 数据源 | 类型 | 覆盖范围 | 获取方式 |
|--------|------|----------|----------|
| AKShare | A股数据 | 股票、基金、指数 | Python库 |
| Tushare | A股数据 | 股票、基金、指数 | API |
| Yahoo Finance | 全球数据 | 股票、基金、指数 | yfinance库 |
| 东方财富 | A股数据 | 基金净值、持仓 | 网页抓取 |
| 天天基金网 | 基金数据 | 基金净值、持仓 | 网页抓取 |

### 8.2 付费数据源

| 数据源 | 类型 | 特点 |
|--------|------|------|
| Wind | 金融终端 | 数据全面、专业 |
| 同花顺iFinD | 金融终端 | 性价比高 |
| Choice | 金融终端 | 东方财富旗下 |

### 8.3 数据获取示例

```python
# AKShare获取基金数据示例
import akshare as ak

# 获取基金净值
fund_code = "000001"  # 华夏成长混合
nav_df = ak.fund_open_fund_info_em(fund=fund_code, indicator="单位净值走势")

# 获取基金持仓
holdings_df = ak.fund_portfolio_hold_em(symbol=fund_code, date="20231231")

# 获取基金经理信息
manager_df = ak.fund_manager_em()
```

---

## 9. 总结

本文档提供了完整的基金分析指标计算方法，包括：

1. **收益率计算**：累计收益、年化收益、区间收益、分红再投资
2. **风险指标**：波动率、最大回撤、下行标准差、VaR/CVaR
3. **风险调整收益**：夏普比率、索提诺比率、卡玛比率、特雷诺比率、信息比率
4. **基准比较**：Alpha、Beta、跟踪误差、超额收益
5. **持仓分析**：集中度、行业配置、调仓检测、换手率
6. **基金经理评估**：任期收益、稳定性评分

所有方法均提供了详细的计算公式、Python实现代码和结果解读，可直接集成到基金分析系统中使用。

---

*文档版本: 1.0.0*
*最后更新: 2024年*
