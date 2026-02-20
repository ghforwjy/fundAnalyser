import { useState, useRef, useCallback, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Column<T> {
  key: string;
  title: string;
  width?: number;
  minWidth?: number;
  maxWidth?: number;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
  render?: (row: T, index: number) => React.ReactNode;
}

interface ResizableTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: (row: T) => string;
  defaultSort?: { key: string; direction: 'asc' | 'desc' };
  className?: string;
  onRowClick?: (row: T) => void;
  emptyText?: string;
  loading?: boolean;
}

export function ResizableTable<T>({
  columns,
  data,
  rowKey,
  defaultSort,
  className,
  onRowClick,
  emptyText = '暂无数据',
  loading = false,
}: ResizableTableProps<T>) {
  // 列宽状态
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>(() => {
    const widths: Record<string, number> = {};
    columns.forEach(col => {
      widths[col.key] = col.width || 120;
    });
    return widths;
  });

  // 排序状态
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(
    defaultSort || null
  );

  // 拖拽状态
  const resizingRef = useRef<{
    columnKey: string;
    startX: number;
    startWidth: number;
  } | null>(null);

  // 计算固定列的偏移位置
  const getFixedLeft = useCallback((columnIndex: number): number => {
    let left = 0;
    for (let i = 0; i < columnIndex; i++) {
      const col = columns[i];
      if (col.fixed === 'left') {
        left += columnWidths[col.key] || col.width || 120;
      }
    }
    return left;
  }, [columns, columnWidths]);

  // 处理排序
  const handleSort = useCallback((columnKey: string) => {
    const column = columns.find(col => col.key === columnKey);
    if (!column?.sortable) return;

    setSortConfig(current => {
      if (current?.key === columnKey) {
        return {
          key: columnKey,
          direction: current.direction === 'asc' ? 'desc' : 'asc',
        };
      }
      return { key: columnKey, direction: 'desc' };
    });
  }, [columns]);

  // 排序后的数据
  const sortedData = useMemo(() => {
    if (!sortConfig) return data;

    return [...data].sort((a, b) => {
      const aValue = (a as any)[sortConfig.key];
      const bValue = (b as any)[sortConfig.key];

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }

      const aStr = String(aValue).toLowerCase();
      const bStr = String(bValue).toLowerCase();

      if (sortConfig.direction === 'asc') {
        return aStr.localeCompare(bStr);
      }
      return bStr.localeCompare(aStr);
    });
  }, [data, sortConfig]);

  // 开始拖拽
  const handleResizeStart = useCallback((e: React.MouseEvent, columnKey: string) => {
    e.preventDefault();
    e.stopPropagation();

    const currentWidth = columnWidths[columnKey] || 120;
    resizingRef.current = {
      columnKey,
      startX: e.clientX,
      startWidth: currentWidth,
    };

    document.addEventListener('mousemove', handleResizeMove);
    document.addEventListener('mouseup', handleResizeEnd);
  }, [columnWidths]);

  // 拖拽中
  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!resizingRef.current) return;

    const { columnKey, startX, startWidth } = resizingRef.current;
    const delta = e.clientX - startX;
    const newWidth = Math.max(60, startWidth + delta);

    setColumnWidths(prev => ({
      ...prev,
      [columnKey]: newWidth,
    }));
  }, []);

  // 结束拖拽
  const handleResizeEnd = useCallback(() => {
    resizingRef.current = null;
    document.removeEventListener('mousemove', handleResizeMove);
    document.removeEventListener('mouseup', handleResizeEnd);
  }, [handleResizeMove]);

  // 获取排序图标
  const getSortIcon = (columnKey: string) => {
    const column = columns.find(col => col.key === columnKey);
    if (!column?.sortable) return null;

    if (sortConfig?.key !== columnKey) {
      return <ArrowUpDown className="w-3.5 h-3.5 text-muted-foreground/50" />;
    }

    return sortConfig.direction === 'asc' 
      ? <ArrowUp className="w-3.5 h-3.5 text-cyan-400" />
      : <ArrowDown className="w-3.5 h-3.5 text-cyan-400" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="py-12 text-center text-muted-foreground">
        {emptyText}
      </div>
    );
  }

  return (
    <div className={cn("flex flex-col h-full", className)}>
      {/* 表格区域 - 表头和内容一起滚动 */}
      <div className="flex-1 overflow-auto scrollbar-thin scrollbar-thumb-muted-foreground/20 scrollbar-track-transparent hover:scrollbar-thumb-muted-foreground/40">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-border">
              {columns.map((column, index) => {
                const isFixedLeft = column.fixed === 'left';
                const isFixedRight = column.fixed === 'right';
                const fixedLeft = isFixedLeft ? getFixedLeft(index) : undefined;

                return (
                  <th
                    key={column.key}
                    className={cn(
                      "relative px-3 py-3 text-left text-sm font-medium text-muted-foreground select-none bg-secondary/30",
                      column.sortable && "cursor-pointer hover:bg-secondary/50 transition-colors",
                      // 固定列使用相同的背景色，但添加毛玻璃效果来遮挡后面的内容
                      isFixedLeft && "sticky z-20 backdrop-blur-md",
                      isFixedRight && "sticky right-0 z-20 backdrop-blur-md"
                    )}
                    style={{
                      width: columnWidths[column.key],
                      minWidth: column.minWidth || 60,
                      maxWidth: column.maxWidth,
                      left: fixedLeft,
                    }}
                    onClick={() => handleSort(column.key)}
                  >
                    <div className={cn(
                      "flex items-center gap-1",
                      column.align === 'center' && "justify-center",
                      column.align === 'right' && "justify-end"
                    )}>
                      <span className="truncate">{column.title}</span>
                      {getSortIcon(column.key)}
                    </div>
                    {/* 拖拽手柄 */}
                    <div
                      className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-cyan-500/50 active:bg-cyan-500 transition-colors"
                      onMouseDown={(e) => handleResizeStart(e, column.key)}
                    />
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row, index) => (
              <tr
                key={rowKey(row)}
                className={cn(
                  "border-b border-border transition-colors",
                  onRowClick && "cursor-pointer hover:bg-accent/30"
                )}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((column, colIndex) => {
                  const isFixedLeft = column.fixed === 'left';
                  const isFixedRight = column.fixed === 'right';
                  const fixedLeft = isFixedLeft ? getFixedLeft(colIndex) : undefined;

                  return (
                    <td
                      key={column.key}
                      className={cn(
                        "px-3 py-3 bg-card/50 backdrop-blur-xl",
                        column.align === 'center' && "text-center",
                        column.align === 'right' && "text-right",
                        isFixedLeft && "sticky z-10",
                        isFixedRight && "sticky right-0 z-10"
                      )}
                      style={{
                        width: columnWidths[column.key],
                        minWidth: column.minWidth || 60,
                        maxWidth: column.maxWidth,
                        left: fixedLeft,
                      }}
                    >
                      {column.render
                        ? column.render(row, index)
                        : (row as any)[column.key] ?? '-'
                      }
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
