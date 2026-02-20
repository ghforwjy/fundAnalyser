import { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  ChevronLeft, 
  ChevronRight, 
  ChevronsLeft, 
  ChevronsRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  BarChart3,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { fundApi, filterApi, type FundInfo } from '@/services/api';

interface FundListProps {
  onFundClick?: (fundCode: string) => void;
}

interface SortCondition {
  field: string;
  direction: 'asc' | 'desc';
}

export default function FundListPage({ onFundClick }: FundListProps) {
  const [funds, setFunds] = useState<FundInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [sort, setSort] = useState<SortCondition | null>(null);
  
  // 筛选条件
  const [filters, setFilters] = useState({
    fund_type: '',
    risk_level: '',
    manager_company: '',
  });

  // 筛选选项
  const [fundTypes, setFundTypes] = useState<string[]>([]);
  const [companies, setCompanies] = useState<string[]>([]);

  // 加载基金列表
  useEffect(() => {
    loadFunds();
  }, [page, pageSize, filters, sort]);

  // 加载筛选选项
  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFunds = async () => {
    try {
      setLoading(true);
      const response = await fundApi.getList({
        page,
        page_size: pageSize,
        fund_type: filters.fund_type || undefined,
        manager_company: filters.manager_company || undefined,
        risk_level: filters.risk_level ? parseInt(filters.risk_level) : undefined,
        keyword: searchTerm || undefined,
        order_by: sort?.field || 'fund_code',
        order_dir: sort?.direction?.toUpperCase() || 'ASC',
      });
      
      if (response.success) {
        setFunds(response.data.data);
        setTotal(response.data.total);
        setTotalPages(response.data.total_pages);
      }
    } catch (error) {
      toast.error('加载基金列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadFilterOptions = async () => {
    try {
      const [typesRes, companiesRes] = await Promise.all([
        filterApi.getFundTypes(),
        filterApi.getCompanies(),
      ]);
      
      if (typesRes.success) {
        setFundTypes(typesRes.data);
      }
      if (companiesRes.success) {
        setCompanies(companiesRes.data);
      }
    } catch (error) {
      console.error('加载筛选选项失败', error);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadFunds();
  };

  const handleSort = (field: string) => {
    if (sort?.field === field) {
      setSort(sort.direction === 'asc' ? { field, direction: 'desc' } : null);
    } else {
      setSort({ field, direction: 'asc' });
    }
  };

  const getSortIcon = (field: string) => {
    if (sort?.field !== field) return <ArrowUpDown className="w-3 h-3 text-muted-foreground" />;
    return sort.direction === 'asc' 
      ? <ArrowUp className="w-3 h-3 text-cyan-400" />
      : <ArrowDown className="w-3 h-3 text-cyan-400" />;
  };

  const getFundTypeBadge = (type: string) => {
    const typeStyles: Record<string, string> = {
      '股票型': 'bg-red-500/20 text-red-400 border-red-500/30',
      '债券型': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      '混合型': 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
      '货币型': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      '指数型': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
      'QDII': 'bg-pink-500/20 text-pink-400 border-pink-500/30',
      'FOF': 'bg-indigo-500/20 text-indigo-400 border-indigo-500/30',
      'ETF': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    };
    return (
      <Badge className={cn('text-xs', typeStyles[type] || 'bg-gray-500/20 text-gray-400')}>
        {type}
      </Badge>
    );
  };

  const getRiskBadge = (level?: number) => {
    if (!level) return '-';
    const colors = ['', 'bg-emerald-500/20 text-emerald-400', 'bg-lime-500/20 text-lime-400', 
                    'bg-yellow-500/20 text-yellow-400', 'bg-orange-500/20 text-orange-400', 'bg-red-500/20 text-red-400'];
    return (
      <Badge className={cn('text-xs', colors[level])}>
        {level}级
      </Badge>
    );
  };

  const handleFundClick = (fundCode: string) => {
    if (onFundClick) {
      onFundClick(fundCode);
    }
  };

  const handleExport = () => {
    if (!funds.length) return;
    
    const csvContent = [
      ['基金代码', '基金名称', '基金类型', '风险等级', '最新净值', '日涨跌', '基金公司'].join(','),
      ...funds.map(fund => [
        fund.fund_code,
        fund.fund_name,
        fund.fund_type,
        fund.risk_level,
        fund.latest_nav || '',
        fund.latest_return || '',
        fund.manager_company,
      ].join(','))
    ].join('\n');
    
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `基金列表_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    toast.success('数据已导出');
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">基金列表</h1>
          <p className="text-muted-foreground mt-1">浏览和筛选基金产品</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-1" />
            导出
          </Button>
          <Button variant="outline" onClick={loadFunds}>
            <RefreshCw className="w-4 h-4 mr-1" />
            刷新
          </Button>
        </div>
      </div>

      {/* 搜索和筛选 */}
      <Card className="glow-border">
        <CardContent className="p-4 space-y-4">
          {/* 搜索框 */}
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="搜索基金代码、名称..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-9"
              />
            </div>
            <Button onClick={handleSearch} className="bg-cyan-500 hover:bg-cyan-600">
              搜索
            </Button>
          </div>

          {/* 筛选条件 */}
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">筛选:</span>
            </div>
            
            <Select 
              value={filters.fund_type} 
              onValueChange={(val) => { setFilters(f => ({ ...f, fund_type: val })); setPage(1); }}
            >
              <SelectTrigger className="w-32">
                <SelectValue placeholder="基金类型" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">全部类型</SelectItem>
                {fundTypes.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>

            <Select 
              value={filters.risk_level} 
              onValueChange={(val) => { setFilters(f => ({ ...f, risk_level: val })); setPage(1); }}
            >
              <SelectTrigger className="w-36">
                <SelectValue placeholder="风险等级" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">全部等级</SelectItem>
                <SelectItem value="1">1-低风险</SelectItem>
                <SelectItem value="2">2-中低风险</SelectItem>
                <SelectItem value="3">3-中风险</SelectItem>
                <SelectItem value="4">4-中高风险</SelectItem>
                <SelectItem value="5">5-高风险</SelectItem>
              </SelectContent>
            </Select>

            <Select 
              value={filters.manager_company} 
              onValueChange={(val) => { setFilters(f => ({ ...f, manager_company: val })); setPage(1); }}
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="基金公司" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">全部公司</SelectItem>
                {companies.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* 基金列表 */}
      <Card className="glow-border">
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border bg-secondary/50">
                      <th className="px-4 py-3 text-left">
                        <button onClick={() => handleSort('fund_code')} className="flex items-center gap-1">
                          <span className="text-sm font-medium text-muted-foreground">基金代码</span>
                          {getSortIcon('fund_code')}
                        </button>
                      </th>
                      <th className="px-4 py-3 text-left">
                        <span className="text-sm font-medium text-muted-foreground">基金名称</span>
                      </th>
                      <th className="px-4 py-3 text-left">
                        <button onClick={() => handleSort('fund_type')} className="flex items-center gap-1">
                          <span className="text-sm font-medium text-muted-foreground">类型</span>
                          {getSortIcon('fund_type')}
                        </button>
                      </th>
                      <th className="px-4 py-3 text-left">
                        <span className="text-sm font-medium text-muted-foreground">风险</span>
                      </th>
                      <th className="px-4 py-3 text-left">
                        <span className="text-sm font-medium text-muted-foreground">净值</span>
                      </th>
                      <th className="px-4 py-3 text-left">
                        <button onClick={() => handleSort('daily_return')} className="flex items-center gap-1">
                          <span className="text-sm font-medium text-muted-foreground">日涨跌</span>
                          {getSortIcon('daily_return')}
                        </button>
                      </th>
                      <th className="px-4 py-3 text-left">
                        <span className="text-sm font-medium text-muted-foreground">基金公司</span>
                      </th>
                      <th className="px-4 py-3 text-left">
                        <span className="text-sm font-medium text-muted-foreground">操作</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {funds.map((fund) => (
                      <tr 
                        key={fund.fund_code} 
                        className="border-b border-border table-row-hover"
                      >
                        <td className="px-4 py-3">
                          <code className="text-sm font-mono text-cyan-400">{fund.fund_code}</code>
                        </td>
                        <td className="px-4 py-3">
                          <button 
                            onClick={() => handleFundClick(fund.fund_code)}
                            className="text-sm font-medium text-left hover:text-cyan-400 transition-colors"
                          >
                            {fund.fund_name}
                          </button>
                        </td>
                        <td className="px-4 py-3">{getFundTypeBadge(fund.fund_type)}</td>
                        <td className="px-4 py-3">{getRiskBadge(fund.risk_level)}</td>
                        <td className="px-4 py-3">
                          <span className="font-mono text-sm">
                            {fund.latest_nav ? fund.latest_nav.toFixed(4) : '-'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {fund.latest_return !== undefined && fund.latest_return !== null ? (
                            <span className={cn(
                              "text-sm font-medium",
                              fund.latest_return >= 0 ? "text-emerald-400" : "text-red-400"
                            )}>
                              {fund.latest_return >= 0 ? '+' : ''}{fund.latest_return.toFixed(2)}%
                            </span>
                          ) : '-'}
                        </td>
                        <td className="px-4 py-3 text-sm text-muted-foreground">{fund.manager_company}</td>
                        <td className="px-4 py-3">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleFundClick(fund.fund_code)}
                            className="text-cyan-400 hover:text-cyan-300"
                          >
                            <BarChart3 className="w-4 h-4 mr-1" />
                            分析
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 空状态 */}
              {funds.length === 0 && (
                <div className="py-12 text-center">
                  <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">未找到符合条件的基金</p>
                </div>
              )}

              {/* 分页 */}
              <div className="flex items-center justify-between px-4 py-3 border-t border-border">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>共 {total} 只基金</span>
                  <div className="flex items-center gap-2">
                    <span>每页</span>
                    <Select value={String(pageSize)} onValueChange={(val) => { setPageSize(Number(val)); setPage(1); }}>
                      <SelectTrigger className="w-16 h-8">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="10">10</SelectItem>
                        <SelectItem value="20">20</SelectItem>
                        <SelectItem value="50">50</SelectItem>
                      </SelectContent>
                    </Select>
                    <span>条</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button variant="outline" size="icon" className="w-8 h-8" onClick={() => setPage(1)} disabled={page === 1}>
                    <ChevronsLeft className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="icon" className="w-8 h-8" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="text-sm px-2">{page} / {totalPages || 1}</span>
                  <Button variant="outline" size="icon" className="w-8 h-8" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="icon" className="w-8 h-8" onClick={() => setPage(totalPages)} disabled={page >= totalPages}>
                    <ChevronsRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
