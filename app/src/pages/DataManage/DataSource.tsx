import { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Server,
  Database,
  Loader2,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import { dataSourceApi, type DataSource, type DataStats } from '@/services/api';

export default function DataSourcePage() {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [stats, setStats] = useState<DataStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sourcesRes, statsRes] = await Promise.all([
        dataSourceApi.getAll(),
        dataSourceApi.getStats(),
      ]);
      
      if (sourcesRes.success) {
        setDataSources(sourcesRes.data);
      }
      if (statsRes.success) {
        setStats(statsRes.data);
      }
    } catch (error) {
      toast.error('加载数据失败');
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

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">数据源</h1>
          <p className="text-muted-foreground mt-1">fundData skill 数据库信息</p>
        </div>
        <Button onClick={loadData} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          刷新
        </Button>
      </div>

      {/* 数据源列表 */}
      <div className="grid gap-4">
        {dataSources.map((source) => (
          <Card key={source.id} className={cn(
            "glow-border card-hover",
            "border-cyan-500/50"
          )}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center">
                      <Server className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold">{source.source_name}</h3>
                        <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          已连接
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm text-muted-foreground">
                          {source.source_type}
                        </span>
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground mt-3">
                    {source.description}
                  </p>

                  <div className="flex items-center gap-6 mt-4 text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Database className="w-4 h-4" />
                      <span>基金: {formatNumber(source.fund_count)}</span>
                    </div>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Server className="w-4 h-4" />
                      <span>净值记录: {formatNumber(source.nav_count)}</span>
                    </div>
                  </div>

                  {source.note && (
                    <div className="mt-3 text-sm text-amber-400">
                      {source.note}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open('https://akshare.akfamily.xyz/', '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-1" />
                    AKShare文档
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 数据统计 */}
      {stats && (
        <Card className="glow-border">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold mb-4">数据统计</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">基金总数</p>
                <p className="text-2xl font-bold">{formatNumber(stats.total_funds)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">净值记录</p>
                <p className="text-2xl font-bold">{formatNumber(stats.total_nav_records)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">净值覆盖基金</p>
                <p className="text-2xl font-bold">{formatNumber(stats.nav_coverage)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">股票持仓</p>
                <p className="text-2xl font-bold">{formatNumber(stats.stock_holdings)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">投资组合</p>
                <p className="text-2xl font-bold">{formatNumber(stats.total_portfolios)}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">组合基金</p>
                <p className="text-2xl font-bold">{formatNumber(stats.total_portfolio_funds)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
