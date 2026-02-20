import { useState, useEffect } from 'react';
import {
  TrendingUp,
  Package,
  Percent,
  Loader2,
  Trash2,
  Wallet,
  Target,
  MoreHorizontal,
  Plus,
  Minus,
  Edit3,
  Coins,
  Tag,
  ChevronDown
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { portfolioApi, type PortfolioSummary, type TransactionRequest, tagApi, type Tag as TagType } from '@/services/api';
import { cn } from '@/lib/utils';
import { ResizableTable, type Column } from '@/components/ui/resizable-table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TagSelector } from '@/components/TagSelector';
import { TagSelectorInline } from '@/components/TagSelectorInline';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

interface PositionManageProps {
  groupId?: number;
}

// 持仓数据类型
interface Position {
  id: number;
  portfolio_id: number;
  fund_code: string;
  fund_name: string;
  fund_type?: string;
  company_name?: string;
  shares?: number;
  buy_date?: string;
  buy_nav?: number;
  amount?: number;
  latest_nav?: number;
  nav_date?: string;
  market_value?: number;
  profit_loss?: number;
  profit_rate?: number;
  daily_return?: number;
  // 可用现金（实时计算：卖出所得 - 买入投入）
  available_cash?: number;
  total_buy_amount?: number;
  total_sell_amount?: number;
  // 收益指标
  return_1m?: number;
  return_6m?: number;
  return_1y?: number;
  // 风险指标
  max_drawdown_1y?: number;
  sharpe_ratio_1y?: number;
  annual_volatility_1y?: number;
  // 排名信息
  rank_in_category?: string;
  rank_category?: string;
  // 数据新鲜度
  metrics_update_time?: string;
  // 标签
  tags?: TagType[];
}

export default function PositionManage({ groupId }: PositionManageProps) {
  const [positions, setPositions] = useState<Position[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [freshnessInfo, setFreshnessInfo] = useState<{
    nav_fresh_count: number;
    metrics_fresh_count: number;
    metrics_updated_count: number;
    total_funds: number;
  } | null>(null);

  // 交易录入弹窗状态
  const [transactionDialogOpen, setTransactionDialogOpen] = useState(false);
  const [transactionType, setTransactionType] = useState<'BUY' | 'SELL'>('BUY');
  const [selectedFund, setSelectedFund] = useState<Position | null>(null);
  const [transactionForm, setTransactionForm] = useState({
    shares: '',
    amount: '',
    nav: '',
    transaction_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  // 交易记录状态
  const [transactions, setTransactions] = useState<Array<{
    id: number;
    transaction_type: 'BUY' | 'SELL';
    transaction_date: string;
    shares: number;
    amount: number;
    notes?: string;
  }>>([]);
  const [transactionTab, setTransactionTab] = useState('input');

  // 盈利录入弹窗状态
  const [profitDialogOpen, setProfitDialogOpen] = useState(false);
  const [profitForm, setProfitForm] = useState({
    current_value: '',
    profit_loss: '',
    import_mode: 'accumulate' as 'overwrite' | 'accumulate',
  });

  // 现金管理弹窗状态
  const [cashDialogOpen, setCashDialogOpen] = useState(false);
  const [cashBalance, setCashBalance] = useState(0);
  const [cashForm, setCashForm] = useState({
    cash: '',
  });

  // 添加基金弹窗状态
  const [addFundDialogOpen, setAddFundDialogOpen] = useState(false);
  const [addFundForm, setAddFundForm] = useState({
    fund_code: '',
    shares: '',
    profit_loss: '',
  });

  // 标签管理弹窗状态
  const [tagDialogOpen, setTagDialogOpen] = useState(false);
  const [selectedFundForTag, setSelectedFundForTag] = useState<Position | null>(null);
  const [fundTags, setFundTags] = useState<TagType[]>([]);
  const [savingTags, setSavingTags] = useState(false);

  // 折叠状态 - 默认折叠
  const [summaryOpen, setSummaryOpen] = useState(false);
  const [positionsOpen, setPositionsOpen] = useState(false);

  useEffect(() => {
    loadData();
  }, [groupId]);

  const loadData = async (forceRefresh: boolean = false) => {
    try {
      if (forceRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      // 加载组合基金列表
      if (groupId) {
        const positionsRes = await portfolioApi.getGroupFunds(groupId, forceRefresh);
        console.log('[PositionManage] API返回数据:', positionsRes);
        if (positionsRes.success) {
          // 查找021094的数据
          const fund021094 = positionsRes.data?.find((f: any) => f.fund_code === '021094');
          if (fund021094) {
            console.log('[PositionManage] 021094数据:', fund021094);
            console.log('[PositionManage] 021094 profit_loss:', fund021094.profit_loss);
          }

          // 加载所有基金的标签
          const allFundTags = await tagApi.getAll();
          const fundTagsMap: Record<string, TagType[]> = {};
          if (allFundTags.success) {
            // 获取每个基金的标签
            for (const position of positionsRes.data) {
              const tagsRes = await tagApi.getFundTags(position.fund_code);
              if (tagsRes.success) {
                fundTagsMap[position.fund_code] = tagsRes.data;
              }
            }
          }

          // 合并标签数据到持仓
          const positionsWithTags = positionsRes.data.map((p: any) => ({
            ...p,
            tags: fundTagsMap[p.fund_code] || []
          }));

          setPositions(positionsWithTags);
          setFreshnessInfo(positionsRes.freshness_summary || null);
        }
      } else {
        setPositions([]);
        setFreshnessInfo(null);
      }

      // 加载汇总数据
      const summaryRes = await portfolioApi.getPortfolioSummary(groupId);
      if (summaryRes.success) {
        setSummary(summaryRes.data);
      }

      // 加载现金余额
      const cashRes = await portfolioApi.getCash(groupId);
      if (cashRes.success) {
        setCashBalance(cashRes.data.cash);
      }
    } catch (error) {
      toast.error('加载数据失败');
      console.error(error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadData(true);
  };

  const handleRemoveFund = async (fundCode: string) => {
    if (!groupId) return;
    if (!confirm(`确定要从组合中移除 ${fundCode} 吗？`)) return;

    try {
      const response = await portfolioApi.removeFundFromGroup(groupId, fundCode);
      if (response.success) {
        toast.success('移除成功');
        loadData();
      }
    } catch (error) {
      toast.error('移除失败');
    }
  };

  // 打开交易录入弹窗
  const openTransactionDialog = async (fund: Position, type: 'BUY' | 'SELL') => {
    setSelectedFund(fund);
    setTransactionType(type);
    setTransactionForm({
      shares: '',
      amount: '',
      nav: '',
      transaction_date: new Date().toISOString().split('T')[0],
      notes: type === 'BUY' ? '买入' : '卖出',
    });
    setTransactionTab('input');
    setTransactionDialogOpen(true);

    // 加载该基金的的交易记录
    if (groupId) {
      try {
        const response = await portfolioApi.getTransactions(groupId, { fund_code: fund.fund_code });
        if (response.success) {
          setTransactions(response.data);
        }
      } catch (error) {
        console.error('加载交易记录失败:', error);
      }
    }
  };

  // 打开盈利录入弹窗
  const openProfitDialog = (fund: Position) => {
    setSelectedFund(fund);
    setProfitForm({
      current_value: '',
      profit_loss: fund.profit_loss ? String(fund.profit_loss.toFixed(2)) : '',
      import_mode: 'accumulate',
    });
    setProfitDialogOpen(true);
  };

  // 打开标签管理弹窗
  const openTagDialog = (fund: Position) => {
    setSelectedFundForTag(fund);
    setFundTags(fund.tags || []);
    setTagDialogOpen(true);
  };

  // 保存基金标签
  const saveFundTags = async () => {
    if (!selectedFundForTag) return;

    setSavingTags(true);
    try {
      const tagIds = fundTags.map((t) => t.id);
      const response = await tagApi.setFundTags(selectedFundForTag.fund_code, tagIds);
      if (response.success) {
        toast.success('标签保存成功');
        setTagDialogOpen(false);
        // 更新本地数据
        setPositions((prev) =>
          prev.map((p) =>
            p.fund_code === selectedFundForTag.fund_code ? { ...p, tags: fundTags } : p
          )
        );
      } else {
        toast.error(response.message || '保存失败');
      }
    } catch (error) {
      toast.error('保存标签失败');
    } finally {
      setSavingTags(false);
    }
  };

  // 打开现金管理弹窗
  const openCashDialog = async () => {
    if (!groupId) return;
    try {
      const response = await portfolioApi.getCash(groupId);
      if (response.success) {
        setCashBalance(response.data.cash);
        setCashForm({ cash: String(response.data.cash) });
        setCashDialogOpen(true);
      }
    } catch (error) {
      toast.error('获取现金余额失败');
    }
  };

  // 提交交易
  const submitTransaction = async () => {
    if (!groupId || !selectedFund) return;

    const shares = parseFloat(transactionForm.shares);
    const amount = parseFloat(transactionForm.amount);

    if (!shares || shares <= 0) {
      toast.error('请输入有效的份额');
      return;
    }
    if (!amount || amount <= 0) {
      toast.error('请输入有效的金额');
      return;
    }

    try {
      const data: TransactionRequest = {
        fund_code: selectedFund.fund_code,
        transaction_type: transactionType,
        transaction_date: transactionForm.transaction_date,
        shares: shares,
        amount: amount,
        nav: transactionForm.nav ? parseFloat(transactionForm.nav) : undefined,
        notes: transactionForm.notes,
      };

      const response = await portfolioApi.recordTransaction(groupId, data);
      if (response.success) {
        toast.success(`${transactionType === 'BUY' ? '买入' : '卖出'}交易记录成功`);
        setTransactionDialogOpen(false);
        loadData();
      } else {
        toast.error(response.message || '交易记录失败');
      }
    } catch (error) {
      toast.error('交易记录失败');
    }
  };

  // 提交盈利录入
  const submitProfit = async () => {
    if (!groupId || !selectedFund) return;

    const profitLoss = parseFloat(profitForm.profit_loss);

    if (isNaN(profitLoss)) {
      toast.error('请输入有效的盈亏金额');
      return;
    }

    try {
      const response = await portfolioApi.importProfitData(groupId, {
        profit_data: [{
          fund_code: selectedFund.fund_code,
          fund_name: selectedFund.fund_name,
          profit_loss: profitLoss,
          // current_value 由后端自动计算：shares × latest_nav
        }],
        import_mode: profitForm.import_mode,
      });

      if (response.success) {
        toast.success('盈利录入成功');
        setProfitDialogOpen(false);
        loadData();
      } else {
        toast.error(response.message || '盈利录入失败');
      }
    } catch (error) {
      toast.error('盈利录入失败');
    }
  };

  // 提交现金更新
  const submitCashUpdate = async () => {
    if (!groupId) return;

    const cash = parseFloat(cashForm.cash);
    if (isNaN(cash) || cash < 0) {
      toast.error('请输入有效的现金金额');
      return;
    }

    try {
      const response = await portfolioApi.updateCash(groupId, cash);
      if (response.success) {
        toast.success('现金余额更新成功');
        setCashDialogOpen(false);
        setCashBalance(cash);
      } else {
        toast.error(response.message || '更新失败');
      }
    } catch (error) {
      toast.error('现金余额更新失败');
    }
  };

  // 提交添加基金
  const submitAddFund = async () => {
    if (!groupId) {
      toast.error('请先选择一个组合');
      return;
    }

    const fundCode = addFundForm.fund_code.trim();
    const shares = parseFloat(addFundForm.shares);
    const profitLoss = parseFloat(addFundForm.profit_loss);

    if (!fundCode) {
      toast.error('请输入基金代码');
      return;
    }
    if (!shares || shares <= 0) {
      toast.error('请输入有效的持有份额');
      return;
    }
    if (isNaN(profitLoss)) {
      toast.error('请输入有效的盈亏金额');
      return;
    }

    try {
      // 第一步：添加基金到组合
      const addResponse = await portfolioApi.addFundToGroup(groupId, {
        fund_code: fundCode,
        shares: shares,
      });

      if (!addResponse.success) {
        toast.error(addResponse.message || '添加基金失败');
        return;
      }

      // 第二步：录入盈亏数据
      const profitResponse = await portfolioApi.importProfitData(groupId, {
        profit_data: [{
          fund_code: fundCode,
          profit_loss: profitLoss,
          // current_value 由后端自动计算：shares × latest_nav
        }],
        import_mode: 'overwrite',
      });

      if (profitResponse.success) {
        toast.success('基金添加成功');
        setAddFundDialogOpen(false);
        setAddFundForm({ fund_code: '', shares: '', profit_loss: '' });
        loadData();
      } else {
        toast.error('基金已添加，但盈亏录入失败：' + (profitResponse.message || '未知错误'));
        loadData();
      }
    } catch (error) {
      toast.error('添加基金失败');
    }
  };

  const formatNumber = (num: number | undefined, decimals: number = 2) => {
    if (num === undefined || num === null) return '-';
    return num.toFixed(decimals);
  };

  const formatCurrency = (num: number | undefined) => {
    if (num === undefined || num === null) return '-';
    return `¥${num.toFixed(2)}`;
  };

  const getProfitColor = (profit: number | undefined) => {
    if (profit === undefined || profit === null) return 'text-muted-foreground';
    return profit >= 0 ? 'text-up' : 'text-down';
  };

  // 表格列定义
  const columns: Column<Position>[] = [
    {
      key: 'fund_info',
      title: '基金',
      width: 280,
      minWidth: 200,
      fixed: 'left',
      render: (position) => (
        <div>
          <p className="font-medium truncate">{position.fund_name}</p>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <code className="font-mono">{position.fund_code}</code>
            {position.fund_type && (
              <>
                <span>·</span>
                <span>{position.fund_type}</span>
              </>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'shares',
      title: '持有份额',
      width: 120,
      minWidth: 100,
      sortable: true,
      align: 'right',
      render: (position) => (
        <span className="font-mono">{formatNumber(position.shares, 4)}</span>
      ),
    },
    {
      key: 'buy_nav',
      title: '买入净值',
      width: 100,
      minWidth: 90,
      sortable: true,
      align: 'right',
      render: (position) => (
        <span className="font-mono">{formatNumber(position.buy_nav, 4)}</span>
      ),
    },
    {
      key: 'latest_nav',
      title: '最新净值',
      width: 110,
      minWidth: 100,
      sortable: true,
      align: 'right',
      render: (position) => (
        <div>
          <div className="font-mono">{formatNumber(position.latest_nav, 4)}</div>
          {position.nav_date && (
            <div className="text-xs text-muted-foreground">
              {position.nav_date}
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'market_value',
      title: '市值',
      width: 130,
      minWidth: 110,
      sortable: true,
      align: 'right',
      render: (position) => (
        <span className="font-mono font-medium">{formatCurrency(position.market_value)}</span>
      ),
    },
    {
      key: 'available_cash',
      title: '可用现金',
      width: 120,
      minWidth: 100,
      sortable: true,
      align: 'right',
      render: (position) => {
        const cash = position.available_cash;
        if (cash === undefined || cash === null) return '-';
        return (
          <span className={cn("font-mono", cash >= 0 ? 'text-up' : 'text-down')}>
            {cash >= 0 ? '+' : ''}{formatCurrency(cash)}
          </span>
        );
      },
    },
    {
      key: 'profit_loss',
      title: '盈亏',
      width: 130,
      minWidth: 110,
      sortable: true,
      align: 'right',
      render: (position) => {
        console.log('[Render] profit_loss:', position.fund_code, position.profit_loss, typeof position.profit_loss);
        return (
          <span className={cn("font-mono font-medium", getProfitColor(position.profit_loss))}>
            {position.profit_loss ? `${position.profit_loss >= 0 ? '+' : ''}${formatCurrency(position.profit_loss)}` : '-'}
          </span>
        );
      },
    },
    {
      key: 'profit_rate',
      title: '收益率',
      width: 100,
      minWidth: 90,
      sortable: true,
      align: 'right',
      render: (position) => (
        <span className={cn("font-mono font-medium", getProfitColor(position.profit_rate))}>
          {position.profit_rate && position.profit_rate >= 0 ? '+' : ''}{formatNumber(position.profit_rate)}%
        </span>
      ),
    },
    {
      key: 'return_1y',
      title: '近1年收益',
      width: 100,
      minWidth: 90,
      sortable: true,
      align: 'right',
      render: (position) => (
        <span className={cn("font-mono", getProfitColor(position.return_1y))}>
          {position.return_1y ? `${position.return_1y >= 0 ? '+' : ''}${formatNumber(position.return_1y)}%` : '-'}
        </span>
      ),
    },
    {
      key: 'max_drawdown_1y',
      title: '最大回撤',
      width: 100,
      minWidth: 90,
      sortable: true,
      align: 'right',
      render: (position) => (
        <span className="font-mono text-down">
          {position.max_drawdown_1y ? `-${formatNumber(position.max_drawdown_1y)}%` : '-'}
        </span>
      ),
    },
    {
      key: 'sharpe_ratio_1y',
      title: '夏普比率',
      width: 100,
      minWidth: 90,
      sortable: true,
      align: 'right',
      render: (position) => (
        <span className="font-mono">
          {position.sharpe_ratio_1y ? formatNumber(position.sharpe_ratio_1y, 2) : '-'}
        </span>
      ),
    },
    {
      key: 'rank_in_category',
      title: '同类排名',
      width: 120,
      minWidth: 100,
      align: 'center',
      render: (position) => (
        <span className="text-sm">
          {position.rank_in_category || '-'}
        </span>
      ),
    },
    {
      key: 'tags',
      title: '标签',
      width: 150,
      minWidth: 120,
      render: (position) => (
        <div className="flex flex-wrap gap-1">
          {position.tags && position.tags.length > 0 ? (
            position.tags.map((tag) => (
              <Badge
                key={tag.id}
                variant="secondary"
                className="text-xs px-1.5 py-0.5"
                style={{
                  backgroundColor: tag.color ? `${tag.color}20` : undefined,
                  color: tag.color,
                  borderColor: tag.color,
                }}
              >
                {tag.name}
              </Badge>
            ))
          ) : (
            <span className="text-xs text-muted-foreground">-</span>
          )}
        </div>
      ),
    },
    {
      key: 'action',
      title: '操作',
      width: 100,
      minWidth: 90,
      align: 'center',
      render: (position) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => openTransactionDialog(position, 'BUY')}>
              <Plus className="w-4 h-4 mr-2 text-green-500" />
              买入
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => openTransactionDialog(position, 'SELL')}>
              <Minus className="w-4 h-4 mr-2 text-orange-500" />
              卖出
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => openProfitDialog(position)}>
              <Edit3 className="w-4 h-4 mr-2 text-blue-500" />
              盈利录入
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => openTagDialog(position)}>
              <Tag className="w-4 h-4 mr-2 text-purple-500" />
              标签管理
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => handleRemoveFund(position.fund_code)}
              className="text-red-500 focus:text-red-500"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              移除
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden gap-2">
      {/* 顶部整体可折叠 - 只占用必要空间 */}
      <Collapsible open={summaryOpen} onOpenChange={setSummaryOpen} className="flex-shrink-0">
        <Card className="glow-border">
          {/* 折叠触发栏 */}
          <CollapsibleTrigger asChild>
            <div className="flex items-center justify-between px-3 py-1.5 cursor-pointer hover:bg-accent/30 transition-colors">
              <div className="flex items-center gap-4">
                {/* 收益概览 */}
                {summary && (
                  <div className="flex items-center gap-2">
                    <Wallet className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-xs font-medium">收益概览</span>
                    <span className="text-xs text-muted-foreground">
                      {formatCurrency(summary.total_market_value)} · 
                      <span className={getProfitColor(summary.total_profit_rate)}>
                        {summary.total_profit_rate >= 0 ? '+' : ''}{formatNumber(summary.total_profit_rate)}%
                      </span>
                    </span>
                  </div>
                )}
                {/* 分隔线 */}
                <div className="w-px h-3 bg-border/50" />
                {/* 持仓明细 */}
                <div className="flex items-center gap-2">
                  <Package className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="text-xs font-medium">持仓明细</span>
                  <Badge variant="secondary" className="text-[10px] h-4 px-1">{positions.length} 只</Badge>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {/* 操作按钮 */}
                {freshnessInfo && (
                  <span className={cn(
                    "text-[10px]",
                    freshnessInfo.metrics_updated_count > 0 ? "text-amber-500" : "text-muted-foreground"
                  )}>
                    {freshnessInfo.metrics_updated_count > 0
                      ? `已更新 ${freshnessInfo.metrics_updated_count} 只`
                      : '数据已最新'}
                  </span>
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    setAddFundDialogOpen(true);
                  }}
                  disabled={!groupId}
                  className="h-6 px-2 text-[10px]"
                >
                  <Plus className="w-3 h-3 mr-1" />
                  添加
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRefresh();
                  }}
                  disabled={refreshing || loading}
                  className="h-6 px-2 text-[10px]"
                >
                  {refreshing ? (
                    <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                  ) : (
                    <Loader2 className="w-3 h-3 mr-1" />
                  )}
                  刷新
                </Button>
                {/* 折叠箭头 */}
                <ChevronDown className={cn(
                  "w-4 h-4 text-muted-foreground transition-transform ml-1",
                  summaryOpen && "rotate-180"
                )} />
              </div>
            </div>
          </CollapsibleTrigger>

          {/* 展开内容：收益详情 */}
          {summary && (
            <CollapsibleContent>
              <div className="px-3 py-2 border-t border-border/50">
                <div className="grid grid-cols-5 gap-2">
                  {/* 总成本 */}
                  <div className="flex items-center gap-1.5">
                    <div className="w-6 h-6 rounded bg-blue-500/20 flex items-center justify-center shrink-0">
                      <Wallet className="w-3 h-3 text-blue-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-[9px] text-muted-foreground">总成本</p>
                      <p className="text-xs font-bold truncate">{formatCurrency(summary.total_cost)}</p>
                    </div>
                  </div>
                  
                  {/* 总市值 */}
                  <div className="flex items-center gap-1.5">
                    <div className="w-6 h-6 rounded bg-cyan-500/20 flex items-center justify-center shrink-0">
                      <Target className="w-3 h-3 text-cyan-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-[9px] text-muted-foreground">总市值</p>
                      <p className="text-xs font-bold truncate">{formatCurrency(summary.total_market_value)}</p>
                    </div>
                  </div>
                  
                  {/* 总收益 */}
                  <div className="flex items-center gap-1.5">
                    <div className={cn(
                      "w-6 h-6 rounded flex items-center justify-center shrink-0",
                      summary.total_profit >= 0 ? "bg-emerald-500/20" : "bg-red-500/20"
                    )}>
                      <TrendingUp className={cn(
                        "w-3 h-3",
                        summary.total_profit >= 0 ? "text-emerald-400" : "text-red-400"
                      )} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-[9px] text-muted-foreground">总收益</p>
                      <p className={cn(
                        "text-xs font-bold truncate",
                        getProfitColor(summary.total_profit)
                      )}>
                        {summary.total_profit >= 0 ? '+' : ''}{formatCurrency(summary.total_profit)}
                      </p>
                    </div>
                  </div>
                  
                  {/* 收益率 */}
                  <div className="flex items-center gap-1.5">
                    <div className={cn(
                      "w-6 h-6 rounded flex items-center justify-center shrink-0",
                      summary.total_profit_rate >= 0 ? "bg-emerald-500/20" : "bg-red-500/20"
                    )}>
                      <Percent className={cn(
                        "w-3 h-3",
                        summary.total_profit_rate >= 0 ? "text-emerald-400" : "text-red-400"
                      )} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-[9px] text-muted-foreground">收益率</p>
                      <p className={cn(
                        "text-xs font-bold truncate",
                        getProfitColor(summary.total_profit_rate)
                      )}>
                        {summary.total_profit_rate >= 0 ? '+' : ''}{formatNumber(summary.total_profit_rate)}%
                      </p>
                    </div>
                  </div>

                  {/* 现金余额 */}
                  <div 
                    className="flex items-center gap-1.5 cursor-pointer hover:bg-accent/30 rounded transition-colors -mx-1 px-1"
                    onClick={openCashDialog}
                  >
                    <div className="w-6 h-6 rounded bg-yellow-500/20 flex items-center justify-center shrink-0">
                      <Coins className="w-3 h-3 text-yellow-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-[9px] text-muted-foreground">现金余额</p>
                      <p className="text-xs font-bold truncate">{formatCurrency(cashBalance)}</p>
                    </div>
                  </div>
                </div>
              </div>
            </CollapsibleContent>
          )}
        </Card>
      </Collapsible>

      {/* 表格区域 - 占据绝大部分空间 */}
      <Card className="glow-border flex-[9] min-h-0 flex flex-col">
        <CardContent className="p-0 flex-1 min-h-0 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
            </div>
          ) : positions.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center">
              <Package className="w-12 h-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">暂无持仓</p>
              <p className="text-sm text-muted-foreground mt-1">
                点击"添加"按钮添加基金到组合
              </p>
            </div>
          ) : (
            <ResizableTable
              columns={columns}
              data={positions}
              rowKey={(position) => position.fund_code}
              defaultSort={{ key: 'market_value', direction: 'desc' }}
              loading={loading}
              emptyText="暂无持仓"
              className="h-full"
            />
          )}
        </CardContent>
      </Card>

      {/* 交易录入弹窗 */}
      <Dialog open={transactionDialogOpen} onOpenChange={setTransactionDialogOpen}>
        <DialogContent className="sm:max-w-[500px] min-h-[400px]">
          <DialogHeader>
            <DialogTitle>
              {transactionType === 'BUY' ? '买入' : '卖出'} {selectedFund?.fund_name}
            </DialogTitle>
          </DialogHeader>
          <Tabs value={transactionTab} onValueChange={setTransactionTab} className="w-full flex flex-col flex-1">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="input">{transactionType === 'BUY' ? '买入录入' : '卖出录入'}</TabsTrigger>
              <TabsTrigger value="history">交易记录</TabsTrigger>
            </TabsList>

            <TabsContent value="input" className="space-y-4 mt-4 flex-1">
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="shares" className="text-right">份额</Label>
                  <Input
                    id="shares"
                    type="number"
                    step="0.0001"
                    value={transactionForm.shares}
                    onChange={(e) => setTransactionForm({ ...transactionForm, shares: e.target.value })}
                    className="col-span-3"
                    placeholder={`${transactionType === 'BUY' ? '买入' : '卖出'}份额`}
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="amount" className="text-right">金额</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={transactionForm.amount}
                    onChange={(e) => setTransactionForm({ ...transactionForm, amount: e.target.value })}
                    className="col-span-3"
                    placeholder={`${transactionType === 'BUY' ? '投入' : '获得'}金额`}
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="date" className="text-right">日期</Label>
                  <Input
                    id="date"
                    type="date"
                    value={transactionForm.transaction_date}
                    onChange={(e) => setTransactionForm({ ...transactionForm, transaction_date: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="notes" className="text-right">备注</Label>
                  <Input
                    id="notes"
                    value={transactionForm.notes}
                    onChange={(e) => setTransactionForm({ ...transactionForm, notes: e.target.value })}
                    className="col-span-3"
                    placeholder="备注（可选）"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setTransactionDialogOpen(false)}>取消</Button>
                <Button onClick={submitTransaction} className={transactionType === 'BUY' ? 'bg-green-600 hover:bg-green-700' : 'bg-orange-600 hover:bg-orange-700'}>
                  确认{transactionType === 'BUY' ? '买入' : '卖出'}
                </Button>
              </DialogFooter>
            </TabsContent>

            <TabsContent value="history" className="mt-4 flex-1">
              <div className="py-4 min-h-[200px]">
                {transactions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    暂无交易记录
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {transactions.map((tx) => (
                      <div
                        key={tx.id}
                        className="flex items-center justify-between p-3 rounded-lg border bg-card"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            tx.transaction_type === 'BUY' ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'
                          }`}>
                            {tx.transaction_type === 'BUY' ? <Plus className="w-4 h-4" /> : <Minus className="w-4 h-4" />}
                          </div>
                          <div>
                            <p className="font-medium text-sm">
                              {tx.transaction_type === 'BUY' ? '买入' : '卖出'}
                            </p>
                            <p className="text-xs text-muted-foreground">{tx.transaction_date}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-mono text-sm">{tx.shares.toFixed(4)} 份</p>
                          <p className="font-mono text-xs text-muted-foreground">¥{tx.amount.toFixed(2)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setTransactionDialogOpen(false)}>关闭</Button>
              </DialogFooter>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>

      {/* 盈利录入弹窗 */}
      <Dialog open={profitDialogOpen} onOpenChange={setProfitDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>盈利录入 - {selectedFund?.fund_name}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">当前市值</Label>
              <div className="col-span-3 text-sm text-muted-foreground">
                {selectedFund?.market_value ? `¥${selectedFund.market_value.toFixed(2)}` : '-'}
                <span className="text-xs ml-2">(自动计算：份额 × 最新净值)</span>
              </div>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="profit_loss" className="text-right">盈亏金额</Label>
              <Input
                id="profit_loss"
                type="number"
                step="0.01"
                value={profitForm.profit_loss}
                onChange={(e) => setProfitForm({ ...profitForm, profit_loss: e.target.value })}
                className="col-span-3"
                placeholder="盈利为正，亏损为负"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="import_mode" className="text-right">导入模式</Label>
              <Select
                value={profitForm.import_mode}
                onValueChange={(value: 'overwrite' | 'accumulate') => setProfitForm({ ...profitForm, import_mode: value })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="accumulate">累加模式（与现有数据累加）</SelectItem>
                  <SelectItem value="overwrite">覆盖模式（替换现有数据）</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setProfitDialogOpen(false)}>取消</Button>
            <Button onClick={submitProfit}>确认录入</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 现金管理弹窗 */}
      <Dialog open={cashDialogOpen} onOpenChange={setCashDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>现金余额管理</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="cash" className="text-right">现金金额</Label>
              <Input
                id="cash"
                type="number"
                step="0.01"
                value={cashForm.cash}
                onChange={(e) => setCashForm({ ...cashForm, cash: e.target.value })}
                className="col-span-3"
                placeholder="现金余额"
              />
            </div>
            <p className="text-xs text-muted-foreground text-center">
              卖出基金所得会自动计入现金余额
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCashDialogOpen(false)}>取消</Button>
            <Button onClick={submitCashUpdate}>确认更新</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 添加基金弹窗 */}
      <Dialog open={addFundDialogOpen} onOpenChange={setAddFundDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>添加基金</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="fund_code" className="text-right">基金代码</Label>
              <Input
                id="fund_code"
                value={addFundForm.fund_code}
                onChange={(e) => setAddFundForm({ ...addFundForm, fund_code: e.target.value })}
                className="col-span-3"
                placeholder="请输入基金代码"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="shares" className="text-right">持有份额</Label>
              <Input
                id="shares"
                type="number"
                step="0.0001"
                value={addFundForm.shares}
                onChange={(e) => setAddFundForm({ ...addFundForm, shares: e.target.value })}
                className="col-span-3"
                placeholder="请输入持有份额"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="profit_loss" className="text-right">当前盈亏</Label>
              <Input
                id="profit_loss"
                type="number"
                step="0.01"
                value={addFundForm.profit_loss}
                onChange={(e) => setAddFundForm({ ...addFundForm, profit_loss: e.target.value })}
                className="col-span-3"
                placeholder="盈利为正，亏损为负"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddFundDialogOpen(false)}>取消</Button>
            <Button onClick={submitAddFund}>确认添加</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 标签管理弹窗 */}
      <Dialog open={tagDialogOpen} onOpenChange={setTagDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>标签管理 - {selectedFundForTag?.fund_name}</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <TagSelectorInline
              fundCode={selectedFundForTag?.fund_code || ''}
              selectedTags={fundTags}
              onTagsChange={setFundTags}
              placeholder="搜索或创建标签..."
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setTagDialogOpen(false)}>取消</Button>
            <Button onClick={saveFundTags} disabled={savingTags}>
              {savingTags ? '保存中...' : '保存'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
