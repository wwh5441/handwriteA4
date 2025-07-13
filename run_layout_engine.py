#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A4排版总装线 - 主运行程序
"""

import os
import asyncio
from playwright.async_api import async_playwright
from markdown_parser import MarkdownParser
from handwritten_composer import HandwrittenComposer
from page_container import A4PageContainer
from config import LayoutConfig, HTMLConfig

async def generate_pdf_from_html(html_file_path, output_filename_base):
    """
    使用Playwright将HTML转换为PDF
    """
    print("🖨️  启动PDF生成器...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # 加载HTML文件
        file_url = f"file://{os.path.abspath(html_file_path)}"
        await page.goto(file_url)
        
        # 等待页面完全加载
        await page.wait_for_timeout(2000)
        
        # PDF输出路径
        pdf_path = f"{output_filename_base}.pdf"
        
        # 生成PDF，使用A4纸张规格
        await page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={
                "top": "0mm",
                "bottom": "0mm", 
                "left": "0mm",
                "right": "0mm"
            }
        )
        
        await browser.close()
        print(f"📄 成功生成PDF文件: '{pdf_path}'")
        return pdf_path

async def run_assembly_line(blocks_to_process, output_filename_base):
    """
    运行总装线，处理指定的内容块并生成HTML和PDF输出。
    """
    print(f"🏭 总装线启动，准备处理 {len(blocks_to_process)} 个内容块...")

    # --- 工位2 & 3: 核心部件组装 与 总装 ---
    # 将ContentBlock列表转换为Page列表
    print("🖋️  进入手写铺排器 (HandwrittenComposer)...")
    composer = HandwrittenComposer()
    pages = composer.compose_document(blocks_to_process)
    print(f"📄 铺排完成，生成了 {len(pages)} 页内容。")

    # --- 工位4: 喷漆与包装 ---
    # 将Page列表转换为最终的HTML文档
    print("🎨 进入A4页面容器 (A4PageContainer)...")
    
    # 数据格式转换：将 List[Page] 转换为 List[Dict]
    pages_content = []
    for page in pages:
        # 将每页的LayoutLine对象转换为HTML字符串，行号只加在data属性中
        html_lines = []
        for line in page.lines:
            line_display = getattr(line, 'line_display', str(line.line_number))
            html_lines.append(f'            <div class="{line.css_class}" data-line="{line_display}">{line.text}</div>')
        
        pages_content.append({
            'header': 'A4排版总装线 - 测试输出',
            'content': '\n'.join(html_lines)
        })

    container = A4PageContainer()
    full_html = container.generate_html_document(
        pages_content, 
        document_title=output_filename_base
    )

    # --- 保存HTML文件 ---
    output_html_path = f"{output_filename_base}.html"
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    print(f"✅ 成功生成HTML文件: '{output_html_path}'")
    
    # --- 工位5: PDF转换与导出 ---
    pdf_path = await generate_pdf_from_html(output_html_path, output_filename_base)
    
    return output_html_path, pdf_path

async def main():
    """主函数"""
    print("--- A4排版总装线启动 ---")
    
    # --- 工位1: 原材料分拣 ---
    print("📦 进入Markdown解析器 (MarkdownParser)...")
    parser = MarkdownParser()
    all_blocks = parser.parse_file('ai_report_5000words.md')
    print(f"🔩 成功分拣出 {len(all_blocks)} 个零件箱 (ContentBlocks)。")

    # --- 处理所有内容块 (完整5000字版本) ---
    blocks_for_processing = all_blocks  # 使用全部42个blocks
    
    print(f"📋 所有{len(blocks_for_processing)}个blocks预览:")
    for i, block in enumerate(blocks_for_processing, 1):
        print(f"  {i}. [{block.type}] {block.text[:40]}...")
        if i >= 10:  # 只显示前10个预览
            print(f"  ... 还有{len(blocks_for_processing)-10}个blocks")
            break
    
    # --- 运行总装线 ---
    html_path, pdf_path = await run_assembly_line(blocks_for_processing, "A4_complete_5000words_demo")
    
    print("\n--- A4排版总装线运行结束 ---")
    print(f"🏆 最终产品:")
    print(f"   📄 HTML文件: {html_path}")
    print(f"   📄 PDF文件: {pdf_path}")


if __name__ == "__main__":
    asyncio.run(main())
