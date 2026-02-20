# 基金数据库管理系统 - 使用指南

## 项目结构

```
fund_platform/
├── backend/              # Python FastAPI 后端
│   ├── main.py          # 后端主程序
│   └── fund.db          # SQLite数据库(自动创建)
├── app/                  # React 前端
│   ├── src/
│   ├── dist/            # 构建输出
│   └── package.json
└── README.md            # 本文件
```

## 运行方式

### 方式一：本地开发运行（推荐）

#### 1. 启动后端服务

```bash
cd fund_platform/backend
python main.py
```

后端服务将在 http://localhost:8000 启动

#### 2. 启动前端开发服务器

```bash
cd fund_platform/app
npm run dev
```

前端将在 http://localhost:5173 启动

#### 3. 访问系统

打开浏览器访问 http://localhost:5173

---

### 方式二：生产部署运行

#### 1. 构建前端

```bash
cd fund_platform/app
npm run build
```

#### 2. 启动后端（同时提供前端静态文件）

修改 `backend/main.py`，添加静态文件服务：

```python
from fastapi.staticfiles import StaticFiles

# 在app创建后添加
app.mount("/", StaticFiles(directory="../app/dist", html=True), name="static")
```

然后启动：

```bash
cd fund_platform/backend
python main.py
```

访问 http://localhost:8000

---

## 当前部署说明

**问题**：前端已部署到公网，但后端运行在本地 localhost:8000，导致前端无法连接后端。

**解决方案**：

### 方案1：本地运行（推荐测试使用）

1. 下载项目到本地电脑
2. 安装Python依赖：`pip install fastapi uvicorn`
3. 启动后端：`python backend/main.py`
4. 安装Node.js依赖：`cd app && npm install`
5. 启动前端：`npm run dev`
6. 访问 http://localhost:5173

### 方案2：部署后端到公网

需要将后端服务部署到有公网IP的服务器上，然后修改前端代码中的API地址。

修改 `app/src/pages/DataManage/TableData.tsx` 和 `DataSource.tsx` 中的：

```typescript
const API_BASE_URL = 'http://你的服务器IP:8000/api';
```

---

## 功能说明

### 1. 表数据浏览
- 路径：数据管理 → 表数据
- 功能：查看数据库中所有表的数据
- 支持：分页、搜索、表切换

### 2. 数据源配置
- 路径：数据管理 → 数据源配置
- 功能：配置AKShare/Tushare数据源
- 支持：测试连接、编辑配置、启动数据采集

### 3. 数据采集
- 路径：数据源配置 → 启动数据采集
- 功能：创建采集任务，后台执行
- 支持：查看任务进度和状态

### 4. 基金列表
- 路径：基金分析 → 基金列表
- 功能：查看基金基本信息
- 支持：搜索、分页

---

## API 接口

启动后端后，访问 http://localhost:8000/docs 查看完整API文档

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/health | GET | 健康检查 |
| /api/data-sources | GET | 获取数据源列表 |
| /api/data-sources/{id}/test | POST | 测试数据源连接 |
| /api/collection/tasks | GET | 获取采集任务列表 |
| /api/collection/tasks | POST | 创建采集任务 |
| /api/database/tables | GET | 获取所有数据表 |
| /api/database/tables/{name}/data | GET | 获取表数据 |
| /api/funds | GET | 获取基金列表 |

---

## 数据库表

系统包含以下数据表：

| 表名 | 说明 | 记录数 |
|------|------|--------|
| data_sources | 数据源配置表 | 2 |
| collection_tasks | 采集任务表 | 动态 |
| fund_basic | 基金基础信息表 | 5 |

---

## 技术栈

- **后端**：Python + FastAPI + SQLite
- **前端**：React + TypeScript + Tailwind CSS + shadcn/ui

---

## 常见问题

### Q: 前端提示"连接后端服务失败"
A: 后端服务未启动或前端无法访问后端。请确保：
1. 后端服务已启动（python main.py）
2. 前端和后端在同一台机器上运行
3. 没有防火墙阻止8000端口

### Q: 如何修改API地址？
A: 修改以下文件中的 `API_BASE_URL`：
- `app/src/pages/DataManage/TableData.tsx`
- `app/src/pages/DataManage/DataSource.tsx`

### Q: 如何添加更多基金数据？
A: 在数据源配置页面点击"启动数据采集"，创建采集任务后会自动添加数据。

---

## 开发计划

- [x] 基础数据表设计
- [x] 后端API开发
- [x] 前端界面开发
- [x] 数据采集功能
- [ ] AKShare真实数据接入
- [ ] Tushare真实数据接入
- [ ] 基金净值历史数据
- [ ] 指标计算功能
