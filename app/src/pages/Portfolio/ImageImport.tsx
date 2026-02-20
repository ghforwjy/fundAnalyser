import { useState, useRef, useCallback } from 'react';
import { 
  Upload, 
  Image as ImageIcon, 
  X, 
  Check, 
  AlertCircle,
  Loader2,
  FileImage,
  Camera,
  Plus
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
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
import { portfolioApi, fundApi, type FundInfo } from '@/services/api';
import { cn } from '@/lib/utils';

// 从图片解析出的原始数据
interface ParsedFundData {
  fundCode: string;
  fundName: string;
  shares: number;
  nav: number;
  amount: number;
  status: 'pending' | 'matched' | 'not_found' | 'imported';
  matchedFund?: FundInfo;
}

interface ImageImportProps {
  groupId?: number;
  onImportSuccess?: () => void;
}

export default function ImageImport({ groupId, onImportSuccess }: ImageImportProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedFundData[]>([]);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [isImporting, setIsImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  // 处理图片 - 模拟OCR解析
  const processImage = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      toast.error('请选择图片文件');
      return;
    }

    setIsProcessing(true);
    
    try {
      // 这里模拟OCR解析结果
      // 实际项目中应该调用OCR API（如百度OCR、腾讯OCR等）
      const mockParsedData = await simulateOCRParsing(file);
      
      // 匹配基金代码
      const matchedData = await matchFunds(mockParsedData);
      
      setParsedData(matchedData);
      // 默认选中所有匹配成功的
      const matchedCodes = new Set(
        matchedData.filter(d => d.status === 'matched').map(d => d.fundCode)
      );
      setSelectedItems(matchedCodes);
      
      toast.success(`成功解析 ${matchedData.length} 条基金记录`);
    } catch (error) {
      toast.error('图片解析失败');
    } finally {
      setIsProcessing(false);
    }
  };

  // 模拟OCR解析（实际项目中替换为真实OCR API）
  const simulateOCRParsing = async (file: File): Promise<ParsedFundData[]> => {
    // 这里模拟从图片中解析出的数据
    // 实际应该调用OCR服务
    return new Promise((resolve) => {
      setTimeout(() => {
        // 模拟解析结果 - 实际项目中这里应该是OCR返回的结果
        resolve([
          { fundCode: '000330', fundName: '汇添富现金宝货币A', shares: 19098.83, nav: 1.0000, amount: 19098.83, status: 'pending' },
          { fundCode: '001052', fundName: '华夏中证500ETF联接', shares: 18463.66, nav: 0.8959, amount: 16541.59, status: 'pending' },
          { fundCode: '003003', fundName: '华夏现金增利', shares: 14645.79, nav: 1.0000, amount: 14645.79, status: 'pending' },
          { fundCode: '022853', fundName: '中航优选领航混合', shares: 7675.50, nav: 1.6224, amount: 12452.73, status: 'pending' },
          { fundCode: '021492', fundName: '中航远见领航混合', shares: 8614.15, nav: 1.2789, amount: 11016.64, status: 'pending' },
        ]);
      }, 1500);
    });
  };

  // 匹配基金代码到数据库
  const matchFunds = async (data: ParsedFundData[]): Promise<ParsedFundData[]> => {
    const results: ParsedFundData[] = [];
    
    for (const item of data) {
      try {
        // 查询基金信息
        const response = await fundApi.getDetail(item.fundCode);
        if (response.success && response.data) {
          results.push({
            ...item,
            status: 'matched',
            matchedFund: response.data,
          });
        } else {
          results.push({
            ...item,
            status: 'not_found',
          });
        }
      } catch (error) {
        results.push({
          ...item,
          status: 'not_found',
        });
      }
    }
    
    return results;
  };

  // 导入选中的基金
  const handleImport = async () => {
    if (selectedItems.size === 0) {
      toast.error('请至少选择一条记录');
      return;
    }

    setIsImporting(true);
    
    const selectedFunds = parsedData.filter(d => selectedItems.has(d.fundCode));
    let successCount = 0;
    let failCount = 0;

    for (const fund of selectedFunds) {
      try {
        // 1. 添加到分组 - 传递完整的持仓信息
        if (groupId) {
          await portfolioApi.addFundToGroup(groupId, {
            fund_code: fund.fundCode,
            fund_name: fund.fundName,
            shares: fund.shares,
            buy_nav: fund.nav,
            amount: fund.amount,
            buy_date: new Date().toISOString().split('T')[0],
          });
        }

        // 2. 添加交易记录（作为买入）
        await portfolioApi.addTransaction({
          fund_code: fund.fundCode,
          transaction_type: 'BUY',
          transaction_date: new Date().toISOString().split('T')[0],
          shares: fund.shares,
          price: fund.nav,
          fee: 0,
          group_id: groupId,
          notes: '从图片导入',
        });

        successCount++;
      } catch (error) {
        failCount++;
      }
    }

    setIsImporting(false);
    
    if (successCount > 0) {
      toast.success(`成功导入 ${successCount} 只基金`);
      onImportSuccess?.();
      setIsOpen(false);
      setParsedData([]);
      setSelectedItems(new Set());
    }
    
    if (failCount > 0) {
      toast.error(`${failCount} 只基金导入失败`);
    }
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
    <>
      <Button
        variant="outline"
        className="border-dashed"
        onClick={() => setIsOpen(true)}
      >
        <Camera className="w-4 h-4 mr-2" />
        图片导入
      </Button>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ImageIcon className="w-5 h-5 text-cyan-400" />
              从图片导入基金
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
              <Button variant="outline" onClick={() => setIsOpen(false)}>
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
    </>
  );
}
