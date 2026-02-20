import { useState } from 'react';
import { 
  LayoutDashboard, 
  Database, 
  Settings, 
  BarChart3, 
  ChevronLeft,
  ChevronRight,
  FolderOpen,
  PieChart,
} from 'lucide-react';
import { cn } from '@/lib/utils';

type Page = 'dashboard' | 'data-source' | 'table-schema' | 'table-data' | 'fund-list' | 'fund-detail' | 'portfolio' | 'settings';

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  page: Page;
  children?: { label: string; page: Page }[];
}

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  collapsed?: boolean;
  onCollapsedChange?: (collapsed: boolean) => void;
}

const navItems: NavItem[] = [
  {
    id: 'dashboard',
    label: '仪表盘',
    icon: LayoutDashboard,
    page: 'dashboard',
  },
  {
    id: 'fund-analysis',
    label: '基金分析',
    icon: BarChart3,
    page: 'fund-list',
    children: [
      { label: '基金列表', page: 'fund-list' },
    ],
  },
  {
    id: 'portfolio',
    label: '投资组合',
    icon: PieChart,
    page: 'portfolio',
  },
  {
    id: 'data-manage',
    label: '数据管理',
    icon: Database,
    page: 'data-source',
    children: [
      { label: '数据源配置', page: 'data-source' },
      { label: '表结构', page: 'table-schema' },
      { label: '表数据', page: 'table-data' },
    ],
  },
  {
    id: 'settings',
    label: '系统设置',
    icon: Settings,
    page: 'settings',
  },
];

export function Sidebar({ currentPage, onNavigate, collapsed = false, onCollapsedChange }: SidebarProps) {
  const [expandedMenus, setExpandedMenus] = useState<string[]>([]);

  const toggleMenu = (menuId: string) => {
    if (collapsed) return; // 折叠状态下不展开子菜单
    setExpandedMenus(prev => 
      prev.includes(menuId) 
        ? prev.filter(id => id !== menuId)
        : [...prev, menuId]
    );
  };

  const isActive = (page: Page) => {
    return currentPage === page;
  };

  const isInGroup = (item: NavItem) => {
    if (item.page === currentPage) return true;
    if (item.children) {
      return item.children.some(child => child.page === currentPage);
    }
    return false;
  };

  const toggleCollapsed = () => {
    onCollapsedChange?.(!collapsed);
  };

  return (
    <aside 
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300",
        collapsed ? "w-16" : "w-60"
      )}
    >
      {/* Logo区域 */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-sidebar-border">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
              <Database className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-sidebar-foreground">FundDB</span>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center mx-auto">
            <Database className="w-4 h-4 text-white" />
          </div>
        )}
        <button
          onClick={toggleCollapsed}
          className={cn(
            "p-1 rounded-md hover:bg-sidebar-accent text-sidebar-foreground/60 hover:text-sidebar-foreground transition-colors",
            collapsed && "absolute -right-3 top-5 w-6 h-6 bg-sidebar border border-sidebar-border rounded-full flex items-center justify-center"
          )}
        >
          {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* 导航菜单 */}
      <nav className="p-3 space-y-1 overflow-y-auto custom-scrollbar" style={{ height: 'calc(100vh - 64px - 48px)' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const hasChildren = item.children && item.children.length > 0;
          const isExpanded = expandedMenus.includes(item.id);
          const active = isInGroup(item);

          return (
            <div key={item.id}>
              <div
                onClick={() => {
                  if (hasChildren && !collapsed) {
                    toggleMenu(item.id);
                  } else {
                    onNavigate(item.page);
                  }
                }}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 cursor-pointer group",
                  active 
                    ? "bg-sidebar-accent text-sidebar-primary border-l-2 border-cyan-500" 
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                )}
                title={collapsed ? item.label : undefined}
              >
                <Icon className={cn(
                  "w-5 h-5 flex-shrink-0 transition-colors",
                  active ? "text-cyan-400" : "group-hover:text-cyan-400"
                )} />
                {!collapsed && (
                  <>
                    <span className="flex-1 text-sm font-medium">{item.label}</span>
                    {hasChildren && (
                      <ChevronRight className={cn(
                        "w-4 h-4 transition-transform duration-200",
                        isExpanded && "rotate-90"
                      )} />
                    )}
                  </>
                )}
              </div>

              {/* 子菜单 */}
              {!collapsed && hasChildren && isExpanded && (
                <div className="ml-4 mt-1 space-y-1 border-l border-sidebar-border pl-3">
                  {item.children?.map((child) => (
                    <div
                      key={child.page}
                      onClick={() => onNavigate(child.page)}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-all duration-200 cursor-pointer",
                        isActive(child.page)
                          ? "bg-cyan-500/10 text-cyan-400" 
                          : "text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent/30"
                      )}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-50"></span>
                      {child.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      {/* 底部版本信息 */}
      {!collapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-3 border-t border-sidebar-border">
          <div className="text-xs text-sidebar-foreground/40 text-center">
            FundDB v1.0.0
          </div>
        </div>
      )}
    </aside>
  );
}
