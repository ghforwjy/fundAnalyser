import { useState, useRef, useCallback, useEffect } from 'react';
import { FolderOpen, Package, TrendingUp, Upload, Image as ImageIcon, X, Check, AlertCircle, Loader2, FileImage, Plus, ChevronLeft, ChevronRight, PlusCircle, Edit2, Trash2, MoreVertical, Save } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import PositionManage from './PositionManage';
import TransactionHistory from './TransactionHistory';
import InvestmentAdvice from './InvestmentAdvice';
import { portfolioApi, fundApi, type FundGroup, type FundInfo } from '@/services/api';
import { cn } from '@/lib/utils';

// 将文件转换为Base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64String = reader.result as string;
      // 移除 data:image/jpeg;base64, 前缀
      const base64 = base64String.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
  });
};

// 从图片解析出的原始数据
interface ParsedFundData {
  fundCode: string;
  fundName: string;
  shares: number;
  nav: number;
  amount: number;
  profit?: number;
  status: 'pending' | 'matched' | 'not_found' | 'imported';
  matchedFund?: FundInfo;
}

export default function Portfolio() {
  const [groups, setGroups] = useState<FundGroup[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<FundGroup | undefined>(undefined);
  const [activeTab, setActiveTab] = useState('positions');
  const [refreshKey, setRefreshKey] = useState(0);
  const [loadingGroups, setLoadingGroups] = useState(false);

  // 组合管理弹窗状态
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '' });

  // 图片导入相关状态
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedFundData[]>([]);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [isImporting, setIsImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // 重复基金检测状态
  const [duplicateFunds, setDuplicateFunds] = useState<ParsedFundData[]>([]);
  const [showDuplicateDialog, setShowDuplicateDialog] = useState(false);
  const [existingFundsInGroup, setExistingFundsInGroup] = useState<Set<string>>(new Set());

  const handleImportSuccess = () => {
    setRefreshKey(prev => prev + 1);
    loadGroups();
  };

  // 加载组合列表
  const loadGroups = async () => {
    try {
      setLoadingGroups(true);
      const response = await portfolioApi.getGroups();
      if (response.success) {
        setGroups(response.data);
        // 如果没有选中组合且列表不为空，默认选中第一个
        if (!selectedGroup && response.data.length > 0) {
          setSelectedGroup(response.data[0]);
        }
      }
    } catch (error) {
      toast.error('加载组合失败');
    } finally {
      setLoadingGroups(false);
    }
  };

  useEffect(() => {
    loadGroups();
  }, []);

  // 创建组合
  const handleCreate = async () => {
    if (!formData.name.trim()) {
      toast.error('请输入组合名称');
      return;
    }
    try {
      const response = await portfolioApi.createGroup(formData);
      if (response.success) {
        toast.success('创建成功');
        setIsCreateDialogOpen(false);
        setFormData({ name: '', description: '' });
        loadGroups();
        // 选中新创建的组合
        if (response.data) {
          setSelectedGroup(response.data);
        }
      }
    } catch (error) {
      toast.error('创建失败');
    }
  };

  // 更新组合
  const handleUpdate = async () => {
    if (!selectedGroup || !formData.name.trim()) {
      toast.error('请输入组合名称');
      return;
    }
    try {
      const response = await portfolioApi.updateGroup(selectedGroup.id, formData);
      if (response.success) {
        toast.success('更新成功');
        setIsEditDialogOpen(false);
        loadGroups();
      }
    } catch (error) {
      toast.error('更新失败');
    }
  };

  // 删除组合
  const handleDelete = async () => {
    if (!selectedGroup) return;
    try {
      const response = await portfolioApi.deleteGroup(selectedGroup.id);
      if (response.success) {
        toast.success('删除成功');
        setIsDeleteDialogOpen(false);
        setSelectedGroup(undefined);
        loadGroups();
      }
    } catch (error) {
      toast.error('删除失败');
    }
  };

  // 打开编辑弹窗
  const openEditDialog = () => {
    if (!selectedGroup) {
      toast.error('请先选择一个组合');
      return;
    }
    setFormData({
      name: selectedGroup.name,
      description: selectedGroup.description || '',
    });
    setIsEditDialogOpen(true);
  };

  // 打开删除弹窗
  const openDeleteDialog = () => {
    if (!selectedGroup) {
      toast.error('请先选择一个组合');
      return;
    }
    setIsDeleteDialogOpen(true);
  };

  // 处理文件拖放
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processImage(files[0]);
    }
  }, []);

  // 处理文件选择
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processImage(file);
    }
  };

  // 处理图片 - 调用火山方舟多模态模型
  const processImage = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      toast.error('请选择图片文件');
      return;
    }

    setIsProcessing(true);
    
    try {
      // 将文件转换为Base64
      console.log('[图片导入] 开始转换图片为Base64...');
      const base64 = await fileToBase64(file);
      console.log('[图片导入] Base64转换完成，长度:', base64.length);
      
      // 调用后端API进行图片识别
      console.log('[图片导入] 调用recognizeImage API...');
      const response = await portfolioApi.recognizeImage(base64);
      console.log('[图片导入] API返回:', response);
      
      if (!response.success) {
        console.error('[图片导入] API返回失败:', response.message);
        toast.error(response.message || '图片识别失败');
        setIsProcessing(false);
        return;
      }
      
      console.log('[图片导入] 识别到的基金数量:', response.data?.length);
      console.log('[图片导入] 识别数据:', response.data);
      
      // 转换为ParsedFundData格式
      const parsedData: ParsedFundData[] = response.data.map(item => ({
        fundCode: item.fundCode,
        fundName: item.fundName,
        shares: item.shares,
        nav: item.nav,
        amount: item.amount,
        profit: item.profit || 0,
        status: 'pending',
      }));
      
      console.log('[图片导入] 转换后的数据:', parsedData);
      
      // 匹配基金代码
      console.log('[图片导入] 开始匹配基金代码...');
      const matchedData = await matchFunds(parsedData);
      console.log('[图片导入] 匹配完成，结果:', matchedData);
      
      setParsedData(matchedData);
      // 默认选中所有匹配成功的
      const matchedCodes = new Set(
        matchedData.filter(d => d.status === 'matched').map(d => d.fundCode)
      );
      setSelectedItems(matchedCodes);
      
      toast.success(`成功解析 ${matchedData.length} 条基金记录`);
    } catch (error) {
      console.error('[图片导入] 处理失败:', error);
      toast.error('图片解析失败: ' + (error as Error).message);
    } finally {
      setIsProcessing(false);
    }
  };

  // 匹配基金代码到数据库
  const matchFunds = async (data: ParsedFundData[]): Promise<ParsedFundData[]> => {
    console.log('[matchFunds] 开始匹配，数据条数:', data.length);
    const results: ParsedFundData[] = [];
    
    for (const item of data) {
      console.log(`[matchFunds] 查询基金: ${item.fundCode}`);
      try {
        // 查询基金信息
        const response = await fundApi.getDetail(item.fundCode);
        console.log(`[matchFunds] ${item.fundCode} 查询结果:`, response);
        if (response.success && response.data) {
          console.log(`[matchFunds] ${item.fundCode} 匹配成功`);
          results.push({
            ...item,
            status: 'matched',
            matchedFund: response.data,
          });
        } else {
          console.log(`[matchFunds] ${item.fundCode} 未找到，success=${response.success}, data=${response.data}`);
          // 数据库中没有该基金，但仍然显示，只是标记为未匹配
          results.push({
            ...item,
            status: 'not_found',
          });
        }
      } catch (error) {
        console.error(`[matchFunds] ${item.fundCode} 查询失败:`, error);
        // 查询失败，仍然显示该基金
        results.push({
          ...item,
          status: 'not_found',
        });
      }
    }
    
    console.log('[matchFunds] 匹配完成，结果数量:', results.length);
    return results;
  };

  // 检查分组中是否已存在基金
  const checkExistingFunds = async (fundCodes: string[]) => {
    if (!selectedGroup?.id) return new Set<string>();
    
    const existing = new Set<string>();
    try {
      const response = await portfolioApi.getGroupFunds(selectedGroup.id);
      if (response.success && response.data) {
        for (const code of fundCodes) {
          const fundExists = response.data.some((f: any) => f.fund_code === code);
          if (fundExists) {
            existing.add(code);
          }
        }
      }
    } catch (error) {
      console.error('检查现有基金失败:', error);
    }
    return existing;
  };

  // 处理重复基金选择
  const handleDuplicateAction = async (action: 'skip' | 'overwrite') => {
    setShowDuplicateDialog(false);
    await executeImport(action);
  };
  
  // 执行导入（分离出来以便复用）
  const executeImport = async (action: 'skip' | 'overwrite' | null = null) => {
    if (selectedItems.size === 0) {
      toast.error('请至少选择一条记录');
      return;
    }

    const selectedFunds = parsedData.filter(d => selectedItems.has(d.fundCode));
    
    // 如果没有传入 action，检查是否有重复基金
    if (selectedGroup?.id && action === null) {
      const fundCodes = selectedFunds.map(f => f.fundCode);
      const existing = await checkExistingFunds(fundCodes);
      
      if (existing.size > 0) {
        // 有重复基金，显示选择对话框
        const duplicates = selectedFunds.filter(f => existing.has(f.fundCode));
        setDuplicateFunds(duplicates);
        setExistingFundsInGroup(existing);
        setShowDuplicateDialog(true);
        return;
      }
    }

    setIsImporting(true);
    
    let successCount = 0;
    let skipCount = 0;
    let overwriteCount = 0;

    for (const fund of selectedFunds) {
      try {
        const isExisting = existingFundsInGroup.has(fund.fundCode);
        
        if (isExisting && action === 'skip') {
          skipCount++;
          continue;
        }
        
        if (isExisting && action === 'overwrite') {
          // 覆盖：先删除旧持仓
          try {
            await portfolioApi.removeFundFromGroup(selectedGroup!.id, fund.fundCode);
          } catch (error) {
            console.error(`删除旧持仓失败 ${fund.fundCode}:`, error);
          }
          overwriteCount++;
        }

        // 添加到分组
        if (selectedGroup?.id) {
          await portfolioApi.addFundToGroup(selectedGroup.id, {
            fund_code: fund.fundCode,
            fund_name: fund.matchedFund?.fund_name || fund.fundName,
            shares: fund.shares,
            buy_nav: fund.nav,
            amount: fund.amount,
          });
        }

        successCount++;
      } catch (error) {
        console.error(`导入基金失败 ${fund.fundCode}:`, error);
      }
    }

    setIsImporting(false);
    
    // 重置状态
    setExistingFundsInGroup(new Set());
    
    if (successCount > 0 || overwriteCount > 0) {
      let message = `成功导入 ${successCount} 只基金`;
      if (overwriteCount > 0) {
        message += `，覆盖 ${overwriteCount} 只`;
      }
      if (skipCount > 0) {
        message += `，跳过 ${skipCount} 只`;
      }
      toast.success(message);
      
      handleImportSuccess();
      setIsImportDialogOpen(false);
      setParsedData([]);
      setSelectedItems(new Set());
    } else if (skipCount > 0) {
      toast.info(`已跳过 ${skipCount} 只重复基金`);
    }
  };

  // 导入选中的基金（入口函数）
  const handleImport = async () => {
    await executeImport(null);
  };

  // 切换选中状态
  const toggleSelection = (fundCode: string) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(fundCode)) {
      newSelected.delete(fundCode);
    } else {
      newSelected.add(fundCode);
    }
    setSelectedItems(newSelected);
  };

  // 全选/取消全选
  const toggleAll = () => {
    const matchedCodes = parsedData
      .filter(d => d.status === 'matched')
      .map(d => d.fundCode);
    
    if (selectedItems.size === matchedCodes.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(matchedCodes));
    }
  };

  const formatNumber = (num: number, decimals: number = 2) => {
    return num.toFixed(decimals);
  };

  const formatCurrency = (num: number) => {
    return `¥${num.toFixed(2)}`;
  };

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
      {/* 页面标题栏 - 紧凑布局 */}
      <div className="flex items-center justify-between flex-shrink-0 mb-4">
        <div className="flex items-center gap-4">
          {/* 标题 */}
          <div>
            <h1 className="text-xl font-bold gradient-text">投资组合</h1>
            <p className="text-xs text-muted-foreground">管理基金分组、持仓和交易记录</p>
          </div>
          
          {/* 组合选择 */}
          <div className="w-56">
            <Select
              value={selectedGroup?.id?.toString()}
              onValueChange={(value) => {
                const group = groups.find(g => g.id.toString() === value);
                if (group) setSelectedGroup(group);
              }}
            >
              <SelectTrigger className="h-9">
                <SelectValue placeholder="选择组合" />
              </SelectTrigger>
              <SelectContent>
                {groups.map((group) => (
                  <SelectItem key={group.id} value={group.id.toString()}>
                    <div className="flex items-center gap-2">
                      <span>{group.name}</span>
                      <span className="text-xs text-muted-foreground">
                        ({group.fund_count || 0}只)
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 组合管理 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                新建组合
              </DropdownMenuItem>
              <DropdownMenuItem onClick={openEditDialog} disabled={!selectedGroup}>
                <Edit2 className="w-4 h-4 mr-2" />
                编辑组合
              </DropdownMenuItem>
              <DropdownMenuItem 
                onClick={openDeleteDialog} 
                disabled={!selectedGroup}
                className="text-red-500"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                删除组合
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Tabs */}
          <TabsList className="h-9">
            <TabsTrigger value="positions" className="flex items-center gap-1.5 text-xs px-3">
              <Package className="w-3.5 h-3.5" />
              持仓管理
            </TabsTrigger>
            <TabsTrigger value="transactions" className="flex items-center gap-1.5 text-xs px-3">
              <TrendingUp className="w-3.5 h-3.5" />
              交易记录
            </TabsTrigger>
          </TabsList>
        </div>

        {/* 操作建议 */}
        <InvestmentAdvice
          groupId={selectedGroup?.id}
          groupName={selectedGroup?.name}
          onRefresh={() => setRefreshKey(prev => prev + 1)}
        />
      </div>

      {/* 持仓管理 - 占据剩余空间 */}
      <div className="flex-1 min-h-0 overflow-hidden">
        <TabsContent value="positions" className="mt-0 h-full">
          <PositionManage 
            key={refreshKey}
            groupId={selectedGroup?.id} 
          />
        </TabsContent>
        
        <TabsContent value="transactions" className="mt-0 h-full">
          <TransactionHistory 
            key={refreshKey}
            groupId={selectedGroup?.id} 
          />
        </TabsContent>
      </div>

      {/* 图片导入对话框 */}
      <Dialog open={isImportDialogOpen} onOpenChange={setIsImportDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ImageIcon className="w-5 h-5 text-cyan-400" />
              从图片导入基金
              {selectedGroup && (
                <Badge variant="secondary" className="ml-2">
                  导入到: {selectedGroup.name}
                </Badge>
              )}
            </DialogTitle>
          </DialogHeader>

          <div className="flex-1 overflow-auto py-4">
            {parsedData.length === 0 ? (
              // 上传区域
              <div
                className={cn(
                  "border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer",
                  isDragging 
                    ? "border-cyan-500 bg-cyan-500/10" 
                    : "border-border hover:border-cyan-500/50"
                )}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileSelect}
                />
                
                {isProcessing ? (
                  <div className="space-y-4">
                    <Loader2 className="w-12 h-12 animate-spin text-cyan-500 mx-auto" />
                    <p className="text-muted-foreground">正在识别图片内容...</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="w-16 h-16 rounded-full bg-cyan-500/10 flex items-center justify-center mx-auto">
                      <Upload className="w-8 h-8 text-cyan-400" />
                    </div>
                    <div>
                      <p className="font-medium">点击或拖拽上传图片</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        支持基金持仓截图，系统将自动识别基金代码和份额
                      </p>
                    </div>
                    <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                      <FileImage className="w-4 h-4" />
                      <span>支持 JPG、PNG 格式</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              // 解析结果表格
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">
                      共 {parsedData.length} 条
                    </Badge>
                    <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400">
                      已匹配 {parsedData.filter(d => d.status === 'matched').length} 条
                    </Badge>
                    {parsedData.filter(d => d.status === 'not_found').length > 0 && (
                      <Badge variant="secondary" className="bg-red-500/20 text-red-400">
                        未找到 {parsedData.filter(d => d.status === 'not_found').length} 条
                      </Badge>
                    )}
                  </div>
                  <Button variant="ghost" size="sm" onClick={toggleAll}>
                    {selectedItems.size === parsedData.filter(d => d.status === 'matched').length 
                      ? '取消全选' 
                      : '全选'}
                  </Button>
                </div>

                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-12">选择</TableHead>
                        <TableHead>基金代码</TableHead>
                        <TableHead>基金名称</TableHead>
                        <TableHead className="text-right">持有份额</TableHead>
                        <TableHead className="text-right">净值</TableHead>
                        <TableHead className="text-right">市值</TableHead>
                        <TableHead>状态</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {parsedData.map((item) => (
                        <TableRow 
                          key={item.fundCode}
                          className={cn(
                            item.status === 'not_found' && "opacity-50"
                          )}
                        >
                          <TableCell>
                            {item.status === 'matched' && (
                              <button
                                className={cn(
                                  "w-5 h-5 rounded border flex items-center justify-center transition-colors",
                                  selectedItems.has(item.fundCode)
                                    ? "bg-cyan-500 border-cyan-500"
                                    : "border-border hover:border-cyan-500"
                                )}
                                onClick={() => toggleSelection(item.fundCode)}
                              >
                                {selectedItems.has(item.fundCode) && (
                                  <Check className="w-3 h-3 text-white" />
                                )}
                              </button>
                            )}
                          </TableCell>
                          <TableCell>
                            <code className="font-mono text-sm">{item.fundCode}</code>
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="font-medium">
                                {item.matchedFund?.fund_name || item.fundName}
                              </p>
                              {item.matchedFund && (
                                <p className="text-xs text-muted-foreground">
                                  {item.matchedFund.fund_type} · {item.matchedFund.company_name}
                                </p>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-right font-mono">
                            {formatNumber(item.shares, 2)}
                          </TableCell>
                          <TableCell className="text-right font-mono">
                            {formatNumber(item.nav, 4)}
                          </TableCell>
                          <TableCell className="text-right font-mono">
                            {formatCurrency(item.amount)}
                          </TableCell>
                          <TableCell>
                            {item.status === 'matched' ? (
                              <Badge variant="secondary" className="bg-emerald-500/20 text-emerald-400">
                                已匹配
                              </Badge>
                            ) : item.status === 'not_found' ? (
                              <Badge variant="secondary" className="bg-red-500/20 text-red-400">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                未找到
                              </Badge>
                            ) : (
                              <Badge variant="secondary">待处理</Badge>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                <div className="text-sm text-muted-foreground">
                  <p>提示：系统将自动匹配基金代码到数据库中的基金信息</p>
                  <p>未找到的基金可能是数据库中暂无该基金的净值数据</p>
                </div>
              </div>
            )}
          </div>

          <DialogFooter className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              {parsedData.length > 0 && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setParsedData([]);
                    setSelectedItems(new Set());
                  }}
                >
                  <X className="w-4 h-4 mr-1" />
                  重新上传
                </Button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => setIsImportDialogOpen(false)}>
                取消
              </Button>
              {parsedData.length > 0 && (
                <Button
                  onClick={handleImport}
                  disabled={selectedItems.size === 0 || isImporting}
                  className="bg-cyan-500 hover:bg-cyan-600"
                >
                  {isImporting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                      导入中...
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4 mr-1" />
                      导入选中 ({selectedItems.size})
                    </>
                  )}
                </Button>
              )}
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 重复基金处理对话框 */}
      <Dialog open={showDuplicateDialog} onOpenChange={setShowDuplicateDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-amber-400" />
              发现重复基金
            </DialogTitle>
          </DialogHeader>
          
          <div className="py-4">
            <p className="text-muted-foreground mb-4">
              以下 {duplicateFunds.length} 只基金已在当前分组中，请选择处理方式：
            </p>
            
            <div className="border rounded-lg overflow-hidden mb-4 max-h-64 overflow-y-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/50 sticky top-0">
                  <tr>
                    <th className="px-4 py-2 text-left font-medium">基金代码</th>
                    <th className="px-4 py-2 text-left font-medium">基金名称</th>
                    <th className="px-4 py-2 text-right font-medium">份额</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {duplicateFunds.map((fund) => (
                    <tr key={fund.fundCode} className="hover:bg-muted/30">
                      <td className="px-4 py-2">
                        <code className="font-mono text-sm">{fund.fundCode}</code>
                      </td>
                      <td className="px-4 py-2">{fund.fundName}</td>
                      <td className="px-4 py-2 text-right font-mono">
                        {formatNumber(fund.shares, 2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>• <strong>跳过</strong>：保留现有数据，不导入这些基金</p>
              <p>• <strong>覆盖</strong>：删除现有数据，使用新数据替换</p>
            </div>
          </div>

          <DialogFooter className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setShowDuplicateDialog(false);
              }}
            >
              取消导入
            </Button>
            <Button
              variant="outline"
              onClick={() => handleDuplicateAction('skip')}
              className="border-emerald-500/50 hover:bg-emerald-500/10"
            >
              跳过重复
            </Button>
            <Button
              onClick={() => handleDuplicateAction('overwrite')}
              className="bg-amber-500 hover:bg-amber-600"
            >
              覆盖导入
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 创建组合对话框 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新建组合</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">组合名称</label>
              <Input
                placeholder="请输入组合名称"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">描述（可选）</label>
              <Textarea
                placeholder="请输入组合描述"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
              <X className="w-4 h-4 mr-1" />
              取消
            </Button>
            <Button onClick={handleCreate} className="bg-cyan-500 hover:bg-cyan-600">
              <Save className="w-4 h-4 mr-1" />
              创建
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 编辑组合对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑组合</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">组合名称</label>
              <Input
                placeholder="请输入组合名称"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">描述（可选）</label>
              <Textarea
                placeholder="请输入组合描述"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              <X className="w-4 h-4 mr-1" />
              取消
            </Button>
            <Button onClick={handleUpdate} className="bg-cyan-500 hover:bg-cyan-600">
              <Save className="w-4 h-4 mr-1" />
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除组合确认对话框 */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">
              确定要删除组合 <span className="font-medium text-foreground">"{selectedGroup?.name}"</span> 吗？
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              组合中的基金将被移除，此操作不可恢复。
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              <Trash2 className="w-4 h-4 mr-1" />
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Tabs>
  );
}
