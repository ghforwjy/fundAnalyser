import { useState } from 'react';
import {
  Lightbulb,
  TrendingUp,
  TrendingDown,
  ChevronDown,
  Scale
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ValueAveragingTab from './ValueAveragingTab';
import TakeProfitTab from './TakeProfitTab';

interface InvestmentAdviceProps {
  groupId?: number;
  groupName?: string;
  onRefresh?: () => void;  // 刷新父组件的基金列表
}

type AdviceType = 'value_averaging' | 'take_profit';

const ADVICE_OPTIONS: { id: AdviceType; name: string; icon: React.ReactNode; description: string; enabled: boolean }[] = [
  {
    id: 'value_averaging',
    name: '定投建议',
    icon: <TrendingUp className="w-4 h-4" />,
    description: '市值定投法：涨时少买、跌时多买',
    enabled: true
  },
  {
    id: 'take_profit',
    name: '止盈建议',
    icon: <TrendingDown className="w-4 h-4" />,
    description: '阶梯止盈法：分批止盈、锁定收益',
    enabled: true
  },
  {
    id: 'dynamic_balance' as AdviceType,
    name: '动态平衡',
    icon: <Scale className="w-4 h-4" />,
    description: '根据资产配置比例动态调整',
    enabled: false
  }
];

export default function InvestmentAdvice({ groupId, groupName, onRefresh }: InvestmentAdviceProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedAdvice, setSelectedAdvice] = useState<AdviceType>('value_averaging');

  // 处理对话框关闭时的刷新
  const handleOpenChange = (open: boolean) => {
    setIsOpen(open);
    // 当对话框关闭时，触发父组件刷新
    if (!open && onRefresh) {
      onRefresh();
    }
  };

  const handleSelectAdvice = (adviceId: AdviceType) => {
    setSelectedAdvice(adviceId);
    setIsOpen(true);
  };

  const selectedOption = ADVICE_OPTIONS.find(o => o.id === selectedAdvice);

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            className="border-dashed border-amber-500/50 hover:bg-amber-500/10"
          >
            <Lightbulb className="w-4 h-4 mr-2 text-amber-400" />
            投资建议
            <ChevronDown className="w-4 h-4 ml-1" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          {ADVICE_OPTIONS.map((option) => (
            <DropdownMenuItem
              key={option.id}
              disabled={!option.enabled}
              className="flex items-center gap-3 py-3"
              onClick={() => option.enabled && handleSelectAdvice(option.id as AdviceType)}
            >
              <span className={option.enabled ? "text-cyan-400" : "text-muted-foreground"}>
                {option.icon}
              </span>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span>{option.name}</span>
                  {!option.enabled && (
                    <Badge variant="secondary" className="text-xs">即将上线</Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{option.description}</p>
              </div>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog open={isOpen} onOpenChange={handleOpenChange}>
        <DialogContent
          className="!w-[95vw] !h-[90vh] !max-w-[1400px] overflow-hidden flex flex-col p-6"
        >
          <DialogHeader className="pb-4 border-b border-border/50">
            <DialogTitle className="flex items-center gap-3 text-xl">
              <Lightbulb className="w-6 h-6 text-amber-400" />
              投资建议
              {groupName && (
                <Badge variant="secondary" className="text-base px-3 py-1">
                  {groupName}
                </Badge>
              )}
              <Tabs value={selectedAdvice} onValueChange={(v) => setSelectedAdvice(v as AdviceType)} className="ml-auto">
                <TabsList className="bg-muted/50">
                  <TabsTrigger value="value_averaging" className="data-[state=active]:bg-cyan-500 data-[state=active]:text-white">
                    <TrendingUp className="w-4 h-4 mr-1" />
                    定投
                  </TabsTrigger>
                  <TabsTrigger value="take_profit" className="data-[state=active]:bg-red-500 data-[state=active]:text-white">
                    <TrendingDown className="w-4 h-4 mr-1" />
                    止盈
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </DialogTitle>
            <DialogDescription className="sr-only">
              投资建议分析
            </DialogDescription>
          </DialogHeader>

          <div className="flex-1 overflow-auto py-6">
            {!groupId ? (
              <div className="text-center py-12">
                <Lightbulb className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">请先选择一个投资组合</p>
              </div>
            ) : (
              <>
                {selectedAdvice === 'value_averaging' && (
                  <ValueAveragingTab groupId={groupId} groupName={groupName} />
                )}
                {selectedAdvice === 'take_profit' && (
                  <TakeProfitTab groupId={groupId} groupName={groupName} onRefresh={onRefresh} />
                )}
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

export { ValueAveragingTab, TakeProfitTab };
