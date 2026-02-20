import { useState } from 'react';
import { 
  Bell, 
  Search, 
  User, 
  Settings, 
  LogOut,
  ChevronDown,
  Menu
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onMenuClick?: () => void;
  className?: string;
}

export function Header({ onMenuClick, className }: HeaderProps) {
  const [searchValue, setSearchValue] = useState('');

  return (
    <header className={cn(
      "h-16 bg-card/80 backdrop-blur-xl border-b border-border flex items-center justify-between px-4 sticky top-0 z-30",
      className
    )}>
      {/* 左侧：菜单按钮 + 搜索 */}
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon" 
          className="lg:hidden"
          onClick={onMenuClick}
        >
          <Menu className="w-5 h-5" />
        </Button>

        {/* 全局搜索 */}
        <div className="relative hidden sm:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="搜索基金、数据表..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            className="w-64 pl-9 bg-secondary/50 border-border focus:border-cyan-500/50 focus:ring-cyan-500/20"
          />
        </div>
      </div>

      {/* 右侧：通知 + 用户 */}
      <div className="flex items-center gap-2">
        {/* 通知按钮 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-cyan-500 rounded-full animate-pulse" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <div className="p-3 border-b border-border">
              <span className="font-medium">通知</span>
            </div>
            <div className="p-2 space-y-1">
              <div className="p-3 rounded-lg bg-cyan-500/5 border border-cyan-500/20">
                <div className="text-sm font-medium text-cyan-400">数据更新完成</div>
                <div className="text-xs text-muted-foreground mt-1">基金净值数据已更新至 2024-01-15</div>
              </div>
              <div className="p-3 rounded-lg hover:bg-secondary/50">
                <div className="text-sm font-medium">系统维护通知</div>
                <div className="text-xs text-muted-foreground mt-1">计划今晚 02:00-04:00 进行系统维护</div>
              </div>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* 用户菜单 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center gap-2 px-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <span className="hidden sm:inline text-sm font-medium">管理员</span>
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <User className="w-4 h-4 mr-2" />
              个人中心
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="w-4 h-4 mr-2" />
              账号设置
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-red-400">
              <LogOut className="w-4 h-4 mr-2" />
              退出登录
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
