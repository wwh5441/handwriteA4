#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A4页面容器生成模块
"""

from config import LayoutConfig, HTMLConfig
from typing import List, Dict, Any
from datetime import datetime

class A4PageContainer:
    """A4页面容器生成器"""
    
    def __init__(self, layout_config: LayoutConfig = None, html_config: HTMLConfig = None):
        self.layout_config = layout_config or LayoutConfig()
        self.html_config = html_config or HTMLConfig()
        
    def generate_css_styles(self) -> str:
        """生成页面CSS样式"""
        
        css = f'''
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {self.layout_config.font_family};
            font-size: {self.layout_config.font_size};
            line-height: {self.layout_config.line_height}px;
            background-color: {self.html_config.background_color};
            padding: 20px;
            color: #333;
        }}
        
        .page {{
            width: {self.layout_config.page_width}px;
            height: {self.layout_config.page_height}px;
            background-color: white;
            margin: 0 auto 20px auto;
            box-shadow: {self.html_config.page_shadow};
            position: relative;
            page-break-after: always;
        }}
        
        .text-area {{
            position: absolute;
            left: {self.layout_config.margin_left}px;
            top: {self.layout_config.margin_top}px;
            width: {self.layout_config.text_area_width}px;
            height: {self.layout_config.text_area_height}px;
            font-size: {self.layout_config.font_size};
            line-height: {self.layout_config.line_height}px;
            font-weight: normal;
            border: {self.html_config.border_style if self.html_config.show_page_borders else 'none'};
        }}
        
        .page-header {{
            position: absolute;
            top: {self.layout_config.margin_top - 40}px;
            left: {self.layout_config.margin_left}px;
            right: {self.layout_config.margin_right}px;
            height: {self.layout_config.header_height}px;
            text-align: center;
            font-size: 12pt;
            color: #666;
            line-height: {self.layout_config.header_height}px;
        }}
        
        .page-footer {{
            position: absolute;
            bottom: {self.layout_config.margin_bottom - 40}px;
            left: {self.layout_config.margin_left}px;
            right: {self.layout_config.margin_right}px;
            height: {self.layout_config.footer_height}px;
            text-align: center;
            font-size: 10pt;
            color: #999;
            line-height: {self.layout_config.footer_height}px;
        }}
        
        /* 文本样式 */
        .bt1 {{
            margin: 0;
            padding: 0;
            font-size: {self.layout_config.font_size};
            font-family: {self.layout_config.font_family};
            font-weight: bold;
            color: {self.layout_config.title_color};
            height: 72px;
            line-height: 72px;
            text-align: left !important;
            text-align-last: left !important;
        }}
        
        /* 标题样式 */
        .bt1, .bt2 {{
            font-weight: bold;
            color: {self.layout_config.title_color};
            height: 72px;
            line-height: 72px;
            text-align: left !important;
            text-align-last: left !important;
        }}
        
        /* 段落样式 */
        .zw1, .zw2, .zw3 {{
            font-weight: normal;
            height: {self.layout_config.line_height}px;
            line-height: {self.layout_config.line_height}px;
            text-align: justify;
            text-align-last: justify;  /* 确保最后一行也两端对齐 */
            word-spacing: 0.1em;       /* 增加单词间距以改善justify效果 */
            letter-spacing: 0.02em;    /* 轻微字符间距调整 */
        }}

        .zw1 {{
            text-indent: {self.layout_config.paragraph_indent}px;
        }}
        
        .zw2 {{
            text-indent: 0;
        }}

        .zw3 {{
            text-indent: 0;
            text-align: left !important;           /* 段落最后一行左对齐 */
            text-align-last: left !important;     /* 确保最后一行左对齐 */
            word-spacing: normal;                  /* 最后一行恢复正常间距 */
            letter-spacing: normal;               /* 最后一行恢复正常间距 */
        }}
        
        /* 调试信息面板 */
        .debug-info {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-size: 11px;
            z-index: 1000;
            max-width: 300px;
            display: {'block' if self.html_config.show_debug_info else 'none'};
        }}
        
        /* 打印样式 */
        @media print {{
            body {{ 
                background: white; 
                padding: 0; 
            }}
            .page {{ 
                margin: 0; 
                box-shadow: none; 
                page-break-after: always;
            }}
            .text-area {{ 
                border: none; 
            }}
            .debug-info {{ 
                display: none; 
            }}
        }}
        '''
        
        return css
    
    def generate_debug_info(self) -> str:
        """生成调试信息面板"""
        if not self.html_config.show_debug_info:
            return ""
        
        page_info = self.layout_config.get_page_info()
        
        debug_html = f'''
        <div class="debug-info">
            <strong>🔧 A4页面容器信息</strong><br>
            📄 页面尺寸: {page_info['page_size']}<br>
            📝 文字区域: {page_info['text_area']}<br>
            📏 页面边距: {page_info['margins']}<br>
            🔤 字体设置: {page_info['font']}<br>
            📐 行高: {page_info['line_height']}<br>
            📊 第一页: {page_info['first_page_lines']}行<br>
            📊 普通页: {page_info['normal_page_lines']}行<br>
            ⏰ 生成时间: {datetime.now().strftime('%H:%M:%S')}
        </div>
        '''
        
        return debug_html
    
    def generate_page_structure(self, page_number: int, total_pages: int, 
                              header_text: str = "", content: str = "") -> str:
        """生成单页结构"""
        
        page_html = f'''
    <!-- 第{page_number}页 -->
    <div class="page">
        <div class="page-header">{header_text}</div>
        <div class="text-area">
{content}
        </div>
        <div class="page-footer">第 {page_number} 页 | 共 {total_pages} 页 | A4自动分页系统</div>
    </div>'''
        
        return page_html
    
    def generate_html_document(self, pages_content: List[Dict[str, Any]], 
                             document_title: str = "") -> str:
        """生成完整HTML文档"""
        
        # 生成CSS样式
        css_styles = self.generate_css_styles()
        
        # 生成调试信息
        debug_info = self.generate_debug_info()
        
        # 文档标题
        doc_title = document_title or self.html_config.title
        
        # HTML文档结构
        html_doc = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{doc_title}</title>
    <style>{css_styles}</style>
</head>
<body>
{debug_info}
'''
        
        # 添加所有页面
        total_pages = len(pages_content)
        for i, page_data in enumerate(pages_content, 1):
            page_html = self.generate_page_structure(
                page_number=i,
                total_pages=total_pages,
                header_text=page_data.get('header', ''),
                content=page_data.get('content', '')
            )
            html_doc += page_html + '\n'
        
        # 闭合标签
        html_doc += '''
    <script>
        console.log('📄 A4页面容器已生成');
        console.log('总页数:', document.querySelectorAll('.page').length);
        console.log('页面配置:', {
            pageSize: '794×1123px',
            textArea: '698×972px',
            lineHeight: '36px',
            fontSize: '15.9pt'
        });
    </script>
</body>
</html>'''
        
        return html_doc

def test_page_container():
    """测试页面容器生成"""
    
    print("🔧 开始测试A4页面容器生成...")
    
    # 创建配置
    layout_config = LayoutConfig()
    html_config = HTMLConfig()
    
    # 创建页面容器
    container = A4PageContainer(layout_config, html_config)
    
    # 输出配置信息到日志
    page_info = layout_config.get_page_info()
    text_area_pos = layout_config.get_text_area_position()
    
    print("\n📊 页面设计数据已加载:")
    print(f"   页面尺寸: {page_info['page_size']}")
    print(f"   文字区域: {page_info['text_area']}")
    print(f"   页面边距: {page_info['margins']}")
    print(f"   字体设置: {page_info['font']}")
    print(f"   行高设置: {page_info['line_height']}")
    print(f"   第一页行数: {page_info['first_page_lines']}")
    print(f"   普通页行数: {page_info['normal_page_lines']}")
    
    print("\n📐 文字区域位置:")
    print(f"   左边距: {text_area_pos['left']}px")
    print(f"   上边距: {text_area_pos['top']}px") 
    print(f"   区域宽度: {text_area_pos['width']}px")
    print(f"   区域高度: {text_area_pos['height']}px")
    
    # 生成测试页面
    test_pages = [
        {
            'header': 'A4页面容器测试文档',
            'content': '''            <div class="bt1">测试标题</div>
            <div class="zw1">这是第一个测试段落，用于验证段首缩进效果。</div>
            <div class="zw2">这是段落的第二行，应该没有缩进。</div>
            <div class="bt2">二级标题测试</div>
            <div class="zw1">这是另一个段落的开始。</div>'''
        }
    ]
    
    # 生成HTML文档
    html_content = container.generate_html_document(
        test_pages, 
        "A4页面容器测试"
    )
    
    # 保存测试文件
    test_file = '/Users/wangweihan/Desktop/TechForesight_0710/test_page_container.html'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ A4页面容器测试文件已生成: {test_file}")
    print("📄 包含完整的页面结构:")
    print("   - A4尺寸页面容器")
    print("   - 精确定位的文字区域") 
    print("   - 页眉页脚区域")
    print("   - 标题和段落样式")
    print("   - 调试信息面板")
    
    return container, page_info

if __name__ == "__main__":
    test_page_container()