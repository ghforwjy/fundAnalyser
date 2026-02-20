import { useState, useEffect } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  MoreVertical,
  Folder,
  Save,
  X,
  Loader2,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { portfolioApi, type FundGroup } from '@/services/api';
import { cn } from '@/lib/utils';

interface GroupManageProps {
  onSelectGroup?: (group: FundGroup) => void;
  selectedGroupId?: number;
  onGroupDeleted?: () => void;
}

export default function GroupManage({ onSelectGroup, selectedGroupId, onGroupDeleted }: GroupManageProps) {
  const [groups, setGroups] = useState<FundGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [currentGroup, setCurrentGroup] = useState<FundGroup | null>(null);
  
  // 表单数据
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  useEffect(() => {
    loadGroups();
  }, []);

  // 当组合列表加载完成且没有选中组合时，默认选中第一个
  useEffect(() => {
    if (groups.length > 0 && selectedGroupId === undefined) {
      onSelectGroup?.(groups[0]);
    }
  }, [groups, selectedGroupId, onSelectGroup]);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const response = await portfolioApi.getGroups();
      if (response.success) {
        setGroups(response.data);
      }
    } catch (error) {
      toast.error('加载分组失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!formData.name.trim()) {
      toast.error('请输入分组名称');
      return;
    }
    
    try {
      const response = await portfolioApi.createGroup(formData);
      if (response.success) {
        toast.success('创建成功');
        setIsCreateDialogOpen(false);
        setFormData({ name: '', description: '' });
        loadGroups();
      }
    } catch (error) {
      toast.error('创建失败');
    }
  };

  const handleUpdate = async () => {
    if (!currentGroup || !formData.name.trim()) {
      toast.error('请输入分组名称');
      return;
    }
    
    try {
      const response = await portfolioApi.updateGroup(currentGroup.id, formData);
      if (response.success) {
        toast.success('更新成功');
        setIsEditDialogOpen(false);
        setCurrentGroup(null);
        loadGroups();
      }
    } catch (error) {
      toast.error('更新失败');
    }
  };

  const handleDelete = async () => {
    if (!currentGroup) return;
    
    try {
      const response = await portfolioApi.deleteGroup(currentGroup.id);
      if (response.success) {
        toast.success('删除成功');
        setIsDeleteDialogOpen(false);
        setCurrentGroup(null);
        loadGroups();
        onGroupDeleted?.();
      }
    } catch (error) {
      toast.error('删除失败');
    }
  };

  const openEditDialog = (group: FundGroup) => {
    setCurrentGroup(group);
    setFormData({
      name: group.name,
      description: group.description || '',
    });
    setIsEditDialogOpen(true);
  };

  const openDeleteDialog = (group: FundGroup) => {
    setCurrentGroup(group);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="space-y-4">
      {/* 分组列表 */}
      <div className="grid gap-3">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
          </div>
        ) : (
          <>
            {/* 各个分组 */}
            {groups.map((group) => (
              <Card 
                key={group.id}
                className={cn(
                  "cursor-pointer transition-all hover:border-cyan-500/50",
                  selectedGroupId === group.id && "border-cyan-500 bg-cyan-500/5"
                )}
                onClick={() => onSelectGroup?.(group)}
              >
                <CardContent className="p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                        <Folder className="w-5 h-5 text-cyan-400" />
                      </div>
                      <div>
                        <h3 className="font-medium">{group.name}</h3>
                        <p className="text-xs text-muted-foreground">
                          {group.fund_count || 0} 只基金
                          {group.description && ` · ${group.description}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant="secondary" 
                        className="text-xs bg-cyan-500/20 text-cyan-400 border-cyan-500/30"
                      >
                        {group.fund_count || 0}
                      </Badge>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={(e) => { e.stopPropagation(); openEditDialog(group); }}>
                            <Edit2 className="w-4 h-4 mr-2" />
                            编辑
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={(e) => { e.stopPropagation(); openDeleteDialog(group); }}
                            className="text-red-500"
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            删除
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </>
        )}
      </div>

      {/* 创建分组按钮 */}
      <Button 
        variant="outline" 
        className="w-full border-dashed"
        onClick={() => setIsCreateDialogOpen(true)}
      >
        <Plus className="w-4 h-4 mr-2" />
        新建分组
      </Button>

      {/* 创建分组对话框 */}
      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新建分组</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">分组名称</label>
              <Input
                placeholder="请输入分组名称"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">描述（可选）</label>
              <Textarea
                placeholder="请输入分组描述"
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

      {/* 编辑分组对话框 */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>编辑分组</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">分组名称</label>
              <Input
                placeholder="请输入分组名称"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">描述（可选）</label>
              <Textarea
                placeholder="请输入分组描述"
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

      {/* 删除确认对话框 */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <p className="text-muted-foreground">
              确定要删除分组 <span className="font-medium text-foreground">"{currentGroup?.name}"</span> 吗？
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              分组中的基金将被移除。
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
    </div>
  );
}
