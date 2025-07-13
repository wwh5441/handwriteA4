#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手写报告铺排器模块
模拟手写报告的逐行文字铺排过程
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from config import LayoutConfig
from char_width import CharWidthCalculator

@dataclass
class ContentBlock:
    """内容块数据结构"""
    type: str  # 'h1', 'h2', 'paragraph'
    text: str
    metadata: Dict[str, Any] = None

@dataclass
class LayoutLine:
    """布局行数据结构"""
    text: str
    css_class: str  # 'main-title', 'section-title', 'paragraph-start', 'paragraph-continue'
    width: float
    utilization: float
    line_number: int
    line_display: str = ""  # 行号显示文本

@dataclass
class Page:
    """页面数据结构"""
    lines: List[LayoutLine]
    page_number: int
    line_count: int
    remaining_lines: int

class HandwrittenComposer:
    """手写报告铺排器
    
    像人写字一样，一行一行写，一行写满就换行
    """
    
    def __init__(self, layout_config: LayoutConfig = None, char_calculator: CharWidthCalculator = None):
        self.config = layout_config or LayoutConfig()
        self.char_calc = char_calculator or CharWidthCalculator()
        
        # 行类型配置
        self.line_types = {
            'h1': {'height': 72, 'lines': 2, 'css_class': 'bt1'},
            'h2': {'height': 72, 'lines': 2, 'css_class': 'bt2'},
            'paragraph_start': {'height': 36, 'lines': 1, 'css_class': 'zw1'},
            'paragraph_continue': {'height': 36, 'lines': 1, 'css_class': 'zw2'},
            'paragraph_end': {'height': 36, 'lines': 1, 'css_class': 'zw3'}
        }
        
        # 页面行数配置
        self.max_lines_per_page = self.config.normal_page_lines  # 27行
        self.first_page_lines = self.config.first_page_lines    # 25行
        
        # 铺排参数 (严格控制溢出)
        self.base_threshold = 0.95     # 95%基准
        self.normal_tolerance = 0.98   # 98%普通容错
        self.word_break_tolerance = 0.99  # 99%拆词容错
    
    def create_page_counter(self, page_number: int) -> List[int]:
        """创建页面行数倒序器"""
        max_lines = self.first_page_lines if page_number == 1 else self.max_lines_per_page
        return list(range(max_lines, 0, -1))  # [27, 26, 25, ..., 2, 1]
    
    def create_line_space(self, block_type: str, is_first_paragraph: bool = False) -> Dict[str, Any]:
        """创建行空间
        
        Args:
            block_type: 'h1', 'h2', 'paragraph'
            is_first_paragraph: 是否段落首行
            
        Returns:
            行空间配置
        """
        if block_type in ['h1', 'h2']:
            return self.line_types[block_type].copy()
        elif block_type == 'paragraph':
            if is_first_paragraph:
                return self.line_types['paragraph_start'].copy()
            else:
                return self.line_types['paragraph_continue'].copy()
        else:
            raise ValueError(f"未知的块类型: {block_type}")
    
    def is_word_boundary(self, text: str, pos: int) -> bool:
        """判断是否为单词边界"""
        if pos >= len(text):
            return True
        
        # 中文字符总是可以断开
        if self.char_calc.classify_char(text[pos]) == 'chinese':
            return True
        
        # 英文需要在单词边界断开
        if pos == 0 or pos == len(text) - 1:
            return True
        
        current_char = text[pos]
        prev_char = text[pos - 1]
        
        # 空格、标点符号处可以断开
        if current_char in ' .,;:!?()[]{}' or prev_char in ' .,;:!?()[]{}':
            return True
        
        return False
    
    def find_best_break_point(self, text: str, max_chars: int) -> int:
        """寻找最佳断行点"""
        if max_chars >= len(text):
            return len(text)
        
        # 从最大字符数向前搜索合适的断点
        for i in range(max_chars, max(0, max_chars - 20), -1):
            if self.is_word_boundary(text, i):
                return i
        
        # 如果找不到合适的断点，强制在最大位置断开
        return max_chars
    
    def find_best_hyphen_position(self, word: str) -> int:
        """为长英文单词找到最佳连字符位置 - 基于音节和语法规则"""
        word_lower = word.lower()
        
        # 特殊单词的预定义分割点
        special_words = {
            'chatgpt': 4,     # chat-gpt
            'artificial': 4,   # arti-ficial  
            'intelligence': 5, # intel-ligence
            'transformer': 5,  # trans-former
            'deepmind': 4,     # deep-mind
            'tensorflow': 6,   # tensor-flow
            'pytorch': 2,      # py-torch
            'machine': 2,      # ma-chine
            'learning': 4,     # learn-ing
            'neural': 3,       # neu-ral
            'network': 3,      # net-work
            'algorithm': 4,    # algo-rithm
            'computer': 3,     # com-puter
            'technology': 4,   # tech-nology
            'development': 6,  # develop-ment
            'processing': 4,   # proc-essing
            'microsoft': 5,    # micro-soft
            'general': 3,      # gen-eral
            'system': 3,       # sys-tem
            'language': 4,     # lang-uage
            'natural': 3,      # nat-ural
            'generation': 4,   # gene-ration
            'foundation': 4,   # found-ation
            'architecture': 5, # archi-tecture
            'understanding': 5, # under-standing
            'information': 2,  # in-formation
            'application': 3,  # app-lication
            'optimization': 4, # opti-mization
            'integration': 4,  # inte-gration
            'implementation': 2, # im-plementation
            'classification': 5, # classi-fication
            'interpretation': 6, # inter-pretation
            'representation': 3, # rep-resentation
            'communication': 3,  # com-munication
            'recommendation': 3, # rec-ommendation
        }
        
        if word_lower in special_words:
            pos = special_words[word_lower]
            # 确保位置合理
            if 2 <= pos <= len(word) - 2:
                return pos
        
        # 通用音节分割规则
        vowels = 'aeiouAEIOU'
        consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        
        # 规则1：在复合词边界分割（如果有明显的词根）
        common_prefixes = ['pre', 'pro', 'anti', 'auto', 'co', 'de', 'dis', 'en', 'em', 'fore', 'in', 'im', 'il', 'ir', 'inter', 'mid', 'mis', 'non', 'over', 'out', 'post', 're', 'semi', 'sub', 'super', 'trans', 'un', 'under']
        common_suffixes = ['able', 'ible', 'al', 'ial', 'ed', 'en', 'er', 'est', 'ful', 'ic', 'ing', 'ion', 'tion', 'ation', 'ition', 'ity', 'ty', 'ive', 'ative', 'itive', 'less', 'ly', 'ment', 'ness', 'ous', 'eous', 'ious', 's', 'es', 'y']
        
        # 检查前缀
        for prefix in sorted(common_prefixes, key=len, reverse=True):
            if word_lower.startswith(prefix) and len(prefix) >= 2 and len(word) - len(prefix) >= 2:
                return len(prefix)
        
        # 检查后缀
        for suffix in sorted(common_suffixes, key=len, reverse=True):
            if word_lower.endswith(suffix) and len(suffix) >= 2 and len(word) - len(suffix) >= 2:
                return len(word) - len(suffix)
        
        # 默认：在中间分割，但避免单字母
        best_pos = len(word) // 2
        
        # 确保前后都有至少2个字符
        if best_pos < 2:
            best_pos = 2
        elif best_pos > len(word) - 2:
            best_pos = len(word) - 2
            
        return best_pos

    def try_hyphenate_word(self, word: str, available_width: float) -> dict:
        """尝试用连字符截断长单词"""
        if len(word) <= 6:  # 短单词不截断
            return None
        
        # 专有名词和技术术语不应该被断开
        protected_words = {
            'openai', 'google', 'deepmind', 'chatgpt', 'claude', 'bert', 
            'transformer', 'attention', 'multihead', 'alphafold', 'waymo',
            'tesla', 'apollo', 'pytorch', 'tensorflow', 'nvidia', 'microsoft',
            'artificial', 'intelligence', 'lamda', 'palm'
        }
        
        if word.lower() in protected_words:
            return None
            
        # 找到最佳连字符位置
        hyphen_pos = self.find_best_hyphen_position(word)
        
        # 计算第一部分 + 连字符的宽度
        first_part = word[:hyphen_pos]
        first_part_with_hyphen = first_part + '-'
        
        first_width = self.char_calc.get_text_width(first_part_with_hyphen)
        
        if first_width <= available_width:
            second_part = word[hyphen_pos:]
            return {
                'fitted': first_part_with_hyphen,
                'remaining': second_part,
                'width': first_width
            }
        
        return None

    def check_punctuation_at_start(self, text: str) -> Tuple[str, str]:
        """检查并处理段首标点符号问题
        
        如果下一行以标点符号开始，将最后一个非标点字符移到下一行
        
        Returns:
            (修正后的当前行, 修正后的剩余文本)
        """
        if not text or not text[0] in '.,;:!?):]}，。；：！？）：】》、':
            return text, text
        
        # 找到所有开头的标点符号
        punct_count = 0
        for char in text:
            if char in '.,;:!?):]}，。；：！？）：】》、':
                punct_count += 1
            else:
                break
        
        # 返回需要移动的标点
        return text[:punct_count], text[punct_count:]

    def fill_line_handwritten(self, text: str, line_config: Dict) -> Tuple[str, str, float, float]:
        """手写式填充行 - 智能英文断字 + 避免段首标点版本
        
        Args:
            text: 待填充文本
            line_config: 行配置信息
            
        Returns:
            (当前行文本, 剩余文本, 实际宽度, 利用率)
        """
        max_width = self.config.text_area_width
        indent = self.config.paragraph_indent if line_config['css_class'] == 'zw1' else 0.0
        available_width = max_width - indent
        
        if not text.strip():
            return "", "", indent, 0.0
        
        current_line = ""
        current_width = 0.0
        pos = 0
        words = []  # 记录单词信息，用于后续处理
        
        # 第一步：智能分词
        i = 0
        while i < len(text):
            if self._is_chinese_char(text[i]):
                # 中文字符单独处理
                words.append({'text': text[i], 'type': 'chinese', 'start': i, 'end': i + 1})
                i += 1
            elif text[i] == ' ':
                # 空格
                words.append({'text': text[i], 'type': 'space', 'start': i, 'end': i + 1})
                i += 1
            elif text[i] in '.,;:!?):]}，。；：！？）：】》、':
                # 标点符号（包含顿号）
                words.append({'text': text[i], 'type': 'punctuation', 'start': i, 'end': i + 1})
                i += 1
            else:
                # 英文单词或数字
                word_start = i
                while i < len(text) and text[i] not in ' .,;:!?):]}，。；：！？）：】》、' and not self._is_chinese_char(text[i]):
                    i += 1
                word_text = text[word_start:i]
                words.append({'text': word_text, 'type': 'english', 'start': word_start, 'end': i})
        
        # 第二步：逐词填充
        word_index = 0
        while word_index < len(words):
            word = words[word_index]
            word_width = self.char_calc.get_text_width(word['text'])
            
            # 检查是否超出宽度
            if current_width + word_width > available_width:
                # 如果是长英文单词，尝试断词
                if word['type'] == 'english' and len(word['text']) > 6:
                    hyphen_result = self.try_hyphenate_word(word['text'], available_width - current_width)
                    if hyphen_result:
                        current_line += hyphen_result['fitted']
                        current_width += hyphen_result['width']
                        
                        # 修改当前单词为剩余部分
                        words[word_index]['text'] = hyphen_result['remaining']
                        break
                
                # 不能断词，结束当前行
                break
            
            current_line += word['text']
            current_width += word_width
            word_index += 1
        
        # 第三步：处理剩余文本和标点符号问题
        remaining_text = ""
        if word_index < len(words):
            remaining_words = words[word_index:]
            remaining_text = ''.join(w['text'] for w in remaining_words)
            
            # 检查剩余文本是否以标点开头
            if remaining_text and remaining_text[0] in '.,;:!?):]}，。；：！？）：】》、':
                # 找到当前行最后一个非空格、非标点的字符
                for i in range(len(current_line) - 1, -1, -1):
                    char = current_line[i]
                    if char not in ' .,;:!?):]}，。；：！？）：】》、':
                        # 将这个字符移到下一行
                        move_char = current_line[i]
                        current_line = current_line[:i] + current_line[i+1:]
                        current_width -= self.char_calc.get_char_width(move_char)
                        remaining_text = move_char + remaining_text
                        break
        
        remaining_text = remaining_text.lstrip()
        actual_width = current_width + indent
        utilization = actual_width / max_width if max_width > 0 else 0.0
        
        return current_line, remaining_text, actual_width, utilization
    
    def _is_chinese_char(self, char: str) -> bool:
        """判断是否为中文字符"""
        return '\u4e00' <= char <= '\u9fff'
    
    def _is_break_point(self, text: str, pos: int) -> bool:
        """判断是否为合适的断行点"""
        if pos >= len(text):
            return True
        
        # 在空格后断行
        if pos > 0 and text[pos - 1] == ' ':
            return True
        
        # 在标点符号后断行
        if pos > 0 and text[pos - 1] in '.,;:!?):]}':
            return True
        
        # 在中文字符后总是可以断行
        if pos > 0 and self._is_chinese_char(text[pos - 1]):
            return True
        
        return False
    
    def compose_block(self, block: ContentBlock, start_line_number: int) -> Tuple[List[LayoutLine], int]:
        """铺排单个内容块
        
        Args:
            block: 内容块
            start_line_number: 起始行号
            
        Returns:
            (布局行列表, 消耗的行数)
        """
        lines = []
        current_line_number = start_line_number
        
        if block.type in ['h1', 'h2']:
            # 标题本身就是72px高度，占用2行空间
            line_config = self.create_line_space(block.type)
            
            # 标题行（本身就是72px，占用2行计数）
            title_line = LayoutLine(
                text=block.text,
                css_class=line_config['css_class'],
                width=self.char_calc.get_text_width(block.text),
                utilization=self.char_calc.get_text_width(block.text) / self.config.text_area_width,
                line_number=current_line_number
            )
            # 为标题添加行号显示信息
            title_line.line_display = f"{current_line_number}+{current_line_number+1}"
            lines.append(title_line)
            
            return lines, 2  # 消耗2行计数
        
        elif block.type == 'paragraph':
            # 段落逐行铺排
            remaining_text = block.text.strip()
            # 检查是否为续行段落
            is_continuation = block.metadata and block.metadata.get('is_continuation', False)
            is_first_line = not is_continuation  # 如果是续行段落，则不是第一行
            lines_used = 0
            
            while remaining_text:
                indent = self.config.paragraph_indent if is_first_line else 0.0
                available_width = self.config.text_area_width - indent
                is_last_line = self.char_calc.get_text_width(remaining_text) <= available_width
                
                if is_first_line:
                    line_config = self.line_types['paragraph_start'].copy()
                elif is_last_line:
                    line_config = self.line_types['paragraph_end'].copy()
                else:
                    line_config = self.line_types['paragraph_continue'].copy()

                line_text, remaining_text, actual_width, utilization = self.fill_line_handwritten(
                    remaining_text, line_config
                )
                
                if not line_text and not remaining_text:
                    break
                
                # If fill_line_handwritten returns an empty line but there's still text,
                # it means the remaining text is just whitespace. We can break.
                if not line_text.strip() and remaining_text.strip() == "":
                    break

                layout_line = LayoutLine(
                    text=line_text,
                    css_class=line_config['css_class'],
                    width=actual_width,
                    utilization=utilization,
                    line_number=current_line_number + lines_used
                )
                # 为正文添加行号显示信息
                layout_line.line_display = str(current_line_number + lines_used)
                lines.append(layout_line)
                
                lines_used += 1
                is_first_line = False

            # Final check to update the last line's class to zw3 if it wasn't caught
            if lines and lines[-1].css_class not in ['bt1', 'bt2', 'zw3']:
                lines[-1].css_class = 'zw3'
            
            return lines, lines_used
        
        else:
            raise ValueError(f"未知的内容块类型: {block.type}")
    
    def compose_page(self, content_blocks: List[ContentBlock], page_number: int) -> Tuple[Page, List[ContentBlock]]:
        """铺排单页内容
        
        Args:
            content_blocks: 内容块列表
            page_number: 页码
            
        Returns:
            (页面对象, 剩余内容块)
        """
        page_counter = self.create_page_counter(page_number)
        max_lines = len(page_counter)
        
        lines = []
        current_line_number = 1
        block_index = 0
        
        print(f"\n📄 开始铺排第{page_number}页 (最大{max_lines}行)")
        print(f"🔢 行数倒序器: {page_counter[:5]}...{page_counter[-3:]}")
        
        while block_index < len(content_blocks):
            block = content_blocks[block_index]
            
            print(f"📝 处理内容块 [{block.type}]: '{block.text[:30]}...' (当前行号{current_line_number})")
            
            # 检查是否有足够空间放置这个块
            if block.type in ['h1', 'h2']:
                # 标题必须完整放在一页，不能跨页
                if current_line_number + 1 > max_lines:  # 标题需要2行，所以检查+1
                    print(f"⚠️  标题空间不足，跳到下一页 (标题需要2行，当前行号{current_line_number})")
                    break
                
                # 铺排标题
                block_lines, lines_used = self.compose_block(block, current_line_number)
                lines.extend(block_lines)
                current_line_number += lines_used
                block_index += 1
                print(f"✅ 标题完成铺排，使用了{lines_used}行，当前行号: {current_line_number}")
            
            else:  # paragraph - 可以跨页拆分
                remaining_lines = max_lines - current_line_number + 1
                print(f"   当前页剩余{remaining_lines}行空间")
                
                if remaining_lines <= 0:
                    print(f"⚠️  页面已满，跳到下一页")
                    break
                
                # 铺排段落（可能只铺排部分内容）
                block_lines, lines_used = self.compose_block(block, current_line_number)
                
                # 检查是否所有行都能放入当前页
                lines_that_fit = []
                lines_consumed = 0
                
                for line in block_lines:
                    if current_line_number + lines_consumed <= max_lines:
                        lines_that_fit.append(line)
                        lines_consumed += 1
                    else:
                        break
                
                if lines_that_fit:
                    # 有部分内容可以放入当前页
                    lines.extend(lines_that_fit)
                    current_line_number += lines_consumed
                    print(f"✅ 段落部分完成铺排，使用了{lines_consumed}行，当前行号: {current_line_number}")
                    
                    # 如果段落还有剩余内容，创建新的段落块
                    if lines_consumed < len(block_lines):
                        remaining_text = ""
                        # 重新组合剩余的行内容
                        for remaining_line in block_lines[lines_consumed:]:
                            remaining_text += remaining_line.text
                        
                        # 更新当前块为剩余内容，标记为续行段落
                        content_blocks[block_index] = ContentBlock(
                            type='paragraph',
                            text=remaining_text,
                            metadata={'is_continuation': True}  # 标记为续行段落
                        )
                        print(f"📝 段落有剩余内容，将在下一页继续处理")
                        # 不增加block_index，下一页继续处理这个块
                    else:
                        # 段落完全处理完成
                        block_index += 1
                
                # 如果当前页已满，跳到下一页
                if current_line_number >= max_lines:
                    print(f"📄 页面已满 (当前行号{current_line_number} >= 最大行数{max_lines})")
                    break
        
        # 创建页面对象
        page = Page(
            lines=lines,
            page_number=page_number,
            line_count=len(lines),
            remaining_lines=max_lines - len(lines)
        )
        
        # 返回剩余的内容块
        remaining_blocks = content_blocks[block_index:]
        
        print(f"📄 第{page_number}页完成: {len(lines)}行，剩余{len(remaining_blocks)}个内容块")
        
        return page, remaining_blocks
    
    def compose_document(self, content_blocks: List[ContentBlock]) -> List[Page]:
        """铺排整个文档
        
        Args:
            content_blocks: 内容块列表
            
        Returns:
            页面列表
        """
        print("🖋️  开始手写报告铺排...")
        print(f"📝 总计 {len(content_blocks)} 个内容块待处理")
        
        pages = []
        remaining_blocks = content_blocks.copy()
        page_number = 1
        
        while remaining_blocks:
            page, remaining_blocks = self.compose_page(remaining_blocks, page_number)
            pages.append(page)
            page_number += 1
            
            if page_number > 20:  # 防护措施
                print("⚠️  页数过多，停止处理")
                break
        
        print(f"✅ 手写报告铺排完成！")
        print(f"📄 总页数: {len(pages)}")
        print(f"📊 统计信息:")
        for i, page in enumerate(pages, 1):
            print(f"   第{i}页: {page.line_count}行，剩余空间{page.remaining_lines}行")
        
        return pages

def test_handwritten_composer():
    """测试手写报告铺排器"""
    
    print("🖋️  开始测试手写报告铺排器...")
    
    # 创建测试内容
    test_blocks = [
        ContentBlock(type='h1', text='人工智能技术发展的重要里程碑与未来展望'),
        ContentBlock(type='h2', text='AI技术发展概述'),
        ContentBlock(type='paragraph', text='近年来，人工智能技术经历了前所未有的快速发展，从深度学习的突破性进展到大型语言模型的涌现，再到多模态AI系统的成熟，每一个技术节点都标志着人类在智能化道路上的重要突破。ChatGPT、GPT-4、Claude等大型语言模型的相继问世，不仅展现了AI在自然语言理解和生成方面的卓越能力，更是开启了通用人工智能(AGI)时代的序幕。'),
        ContentBlock(type='h2', text='Transformer架构突破'),
        ContentBlock(type='paragraph', text='在技术架构层面，Transformer架构的提出彻底改变了自然语言处理领域的发展轨迹。这种基于注意力机制的神经网络架构，通过Self-Attention和Multi-Head Attention的创新设计，使得模型能够并行处理序列数据。'),
    ]
    
    # 创建铺排器
    composer = HandwrittenComposer()
    
    # 测试铺排
    pages = composer.compose_document(test_blocks)
    
    # 输出结果
    print(f"\n📋 铺排结果详情:")
    for page in pages:
        print(f"\n📄 第{page.page_number}页:")
        for line in page.lines:
            print(f"   第{line.line_number}行 [{line.css_class}]: '{line.text}' (宽度:{line.width:.1f}px, 利用率:{line.utilization:.1%})")
    
    return composer, pages

if __name__ == "__main__":
    test_handwritten_composer()