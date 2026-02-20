import { useState, useEffect } from 'react';
import { 
  Database, 
  TrendingUp, 
  TrendingDown, 
  PieChart,
  Activity,
  Calendar,
  RefreshCw,
  Server,
  Table2,
  Users,
  Loader2,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { dashboardApi, syncApi, type DashboardStats, type SyncStatus } from '@/services/api';

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
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, syncRes] = await Promise.all([
        dashboardApi.getStats(),
        syncApi.getStatus(),
      ]);
      
      if (statsRes.success) {
        setStats(statsRes.data);
      }
      if (syncRes.success) {
        setSyncStatus(syncRes.data);
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
      value: formatNumber(stats?.fund_stats?.total_funds), 
      change: `${stats?.fund_stats?.type_count || 0}种类型`, 
      icon: Database,
      color: 'cyan'
    },
    { 
      title: '净值记录', 
      value: formatNumber(stats?.nav_stats?.total_records), 
      change: `覆盖${formatNumber(stats?.nav_stats?.covered_funds)}只基金`, 
      icon: TrendingUp,
      color: 'emerald'
    },
    { 
      title: '数据表', 
      value: formatNumber(stats?.sync_status?.total_tables), 
      change: `${stats?.sync_status?.synced_tables || 0}个已同步`, 
      icon: Table2,
      color: 'purple'
    },
    { 
      title: '基金公司', 
      value: formatNumber(stats?.fund_stats?.company_count), 
      change: '持续更新中', 
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
          <p className="text-muted-foreground mt-1">基金数据库整体运行状态</p>
        </div>
        <Button onClick={loadDashboardData} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
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
            {syncStatus.slice(0, 5).map((item) => (
              <div key={item.table_name} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div className="flex items-center gap-3">
                  {item.last_sync_status === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-400" />
                  )}
                  <span className="text-sm">{item.table_name}</span>
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>{formatNumber(item.total_records)}条记录</span>
                  <span>最后同步: {item.last_sync_time ? new Date(item.last_sync_time).toLocaleString('zh-CN') : '从未'}</span>
                </div>
              </div>
            ))}
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
            <Button className="bg-cyan-500 hover:bg-cyan-600">
              <RefreshCw className="w-4 h-4 mr-2" />
              同步基金列表
            </Button>
            <Button variant="outline">
              <TrendingUp className="w-4 h-4 mr-2" />
              同步净值数据
            </Button>
            <Button variant="outline">
              <Database className="w-4 h-4 mr-2" />
              查看数据库
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
