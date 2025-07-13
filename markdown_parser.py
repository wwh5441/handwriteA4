#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown解析器模块
将Markdown文件解析为结构化的ContentBlock列表
"""

from typing import List
from handwritten_composer import ContentBlock

class MarkdownParser:
    """
    一个简单的Markdown解析器，用于将特定格式的Markdown文件
    转换为ContentBlock对象列表。
    
    支持的格式:
    - H1: # 标题
    - H2: ## 标题
    - Paragraph: 普通文本段落，由空行分隔
    """

    def parse_file(self, file_path: str) -> List[ContentBlock]:
        """
        解析指定的Markdown文件。

        Args:
            file_path: Markdown文件的路径。

        Returns:
            一个包含ContentBlock对象的列表。
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        return self.parse_lines(lines)

    def parse_lines(self, lines: List[str]) -> List[ContentBlock]:
        """
        解析一个字符串行列表。

        Args:
            lines: 从文件中读取的行列表。

        Returns:
            一个包含ContentBlock对象的列表。
        """
        blocks: List[ContentBlock] = []
        paragraph_buffer: List[str] = []

        def flush_paragraph_buffer():
            """将段落缓冲区的内容打包成一个块并清空缓冲区。"""
            if paragraph_buffer:
                paragraph_text = "".join(paragraph_buffer).strip()
                if paragraph_text:
                    blocks.append(ContentBlock(type='paragraph', text=paragraph_text))
                paragraph_buffer.clear()

        for line in lines:
            stripped_line = line.strip()

            if not stripped_line or stripped_line == '---' or stripped_line.startswith('>'):
                # 忽略空行、分隔线和引用行
                flush_paragraph_buffer()
                continue

            if stripped_line.startswith('# '):
                flush_paragraph_buffer()
                blocks.append(ContentBlock(type='h1', text=stripped_line.lstrip('# ').strip()))
            elif stripped_line.startswith('## '):
                flush_paragraph_buffer()
                blocks.append(ContentBlock(type='h2', text=stripped_line.lstrip('## ').strip()))
            else:
                # 将非空行添加到段落缓冲区
                paragraph_buffer.append(line)
        
        # 处理文件末尾可能存在的最后一个段落
        flush_paragraph_buffer()

        return blocks

def test_markdown_parser():
    """测试Markdown解析器"""
    print("🔧 开始测试Markdown解析器...")
    
    parser = MarkdownParser()
    md_file = 'ai_report_5000words.md'
    
    print(f"📄 正在解析文件: {md_file}")
    content_blocks = parser.parse_file(md_file)
    
    print(f"\n✅ 解析完成！总共生成 {len(content_blocks)} 个内容块。")
    
    print("\n📦 前5个内容块 (零件箱) 预览:")
    for i, block in enumerate(content_blocks[:5]):
        print(f"  --- Block {i+1} ---")
        print(f"  Type: {block.type}")
        print(f"  Text: '{block.text[:50]}...'") # 预览前50个字符
        
    # 验证块的类型是否正确
    expected_types = ['h1', 'h1', 'h2', 'paragraph', 'h2']
    print("\n🔍 验证前5个块的类型:")
    for i, block in enumerate(content_blocks[:5]):
        expected = expected_types[i]
        status = "✅" if block.type == expected else "❌"
        print(f"  {status} Block {i+1}: 类型为 '{block.type}' (期望: '{expected}')")

if __name__ == "__main__":
    test_markdown_parser()
