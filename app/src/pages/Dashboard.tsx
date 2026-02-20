import { useState, useEffect } from 'react';
import { 
  Database, 
  TrendingUp, 
  PieChart,
  Activity,
  Server,
  Table2,
  Users,
  Loader2,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { dataSourceApi, dbApi, type DataStats } from '@/services/api';
import { useNavigate } from 'react-router-dom';

// 简单的折线图
function MiniChart() {
  const data = [30, 45, 35, 50, 40, 60, 55, 70, 65, 80];
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min;
  
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((d - min) / range) * 80 - 10;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg className="w-full h-24" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polyline
        points={points}
        fill="none"
        stroke="#0ea5e9"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polygon
        points={`0,100 ${points} 100,100`}
        fill="url(#miniGradient)"
        opacity="0.3"
      />
      <defs>
        <linearGradient id="miniGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

// 简单的饼图
function MiniPieChart() {
  const data = [
    { label: '混合型', value: 35, color: '#0ea5e9' },
    { label: '股票型', value: 25, color: '#ef4444' },
    { label: '债券型', value: 20, color: '#10b981' },
    { label: '货币型', value: 15, color: '#f59e0b' },
    { label: '其他', value: 5, color: '#8b5cf6' },
  ];
  
  let cumulativePercent = 0;
  
  return (
    <div className="flex items-center gap-6">
      <svg className="w-32 h-32" viewBox="0 0 100 100">
        {data.map((item) => {
          const startPercent = cumulativePercent;
          cumulativePercent += item.value;
          const endPercent = cumulativePercent;
          
          const startAngle = (startPercent / 100) * 360 - 90;
          const endAngle = (endPercent / 100) * 360 - 90;
          
          const startX = 50 + 40 * Math.cos((startAngle * Math.PI) / 180);
          const startY = 50 + 40 * Math.sin((startAngle * Math.PI) / 180);
          const endX = 50 + 40 * Math.cos((endAngle * Math.PI) / 180);
          const endY = 50 + 40 * Math.sin((endAngle * Math.PI) / 180);
          
          const largeArcFlag = item.value > 50 ? 1 : 0;
          
          return (
            <path
              key={item.label}
              d={`M 50 50 L ${startX} ${startY} A 40 40 0 ${largeArcFlag} 1 ${endX} ${endY} Z`}
              fill={item.color}
              stroke="rgba(17,24,39,0.8)"
              strokeWidth="2"
            />
          );
        })}
        <circle cx="50" cy="50" r="20" fill="rgba(17,24,39,0.8)" />
      </svg>
      <div className="flex flex-col gap-2 text-sm">
        {data.map((item) => (
          <div key={item.label} className="flex items-center gap-2">
            <div 
              className="w-3 h-3 rounded-sm" 
              style={{ backgroundColor: item.color }}
            />
            <span className="text-muted-foreground">{item.label}</span>
            <span className="font-medium">{item.value}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DataStats | null>(null);
  const [tableCount, setTableCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, tablesRes] = await Promise.all([
        dataSourceApi.getStats(),
        dbApi.getTables(),
      ]);
      
      if (statsRes.success) {
        setStats(statsRes.data);
      }
      if (tablesRes.success) {
        setTableCount(tablesRes.data.length);
      }
    } catch (error) {
      toast.error('加载仪表盘数据失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number | undefined) => {
    if (num === undefined || num === null) return '-';
    if (num >= 10000) {
      return (num / 10000).toFixed(1) + '万';
    }
    return num.toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
      </div>
    );
  }

  const statCards = [
    { 
      title: '基金总数', 
      value: formatNumber(stats?.total_funds), 
      change: '来自fundData skill', 
      icon: Database,
      color: 'cyan'
    },
    { 
      title: '净值记录', 
      value: formatNumber(stats?.total_nav_records), 
      change: `覆盖${formatNumber(stats?.nav_coverage)}只基金`, 
      icon: TrendingUp,
      color: 'emerald'
    },
    { 
      title: '数据表', 
      value: tableCount, 
      change: 'fundData数据库', 
      icon: Table2,
      color: 'purple'
    },
    { 
      title: '投资组合', 
      value: formatNumber(stats?.total_portfolios), 
      change: `${formatNumber(stats?.total_portfolio_funds)}只基金`, 
      icon: Users,
      color: 'amber'
    },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">数据概览</h1>
          <p className="text-muted-foreground mt-1">fundData skill 数据库状态</p>
        </div>
        <Button onClick={loadDashboardData} variant="outline">
          <Loader2 className="w-4 h-4 mr-2" />
          刷新
        </Button>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Card key={stat.title} className="glow-border card-hover">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.title}</p>
                  <p className="text-3xl font-bold mt-2">{stat.value}</p>
                  <p className="text-sm text-emerald-400 mt-1">{stat.change}</p>
                </div>
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center",
                  `bg-${stat.color}-500/20`
                )}>
                  <stat.icon className={cn("w-5 h-5", `text-${stat.color}-400`)} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 图表区域 */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="glow-border">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              数据增长趋势
            </CardTitle>
          </CardHeader>
          <CardContent>
            <MiniChart />
          </CardContent>
        </Card>

        <Card className="glow-border">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <PieChart className="w-5 h-5 text-cyan-400" />
              基金类型分布
            </CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-center">
            <MiniPieChart />
          </CardContent>
        </Card>
      </div>

      {/* 数据源状态 */}
      <Card className="glow-border">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Server className="w-5 h-5 text-cyan-400" />
            数据源状态
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-border">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span className="text-sm">fundData skill 本地SQLite数据库</span>
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>已连接</span>
                <span>数据由fundData skill维护</span>
              </div>
            </div>
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4 text-cyan-400" />
                <span className="text-sm">股票持仓数据</span>
              </div>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{formatNumber(stats?.stock_holdings)}条记录</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 快速操作 */}
      <Card className="glow-border">
        <CardHeader>
          <CardTitle className="text-lg">快速操作</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button 
              className="bg-cyan-500 hover:bg-cyan-600"
              onClick={() => navigate('/funds')}
            >
              <Database className="w-4 h-4 mr-2" />
              查看基金列表
            </Button>
            <Button 
              variant="outline"
              onClick={() => navigate('/portfolio')}
            >
              <Users className="w-4 h-4 mr-2" />
              投资组合
            </Button>
            <Button 
              variant="outline"
              onClick={() => navigate('/data/tables')}
            >
              <Table2 className="w-4 h-4 mr-2" />
              查看数据表
            </Button>
            <Button 
              variant="outline"
              onClick={() => window.open('https://akshare.akfamily.xyz/', '_blank')}
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              AKShare文档
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
