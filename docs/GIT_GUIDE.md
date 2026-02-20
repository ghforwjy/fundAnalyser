# Git 使用指南

> 基于 fundAnalyser 项目的实际操作经验总结

## 目录

1. [环境配置](#环境配置)
2. [项目初始化](#项目初始化)
3. [日常操作流程](#日常操作流程)
4. [常见问题解决](#常见问题解决)
5. [命令速查表](#命令速查表)

---

## 环境配置

### 1. 安装 Git

在 Windows PowerShell 中执行：

```powershell
# 下载 Git 安装包
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe" -OutFile "$env:TEMP\Git-2.43.0-64-bit.exe"

# 静默安装
& "$env:TEMP\Git-2.43.0-64-bit.exe" /VERYSILENT /NORESTART

# 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
```

**验证安装**：
```powershell
& 'C:\Program Files\Git\bin\git.exe' --version
```

### 2. 配置用户信息

```powershell
& 'C:\Program Files\Git\bin\git.exe' config --global user.email "179537@qq.com"
& 'C:\Program Files\Git\bin\git.exe' config --global user.name "ghforwjy"
```

---

## 项目初始化

### 1. 初始化 Git 仓库

```powershell
cd D:\mycode\fundAnalyser
& 'C:\Program Files\Git\bin\git.exe' init
```

### 2. 配置 .gitignore

创建 `.gitignore` 文件，排除不需要版本控制的文件：

```gitignore
# Dependencies
node_modules/
package-lock.json
yarn.lock
pnpm-lock.yaml

# Build outputs
dist/
build/
*.tsbuildinfo

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Cache
.cache/
*.cache
.eslintcache
.stylelintcache

# Test coverage
coverage/
.nyc_output/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database（根据需要决定是否忽略）
# *.db
# *.sqlite
# *.sqlite3

# Temporary files
*.tmp
*.temp
*.bak
*.backup
```

### 3. 添加远程仓库

```powershell
& 'C:\Program Files\Git\bin\git.exe' remote add origin https://github.com/ghforwjy/fundAnalyser.git
```

验证远程仓库：
```powershell
& 'C:\Program Files\Git\bin\git.exe' remote -v
```

---

## 日常操作流程

### 标准推送流程

```powershell
# 1. 进入项目目录
cd D:\mycode\fundAnalyser

# 2. 检查当前状态
& 'C:\Program Files\Git\bin\git.exe' status

# 3. 添加所有更改到暂存区
& 'C:\Program Files\Git\bin\git.exe' add .

# 4. 提交更改（编写有意义的提交信息）
& 'C:\Program Files\Git\bin\git.exe' commit -m "提交说明：添加了xxx功能"

# 5. 推送到远程仓库
& 'C:\Program Files\Git\bin\git.exe' push origin master
```

### 查看提交历史

```powershell
# 简洁格式
& 'C:\Program Files\Git\bin\git.exe' log --oneline -10

# 详细格式
& 'C:\Program Files\Git\bin\git.exe' log
```

### 查看分支状态

```powershell
& 'C:\Program Files\Git\bin\git.exe' branch -vv
```

---

## 常见问题解决

### 问题 1：git 命令找不到

**现象**：
```
'git' 不是内部或外部命令
```

**原因**：Git 未安装或未添加到环境变量

**解决**：
1. 安装 Git（见环境配置部分）
2. 使用完整路径调用：`& 'C:\Program Files\Git\bin\git.exe'`

---

### 问题 2：提交时提示需要配置用户名和邮箱

**现象**：
```
Author identity unknown
*** Please tell me who you are.
```

**解决**：
```powershell
& 'C:\Program Files\Git\bin\git.exe' config user.email "179537@qq.com"
& 'C:\Program Files\Git\bin\git.exe' config user.name "ghforwjy"
```

---

### 问题 3：误将 node_modules 等临时文件加入 git

**现象**：仓库体积过大，包含不必要的文件

**解决**：
```powershell
# 1. 从暂存区移除所有文件（保留工作目录）
& 'C:\Program Files\Git\bin\git.exe' rm -r --cached .

# 2. 确保 .gitignore 配置正确

# 3. 重新添加文件（此时 .gitignore 会生效）
& 'C:\Program Files\Git\bin\git.exe' add .

# 4. 提交更改
& 'C:\Program Files\Git\bin\git.exe' commit -m "清理临时文件，更新 .gitignore"
```

---

### 问题 4：SSH 推送失败

**现象**：
```
Permission denied (publickey)
fatal: Could not read from remote repository
```

**原因**：本地没有配置 SSH 密钥或密钥未添加到 GitHub

**解决**：改用 HTTPS 方式
```powershell
# 修改远程 URL 为 HTTPS
& 'C:\Program Files\Git\bin\git.exe' remote set-url origin https://github.com/ghforwjy/fundAnalyser.git
```

---

### 问题 5：推送时卡住无响应

**现象**：执行 push 命令后长时间没有输出

**可能原因**：
1. 网络连接问题
2. 终端环境问题
3. 需要输入用户名密码但未显示提示

**解决**：
1. 检查网络连接
2. 确保使用正确的终端路径
3. 等待命令完成（大型仓库首次推送可能需要几分钟）
4. 检查 GitHub 仓库是否存在且可访问

---

### 问题 6：数据库文件是否上传

**场景**：需要决定将 `.db` 文件是否加入版本控制

**方案 A：上传数据库文件**（适合小型项目或需要共享数据）
```gitignore
# 在 .gitignore 中注释掉数据库忽略规则
# *.db
# *.sqlite
# *.sqlite3
```

**方案 B：忽略数据库文件**（适合大型数据库或敏感数据）
```gitignore
# 在 .gitignore 中启用数据库忽略规则
*.db
*.sqlite
*.sqlite3
```

---

## 命令速查表

| 操作 | 命令 |
|------|------|
| 查看状态 | `& 'C:\Program Files\Git\bin\git.exe' status` |
| 添加文件 | `& 'C:\Program Files\Git\bin\git.exe' add .` |
| 提交更改 | `& 'C:\Program Files\Git\bin\git.exe' commit -m "说明"` |
| 推送到远程 | `& 'C:\Program Files\Git\bin\git.exe' push origin master` |
| 查看日志 | `& 'C:\Program Files\Git\bin\git.exe' log --oneline` |
| 查看分支 | `& 'C:\Program Files\Git\bin\git.exe' branch -vv` |
| 查看远程 | `& 'C:\Program Files\Git\bin\git.exe' remote -v` |
| 添加远程 | `& 'C:\Program Files\Git\bin\git.exe' remote add origin <url>` |
| 修改远程 | `& 'C:\Program Files\Git\bin\git.exe' remote set-url origin <url>` |
| 清理缓存 | `& 'C:\Program Files\Git\bin\git.exe' rm -r --cached .` |

---

## 最佳实践

1. **使用完整路径调用 Git**：在 Windows PowerShell 中，使用 `& 'C:\Program Files\Git\bin\git.exe'` 比直接使用 `git` 更可靠

2. **编写有意义的提交信息**：描述本次提交的主要变更内容

3. **定期推送**：避免积累大量未推送的提交

4. **检查 .gitignore**：确保敏感文件和临时文件不被上传

5. **验证推送结果**：推送后使用 `git branch -vv` 或查看 GitHub 仓库确认成功

---

## 相关链接

- GitHub 仓库：https://github.com/ghforwjy/fundAnalyser
- Git 官方文档：https://git-scm.com/doc
