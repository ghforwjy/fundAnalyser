# ComfyUI 安装与配置指南

本文档提供了在本地环境中安装和配置 ComfyUI 的详细步骤，以及如何安装 RunningHub 节点和千问 VAE 模型。

## 目录

1. [ComfyUI 安装](#comfyui-安装)
2. [RunningHub 节点安装](#runninghub-节点安装)
3. [千问 VAE 模型下载与安装](#千问-vae-模型下载与安装)

---

## ComfyUI 安装

### 步骤 1：下载 ComfyUI

1. 访问 ComfyUI GitHub 仓库：[https://github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)
2. 点击 "Code" 按钮，选择 "Download ZIP" 下载完整代码包
3. 解压下载的 ZIP 文件到本地目录，例如 `D:\ComfyUI`

### 步骤 2：安装依赖

1. 确保已安装 Python 3.10 或更高版本
2. 打开命令提示符，导航到 ComfyUI 目录
3. 执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### 步骤 3：启动 ComfyUI

1. 在 ComfyUI 目录中执行 `run_nvidia_gpu.bat`（如果有 NVIDIA GPU）或 `run_cpu.bat`（仅使用 CPU）
2. 等待启动完成后，在浏览器中访问 `http://localhost:8188` 打开 ComfyUI 界面

---

## RunningHub 节点安装

### 步骤 1：下载 RunningHub 节点

1. 访问 RunningHub GitHub 仓库：[https://github.com/RunningHubAI/RunningHub-Nodes](https://github.com/RunningHubAI/RunningHub-Nodes)
2. 点击 "Code" 按钮，选择 "Download ZIP" 下载完整代码包

### 步骤 2：安装节点

1. 解压下载的 ZIP 文件
2. 将解压后的 `RunningHub-Nodes` 文件夹复制到 ComfyUI 的 `custom_nodes` 目录中
   - 例如：`D:\ComfyUI\custom_nodes\RunningHub-Nodes`

### 步骤 3：安装节点依赖

1. 打开命令提示符，导航到 `RunningHub-Nodes` 目录
2. 执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### 步骤 4：重启 ComfyUI

1. 关闭当前运行的 ComfyUI 实例
2. 重新启动 ComfyUI
3. 在 ComfyUI 界面中，您应该能够在节点列表中看到 RunningHub 相关节点

---

## 千问 VAE 模型下载与安装

### 步骤 1：下载千问 VAE 模型

千问 VAE 模型下载地址：

- [qwen_image_vae.safetensors](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct/resolve/main/qwen_image_vae.safetensors)

### 步骤 2：安装模型

1. 下载完成后，将 `qwen_image_vae.safetensors` 文件复制到 ComfyUI 的 `models\vae` 目录中
   - 例如：`D:\ComfyUI\models\vae\qwen_image_vae.safetensors`

### 步骤 3：在 ComfyUI 中使用模型

1. 重启 ComfyUI
2. 在 ComfyUI 界面中，添加一个 "Load VAE" 节点
3. 在 "VAE" 下拉菜单中，选择 "qwen_image_vae.safetensors"
4. 连接该节点到您的工作流中

### 注意事项

- 确保模型文件名称正确，避免重命名
- 如果在下拉菜单中没有看到模型，请检查文件路径是否正确
- 千问 VAE 模型适用于处理中文图像和多模态任务，能够提供更好的图像理解和生成效果

---

## 验证安装

安装完成后，您可以通过以下步骤验证所有组件是否正确安装：

1. 启动 ComfyUI
2. 检查节点列表中是否有 RunningHub 相关节点
3. 检查 VAE 模型列表中是否有千问 VAE 模型
4. 创建一个简单的工作流，测试节点和模型是否正常工作

如果遇到任何问题，请检查文件路径是否正确，依赖是否完全安装，以及 ComfyUI 是否以管理员权限运行。