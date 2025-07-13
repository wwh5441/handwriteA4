# TechForesight A4 自动排版引擎 (v0.1.0)

TechForesight A4 自动排版引擎是一个能将指定的 Markdown 文件自动、精确地排版成 A4 页面格式的工具，并可输出为 HTML 和 PNG 格式。

## 功能特性

- **精准的字符级宽度计算**：支持中英文、数字、标点符号的混合排版。
- **自动化A4页面布局**：严格按照 A4 纸张的物理尺寸进行内容填充和分页。
- **Markdown 输入**：支持 H1、H2 标题和标准段落作为输入。
- **多格式输出**：可生成 HTML 文件用于预览，并可进一步生成 PNG 格式的页面截图。

## 使用说明

本说明针对已打包的 `forgit0714` 版本。

### 1. 环境要求

- Python 3.9+
- pip (Python 包管理器)

### 2. 安装依赖

在开始之前，请确保已安装所有必需的 Python 包和浏览器核心。

**(1) 安装 Python 依赖包:**

打开终端，进入 `forgit0714` 目录，然后运行以下命令：

```bash
pip install -r requirements.txt
```

**(2) 安装 Playwright 浏览器依赖:**

本工具使用 Playwright 生成页面截图，它需要一个浏览器核心。请运行以下命令进行安装（仅需首次运行）：

```bash
playwright install chromium
```
*注意：此步骤会下载一个浏览器内核，需要一些时间。*

### 3. 如何运行

一切准备就绪后，运行主脚本即可开始排版。

```bash
python3 run_layout_engine.py
```

### 4. 查看产物

脚本运行成功后，将在 `forgit0714` 目录下生成以下文件：

- `A4_first_4_blocks_demo.html`: 排版结果的HTML文件。
- `A4_first_4_blocks_demo.png`: 第一页的PNG截图。

你可以直接在浏览器中打开 `.html` 文件，或查看 `.png` 图片来检查排版效果。

---
*原始项目文档保留在下方。*

# TechForesight

TechForesight 是一个 AI 技术资讯分析工具，用于自动收集、分析和生成 AI 相关的技术资讯报告。

## 快速开始

### 环境要求

- Python 3.10
- 虚拟环境 py310foruse
- Unix-like 操作系统 (Linux/macOS)

### 一键启动

```bash
# 给启动脚本添加执行权限
chmod +x start.sh

# 运行启动脚本
./start.sh
```

### 手动安装步骤

1. 确保已安装 Python 3.10
```bash
python3.10 --version
```

2. 创建虚拟环境（如果尚未创建）
```bash
python3.10 -m venv py310foruse
```

3. 激活虚拟环境
```bash
source py310foruse/bin/activate
```

4. 安装依赖
```bash
pip install -r requirements.txt
```

5. 安装 Playwright 依赖
```bash
playwright install
playwright install-deps
```

### 环境打包

如果需要将环境打包以便在其他机器上使用，可以使用以下方法：

1. 使用 pip freeze 导出完整依赖
```bash
pip freeze > requirements_full.txt
```

2. 使用 venv-pack 打包虚拟环境（需要先安装 venv-pack）
```bash
pip install venv-pack
venv-pack -o py310foruse.tar.gz
```

3. 在新机器上解压和使用
```bash
mkdir -p py310foruse
tar xzf py310foruse.tar.gz -C py310foruse
source py310foruse/bin/activate
```

## 配置

1. 确保 `weixin_credentials.json` 文件存在并包含正确的凭据
2. 确保 Google API 密钥已正确配置

## 故障排除

如果遇到问题：

1. 检查 Python 版本是否为 3.10
2. 确保虚拟环境已正确激活
3. 检查依赖是否完整安装
4. 查看日志文件获取详细错误信息

## 许可证

版权所有 © 2024 