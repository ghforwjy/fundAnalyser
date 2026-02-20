import { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Moon, 
  Sun, 
  Database, 
  Bell, 
  Shield, 
  Globe,
  Save,
  RefreshCw
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    darkMode: true,
    notifications: true,
    autoSync: true,
    syncInterval: '24',
    dataRetention: '365',
    apiTimeout: '30'
  });

  const handleSave = () => {
    toast.success('设置已保存');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">系统设置</h1>
          <p className="text-muted-foreground mt-1">管理系统配置和偏好设置</p>
        </div>
        <Button onClick={handleSave}>
          <Save className="w-4 h-4 mr-2" />
          保存设置
        </Button>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Moon className="w-5 h-5" />
              外观设置
            </CardTitle>
            <CardDescription>自定义应用的外观和显示</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">深色模式</p>
                <p className="text-sm text-muted-foreground">启用深色主题界面</p>
              </div>
              <Switch 
                checked={settings.darkMode} 
                onCheckedChange={(checked) => setSettings({...settings, darkMode: checked})}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5" />
              通知设置
            </CardTitle>
            <CardDescription>管理系统通知和提醒</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">系统通知</p>
                <p className="text-sm text-muted-foreground">接收数据同步和系统更新通知</p>
              </div>
              <Switch 
                checked={settings.notifications} 
                onCheckedChange={(checked) => setSettings({...settings, notifications: checked})}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCw className="w-5 h-5" />
              数据同步
            </CardTitle>
            <CardDescription>配置数据自动同步选项</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">自动同步</p>
                <p className="text-sm text-muted-foreground">定期自动同步基金数据</p>
              </div>
              <Switch 
                checked={settings.autoSync} 
                onCheckedChange={(checked) => setSettings({...settings, autoSync: checked})}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="font-medium mb-2">同步间隔（小时）</p>
                <Input 
                  type="number" 
                  value={settings.syncInterval}
                  onChange={(e) => setSettings({...settings, syncInterval: e.target.value})}
                />
              </div>
              <div>
                <p className="font-medium mb-2">数据保留天数</p>
                <Input 
                  type="number" 
                  value={settings.dataRetention}
                  onChange={(e) => setSettings({...settings, dataRetention: e.target.value})}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              安全设置
            </CardTitle>
            <CardDescription>配置API访问和安全选项</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="font-medium mb-2">API超时时间（秒）</p>
              <Input 
                type="number" 
                value={settings.apiTimeout}
                onChange={(e) => setSettings({...settings, apiTimeout: e.target.value})}
                className="max-w-xs"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5" />
              系统信息
            </CardTitle>
            <CardDescription>当前系统版本和状态</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">系统版本</p>
                <p className="font-medium">v1.0.0</p>
              </div>
              <div>
                <p className="text-muted-foreground">数据库版本</p>
                <p className="font-medium">SQLite 3.x</p>
              </div>
              <div>
                <p className="text-muted-foreground">数据源</p>
                <p className="font-medium">AKShare</p>
              </div>
              <div>
                <p className="text-muted-foreground">最后更新</p>
                <p className="font-medium">2026-02-14</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}