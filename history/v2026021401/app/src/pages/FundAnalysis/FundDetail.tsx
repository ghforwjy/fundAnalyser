import { useState, useEffect } from 'react';
import { 
  ArrowLeft, 
  Star, 
  Share2, 
  TrendingUp, 
  TrendingDown,
  Calendar,
  Building2,
  User,
  BarChart3,
  PieChart,
  Briefcase,
  Info,
  Wallet,
  Percent,
  Shield,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { fundApi, type FundInfo, type FundNav, type FundHolding } from '@/services/api';

// 简单的折线图组件
function SimpleLineChart({ data }: { data: { date: string; nav: number }[] }) {
  if (!data.length) return <div className="h-64 flex items-center justify-center text-muted-foreground">暂无数据</div>;
  
  const maxNav = Math.max(...data.map(d => d.nav));
  const minNav = Math.min(...data.map(d => d.nav));
  const navRange = maxNav - minNav || 1;
  
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((d.nav - minNav) / navRange) * 80 - 10;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="h-64 w-full relative">
      <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {[0, 25, 50, 75, 100].map(y => (
          <line key={y} x1="0" y1={y} x2="100" y2={y} stroke="rgba(148,163,184,0.1)" strokeWidth="0.5" />
        ))}
        
        <polyline
          points={points}
          fill="none"
          stroke="#0ea5e9"
          strokeWidth="1"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        <polygon
          points={`0,100 ${points} 100,100`}
          fill="url(#gradient)"
          opacity="0.3"
        />
        
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
      
      <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-muted-foreground">
        {data.filter((_, i) => i % Math.ceil(data.length / 6) === 0).map(d => (
          <span key={d.date}>{d.date.slice(5)}</span>
        ))}
      </div>
    </div>
  );
}

// 简单的柱状图组件
function SimpleBarChart({ data }: { data: { name: string; value: number }[] }) {
  if (!data.length) return <div className="text-muted-foreground">暂无数据</div>;
  
  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="space-y-2">
      {data.map((item) => (
        <div key={item.name} className="flex items-center gap-3">
          <span className="w-16 text-sm text-muted-foreground">{item.name}</span>
          <div className="flex-1 h-6 bg-secondary/50 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
              style={{ width: `${(item.value / maxValue) * 100}%` }}
            />
          </div>
          <span className="w-12 text-sm font-medium text-right">{item.value.toFixed(2)}%</span>
        </div>
      ))}
    </div>
  );
}

interface FundDetailProps {
  fundCode: string;
  onBack?: () => void;
}

export default function FundDetailPage({ fundCode, onBack }: FundDetailProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('1Y');
  const [loading, setLoading] = useState(true);
  
  // 数据状态
  const [fund, setFund] = useState<FundInfo | null>(null);
  const [navHistory, setNavHistory] = useState<FundNav[]>([]);
  const [holdings, setHoldings] = useState<FundHolding[]>([]);
  const [industryAlloc, setIndustryAlloc] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);

  // 加载基金详情
  useEffect(() => {
    if (fundCode) {
      loadFundDetail();
    }
  }, [fundCode]);

  // 加载净值历史
  useEffect(() => {
    if (fundCode && activeTab === 'performance') {
      loadNavHistory();
    }
  }, [fundCode, activeTab, timeRange]);

  // 加载持仓数据
  useEffect(() => {
    if (fundCode && activeTab === 'holdings') {
      loadHoldings();
      loadIndustryAllocation();
    }
  }, [fundCode, activeTab]);

  const loadFundDetail = async () => {
    try {
      setLoading(true);
      const response = await fundApi.getDetail(fundCode);
      if (response.success) {
        setFund(response.data.basic_info);
        setMetrics(response.data.metrics);
      }
    } catch (error) {
      toast.error('加载基金详情失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadNavHistory = async () => {
    try {
      const days = {
        '1M': 30, '3M': 90, '6M': 180, '1Y': 365, '3Y': 1095, 'ALL': 3650
      }[timeRange] || 365;
      
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      const response = await fundApi.getNavHistory(fundCode, startDate, endDate);
      if (response.success) {
        setNavHistory(response.data);
      }
    } catch (error) {
      console.error('加载净值历史失败', error);
    }
  };

  const loadHoldings = async () => {
    try {
      const response = await fundApi.getHoldings(fundCode);
      if (response.success) {
        setHoldings(response.data);
      }
    } catch (error) {
      console.error('加载持仓失败', error);
    }
  };

  const loadIndustryAllocation = async () => {
    try {
      const response = await fundApi.getIndustryAllocation(fundCode);
      if (response.success) {
        setIndustryAlloc(response.data);
      }
    } catch (error) {
      console.error('加载行业配置失败', error);
    }
  };

  const getFundTypeBadge = (type: string) => {
    const typeStyles: Record<string, string> = {
      '股票型': 'bg-red-500/20 text-red-400 border-red-500/30',
      '债券型': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      '混合型': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
      '货币型': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      '指数型': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    };
    return (
      <Badge className={cn('text-sm px-3 py-1', typeStyles[type] || 'bg-gray-500/20 text-gray-400')}>
        {type}
      </Badge>
    );
  };

  const formatReturn = (value: number | undefined) => {
    if (value === undefined || value === null) return '-';
    const color = value >= 0 ? 'text-emerald-400' : 'text-red-400';
    const sign = value >= 0 ? '+' : '';
    return <span className={color}>{sign}{value.toFixed(2)}%</span>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
      </div>
    );
  }

  if (!fund) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">基金不存在</p>
        <Button onClick={onBack} className="mt-4">返回</Button>
      </div>
    );
  }

  // 准备图表数据
  const chartData = navHistory.map(nav => ({
    date: nav.trade_date,
    nav: nav.unit_nav,
  }));

  // 准备行业配置数据
  const industryData = industryAlloc.map(item => ({
    name: item.sector_name || item.industry || '其他',
    value: item.nav_ratio || 0,
  }));

  return (
    <div className="space-y-6">
      {/* 头部导航 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={onBack}>
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{fund.fund_name}</h1>
              <code className="px-2 py-1 rounded bg-secondary text-sm font-mono text-cyan-400">{fund.fund_code}</code>
            </div>
            <p className="text-muted-foreground text-sm mt-1">{fund.manager_company}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadFundDetail}>
            <RefreshCw className="w-4 h-4 mr-1" />
            刷新
          </Button>
          <Button variant="outline" size="sm">
            <Star className="w-4 h-4 mr-1" />
            收藏
          </Button>
        </div>
      </div>

      {/* 净值卡片 */}
      <Card className="glow-border bg-gradient-to-br from-cyan-500/10 to-blue-500/10">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                最新净值 {fund.nav_date ? `(${fund.nav_date})` : ''}
              </p>
              <div className="flex items-baseline gap-3">
                <span className="text-4xl font-bold font-mono">
                  {fund.latest_nav ? fund.latest_nav.toFixed(4) : '-'}
                </span>
                {fund.latest_return !== undefined && (
                  <span className={cn(
                    "text-lg font-medium flex items-center",
                    fund.latest_return >= 0 ? "text-emerald-400" : "text-red-400"
                  )}>
                    {fund.latest_return >= 0 ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
                    {fund.latest_return >= 0 ? '+' : ''}{fund.latest_return.toFixed(2)}%
                  </span>
                )}
              </div>
            </div>
            <div className="text-right">
              {getFundTypeBadge(fund.fund_type)}
              <p className="text-sm text-muted-foreground mt-2">风险等级: {fund.risk_level}级</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 标签页 */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">基本信息</TabsTrigger>
          <TabsTrigger value="performance">历史表现</TabsTrigger>
          <TabsTrigger value="holdings">持仓分析</TabsTrigger>
          <TabsTrigger value="manager">基金经理</TabsTrigger>
        </TabsList>

        {/* 基本信息 */}
        <TabsContent value="overview" className="space-y-6">
          {/* 业绩概览 */}
          {metrics?.return && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { key: 'return_1m', label: '近1月' },
                { key: 'return_3m', label: '近3月' },
                { key: 'return_6m', label: '近6月' },
                { key: 'return_1y', label: '近1年' },
              ].map(({ key, label }) => (
                <Card key={key} className="glow-border">
                  <CardContent className="p-4">
                    <p className="text-sm text-muted-foreground">{label}</p>
                    <p className="text-xl font-bold mt-1">
                      {formatReturn(metrics.return[key])}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* 详细信息 */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="glow-border">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Info className="w-5 h-5 text-cyan-400" />
                  基金概况
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">基金全称</span>
                  <span className="text-right max-w-[60%]">{fund.fund_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">基金类型</span>
                  <span>{fund.fund_type} {fund.sub_type ? `(${fund.sub_type})` : ''}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">成立日期</span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {fund.establish_date || '-'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">投资风格</span>
                  <span>{fund.invest_style || '-'}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="glow-border">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Percent className="w-5 h-5 text-cyan-400" />
                  费率信息
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">管理费率</span>
                  <span>{fund.manage_fee_rate ? (fund.manage_fee_rate * 100).toFixed(2) : '-'}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">托管费率</span>
                  <span>{fund.custodian_fee_rate ? (fund.custodian_fee_rate * 100).toFixed(2) : '-'}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">基金管理人</span>
                  <span className="flex items-center gap-1">
                    <Building2 className="w-4 h-4" />
                    {fund.manager_company}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">基金托管人</span>
                  <span>{fund.custodian || '-'}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 业绩基准 */}
          {fund.benchmark && (
            <Card className="glow-border">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-cyan-400" />
                  业绩比较基准
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{fund.benchmark}</p>
              </CardContent>
            </Card>
          )}

          {/* 投资范围 */}
          {fund.invest_scope && (
            <Card className="glow-border">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Shield className="w-5 h-5 text-cyan-400" />
                  投资范围
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{fund.invest_scope}</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* 历史表现 */}
        <TabsContent value="performance" className="space-y-6">
          {/* 时间范围选择 */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">时间范围:</span>
            {['1M', '3M', '6M', '1Y', '3Y', 'ALL'].map(range => (
              <Button
                key={range}
                variant={timeRange === range ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange(range)}
                className={timeRange === range ? 'bg-cyan-500 hover:bg-cyan-600' : ''}
              >
                {range === 'ALL' ? '全部' : `近${range}`}
              </Button>
            ))}
          </div>

          {/* 净值走势图 */}
          <Card className="glow-border">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
                净值走势
              </CardTitle>
            </CardHeader>
            <CardContent>
              <SimpleLineChart data={chartData} />
            </CardContent>
          </Card>

          {/* 风险指标 */}
          {metrics && (
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="glow-border">
                <CardHeader>
                  <CardTitle className="text-lg">收益指标</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">累计收益率</span>
                    <span className="text-emerald-400 font-medium">
                      {formatReturn(metrics.return?.total_return)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">年化收益率</span>
                    <span className="text-emerald-400 font-medium">
                      {formatReturn(metrics.return?.annualized_return)}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card className="glow-border">
                <CardHeader>
                  <CardTitle className="text-lg">风险指标</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">最大回撤</span>
                    <span className="text-red-400 font-medium">
                      {metrics.risk?.max_drawdown ? `${metrics.risk.max_drawdown.toFixed(2)}%` : '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">波动率</span>
                    <span className="font-mono">
                      {metrics.risk?.volatility ? `${metrics.risk.volatility.toFixed(2)}%` : '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">夏普比率</span>
                    <span className="font-mono text-cyan-400">
                      {metrics.risk_adjusted?.sharpe_ratio?.toFixed(2) || '-'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        {/* 持仓分析 */}
        <TabsContent value="holdings" className="space-y-6">
          {/* 持仓概览 */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="glow-border">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <PieChart className="w-5 h-5 text-cyan-400" />
                  持仓集中度
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">持仓股票数量</span>
                  <span className="font-medium">{holdings.length}只</span>
                </div>
                {holdings.length > 0 && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">前10大持仓占比</span>
                      <span className="font-medium">
                        {holdings.slice(0, 10).reduce((sum, h) => sum + (h.nav_ratio || 0), 0).toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">前5大持仓占比</span>
                      <span className="font-medium">
                        {holdings.slice(0, 5).reduce((sum, h) => sum + (h.nav_ratio || 0), 0).toFixed(2)}%
                      </span>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            <Card className="glow-border">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-cyan-400" />
                  行业分布
                </CardTitle>
              </CardHeader>
              <CardContent>
                <SimpleBarChart data={industryData} />
              </CardContent>
            </Card>
          </div>

          {/* 持仓明细 */}
          <Card className="glow-border">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-cyan-400" />
                持仓明细
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border bg-secondary/50">
                      <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">排名</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">股票代码</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">股票名称</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">占净值比</th>
                      <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">持仓市值(万元)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {holdings.map((holding, index) => (
                      <tr 
                        key={holding.stock_code} 
                        className="border-b border-border table-row-hover"
                      >
                        <td className="px-4 py-3 text-sm">{holding.rank_num || index + 1}</td>
                        <td className="px-4 py-3">
                          <code className="text-sm font-mono text-cyan-400">{holding.stock_code}</code>
                        </td>
                        <td className="px-4 py-3 text-sm">{holding.stock_name}</td>
                        <td className="px-4 py-3 text-right text-sm font-medium">
                          {holding.nav_ratio ? `${holding.nav_ratio.toFixed(2)}%` : '-'}
                        </td>
                        <td className="px-4 py-3 text-right text-sm font-mono">
                          {holding.market_value ? holding.market_value.toLocaleString() : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {holdings.length === 0 && (
                <div className="py-12 text-center text-muted-foreground">
                  暂无持仓数据
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* 基金经理 */}
        <TabsContent value="manager" className="space-y-6">
          <Card className="glow-border">
            <CardContent className="p-6">
              <div className="flex items-start gap-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                  <User className="w-10 h-10 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold">{fund.manager_name || '暂无信息'}</h3>
                  <p className="text-muted-foreground">{fund.manager_company}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
