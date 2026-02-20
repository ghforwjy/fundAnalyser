import { useState, useEffect } from 'react';
import { 
  Database, 
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
  RefreshCw,
  X,
  Loader2
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { dbApi, type TableInfo } from '@/services/api';
import { getFieldLabel, getTableLabel } from '@/config/fieldLabels';

interface SortCondition {
  field: string;
  direction: 'asc' | 'desc';
}

export default function TableDataPage() {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableData, setTableData] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [sort, setSort] = useState<SortCondition | null>(null);

  useEffect(() => {
    loadTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      loadTableData();
    }
  }, [selectedTable, page, pageSize, searchTerm, sort]);

  const loadTables = async () => {
    try {
      setLoading(true);
      const response = await dbApi.getTables();
      if (response.success) {
        setTables(response.data);
        if (response.data.length > 0) {
          setSelectedTable(response.data[0].table_name);
        }
      }
    } catch (error) {
      toast.error('加载表列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadTableData = async () => {
    if (!selectedTable) return;
    
    try {
      setDataLoading(true);
      const response = await dbApi.getTableData({
        tableName: selectedTable,
        page,
        pageSize,
        search: searchTerm || undefined,
        sortField: sort?.field,
        sortDir: sort?.direction,
      });
      if (response.success) {
        setTableData(response.data.data);
        setTotal(response.data.total);
        setTotalPages(response.data.total_pages);
        
        if (response.data.data.length > 0) {
          setColumns(Object.keys(response.data.data[0]));
        } else {
          setColumns([]);
        }
      }
    } catch (error) {
      toast.error('加载表数据失败');
      console.error(error);
    } finally {
      setDataLoading(false);
    }
  };

  const handleSort = (field: string) => {
    setPage(1);
    if (sort?.field === field) {
      if (sort.direction === 'asc') {
        setSort({ field, direction: 'desc' });
      } else {
        setSort(null);
      }
    } else {
      setSort({ field, direction: 'asc' });
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadTableData();
  };

  const getSortIcon = (field: string) => {
    if (sort?.field !== field) {
      return <ArrowUpDown className="w-3 h-3 text-muted-foreground" />;
    }
    return sort.direction === 'asc' 
      ? <ArrowUp className="w-3 h-3 text-cyan-400" />
      : <ArrowDown className="w-3 h-3 text-cyan-400" />;
  };

  const formatValue = (value: any, column: string) => {
    if (value === null || value === undefined) return '-';
    
    if (column.includes('return') && typeof value === 'number') {
      const color = value >= 0 ? 'text-up' : 'text-down';
      const sign = value >= 0 ? '+' : '';
      return <span className={color}>{sign}{value.toFixed(2)}%</span>;
    }
    
    if (column.includes('nav') || column.includes('ratio') || column.includes('rate')) {
      if (typeof value === 'number') {
        return <span className="font-mono">{value.toFixed(4)}</span>;
      }
    }
    
    if (column === 'fund_type') {
      const typeColors: Record<string, string> = {
        '股票型': 'tag-stock',
        '债券型': 'tag-bond',
        '混合型': 'tag-mixed',
        '货币型': 'tag-money',
        '指数型': 'tag-index',
      };
      return (
        <Badge className={cn('text-xs', typeColors[value] || '')}>
          {value}
        </Badge>
      );
    }
    
    if (column === 'status' || column === 'subscribe_status' || column === 'redeem_status') {
      const isNormal = value === '正常' || value === '开放' || value === '开放申购' || value === '开放赎回';
      return (
        <Badge className={isNormal 
          ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' 
          : 'bg-red-500/20 text-red-400 border-red-500/30'
        }>
          {value}
        </Badge>
      );
    }
    
    if (typeof value === 'string' && value.length > 50) {
      return value.substring(0, 50) + '...';
    }
    
    return String(value);
  };

  const handleExport = () => {
    if (!tableData.length) return;
    
    const csvContent = [
      columns.join(','),
      ...tableData.map(row => columns.map(col => {
        const val = row[col];
        if (val === null || val === undefined) return '';
        const str = String(val);
        if (str.includes(',') || str.includes('"')) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      }).join(','))
    ].join('\n');
    
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${selectedTable}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    
    toast.success('数据已导出');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
      </div>
    );
  }

  const tableOptions = tables.map(t => ({
    value: t.table_name,
    label: `${getTableLabel(t.table_name)} (${t.record_count || 0}条)`,
  }));

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">表数据浏览</h1>
          <p className="text-muted-foreground mt-1">查看和管理数据库表中的数据</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="w-4 h-4 mr-1" />
            导出
          </Button>
          <Button variant="outline" size="sm" onClick={loadTableData}>
            <RefreshCw className="w-4 h-4 mr-1" />
            刷新
          </Button>
        </div>
      </div>

      {/* 表选择和搜索 */}
      <Card className="glow-border">
        <CardContent className="p-4 space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-cyan-400" />
              <span className="text-sm font-medium">选择数据表</span>
            </div>
            <Select value={selectedTable} onValueChange={(val) => { setSelectedTable(val); setPage(1); setSearchTerm(''); setSort(null); }}>
              <SelectTrigger className="w-72">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {tableOptions.map(option => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="flex-1 max-w-md flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="搜索数据..."
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
          </div>
        </CardContent>
      </Card>

      {/* 数据表格 */}
      <Card className="glow-border">
        <CardContent className="p-0">
          {dataLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
            </div>
          ) : (
            <>
              <div className="overflow-auto max-h-[500px]">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border bg-secondary/50">
                      {columns.map(column => (
                        <th key={column} className="px-4 py-3 text-left">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium text-muted-foreground">
                              {getFieldLabel(column, selectedTable)}
                            </span>
                            <button
                              onClick={() => handleSort(column)}
                              className="p-1 hover:bg-secondary rounded"
                            >
                              {getSortIcon(column)}
                            </button>
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.map((row, index) => (
                      <tr 
                        key={index} 
                        className={cn(
                          "border-b border-border table-row-hover",
                          index % 2 === 1 && "bg-secondary/20"
                        )}
                      >
                        {columns.map(column => (
                          <td key={column} className="px-4 py-3 text-sm">
                            {formatValue(row[column], column)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 空状态 */}
              {tableData.length === 0 && (
                <div className="py-12 text-center">
                  <Database className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">暂无数据</p>
                </div>
              )}

              {/* 分页 */}
              <div className="flex items-center justify-between px-4 py-3 border-t border-border">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>共 {total} 条记录</span>
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
                        <SelectItem value="100">100</SelectItem>
                      </SelectContent>
                    </Select>
                    <span>条</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="icon"
                    className="w-8 h-8"
                    onClick={() => setPage(1)}
                    disabled={page === 1}
                  >
                    <ChevronsLeft className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className="w-8 h-8"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  
                  <span className="text-sm px-2">
                    {page} / {totalPages || 1}
                  </span>
                  
                  <Button
                    variant="outline"
                    size="icon"
                    className="w-8 h-8"
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                  >
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className="w-8 h-8"
                    onClick={() => setPage(totalPages)}
                    disabled={page >= totalPages}
                  >
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
