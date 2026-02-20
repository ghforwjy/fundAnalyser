import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Loader2, History, Info } from 'lucide-react';
import { portfolioApi } from '@/services/api';

interface TransactionHistoryProps {
  groupId?: number;
}

// 持仓历史记录类型
interface HoldingHistory {
  id: number;
  portfolio_id: number;
  fund_code: string;
  fund_name: string;
  record_date: string;
  shares: number;
  nav: number;
  market_value: number;
}

export default function TransactionHistory({ groupId }: TransactionHistoryProps) {
  const [history, setHistory] = useState<HoldingHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, [groupId]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      if (groupId) {
        const response = await portfolioApi.getGroupHistory(groupId, 50);
        if (response.success) {
          setHistory(response.data);
        }
      } else {
        setHistory([]);
      }
    } catch (error) {
      console.error('加载历史记录失败:', error);
    } finally {
      setLoading(false);
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

  return (
    <Card className="glow-border">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <History className="w-5 h-5 text-cyan-400" />
          持仓历史
          <Badge variant="secondary">{history.length} 条</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
          </div>
        ) : history.length === 0 ? (
          <div className="py-12 text-center">
            <Info className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">暂无持仓历史记录</p>
            <p className="text-sm text-muted-foreground mt-1">
              持仓历史由 fundData skill 维护
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>日期</TableHead>
                  <TableHead>基金</TableHead>
                  <TableHead className="text-right">份额</TableHead>
                  <TableHead className="text-right">净值</TableHead>
                  <TableHead className="text-right">市值</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>{record.record_date}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{record.fund_name}</p>
                        <code className="text-xs text-muted-foreground">{record.fund_code}</code>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">{formatNumber(record.shares, 4)}</TableCell>
                    <TableCell className="text-right font-mono">{formatNumber(record.nav, 4)}</TableCell>
                    <TableCell className="text-right font-mono">{formatCurrency(record.market_value)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
