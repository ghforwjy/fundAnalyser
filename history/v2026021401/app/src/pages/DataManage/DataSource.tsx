import { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  CheckCircle2, 
  XCircle, 
  RefreshCw, 
  Star,
  Server,
  Key,
  Clock,
  Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { cn } from '@/lib/utils';
import { dataSourceApi, type DataSource } from '@/services/api';

export default function DataSourcePage() {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [editingSource, setEditingSource] = useState<DataSource | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<Partial<DataSource>>({});
  const [tokenInput, setTokenInput] = useState('');

  // 加载数据源列表
  useEffect(() => {
    loadDataSources();
  }, []);

  const loadDataSources = async () => {
    try {
      setLoading(true);
      const response = await dataSourceApi.getAll();
      if (response.success) {
        setDataSources(response.data);
      }
    } catch (error) {
      toast.error('加载数据源失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestConnection = async (source: DataSource) => {
    setTestingId(source.id);
    try {
      const result = await dataSourceApi.test(source.source_name);
      if (result.success) {
        toast.success(`${source.source_name} 连接成功`, {
          description: result.message,
        });
        // 刷新列表以更新状态
        loadDataSources();
      } else {
        toast.error(`${source.source_name} 连接失败`, {
          description: result.message,
        });
      }
    } catch (error) {
      toast.error('测试连接出错', {
        description: error instanceof Error ? error.message : '未知错误',
      });
    } finally {
      setTestingId(null);
    }
  };

  const handleEdit = (source: DataSource) => {
    setEditingSource(source);
    setFormData({ ...source });
    setTokenInput(source.api_key || '');
    setIsEditDialogOpen(true);
  };

  const handleSave = async () => {
    if (!editingSource) return;

    try {
      // 如果有token输入，更新token
      if (tokenInput && tokenInput !== editingSource.api_key) {
        await dataSourceApi.updateConfig(editingSource.source_name, tokenInput);
        toast.success('配置已保存');
        loadDataSources();
      }
      setIsEditDialogOpen(false);
    } catch (error) {
      toast.error('保存配置失败');
      console.error(error);
    }
  };

  const handleDelete = (id: number) => {
    setDeletingId(id);
    setIsDeleteDialogOpen(true);
  };

  const confirmDelete = () => {
    // 实际项目中调用删除API
    toast.info('删除功能暂不可用');
    setIsDeleteDialogOpen(false);
    setDeletingId(null);
  };

  const handleSetDefault = (id: number) => {
    // 实际项目中调用设置默认API
    toast.info('设置默认功能暂不可用');
  };

  const getStatusBadge = (source: DataSource) => {
    if (!source.is_active) {
      return (
        <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">
          已禁用
        </Badge>
      );
    }
    
    if (source.is_connected) {
      return (
        <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
          <CheckCircle2 className="w-3 h-3 mr-1" />
          正常
        </Badge>
      );
    }
    
    if (source.last_test_result === 'failed') {
      return (
        <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
          <XCircle className="w-3 h-3 mr-1" />
          异常
        </Badge>
      );
    }
    
    return (
      <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
        未测试
      </Badge>
    );
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'akshare':
        return 'AKShare';
      case 'tushare':
        return 'Tushare Pro';
      case 'custom':
        return '自定义';
      default:
        return type;
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '从未';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN');
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
          <h1 className="text-2xl font-bold gradient-text">数据源配置</h1>
          <p className="text-muted-foreground mt-1">管理基金数据的数据源连接和参数</p>
        </div>
        <Button onClick={loadDataSources} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          刷新
        </Button>
      </div>

      {/* 数据源列表 */}
      <div className="grid gap-4">
        {dataSources.map((source) => (
          <Card key={source.id} className={cn(
            "glow-border card-hover",
            source.source_name === 'akshare' && "border-cyan-500/50"
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
                        {source.source_name === 'akshare' && (
                          <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                            <Star className="w-3 h-3 mr-1 fill-current" />
                            默认
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        {getStatusBadge(source)}
                        <span className="text-sm text-muted-foreground">
                          {getTypeLabel(source.source_type)}
                        </span>
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground mt-3">
                    {source.description || '暂无描述'}
                  </p>

                  <div className="flex items-center gap-6 mt-4 text-sm">
                    {source.api_key && (
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Key className="w-4 h-4" />
                        <span>Token: {source.api_key.slice(-8)}</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>最后测试: {formatDate(source.last_test_time)}</span>
                    </div>
                    {source.rate_limit && (
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <RefreshCw className="w-4 h-4" />
                        <span>限流: {source.rate_limit}/分钟</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleTestConnection(source)}
                    disabled={testingId === source.id}
                  >
                    {testingId === source.id ? (
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4 mr-1" />
                    )}
                    测试连接
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleEdit(source)}
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 编辑对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>编辑数据源</DialogTitle>
            <DialogDescription>
              配置数据源的连接参数和认证信息
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>数据源名称</Label>
              <Input
                value={editingSource?.source_name || ''}
                disabled
              />
            </div>

            <div className="space-y-2">
              <Label>数据源类型</Label>
              <Input
                value={getTypeLabel(editingSource?.source_type || '')}
                disabled
              />
            </div>

            {editingSource?.source_type === 'tushare' && (
              <div className="space-y-2">
                <Label>Token</Label>
                <Input
                  type="password"
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  placeholder="输入您的 Tushare Pro Token"
                />
                <p className="text-xs text-muted-foreground">
                  您的Token将被安全存储，仅用于访问Tushare Pro API
                </p>
              </div>
            )}

            <div className="space-y-2">
              <Label>API地址</Label>
              <Input
                value={editingSource?.base_url || ''}
                disabled
              />
            </div>

            <div className="flex items-center justify-between">
              <Label>启用数据源</Label>
              <Switch
                checked={editingSource?.is_active || false}
                disabled
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSave} className="bg-cyan-500 hover:bg-cyan-600">
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除确认对话框 */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              删除后将无法恢复该数据源的配置，是否继续？
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-red-500 hover:bg-red-600">
              删除
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
