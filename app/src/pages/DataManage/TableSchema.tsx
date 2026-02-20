import { useState, useEffect } from 'react';
import { 
  Table2, 
  Database, 
  Key, 
  Link2, 
  FileText, 
  Calendar,
  Hash,
  Type,
  CheckCircle2,
  XCircle,
  Download,
  Eye,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { dbApi, type TableInfo, type TableDetail } from '@/services/api';
import { getFieldLabel, getTableLabel } from '@/config/fieldLabels';

export default function TableSchemaPage() {
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableDetail, setTableDetail] = useState<TableDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [ddlDialogOpen, setDdlDialogOpen] = useState(false);

  // 加载表列表
  useEffect(() => {
    loadTables();
  }, []);

  // 加载表详情
  useEffect(() => {
    if (selectedTable) {
      loadTableDetail(selectedTable);
    }
  }, [selectedTable]);

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

  const loadTableDetail = async (tableName: string) => {
    try {
      setDetailLoading(true);
      const response = await dbApi.getTableInfo(tableName);
      if (response.success) {
        setTableDetail(response.data);
      }
    } catch (error) {
      toast.error('加载表详情失败');
      console.error(error);
    } finally {
      setDetailLoading(false);
    }
  };

  const filteredColumns = tableDetail?.columns.filter(col =>
    col.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (col.type && col.type.toLowerCase().includes(searchTerm.toLowerCase()))
  ) || [];

  const generateDDL = (detail: TableDetail): string => {
    const columns = detail.columns.map(col => {
      let def = `  ${col.name} ${col.type}`;
      if (col.notnull) def += ' NOT NULL';
      if (col.dflt_value) def += ` DEFAULT ${col.dflt_value}`;
      if (col.pk) def += ' PRIMARY KEY';
      return def;
    }).join(',\n');

    const indexStatements = detail.indexes.map(idx => {
      return `CREATE ${idx.unique ? 'UNIQUE ' : ''}INDEX ${idx.name} ON ${detail.table_name} (...);`;
    }).join('\n');

    let ddl = `-- 表结构: ${detail.table_name}\n`;
    ddl += `-- 记录数: ${detail.record_count.toLocaleString()}\n\n`;
    ddl += `CREATE TABLE ${detail.table_name} (\n${columns}\n);\n`;
    
    if (indexStatements) {
      ddl += `\n-- 索引\n${indexStatements}`;
    }
    
    return ddl;
  };

  const getDataTypeIcon = (dataType: string) => {
    if (!dataType) return <Database className="w-4 h-4 text-muted-foreground" />;
    if (dataType.includes('VARCHAR') || dataType.includes('TEXT')) {
      return <Type className="w-4 h-4 text-cyan-400" />;
    } else if (dataType.includes('INT') || dataType.includes('DECIMAL') || dataType.includes('FLOAT')) {
      return <Hash className="w-4 h-4 text-purple-400" />;
    } else if (dataType.includes('DATE') || dataType.includes('TIME')) {
      return <Calendar className="w-4 h-4 text-amber-400" />;
    }
    return <Database className="w-4 h-4 text-muted-foreground" />;
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
    label: `${getTableLabel(t.table_name)} (${t.table_name})`,
  }));

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold gradient-text">数据库表结构</h1>
          <p className="text-muted-foreground mt-1">查看数据库表结构和字段说明</p>
        </div>
        <Button onClick={loadTables} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          刷新
        </Button>
      </div>

      {/* 表选择 */}
      <Card className="glow-border">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-cyan-400" />
              <Label className="text-sm font-medium">选择数据表</Label>
            </div>
            <Select value={selectedTable} onValueChange={setSelectedTable}>
              <SelectTrigger className="w-80">
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
          </div>
        </CardContent>
      </Card>

      {/* 表信息概览 */}
      {tableDetail && (
        <Card className="glow-border">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Table2 className="w-6 h-6 text-cyan-400" />
                <div>
                  <CardTitle className="text-xl">{getTableLabel(tableDetail.table_name)}</CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {tableDetail.table_name} · {tables.find(t => t.table_name === tableDetail.table_name)?.index_count || 0} 个索引
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => setDdlDialogOpen(true)}>
                  <FileText className="w-4 h-4 mr-1" />
                  查看DDL
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-8 text-sm">
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">字段数:</span>
                <span className="font-medium">{tableDetail.columns.length}</span>
              </div>
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">记录数:</span>
                <span className="font-medium">{tableDetail.record_count.toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-2">
                <Key className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">主键:</span>
                <span className="font-medium">
                  {tableDetail.columns.filter(c => c.pk).map(c => c.name).join(', ') || '无'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 字段搜索 */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Input
            placeholder="搜索字段名或类型..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* 字段列表 */}
      <Card className="glow-border">
        <CardContent className="p-0">
          {detailLoading ? (
            <div className="flex items-center justify-center h-32">
              <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
            </div>
          ) : (
            <div className="overflow-auto max-h-[500px]">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-secondary/50">
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">字段名</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">中文名</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">数据类型</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">可空</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">约束</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">默认值</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredColumns.map((col, index) => (
                    <tr
                      key={col.name}
                      className={cn(
                        "border-b border-border table-row-hover",
                        index % 2 === 1 && "bg-secondary/20"
                      )}
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {getDataTypeIcon(col.type)}
                          <code className="text-sm font-mono text-cyan-400">{col.name}</code>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-sm text-foreground">
                          {getFieldLabel(col.name, tableDetail?.table_name)}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="outline" className="font-mono text-xs">
                          {col.type}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        {!col.notnull ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-400" />
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          {col.pk > 0 && (
                            <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 text-xs">
                              <Key className="w-3 h-3 mr-1" />
                              PK
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {col.dflt_value || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* DDL对话框 */}
      <Dialog open={ddlDialogOpen} onOpenChange={setDdlDialogOpen}>
        <DialogContent className="sm:max-w-[700px]">
          <DialogHeader>
            <DialogTitle>DDL - {tableDetail?.table_name}</DialogTitle>
            <DialogDescription>
              表的创建语句（SQL）
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            <pre className="p-4 rounded-lg bg-secondary/80 overflow-x-auto text-sm font-mono">
              <code>{tableDetail && generateDDL(tableDetail)}</code>
            </pre>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setDdlDialogOpen(false)}>
              关闭
            </Button>
            <Button 
              className="bg-cyan-500 hover:bg-cyan-600"
              onClick={() => {
                if (tableDetail) {
                  navigator.clipboard.writeText(generateDDL(tableDetail));
                  toast.success('已复制到剪贴板');
                }
              }}
            >
              <Download className="w-4 h-4 mr-1" />
              复制到剪贴板
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
