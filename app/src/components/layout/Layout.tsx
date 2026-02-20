import { useState } from 'react';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { cn } from '@/lib/utils';

type Page = 'dashboard' | 'data-source' | 'table-schema' | 'table-data' | 'fund-list' | 'fund-detail';

interface LayoutProps {
  children: React.ReactNode;
  currentPage: Page;
  onNavigate: (page: Page) => void;
  className?: string;
}

export function Layout({ children, currentPage, onNavigate, className }: LayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className={cn("min-h-screen bg-background bg-grid", className)}>
      {/* 侧边栏 - 桌面端固定 */}
      <div className="hidden lg:block">
        <Sidebar 
          currentPage={currentPage} 
          onNavigate={onNavigate}
          collapsed={sidebarCollapsed}
          onCollapsedChange={setSidebarCollapsed}
        />
      </div>

      {/* 主内容区 - 根据侧边栏状态动态调整边距 */}
      <div className={cn(
        "transition-all duration-300",
        sidebarCollapsed ? "lg:ml-16" : "lg:ml-60"
      )}>
        <Header />
        
        <main className="p-4 lg:p-6 h-[calc(100vh-64px)] overflow-auto">
          {/* 背景光晕 */}
          <div className="fixed inset-0 bg-glow pointer-events-none" />
          
          {/* 页面内容 */}
          <div className="relative z-10 h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
