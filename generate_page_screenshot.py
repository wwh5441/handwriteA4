#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成页面截图工具
"""

import asyncio
from playwright.async_api import async_playwright
import os

async def capture_first_page_screenshot(html_file_path: str, output_path: str = None):
    """截取HTML文件第一页的截图
    
    Args:
        html_file_path: HTML文件路径
        output_path: 输出PNG路径，默认为同目录下的同名PNG文件
    """
    
    if not os.path.exists(html_file_path):
        raise FileNotFoundError(f"HTML文件不存在: {html_file_path}")
    
    if output_path is None:
        output_path = html_file_path.replace('.html', '_page1.png')
    
    print(f"📸 开始截取页面截图...")
    print(f"   HTML文件: {html_file_path}")
    print(f"   输出文件: {output_path}")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 设置页面尺寸（稍大一些以容纳页面周围的空白）
        await page.set_viewport_size({"width": 1000, "height": 1400})
        
        # 加载HTML文件
        file_url = f"file://{os.path.abspath(html_file_path)}"
        await page.goto(file_url)
        
        # 等待页面加载完成
        await page.wait_for_load_state('networkidle')
        
        # 等待字体加载
        await asyncio.sleep(2)
        
        # 查找第一个页面元素
        first_page = await page.query_selector('.page')
        if not first_page:
            raise ValueError("未找到页面元素(.page)")
        
        # 截取第一页的截图
        await first_page.screenshot(path=output_path, type='png')
        
        # 关闭浏览器
        await browser.close()
    
    print(f"✅ 截图完成: {output_path}")
    return output_path

async def main():
    """主函数"""
    html_file = '/Users/wangweihan/Desktop/TechForesight_0710/A4_full_layout_test.html'
    
    try:
        screenshot_path = await capture_first_page_screenshot(html_file)
        print(f"\n🎉 第一页截图已生成!")
        print(f"📁 文件位置: {screenshot_path}")
        print(f"📐 可以查看当前排版效果，识别需要调整的问题")
        
        return screenshot_path
        
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        print("💡 请确保已安装 playwright: pip install playwright")
        print("💡 并安装浏览器: playwright install chromium")
        return None

if __name__ == "__main__":
    asyncio.run(main())