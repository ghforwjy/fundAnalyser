import { useState, useEffect, useCallback } from 'react';
import { Check, Plus, X, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { tagApi, type Tag } from '@/services/api';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface TagSelectorInlineProps {
  fundCode: string;
  selectedTags: Tag[];
  onTagsChange: (tags: Tag[]) => void;
  placeholder?: string;
}

export function TagSelectorInline({
  fundCode,
  selectedTags,
  onTagsChange,
  placeholder = '搜索或创建标签...',
}: TagSelectorInlineProps) {
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 加载所有标签
  const loadTags = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await tagApi.getAll();
      if (response.success) {
        setAllTags(response.data);
      }
    } catch (error) {
      console.error('加载标签失败:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTags();
  }, [loadTags]);

  // 搜索标签
  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      setIsLoading(true);
      try {
        const response = await tagApi.search(query);
        if (response.success) {
          setAllTags(response.data);
        }
      } catch (error) {
        console.error('搜索标签失败:', error);
      } finally {
        setIsLoading(false);
      }
    } else {
      loadTags();
    }
  };

  // 创建新标签
  const handleCreateTag = async () => {
    if (!searchQuery.trim()) return;

    setIsCreating(true);
    try {
      const response = await tagApi.create({ name: searchQuery.trim() });
      if (response.success && response.data) {
        const newTag = response.data;
        setAllTags((prev) => [...prev, newTag]);
        onTagsChange([...selectedTags, newTag]);
        toast.success(`标签 "${searchQuery}" 创建成功`);
        setSearchQuery('');
      } else {
        toast.error(response.message || '创建标签失败');
      }
    } catch (error) {
      toast.error('创建标签失败');
    } finally {
      setIsCreating(false);
    }
  };

  // 选择/取消选择标签
  const handleToggleTag = (tag: Tag) => {
    const isSelected = selectedTags.some((t) => t.id === tag.id);
    if (isSelected) {
      onTagsChange(selectedTags.filter((t) => t.id !== tag.id));
    } else {
      onTagsChange([...selectedTags, tag]);
    }
  };

  // 移除已选标签
  const handleRemoveTag = (tagId: number) => {
    onTagsChange(selectedTags.filter((t) => t.id !== tagId));
  };

  // 检查搜索的标签是否已存在
  const tagExists = allTags.some(
    (tag) => tag.name.toLowerCase() === searchQuery.trim().toLowerCase()
  );

  // 按分类分组标签
  const groupedTags = allTags.reduce((acc, tag) => {
    const category = tag.category || '未分类';
    if (!acc[category]) {
      acc[category] = [];
    }
    // 只显示未选中的标签在列表中
    const isSelected = selectedTags.some((t) => t.id === tag.id);
    if (!isSelected) {
      acc[category].push(tag);
    }
    return acc;
  }, {} as Record<string, Tag[]>);

  // 过滤掉空的分类
  const nonEmptyGroups = Object.entries(groupedTags).filter(
    ([, tags]) => tags.length > 0
  );

  return (
    <div className="space-y-4">
      {/* 已选标签展示 */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedTags.map((tag) => (
            <Badge
              key={tag.id}
              variant="secondary"
              className="gap-1 px-2 py-1 cursor-pointer hover:opacity-80"
              style={{
                backgroundColor: tag.color ? `${tag.color}20` : undefined,
                borderColor: tag.color,
                color: tag.color,
              }}
              onClick={() => handleRemoveTag(tag.id)}
            >
              {tag.name}
              <X className="w-3 h-3" />
            </Badge>
          ))}
        </div>
      )}

      {/* 搜索输入框 */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder={placeholder}
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* 标签列表 */}
      <div className="border rounded-md max-h-[240px] overflow-y-auto">
        {isLoading ? (
          <div className="py-8 text-center text-muted-foreground">
            加载中...
          </div>
        ) : nonEmptyGroups.length === 0 && !searchQuery.trim() ? (
          <div className="py-8 text-center text-muted-foreground">
            暂无标签，请创建新标签
          </div>
        ) : (
          <div className="py-2">
            {/* 创建新标签选项 */}
            {searchQuery.trim() && !tagExists && (
              <div className="px-2 pb-2 border-b">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCreateTag}
                  disabled={isCreating}
                  className="w-full justify-start gap-2 text-muted-foreground hover:text-foreground"
                >
                  <Plus className="w-4 h-4" />
                  创建 "{searchQuery}"
                </Button>
              </div>
            )}

            {/* 按分类展示标签 */}
            {nonEmptyGroups.map(([category, tags], groupIndex) => (
              <div
                key={category}
                className={cn(
                  'px-2',
                  groupIndex > 0 && 'border-t mt-2 pt-2'
                )}
              >
                <div className="text-xs font-medium text-muted-foreground px-2 py-1">
                  {category}
                </div>
                <div className="space-y-1">
                  {tags.map((tag) => (
                    <button
                      key={tag.id}
                      onClick={() => handleToggleTag(tag)}
                      className="w-full flex items-center gap-2 px-2 py-1.5 rounded-sm hover:bg-accent text-left transition-colors"
                    >
                      <div
                        className="w-3 h-3 rounded-full flex-shrink-0"
                        style={{ backgroundColor: tag.color || '#3b82f6' }}
                      />
                      <span className="flex-1 text-sm">{tag.name}</span>
                      <Check className="w-4 h-4 text-muted-foreground opacity-0" />
                    </button>
                  ))}
                </div>
              </div>
            ))}

            {/* 搜索结果为空 */}
            {searchQuery.trim() && nonEmptyGroups.length === 0 && tagExists && (
              <div className="py-4 text-center text-sm text-muted-foreground">
                该标签已被选中
              </div>
            )}
          </div>
        )}
      </div>

      {/* 提示文字 */}
      <p className="text-xs text-muted-foreground">
        点击标签选择，点击已选标签可取消选择
      </p>
    </div>
  );
}

export default TagSelectorInline;
