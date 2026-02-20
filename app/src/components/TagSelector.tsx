import { useState, useEffect, useCallback } from 'react';
import { Check, Plus, X, Search, Tag as TagIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { tagApi, type Tag } from '@/services/api';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface TagSelectorProps {
  fundCode: string;
  selectedTags: Tag[];
  onTagsChange: (tags: Tag[]) => void;
  placeholder?: string;
}

export function TagSelector({
  fundCode,
  selectedTags,
  onTagsChange,
  placeholder = '选择或搜索标签...',
}: TagSelectorProps) {
  const [open, setOpen] = useState(false);
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  // 加载所有标签
  const loadTags = useCallback(async () => {
    try {
      const response = await tagApi.getAll();
      if (response.success) {
        setAllTags(response.data);
      }
    } catch (error) {
      console.error('加载标签失败:', error);
    }
  }, []);

  useEffect(() => {
    loadTags();
  }, [loadTags]);

  // 搜索标签
  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim()) {
      try {
        const response = await tagApi.search(query);
        if (response.success) {
          setAllTags(response.data);
        }
      } catch (error) {
        console.error('搜索标签失败:', error);
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

  // 选择标签
  const handleSelectTag = (tag: Tag) => {
    const isSelected = selectedTags.some((t) => t.id === tag.id);
    if (isSelected) {
      onTagsChange(selectedTags.filter((t) => t.id !== tag.id));
    } else {
      onTagsChange([...selectedTags, tag]);
    }
  };

  // 移除标签
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
    acc[category].push(tag);
    return acc;
  }, {} as Record<string, Tag[]>);

  return (
    <div className="space-y-2">
      {/* 已选标签展示 */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {selectedTags.map((tag) => (
            <Badge
              key={tag.id}
              variant="secondary"
              className="gap-1 px-2 py-1"
              style={{
                backgroundColor: tag.color ? `${tag.color}20` : undefined,
                borderColor: tag.color,
                color: tag.color,
              }}
            >
              {tag.name}
              <button
                onClick={() => handleRemoveTag(tag.id)}
                className="ml-1 rounded-full hover:bg-black/10 p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}

      {/* 标签选择器 */}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between"
          >
            <span className="flex items-center gap-2 text-muted-foreground">
              <TagIcon className="w-4 h-4" />
              {placeholder}
            </span>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[300px] p-0" align="start">
          <Command>
            <CommandInput
              placeholder="搜索标签..."
              value={searchQuery}
              onValueChange={handleSearch}
            />
            <CommandList className="max-h-[300px]">
              <CommandEmpty className="py-2 px-2">
                {searchQuery.trim() && !tagExists ? (
                  <div className="flex flex-col items-center gap-2 py-2">
                    <p className="text-sm text-muted-foreground">
                      未找到 "{searchQuery}"
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={handleCreateTag}
                      disabled={isCreating}
                      className="gap-1"
                    >
                      <Plus className="w-4 h-4" />
                      创建标签 "{searchQuery}"
                    </Button>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">未找到标签</p>
                )}
              </CommandEmpty>

              {/* 创建新标签选项（当搜索不存在时） */}
              {searchQuery.trim() && !tagExists && (
                <CommandGroup heading="创建新标签">
                  <CommandItem
                    onSelect={handleCreateTag}
                    disabled={isCreating}
                    className="cursor-pointer"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    创建 "{searchQuery}"
                  </CommandItem>
                </CommandGroup>
              )}

              {/* 按分类展示标签 */}
              {Object.entries(groupedTags).map(([category, tags]) => (
                <CommandGroup key={category} heading={category}>
                  {tags.map((tag) => {
                    const isSelected = selectedTags.some(
                      (t) => t.id === tag.id
                    );
                    return (
                      <CommandItem
                        key={tag.id}
                        onSelect={() => handleSelectTag(tag)}
                        className="cursor-pointer"
                      >
                        <div className="flex items-center gap-2 flex-1">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: tag.color || '#3b82f6' }}
                          />
                          <span>{tag.name}</span>
                        </div>
                        {isSelected && <Check className="w-4 h-4" />}
                      </CommandItem>
                    );
                  })}
                </CommandGroup>
              ))}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}

export default TagSelector;
