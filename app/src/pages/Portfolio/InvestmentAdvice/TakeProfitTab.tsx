import { useState, useEffect } from 'react';
import {
  TrendingDown,
  Loader2,
  Info,
  BarChart3,
  Settings,
  ChevronDown,
  Check,
  Plus,
  Trash2,
  Edit2,
  Star,
  X,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { toast } from 'sonner';
import { 
  portfolioApi, 
  type TakeProfitAdvice, 
  type TakeProfitTemplate,
  type FundTakeProfitConfig
} from '@/services/api';
import { cn } from '@/lib/utils';

interface TakeProfitTabProps {
  groupId: number;
  groupName?: string;
  onRefresh?: () => void;  // 执行交易后刷新父组件
}

export default function TakeProfitTab({ groupId, groupName, onRefresh }: TakeProfitTabProps) {
  const [advice, setAdvice] = useState<TakeProfitAdvice | null>(null);
  const [templates, setTemplates] = useState<TakeProfitTemplate[]>([]);
  const [configs, setConfigs] = useState<FundTakeProfitConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [editTemplate, setEditTemplate] = useState<TakeProfitTemplate | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  // 表单状态
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    first_threshold: 20,
    first_sell_ratio: 30,
    step_size: 5,
    follow_up_sell_ratio: 20,
    enable_cost_control: true,
    target_diluted_cost: 0,
    enable_buy_back: false,
    buy_back_threshold: 20,
  });

  useEffect(() => {
    loadTemplates();
    loadAdvice();
    loadConfigs();
  }, [groupId]);

  const loadTemplates = async () => {
    try {
      setLoadingTemplates(true);
      const response = await portfolioApi.getTakeProfitTemplates();
      if (response.success) {
        setTemplates(response.data);
      }
    } catch (error) {
      console.error('加载止盈模板失败:', error);
    } finally {
      setLoadingTemplates(false);
    }
  };

  const loadAdvice = async () => {
    if (!groupId) return;

    try {
      setLoading(true);
      const response = await portfolioApi.getTakeProfitAdvice(groupId);
      console.log('API Response:', response);
      if (response.success) {
        // 调试输出021094基金的数据
        const fund021094 = response.data.funds.find((f: TakeProfitFundResult) => f.fund_code === '021094');
        if (fund021094) {
          console.log('021094基金数据:', fund021094);
          console.log('action:', fund021094.action, 'type:', typeof fund021094.action);
          console.log('action === "BUY":', fund021094.action === 'BUY');
        }
        setAdvice(response.data);
      } else {
        toast.error(response.message || '获取止盈建议失败');
      }
    } catch (error) {
      console.error('获取止盈建议失败:', error);
      toast.error('获取止盈建议失败');
    } finally {
      setLoading(false);
    }
  };

  const loadConfigs = async () => {
    if (!groupId) return;

    try {
      const response = await portfolioApi.getPortfolioTakeProfitConfigs(groupId);
      if (response.success) {
        setConfigs(response.data);
      }
    } catch (error) {
      console.error('获取止盈配置失败:', error);
    }
  };

  const handleExecuteBuyBack = async (fund: TakeProfitFundResult) => {
    if (!groupId || !fund.buy_back_shares || !fund.buy_back_amount) return;

    // 添加确认对话框
    const confirmed = window.confirm(
      `确认执行波段捡回？\n\n` +
      `基金：${fund.fund_name} (${fund.fund_code})\n` +
      `捡回份额：${fund.buy_back_shares.toFixed(2)} 份\n` +
      `预计花费：¥${fund.buy_back_amount.toFixed(2)}\n` +
      `当前净值：${fund.current_nav.toFixed(4)}\n\n` +
      `捡回后该笔卖出记录将被标记为已回收。`
    );

    if (!confirmed) return;

    try {
      // 从algorithm_details中提取目标卖出交易ID
      // 格式: "目标卖出记录ID: 123"
      const targetIdMatch = fund.algorithm_details?.find(d => d.includes('目标卖出记录ID'));
      const targetSellTransactionId = targetIdMatch
        ? parseInt(targetIdMatch.match(/ID:\s*(\d+)/)?.[1] || '0')
        : 0;

      if (!targetSellTransactionId) {
        toast.error('无法获取目标卖出记录ID');
        return;
      }

      const response = await portfolioApi.executeBuyBackTransaction(groupId, fund.fund_code, {
        target_sell_transaction_id: targetSellTransactionId,
        shares: fund.buy_back_shares,
        amount: fund.buy_back_amount,
        nav: fund.current_nav,
      });

      if (response.success) {
        toast.success(response.message);
        loadAdvice(); // 刷新建议
        // 触发父组件刷新，更新基金列表的现金字段
        if (onRefresh) {
          onRefresh();
        }
      } else {
        toast.error(response.message || '执行捡回失败');
      }
    } catch (error) {
      console.error('执行捡回失败:', error);
      toast.error('执行捡回失败');
    }
  };

  const handleCreateTemplate = () => {
    setEditTemplate(null);
    setIsCreating(true);
    setFormData({
      name: '',
      description: '',
      first_threshold: 20,
      first_sell_ratio: 30,
      step_size: 5,
      follow_up_sell_ratio: 20,
      enable_cost_control: true,
      target_diluted_cost: 0,
      enable_buy_back: false,
      buy_back_threshold: 20,
    });
    setTemplateDialogOpen(true);
  };

  const handleEditTemplate = (template: TakeProfitTemplate) => {
    setEditTemplate(template);
    setIsCreating(false);
    // 调试输出
    console.log('Editing template:', template);
    console.log('enable_buy_back raw value:', template.enable_buy_back, 'type:', typeof template.enable_buy_back);
    setFormData({
      name: template.name,
      description: template.description || '',
      first_threshold: Math.round(template.first_threshold * 100),
      first_sell_ratio: Math.round(template.first_sell_ratio * 100),
      step_size: Math.round(template.step_size * 100),
      follow_up_sell_ratio: Math.round(template.follow_up_sell_ratio * 100),
      enable_cost_control: template.enable_cost_control === 1 || template.enable_cost_control === true,
      target_diluted_cost: template.target_diluted_cost,
      enable_buy_back: template.enable_buy_back === 1 || template.enable_buy_back === true,
      buy_back_threshold: Math.round((template.buy_back_threshold || 0.20) * 100),
    });
    setTemplateDialogOpen(true);
  };

  const handleSaveTemplate = async () => {
    if (!formData.name.trim()) {
      toast.error('请输入模板名称');
      return;
    }

    const data = {
      name: formData.name,
      description: formData.description,
      first_threshold: formData.first_threshold / 100,
      first_sell_ratio: formData.first_sell_ratio / 100,
      step_size: formData.step_size / 100,
      follow_up_sell_ratio: formData.follow_up_sell_ratio / 100,
      enable_cost_control: formData.enable_cost_control,
      target_diluted_cost: formData.target_diluted_cost,
      enable_buy_back: formData.enable_buy_back,
      buy_back_threshold: formData.buy_back_threshold / 100,
    };

    try {
      let response;
      if (isCreating) {
        response = await portfolioApi.createTakeProfitTemplate(data);
      } else if (editTemplate) {
        response = await portfolioApi.updateTakeProfitTemplate(editTemplate.id, data);
      }

      if (response?.success) {
        toast.success(isCreating ? '模板创建成功' : '模板更新成功');
        setTemplateDialogOpen(false);
        loadTemplates();
        loadAdvice();
      } else {
        toast.error(response?.message || '操作失败');
      }
    } catch (error) {
      toast.error('操作失败');
    }
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (!confirm('确定要删除此模板吗？')) return;

    try {
      const response = await portfolioApi.deleteTakeProfitTemplate(templateId);
      if (response.success) {
        toast.success('模板删除成功');
        loadTemplates();
        loadAdvice();
      } else {
        toast.error(response.message || '删除失败');
      }
    } catch (error) {
      toast.error('删除失败');
    }
  };

  const handleSetDefaultTemplate = async (templateId: number) => {
    try {
      const response = await portfolioApi.setDefaultTakeProfitTemplate(templateId);
      if (response.success) {
        toast.success('默认模板设置成功');
        loadTemplates();
      } else {
        toast.error(response.message || '设置失败');
      }
    } catch (error) {
      toast.error('设置失败');
    }
  };

  const formatCurrency = (num: number | undefined | null) => {
    if (num === undefined || num === null) return '-';
    return `¥${num.toFixed(2)}`;
  };

  const formatPercent = (num: number | undefined | null) => {
    if (num === undefined || num === null) return '-';
    return `${(num * 100).toFixed(2)}%`;
  };

  const getActionColor = (action: string) => {
    if (action === 'SELL') return 'text-down';
    if (action === 'BUY') return 'text-blue-400';
    if (action === 'STOP') return 'text-emerald-400';
    return 'text-muted-foreground';
  };

  const getActionBadge = (action: string, fund?: TakeProfitFundResult) => {
    if (action === 'SELL' && fund) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge className="bg-red-500/20 text-red-400 border-red-500/30 cursor-help">卖出</Badge>
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-sm">
              <div className="space-y-2 text-sm">
                <p className="font-medium text-red-400">卖出数量计算算法</p>
                <div className="space-y-1 text-muted-foreground">
                  <p>卖出份额 = 当前份额 × 卖出比例</p>
                  <p>卖出金额 = 卖出份额 × 当前净值</p>
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <p className="text-xs text-cyan-400">当前计算：</p>
                  <p className="font-mono text-xs">
                    {fund.current_shares.toFixed(2)} × {(fund.sell_ratio! * 100).toFixed(0)}% = {fund.sell_shares?.toFixed(2)} 份
                  </p>
                  <p className="font-mono text-xs">
                    {fund.sell_shares?.toFixed(2)} × {fund.current_nav.toFixed(4)} = {formatCurrency(fund.sell_amount)}
                  </p>
                </div>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }
    if (action === 'BUY' && fund) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 cursor-help">捡回</Badge>
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-sm">
              <div className="space-y-2 text-sm">
                <p className="font-medium text-blue-400">波段捡回计算算法</p>
                <div className="space-y-1 text-muted-foreground">
                  <p>跌幅 = (卖出净值 - 当前净值) / 卖出净值</p>
                  <p>捡回份额 = 原卖出份额</p>
                  <p>捡回金额 = 捡回份额 × 当前净值</p>
                </div>
                <div className="border-t border-border pt-2 mt-2">
                  <p className="text-xs text-cyan-400">当前计算：</p>
                  <p className="font-mono text-xs">
                    目标卖出净值: {fund.target_sell_nav?.toFixed(4)}
                  </p>
                  <p className="font-mono text-xs">
                    当前跌幅: {(fund.decline_rate! * 100).toFixed(2)}%
                  </p>
                  <p className="font-mono text-xs">
                    捡回 {fund.buy_back_shares?.toFixed(2)} 份 = {formatCurrency(fund.buy_back_amount)}
                  </p>
                </div>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }
    if (action === 'SELL') return <Badge className="bg-red-500/20 text-red-400 border-red-500/30">卖出</Badge>;
    if (action === 'BUY') return <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30">捡回</Badge>;
    if (action === 'STOP') return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">停止止盈</Badge>;
    if (action === 'HOLD') return <Badge variant="secondary">持有</Badge>;
    return <Badge variant="outline">{action}</Badge>;
  };

  const getTemplateName = (fundCode: string) => {
    const config = configs.find(c => c.fund_code === fundCode);
    if (config?.param_source === 'custom') return '自定义';
    if (config?.template_name) return config.template_name;
    const defaultTemplate = templates.find(t => t.is_default === 1);
    return defaultTemplate?.name || '默认';
  };

  const handleSetFundTemplate = async (fundCode: string, templateId: number | null) => {
    try {
      const response = await portfolioApi.setFundTakeProfitConfig(groupId, fundCode, {
        template_id: templateId ?? undefined
      });
      if (response.success) {
        toast.success('设置成功');
        loadConfigs();
        loadAdvice();
      } else {
        toast.error(response.message || '设置失败');
      }
    } catch (error) {
      toast.error('设置失败');
    }
  };

  const handleResetFundConfig = async (fundCode: string) => {
    try {
      const response = await portfolioApi.resetFundTakeProfitConfig(groupId, fundCode);
      if (response.success) {
        toast.success('重置成功');
        loadConfigs();
        loadAdvice();
      } else {
        toast.error(response.message || '重置失败');
      }
    } catch (error) {
      toast.error('重置失败');
    }
  };

  const defaultTemplate = templates.find(t => t.is_default === 1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-border/50">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-muted-foreground">当前默认模板：</span>
          {loadingTemplates ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Badge variant="secondary" className="text-base px-3 py-1">
              {defaultTemplate?.name || '标准型'}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              loadAdvice();
              toast.success('已刷新');
            }}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setTemplateDialogOpen(true)}
          >
            <Settings className="w-4 h-4 mr-2" />
            模板管理
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
          <span className="ml-3 text-muted-foreground">正在计算止盈建议...</span>
        </div>
      ) : !advice ? (
        <div className="flex items-center justify-center py-12">
          <Info className="w-8 h-8 text-muted-foreground mr-3" />
          <span className="text-muted-foreground">暂无止盈建议数据</span>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-6 p-4 bg-muted/30 rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">持仓基金</p>
                <p className="text-2xl font-bold">{advice.summary.total_funds} <span className="text-base font-normal text-muted-foreground">只</span></p>
              </div>
            </div>

            <div className="w-px h-12 bg-border hidden sm:block" />

            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
                <TrendingDown className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">建议卖出</p>
                <p className="text-2xl font-bold text-red-400">{advice.summary.need_action_count} <span className="text-base font-normal text-muted-foreground">只</span></p>
              </div>
            </div>

            <div className="w-px h-12 bg-border hidden sm:block" />

            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gray-500/20 flex items-center justify-center">
                <Info className="w-6 h-6 text-gray-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">继续持有</p>
                <p className="text-2xl font-bold">{advice.summary.hold_count} <span className="text-base font-normal text-muted-foreground">只</span></p>
              </div>
            </div>

            <div className="w-px h-12 bg-border hidden sm:block" />

            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
                <Check className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">停止止盈</p>
                <p className="text-2xl font-bold text-emerald-400">{advice.summary.stop_count} <span className="text-base font-normal text-muted-foreground">只</span></p>
              </div>
            </div>

            {/* 建议捡回 */}
            {(advice.summary.buy_back_count > 0 || advice.summary.total_buy_back_amount > 0) && (
              <>
                <div className="w-px h-12 bg-border hidden sm:block" />
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                    <TrendingDown className="w-6 h-6 text-blue-400 rotate-180" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">建议捡回</p>
                    <p className="text-2xl font-bold text-blue-400">{advice.summary.buy_back_count || 0} <span className="text-base font-normal text-muted-foreground">只</span></p>
                  </div>
                </div>
              </>
            )}

            {/* 预计卖出金额 */}
            {advice.summary.total_sell_amount > 0 && (
              <>
                <div className="w-px h-12 bg-border hidden sm:block" />
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
                    <span className="text-lg font-bold text-amber-400">¥</span>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">预计卖出金额</p>
                    <p className="text-2xl font-bold text-amber-400">{formatCurrency(advice.summary.total_sell_amount)}</p>
                  </div>
                </div>
              </>
            )}

            {/* 预计捡回金额 */}
            {(advice.summary.total_buy_back_amount > 0) && (
              <>
                <div className="w-px h-12 bg-border hidden sm:block" />
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                    <span className="text-lg font-bold text-blue-400">¥</span>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">预计捡回金额</p>
                    <p className="text-2xl font-bold text-blue-400">{formatCurrency(advice.summary.total_buy_back_amount)}</p>
                  </div>
                </div>
              </>
            )}
          </div>

          <Card className="glow-border">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-red-400" />
                止盈建议明细
                <Badge variant="secondary">{advice.funds.length} 只基金</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead>基金</TableHead>
                      <TableHead className="text-right">当前份额</TableHead>
                      <TableHead className="text-right">当前净值</TableHead>
                      <TableHead className="text-right">持仓市值</TableHead>
                      <TableHead className="text-right">买入净值</TableHead>
                      <TableHead className="text-right">当前收益率</TableHead>
                      <TableHead className="text-right">可用现金</TableHead>
                      <TableHead className="text-right">卖出记录</TableHead>
                      <TableHead className="text-right">摊薄成本</TableHead>
                      <TableHead className="text-center">建议操作</TableHead>
                      <TableHead className="text-center">使用模板</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {advice.funds.map((fund) => (
                      <TableRow key={fund.fund_code} className="table-row-hover">
                        <TableCell>
                          <div>
                            <p className="font-medium">{fund.fund_name}</p>
                            <code className="text-xs text-muted-foreground font-mono">{fund.fund_code}</code>
                          </div>
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {fund.current_shares.toFixed(2)}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {fund.current_nav.toFixed(4)}
                        </TableCell>
                        <TableCell className="text-right font-mono font-medium text-cyan-400">
                          {formatCurrency(fund.current_value)}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {fund.buy_nav.toFixed(4)}
                        </TableCell>
                        <TableCell className={cn(
                          "text-right font-mono font-medium",
                          fund.current_profit_rate >= 0 ? "text-up" : "text-down"
                        )}>
                          {fund.current_profit_rate >= 0 ? '+' : ''}{(fund.current_profit_rate * 100).toFixed(2)}%
                        </TableCell>
                        <TableCell className={cn(
                          "text-right font-mono",
                          fund.available_cash <= 0 ? "text-orange-400" : "text-muted-foreground"
                        )}>
                          {formatCurrency(fund.available_cash)}
                        </TableCell>
                        <TableCell className="text-right font-mono text-muted-foreground">
                          {fund.has_sell_record ? (
                            <span>{fund.last_sell_nav?.toFixed(4)} ({fund.last_sell_date})</span>
                          ) : (
                            <span className="text-muted-foreground">无</span>
                          )}
                        </TableCell>
                        <TableCell className="text-right font-mono">
                          {fund.diluted_cost?.toFixed(4) || '-'}
                        </TableCell>
                        <TableCell className="text-center">
                          <div className="flex flex-col items-center gap-1">
                            {getActionBadge(fund.action, fund)}
                            {fund.action === 'SELL' && fund.sell_amount !== null && (
                              <span className="text-sm text-red-400 font-medium">
                                {formatCurrency(fund.sell_amount)}
                              </span>
                            )}
                            {fund.action === 'BUY' && fund.buy_back_amount !== null && (
                              <>
                                <span className="text-sm text-blue-400 font-medium">
                                  {formatCurrency(fund.buy_back_amount)}
                                </span>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="h-6 px-2 text-xs border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
                                  onClick={() => handleExecuteBuyBack(fund)}
                                >
                                  执行捡回
                                </Button>
                              </>
                            )}
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm" className="h-8 px-2">
                                {getTemplateName(fund.fund_code)}
                                <ChevronDown className="w-4 h-4 ml-1" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              {templates.map((template) => (
                                <DropdownMenuItem
                                  key={template.id}
                                  onClick={() => handleSetFundTemplate(fund.fund_code, template.id)}
                                >
                                  {template.name}
                                  {template.is_default === 1 && (
                                    <Badge variant="secondary" className="ml-2 text-xs">默认</Badge>
                                  )}
                                </DropdownMenuItem>
                              ))}
                              <DropdownMenuItem
                                onClick={() => handleResetFundConfig(fund.fund_code)}
                                className="text-muted-foreground"
                              >
                                重置为默认
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          <Card className="glow-border">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Info className="w-4 h-4" />
                数据来源说明
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground space-y-1">
                <p>• 当前份额、买入净值、摊薄成本：<code className="text-cyan-400">list_portfolio_funds()</code></p>
                <p>• 当前净值：<code className="text-cyan-400">get_fund_nav()</code>（自动检查新鲜度，过期自动同步）</p>
                <p>• 卖出记录：<code className="text-cyan-400">get_portfolio_transactions()</code></p>
              </div>
            </CardContent>
          </Card>

          {advice.funds.find(f => f.algorithm_details?.length > 0) && (
            <Card className="glow-border">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  算法详情（第一只基金）
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm max-h-60 overflow-y-auto">
                  {advice.funds[0]?.algorithm_details?.map((detail, index) => (
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

      {/* 模板管理对话框 */}
      <Dialog open={templateDialogOpen} onOpenChange={setTemplateDialogOpen}>
        <DialogContent className="!max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              止盈参数模板管理
            </DialogTitle>
            <DialogDescription>
              管理止盈参数模板，设置默认模板，或为单只基金指定不同模板
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-auto py-4">
            <div className="flex justify-end mb-4">
              <Button onClick={handleCreateTemplate}>
                <Plus className="w-4 h-4 mr-2" />
                新建模板
              </Button>
            </div>

            <div className="space-y-3">
              {templates.map((template) => (
                <Card key={template.id} className={cn(
                  "transition-colors",
                  template.is_default ? "border-amber-500/50 bg-amber-500/5" : ""
                )}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-medium text-lg">{template.name}</h4>
                          {template.is_default === 1 && (
                            <Badge className="bg-amber-500 text-white">
                              <Star className="w-3 h-3 mr-1" />
                              默认
                            </Badge>
                          )}
                          {template.is_system === 1 && (
                            <Badge variant="secondary">系统预设</Badge>
                          )}
                        </div>
                        {template.description && (
                          <p className="text-sm text-muted-foreground mb-3">{template.description}</p>
                        )}
                        <div className="flex flex-wrap gap-4 text-sm">
                          <span className="text-muted-foreground">
                            首次阈值: <span className="text-foreground font-medium">{(template.first_threshold * 100).toFixed(0)}%</span>
                          </span>
                          <span className="text-muted-foreground">
                            首次卖出: <span className="text-foreground font-medium">{(template.first_sell_ratio * 100).toFixed(0)}%</span>
                          </span>
                          <span className="text-muted-foreground">
                            阶梯步长: <span className="text-foreground font-medium">{(template.step_size * 100).toFixed(0)}%</span>
                          </span>
                          <span className="text-muted-foreground">
                            后续卖出: <span className="text-foreground font-medium">{(template.follow_up_sell_ratio * 100).toFixed(0)}%</span>
                          </span>
                          <span className="text-muted-foreground">
                            成本控制: <span className="text-foreground font-medium">{template.enable_cost_control ? '启用' : '禁用'}</span>
                          </span>
                          {(template.enable_buy_back === 1 || template.enable_buy_back === true) && (
                            <span className="text-muted-foreground">
                              波段捡回: <span className="text-blue-400 font-medium">启用 ({(template.buy_back_threshold * 100).toFixed(0)}%)</span>
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 ml-4">
                        {template.is_default !== 1 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSetDefaultTemplate(template.id)}
                            title="设为默认"
                          >
                            <Star className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditTemplate(template)}
                          title="编辑"
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        {template.is_system !== 1 && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteTemplate(template.id)}
                            title="删除"
                            className="text-red-400 hover:text-red-500"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* 创建/编辑模板对话框 */}
      <Dialog open={templateDialogOpen && (isCreating || !!editTemplate)} onOpenChange={(open) => {
        if (!open) {
          setIsCreating(false);
          setEditTemplate(null);
        }
      }}>
        <DialogContent className="!max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {isCreating ? '新建止盈参数模板' : '编辑止盈参数模板'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>模板名称</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="请输入模板名称"
              />
            </div>

            <div className="space-y-2">
              <Label>模板描述</Label>
              <Input
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="请输入模板描述（可选）"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>首次止盈阈值 (%)</Label>
                <Input
                  type="number"
                  value={formData.first_threshold}
                  onChange={(e) => setFormData({ ...formData, first_threshold: Number(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label>首次卖出比例 (%)</Label>
                <Input
                  type="number"
                  value={formData.first_sell_ratio}
                  onChange={(e) => setFormData({ ...formData, first_sell_ratio: Number(e.target.value) })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>阶梯步长 (%)</Label>
                <Input
                  type="number"
                  value={formData.step_size}
                  onChange={(e) => setFormData({ ...formData, step_size: Number(e.target.value) })}
                />
              </div>
              <div className="space-y-2">
                <Label>后续卖出比例 (%)</Label>
                <Input
                  type="number"
                  value={formData.follow_up_sell_ratio}
                  onChange={(e) => setFormData({ ...formData, follow_up_sell_ratio: Number(e.target.value) })}
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Label>启用成本控制</Label>
              <Switch
                checked={formData.enable_cost_control}
                onCheckedChange={(checked) => setFormData({ ...formData, enable_cost_control: checked })}
              />
            </div>

            {formData.enable_cost_control && (
              <div className="space-y-2">
                <Label>目标摊薄成本</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.target_diluted_cost}
                  onChange={(e) => setFormData({ ...formData, target_diluted_cost: Number(e.target.value) })}
                />
              </div>
            )}

            {/* 波段捡回设置 */}
            <div className="border-t border-border pt-4 mt-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Label>启用波段捡回（高抛低吸）</Label>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="w-4 h-4 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent side="right" className="max-w-xs">
                        <p className="text-sm">当净值低于最近一次卖出价格达到设定阈值时，使用卖出所得现金买回相同份额，实现高抛低吸</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <Switch
                  checked={formData.enable_buy_back}
                  onCheckedChange={(checked) => setFormData({ ...formData, enable_buy_back: checked })}
                />
              </div>

              {formData.enable_buy_back && (
                <div className="space-y-2">
                  <Label>捡回阈值 (%)</Label>
                  <Input
                    type="number"
                    value={formData.buy_back_threshold}
                    onChange={(e) => setFormData({ ...formData, buy_back_threshold: Number(e.target.value) })}
                  />
                  <p className="text-xs text-muted-foreground">
                    当净值低于最近一次卖出价格达到此阈值时触发捡回
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setIsCreating(false);
                setEditTemplate(null);
              }}
            >
              取消
            </Button>
            <Button onClick={handleSaveTemplate}>
              {isCreating ? '创建' : '保存'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
