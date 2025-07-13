#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A4布局系统配置模块
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class LayoutConfig:
    """布局配置类"""
    
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
    text_area_height: int = 972    # 文字区域高度: 1123-71*2=981px (调整后972px)
    
    # 页眉页脚区域
    header_height: int = 30        # 页眉高度
    footer_height: int = 30        # 页脚高度
    
    # 字体设置
    font_size: str = "15.9pt"      # 字体大小
    font_family: str = '"Microsoft YaHei", "微软雅黑", sans-serif'
    line_height: int = 36          # 行高: 36px
    
    # 缩进设置
    paragraph_indent: float = 43.6  # 段首缩进: 2em ≈ 43.6px
    
    # 分页设置
    first_page_lines: int = 27     # 第一页最大行数(与普通页相同)
    normal_page_lines: int = 27    # 普通页最大行数
    
    # 标题设置
    main_title_font_size: str = "15.9pt"    # 主标题字体大小(与正文相同)
    section_title_font_size: str = "15.9pt"  # 二级标题字体大小(与正文相同)
    title_color: str = "#A60000"          # 标题颜色(红色)
    
    def get_text_area_position(self) -> Dict[str, int]:
        """获取文字区域位置信息"""
        return {
            'left': self.margin_left,
            'top': self.margin_top,
            'width': self.text_area_width,
            'height': self.text_area_height
        }
    
    def get_page_info(self) -> Dict[str, Any]:
        """获取页面信息摘要"""
        return {
            'page_size': f"{self.page_width}×{self.page_height}px",
            'text_area': f"{self.text_area_width}×{self.text_area_height}px",
            'margins': f"上下{self.margin_top}px, 左右{self.margin_left}px",
            'font': f"{self.font_size} {self.font_family}",
            'line_height': f"{self.line_height}px",
            'first_page_lines': self.first_page_lines,
            'normal_page_lines': self.normal_page_lines
        }

@dataclass
class HTMLConfig:
    """HTML生成配置类"""
    
    title: str = "A4自动分页文档"
    show_debug_info: bool = True
    show_page_borders: bool = True
    include_print_styles: bool = True
    
    # CSS样式配置
    background_color: str = "#f0f0f0"
    page_shadow: str = "0 4px 8px rgba(0,0,0,0.1)"
    border_style: str = "1px dashed #ccc"