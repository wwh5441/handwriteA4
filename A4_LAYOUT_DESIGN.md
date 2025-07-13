# A4中英文混排自动分页系统 - 程序设计文档

---
*文档更新于 2025年7月13日星期日*

## 1.bis 核心思想：A4排版总装线

经过深入讨论，我们将系统核心思想升级为“A4排版总装线”模型。此模型将抽象的软件流程类比为具体的工业装配线，使系统各模块的职责和数据流动更加清晰。

**工作总线**: 以**内容块 (Content Block)** 的流动为主线，以**页面行数 (Page Lines)** 和**行宽度 (Line Width)** 为严格的物理约束，驱动整个排版流程。

### 总装线流程图 (根据 v0.1.0 实现)

```
[Markdown File] -> [MarkdownParser] -> [List<ContentBlock>] -> [HandwrittenComposer] -> [List<Page>] -> [A4PageContainer] -> [HTML String] -> [.html File]
```

### 各工位详解 (根据 v0.1.0 实现)

| 装配线阶段 | 核心任务 | 输入 (Input) | 输出 (Output) | 实际对应模块 (`run_layout_engine.py`) |
| :--- | :--- | :--- | :--- | :--- |
| **1. 原材料分拣** | 将Markdown文本分拣成标准化的内容块 | `.md` 文件 | `List[ContentBlock]` | `markdown_parser.MarkdownParser` |
| **2. 核心排版** | 将内容块的文字铺排成带布局的页面 | `List[ContentBlock]` | `List[Page]` | `handwritten_composer.HandwrittenComposer` |
| **3. 渲染与包装** | 将页面对象渲染成最终的HTML文档 | `List[Page]` | `HTML String` | `page_container.A4PageContainer` |

这个模型是整个系统设计的基石，它强调了**数据驱动**和**单一职责**的设计原则。后续所有开发都将遵循此模型。

---

## 1. 总体架构设计

### 1.1 设计原则
- **单一职责**：每个模块只负责一个明确的功能
- **数据驱动**：基于标准化的MD文档输入
- **可测试性**：每个组件都可以独立测试
- **可配置性**：字体、尺寸等参数可配置

### 1.2 系统架构图
```
MD文档 → MD解析器 → 内容结构 → 布局引擎 → HTML生成器 → A4 HTML文档
  ↓         ↓          ↓         ↓          ↓           ↓
输入源    解析模块    数据层    核心算法    渲染模块     输出产品
```

## 2. 数据结构设计

### 2.1 输入格式标准
```markdown
# 主标题 (H1)
## 主题标题 (H2) 
正文段落内容...
```

### 2.2 内存数据结构
```python
ContentBlock = {
    'type': 'h1' | 'h2' | 'paragraph',
    'text': str,
    'metadata': dict
}

LayoutLine = {
    'text': str,
    'class': 'main-title' | 'section-title' | 'paragraph-start' | 'paragraph-continue',
    'width': float,
    'utilization': float
}

Page = {
    'lines': List[LayoutLine],
    'page_number': int,
    'line_count': int
}
```

## 3. 核心模块设计

### 3.1 MD解析器 (MarkdownParser)
**职责**：将MD文档解析为结构化数据

**接口**：
```python
class MarkdownParser:
    def parse_file(self, md_file_path: str) -> List[ContentBlock]:
        """解析MD文件，返回内容块列表"""
        pass
    
    def parse_text(self, md_text: str) -> List[ContentBlock]:
        """解析MD文本，返回内容块列表"""
        pass
```

**处理规则**：
- `# 标题` → ContentBlock(type='h1')
- `## 标题` → ContentBlock(type='h2')  
- 正文段落 → ContentBlock(type='paragraph')

### 3.2 手写报告铺排器 (HandwrittenComposer)
**职责**：模拟手写报告的逐行文字铺排过程

**设计理念**：像人写字一样，一行一行写，一行写满就换行

**接口**：
```python
class HandwrittenComposer:
    def __init__(self, config: LayoutConfig, char_calculator: CharWidthCalculator):
        """初始化铺排配置"""
        pass
    
    def compose_document(self, content_blocks: List[ContentBlock]) -> List[Page]:
        """铺排整个文档"""
        pass
    
    def compose_page(self, content_blocks: List[ContentBlock], page_number: int) -> Page:
        """铺排单页内容"""
        pass
    
    def create_line_space(self, block_type: str) -> Dict[str, Any]:
        """创建行空间"""
        pass
    
    def fill_line_handwritten(self, text: str, line_config: Dict) -> Tuple[str, str]:
        """手写式填充行"""
        pass
```

**核心算法 - 手写报告铺排流程**：

**Step 2.2: 行类型识别与空间分配**
- H1/H2标题 → 创建72px高度空间（2行），红色粗体
- P段落 → 创建36px高度空间（1行）
- 段落细分：
  - 首行：缩进2字符(43.6px) + 两端对齐
  - 正文行：无缩进 + 两端对齐  
  - 尾行：无缩进 + 左对齐

**Step 2.3: 逐字铺排算法**
```python
def handwritten_fill_algorithm(text: str, max_width: float) -> str:
    """手写填充算法"""
    current_line = ""
    for char in text:
        # 像写字一样，一个字一个字放入
        temp_line = current_line + char
        width = calculate_width(temp_line)
        
        if width <= max_width * 0.965:  # 96.5%基准
            current_line = temp_line
        else:
            # 尝试再写一个字/词
            next_char_width = get_next_unit_width(text, current_pos)
            if width + next_char_width <= max_width * 1.01:  # 101%容错
                current_line = temp_line  # 允许
            elif is_word_break and width + next_char_width <= max_width * 1.03:  # 103%拆词容错
                current_line = temp_line  # 允许拆词
            else:
                break  # 放弃，结束当前行
    return current_line
```

**Step 2.4: 页面计数器**
- 每页27行倒序器：`[27, 26, 25, ..., 3, 2, 1]`
- 行计数辅助：`remaining_lines = 27 - current_line_count`
- 每行独立HTML容器：`<p class="line-{line_number}">`

### 3.3 字符宽度计算器 (CharWidthCalculator)
**职责**：精确计算字符宽度

**接口**：
```python
class CharWidthCalculator:
    def get_char_width(self, char: str) -> float:
        """获取单个字符宽度"""
        pass
    
    def get_text_width(self, text: str) -> float:
        """获取文本总宽度"""
        pass
```

**字符分类**：
- 中文字符：17.5px
- 英文字母：11.0px  
- 数字字符：9.0px
- 标点符号：14.0px

### 3.4 分页器 (Paginator)
**职责**：将布局行分配到页面

**接口**：
```python
class Paginator:
    def paginate(self, lines: List[LayoutLine]) -> List[Page]:
        """将行分页"""
        pass
```

**分页规则**：
- 第一页：25行（含标题占用）
- 后续页：27行
- 标题占用额外空间

### 3.5 HTML生成器 (HTMLGenerator)
**职责**：生成A4格式的HTML文档

**接口**：
```python
class HTMLGenerator:
    def generate(self, pages: List[Page], config: HTMLConfig) -> str:
        """生成完整HTML文档"""
        pass
    
    def generate_page(self, page: Page, page_num: int) -> str:
        """生成单页HTML"""
        pass
```

## 4. 配置系统设计

### 4.1 布局配置 (LayoutConfig) ✅已实现
```python
@dataclass
class LayoutConfig:
    # A4页面尺寸 (基于CSS像素)
    page_width: int = 794          # A4宽度: 210mm
    page_height: int = 1123        # A4高度: 297mm
    
    # 页面边距设置
    margin_left: int = 48          # 左边距: 12.7mm
    margin_top: int = 71           # 上边距: 18.9mm
    margin_right: int = 48         # 右边距: 12.7mm
    margin_bottom: int = 71        # 下边距: 18.9mm
    
    # 文字区域计算
    text_area_width: int = 698     # 文字区域宽度: 794-48*2=698px
    text_area_height: int = 972    # 文字区域高度: 1123-71*2=972px
    
    # 字体设置 (所有文本统一字体大小)
    font_size: str = "15.9pt"      # 统一字体大小
    font_family: str = '"Microsoft YaHei", "微软雅黑", sans-serif'
    line_height: int = 36          # 行高: 36px
    
    # 标题设置 (字体大小与正文相同)
    main_title_font_size: str = "15.9pt"    # 主标题字体大小(与正文相同)
    section_title_font_size: str = "15.9pt"  # 二级标题字体大小(与正文相同)
    title_color: str = "#A60000"          # 标题颜色(红色)
    
    # 缩进设置
    paragraph_indent: float = 43.6  # 段首缩进: 2em ≈ 43.6px
    
    # 分页设置
    first_page_lines: int = 25     # 第一页最大行数(含标题占用)
    normal_page_lines: int = 27    # 普通页最大行数
```

### 4.2 HTML配置 (HTMLConfig)
```python
@dataclass 
class HTMLConfig:
    title: str = "A4自动分页文档"
    show_debug_info: bool = True
    show_page_borders: bool = True
    include_print_styles: bool = True
```

## 5. 程序入口设计

### 5.1 主程序 (main.py)
```python
def main(md_file: str, output_file: str):
    """主程序入口"""
    
    # 1. 解析MD文档
    parser = MarkdownParser()
    content_blocks = parser.parse_file(md_file)
    
    # 2. 布局处理
    layout_config = LayoutConfig()
    layout_engine = LayoutEngine(layout_config)
    lines = layout_engine.layout_content(content_blocks)
    
    # 3. 分页处理
    paginator = Paginator()
    pages = paginator.paginate(lines)
    
    # 4. 生成HTML
    html_config = HTMLConfig()
    html_generator = HTMLGenerator()
    html_content = html_generator.generate(pages, html_config)
    
    # 5. 保存文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 生成完成: {output_file}")
    print(f"📊 总页数: {len(pages)}")
```

## 6. 文件结构设计

```
a4_layout_system/
├── main.py                    # 主程序入口
├── config.py                  # 配置类定义
├── parsers/
│   └── markdown_parser.py     # MD解析器
├── layout/
│   ├── layout_engine.py       # 布局引擎
│   ├── char_width.py          # 字符宽度计算
│   └── paginator.py           # 分页器
├── generators/
│   └── html_generator.py      # HTML生成器
├── tests/
│   ├── test_parser.py         # 解析器测试
│   ├── test_layout.py         # 布局引擎测试
│   └── test_generator.py      # 生成器测试
└── assets/
    ├── ai_report_5000words.md # 测试文档
    └── templates/
        └── page_template.html # HTML模板
```

## 7. 开发顺序与进度

### ✅ Phase 1: 基础架构 (已完成)
1. ✅ 创建配置系统 (config.py)
2. ✅ 创建A4页面容器 (page_container.py)
3. ✅ HTML结构与CSS样式系统
4. ✅ 基础测试验证

### 🔄 Phase 2: 核心算法 (进行中)
1. ✅ 实现字符宽度计算器 (char_width.py)
2. 🔄 实现手写报告铺排器 (handwritten_composer.py)
3. 实现MD解析器 (markdown_parser.py)
4. 测试真实内容布局效果

### Phase 3: 分页与输出
1. 实现分页器 (paginator.py)
2. 实现HTML生成器 (html_generator.py)
3. 整合主程序 (main.py)

### Phase 4: 优化完善
1. 性能优化
2. 边缘情况处理
3. 完善测试覆盖

## 8. 质量标准

### 8.1 功能要求
- ✅ 支持H1/H2标题和正文段落
- ✅ 精确的A4页面布局
- ✅ 正确的段首缩进和行对齐
- ✅ 自动分页和页眉页脚

### 8.2 性能要求
- 5000字文档处理时间 < 1秒
- 内存使用 < 50MB
- 支持10万字长文档

### 8.3 代码质量
- 单元测试覆盖率 > 80%
- 类型注解完整
- 文档字符串完整
- 代码风格符合PEP8

## 9. 实际实现进展

### 9.1 已完成模块

#### ✅ config.py - 配置系统
- **功能**: 完整的布局和HTML配置类
- **特点**: 数据类设计，参数可配置，包含辅助方法
- **验证**: 通过测试，配置数据正确加载

#### ✅ page_container.py - A4页面容器
- **功能**: 完整的A4页面HTML结构生成
- **特点**: 
  - 精确的A4尺寸控制 (794×1123px)
  - 规范的文字区域定位 (698×972px)  
  - 完整的CSS样式系统
  - 页眉页脚自动生成
  - 调试信息面板
  - 打印样式优化
- **验证**: 生成测试文件 `test_page_container.html`

#### ✅ char_width.py - 字符宽度计算器
- **功能**: 精确的中英文混合字符宽度计算
- **特点**:
  - 支持7种字符类型分类 (中文、英文大小写、数字、标点、空格、特殊符号)
  - 基于15.9pt字体的精确宽度映射
  - 智能行适配算法 (96.5%基准 + 101%/103%容错)
  - 行宽利用率计算 (测试达到99.5%利用率)
- **验证**: 通过完整测试，支持复杂中英文混排

#### ✅ 字体规范统一
- **重要更新**: 所有文本(主标题、二级标题、正文)统一使用 **15.9pt** 字体
- **设计理念**: 通过粗体和颜色区分标题，而非字体大小

### 9.2 技术规格确认

| 规格项目 | 设计值 | 实现值 | 状态 |
|---------|-------|-------|------|
| 页面尺寸 | 794×1123px | 794×1123px | ✅ |
| 文字区域 | 698×972px | 698×972px | ✅ |
| 页面边距 | 48px左右, 71px上下 | 48px左右, 71px上下 | ✅ |
| 字体大小 | 15.9pt统一 | 15.9pt统一 | ✅ |
| 行高 | 36px | 36px | ✅ |
| 段首缩进 | 43.6px(2em) | 43.6px | ✅ |
| 第一页行数 | 25行 | 25行 | ✅ |
| 普通页行数 | 27行 | 27行 | ✅ |

### 9.3 测试验证文件
- **输入源**: `ai_report_5000words.md` (2个H1, 19个H2, 20个段落, 3883字符)
- **页面容器**: `test_page_container.html` (A4结构验证)
- **配置验证**: 所有参数通过配置系统正确加载

### 9.4 下一步计划
- **Phase 2**: 实现字符宽度计算器和布局引擎
- **目标**: 将MD内容填充到A4容器中，实现自动换行和分页

---

**设计版本**: v1.1  
**创建日期**: 2025-01-13  
**更新日期**: 2025-01-13  
**设计原则**: 简单、可靠、可维护  
**实现状态**: Phase 1 完成，Phase 2 进行中