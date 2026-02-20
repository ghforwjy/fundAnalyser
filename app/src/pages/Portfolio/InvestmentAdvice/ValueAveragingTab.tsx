import { useState, useEffect } from 'react';
import {
  TrendingUp,
  Wallet,
  Scale,
  Loader2,
  Info,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
  Calculator
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { toast } from 'sonner';
import { portfolioApi, type InvestmentMode, type InvestmentAdvice } from '@/services/api';
import { cn } from '@/lib/utils';

interface ValueAveragingTabProps {
  groupId: number;
  groupName?: string;
}

const MODE_CONFIG: Record<string, { icon: React.ReactNode; color: string }> = {
  value_averaging: {
    icon: <TrendingUp className="w-5 h-5" />,
    color: 'text-emerald-400'
  },
  fixed_amount: {
    icon: <Wallet className="w-5 h-5" />,
    color: 'text-blue-400'
  },
  dynamic_balance: {
    icon: <Scale className="w-5 h-5" />,
    color: 'text-amber-400'
  }
};

export default function ValueAveragingTab({ groupId, groupName }: ValueAveragingTabProps) {
  const [modes, setModes] = useState<InvestmentMode[]>([]);
  const [selectedMode, setSelectedMode] = useState<string>('value_averaging');
  const [advice, setAdvice] = useState<InvestmentAdvice | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingModes, setLoadingModes] = useState(false);
  const [simulate, setSimulate] = useState(true);

  useEffect(() => {
    loadInvestmentModes();
  }, []);

  useEffect(() => {
    if (groupId && selectedMode) {
      loadInvestmentAdvice();
    }
  }, [groupId, selectedMode, simulate]);

  const loadInvestmentModes = async () => {
    try {
      setLoadingModes(true);
      const response = await portfolioApi.getInvestmentModes();
      if (response.success) {
        setModes(response.data);
      }
    } catch (error) {
      console.error('加载定投模式失败:', error);
    } finally {
      setLoadingModes(false);
    }
  };

  const loadInvestmentAdvice = async () => {
    if (!groupId) return;
    
    console.log(`[定投建议] 开始加载: groupId=${groupId}, mode=${selectedMode}, simulate=${simulate}`);
    try {
      setLoading(true);
      const response = await portfolioApi.getInvestmentAdvice(groupId, selectedMode, simulate);
      console.log('[定投建议] API响应:', response);
      if (response.success) {
        setAdvice(response.data);
      } else {
        toast.error(response.message || '获取投资建议失败');
      }
    } catch (error) {
      console.error('获取投资建议失败:', error);
      toast.error('获取投资建议失败');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (num: number | undefined) => {
    if (num === undefined || num === null) return '-';
    return `¥${num.toFixed(2)}`;
  };

  const formatNumber = (num: number | undefined, decimals: number = 2) => {
    if (num === undefined || num === null) return '-';
    return num.toFixed(decimals);
  };

  const getActionIcon = (action: string) => {
    if (action === '买入') return <ArrowUpRight className="w-4 h-4 text-up" />;
    if (action === '卖出') return <ArrowDownRight className="w-4 h-4 text-down" />;
    return <Minus className="w-4 h-4 text-gray-400" />;
  };

  const getActionColor = (action: string) => {
    if (action === '买入') return 'text-up';
    if (action === '卖出') return 'text-down';
    return 'text-gray-400';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4 pb-4 border-b border-border/50">
        <span className="text-sm font-medium text-muted-foreground flex items-center gap-2 flex-shrink-0">
          <Calculator className="w-4 h-4" />
          定投模式：
        </span>
        <div className="flex gap-2 flex-wrap">
          {loadingModes ? (
            <Loader2 className="w-5 h-5 animate-spin text-cyan-500" />
          ) : (
            modes.map((mode) => (
              <Button
                key={mode.id}
                variant={selectedMode === mode.id ? "default" : "outline"}
                size="sm"
                disabled={!mode.enabled}
                className={cn(
                  "h-auto py-2 px-4",
                  selectedMode === mode.id 
                    ? "bg-cyan-500 hover:bg-cyan-600" 
                    : "hover:border-cyan-500/50",
                  !mode.enabled && "opacity-50 cursor-not-allowed"
                )}
                onClick={() => mode.enabled && setSelectedMode(mode.id)}
              >
                <div className="flex items-center gap-2">
                  <span className={MODE_CONFIG[mode.id]?.color}>
                    {MODE_CONFIG[mode.id]?.icon || <TrendingUp className="w-4 h-4" />}
                  </span>
                  <span>{mode.name}</span>
                  {!mode.enabled && (
                    <Badge variant="secondary" className="text-xs ml-1">即将上线</Badge>
                  )}
                </div>
              </Button>
            ))
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
          <span className="ml-3 text-muted-foreground">正在计算投资建议...</span>
        </div>
      ) : !advice ? (
        <div className="flex items-center justify-center py-12">
          <Info className="w-8 h-8 text-muted-foreground mr-3" />
          <span className="text-muted-foreground">暂无投资建议数据</span>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center gap-4 p-3 bg-muted/50 rounded-lg text-sm">
            <span className="text-muted-foreground">计算周期：</span>
            <Badge variant="secondary">{advice.base_date}</Badge>
            <span className="text-muted-foreground">→</span>
            <Badge variant="secondary">{advice.target_date}</Badge>
            <span className="text-muted-foreground">（{advice.funds[0]?.days_diff || 30}天）</span>
          </div>

          <div className="flex flex-wrap items-center gap-6 p-4 bg-muted/30 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">基金数量</p>
                <p className="text-2xl font-bold">{advice.summary.total_funds} <span className="text-base font-normal text-muted-foreground">只</span></p>
              </div>
            </div>

            <div className="w-px h-12 bg-border hidden sm:block" />

            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
                <Wallet className="w-6 h-6 text-cyan-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">当前持仓市值</p>
                <p className="text-2xl font-bold">{formatCurrency(advice.summary.total_holding_value)}</p>
              </div>
            </div>

            <div className="w-px h-12 bg-border hidden sm:block" />

            <div className="flex items-center gap-3">
              <div className={cn(
                "w-12 h-12 rounded-xl flex items-center justify-center",
                advice.summary.total_suggested_invest >= 0 ? "bg-up" : "bg-down"
              )}>
                <TrendingUp className={cn(
                  "w-6 h-6",
                  advice.summary.total_suggested_invest >= 0 ? "text-up" : "text-down"
                )} />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">本期建议操作</p>
                <p className={cn(
                  "text-2xl font-bold",
                  advice.summary.total_suggested_invest >= 0 ? "text-up" : "text-down"
                )}>
                  {advice.summary.total_suggested_invest >= 0 ? '买入 ' : '卖出 '}
                  {formatCurrency(Math.abs(advice.summary.total_suggested_invest))}
                </p>
              </div>
            </div>

            <div className="w-px h-12 bg-border hidden sm:block" />

            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                <Info className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">市场阶段</p>
                <p className="text-2xl font-bold">{advice.funds[0]?.market_phase || '未知'}</p>
              </div>
            </div>
          </div>

          <Card className="glow-border">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-cyan-400" />
                定投方案明细
                <Badge variant="secondary">{advice.funds.length} 只基金</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead>基金</TableHead>
                      <TableHead className="text-right">基准市值</TableHead>
                      <TableHead className="text-right">当前市值</TableHead>
                      <TableHead className="text-right">原有盈亏</TableHead>
                      <TableHead className="text-right">目标增长</TableHead>
                      <TableHead className="text-right">建议操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {advice.funds.map((fund) => (
                      <TableRow key={fund.fund_code} className="table-row-hover">
                        <TableCell>
                          <div>
                            <p className="font-medium">{fund.fund_name}</p>
                            <div className="flex items-center gap-2 text-xs text-muted-foreground">
                              <code className="font-mono">{fund.fund_code}</code>
                              <span>·</span>
                              <span>{fund.shares_at_base.toFixed(2)}份→{fund.current_shares.toFixed(2)}份</span>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          <div>{formatCurrency(fund.base_value)}</div>
                          <div className="text-xs text-muted-foreground">{fund.nav_at_base.toFixed(4)}元</div>
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          <div>{formatCurrency(fund.actual_value)}</div>
                          <div className="text-xs text-muted-foreground">{fund.latest_nav.toFixed(4)}元</div>
                        </TableCell>
                        <TableCell className={cn("text-right font-mono", fund.original_holding_profit >= 0 ? "text-up" : "text-down")}>
                          {fund.original_holding_profit >= 0 ? '+' : ''}{formatCurrency(fund.original_holding_profit)}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          <div>{formatCurrency(fund.target_growth)}</div>
                          <div className="text-xs text-muted-foreground">{formatNumber(fund.avg_monthly_return)}%/月</div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className={cn("flex items-center justify-end gap-1", getActionColor(fund.invest_action))}>
                            {getActionIcon(fund.invest_action)}
                            <span>{fund.invest_action}</span>
                          </div>
                          <div className={cn("font-mono font-medium", getActionColor(fund.invest_action))}>
                            {formatCurrency(Math.abs(fund.suggested_invest))}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          {advice.funds[0]?.algorithm_details && (
            <Card className="glow-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  算法说明
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  {advice.funds[0].algorithm_details.map((detail: string, index: number) => (
                    <p key={index} className={cn(
                      detail.startsWith('【') ? "font-medium text-cyan-400 mt-3" : "text-muted-foreground"
                    )}>
                      {detail}
                    </p>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
