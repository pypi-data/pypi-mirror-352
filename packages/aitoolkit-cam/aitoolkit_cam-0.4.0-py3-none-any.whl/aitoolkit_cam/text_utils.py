#!/usr/bin/env python3
"""
文字工具模块 - 支持在图像上添加中文文字
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import logging

logger = logging.getLogger("aitoolkit_cam")

def add_chinese_text(image, text, position=(10, 30), font_size=24, color=(0, 255, 0), font_path=None):
    """
    在图像上添加中文文字
    
    参数:
        image: 输入图像 (BGR格式)
        text: 要添加的文字内容
        position: 文字位置 (x, y)
        font_size: 字体大小
        color: 文字颜色 (B, G, R)
        font_path: 字体文件路径，如果为None则使用系统默认字体
    
    返回:
        添加文字后的图像
    """
    if image is None:
        return None
    
    try:
        # 复制图像避免修改原图
        img_copy = image.copy()
        
        # 转换BGR到RGB (PIL使用RGB格式)
        img_rgb = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
        
        # 创建PIL图像对象
        pil_img = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_img)
        
        # 获取字体
        font = get_chinese_font(font_size, font_path)
        
        # 转换颜色格式 (BGR -> RGB)
        rgb_color = (color[2], color[1], color[0])
        
        # 添加文字
        draw.text(position, text, font=font, fill=rgb_color)
        
        # 转换回OpenCV格式 (RGB -> BGR)
        result = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        return result
        
    except Exception as e:
        logger.warning(f"添加中文文字失败: {e}")
        # 如果失败，尝试使用OpenCV添加英文
        try:
            cv2.putText(img_copy, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                       font_size/30, color, 2)
            return img_copy
        except:
            return image

def get_chinese_font(font_size=24, font_path=None):
    """
    获取中文字体
    
    参数:
        font_size: 字体大小
        font_path: 指定字体路径
    
    返回:
        PIL字体对象
    """
    if font_path and os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, font_size)
        except:
            logger.warning(f"无法加载指定字体: {font_path}")
    
    # 尝试系统常见中文字体
    font_candidates = [
        # Windows系统字体
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",    # 黑体
        "C:/Windows/Fonts/simsun.ttc",    # 宋体
        "C:/Windows/Fonts/simkai.ttf",    # 楷体
        
        # Linux系统字体
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        
        # 相对路径（项目目录下的字体）
        "./fonts/msyh.ttc",
        "./fonts/simhei.ttf",
    ]
    
    for font_path in font_candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except Exception as e:
                logger.debug(f"尝试字体 {font_path} 失败: {e}")
                continue
    
    # 如果都失败了，使用默认字体
    try:
        return ImageFont.load_default()
    except:
        logger.warning("无法加载任何字体，将使用OpenCV默认字体")
        return None

def add_text_with_background(image, text, position=(10, 30), font_size=24, 
                           text_color=(255, 255, 255), bg_color=(0, 0, 0), 
                           padding=5, font_path=None):
    """
    添加带背景的中文文字
    
    参数:
        image: 输入图像
        text: 文字内容
        position: 文字位置
        font_size: 字体大小
        text_color: 文字颜色 (B, G, R)
        bg_color: 背景颜色 (B, G, R)
        padding: 背景边距
        font_path: 字体路径
    
    返回:
        处理后的图像
    """
    if image is None:
        return None
    
    try:
        img_copy = image.copy()
        
        # 转换到PIL格式
        img_rgb = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_img)
        
        # 获取字体
        font = get_chinese_font(font_size, font_path)
        
        # 获取文字尺寸
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            # 估算文字尺寸
            text_width = len(text) * font_size
            text_height = font_size
        
        # 绘制背景矩形
        bg_x1 = position[0] - padding
        bg_y1 = position[1] - padding
        bg_x2 = position[0] + text_width + padding
        bg_y2 = position[1] + text_height + padding
        
        # 转换背景颜色 (BGR -> RGB)
        rgb_bg_color = (bg_color[2], bg_color[1], bg_color[0])
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=rgb_bg_color)
        
        # 添加文字
        rgb_text_color = (text_color[2], text_color[1], text_color[0])
        draw.text(position, text, font=font, fill=rgb_text_color)
        
        # 转换回OpenCV格式
        result = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return result
        
    except Exception as e:
        logger.warning(f"添加带背景文字失败: {e}")
        return add_chinese_text(image, text, position, font_size, text_color, font_path)

def add_multiline_text(image, text_lines, start_position=(10, 30), font_size=24, 
                      color=(0, 255, 0), line_spacing=10, font_path=None):
    """
    添加多行中文文字
    
    参数:
        image: 输入图像
        text_lines: 文字行列表
        start_position: 起始位置
        font_size: 字体大小
        color: 文字颜色
        line_spacing: 行间距
        font_path: 字体路径
    
    返回:
        处理后的图像
    """
    if image is None or not text_lines:
        return image
    
    result = image.copy()
    x, y = start_position
    
    for i, line in enumerate(text_lines):
        current_y = y + i * (font_size + line_spacing)
        result = add_chinese_text(result, line, (x, current_y), font_size, color, font_path)
    
    return result

def create_text_overlay(width, height, text, position=(10, 30), font_size=24, 
                       text_color=(255, 255, 255), bg_color=(0, 0, 0), 
                       alpha=0.7, font_path=None):
    """
    创建文字覆盖层
    
    参数:
        width, height: 覆盖层尺寸
        text: 文字内容
        position: 文字位置
        font_size: 字体大小
        text_color: 文字颜色
        bg_color: 背景颜色
        alpha: 透明度 (0-1)
        font_path: 字体路径
    
    返回:
        文字覆盖层图像
    """
    # 创建透明背景
    overlay = np.zeros((height, width, 3), dtype=np.uint8)
    overlay[:] = bg_color
    
    # 添加文字
    overlay = add_chinese_text(overlay, text, position, font_size, text_color, font_path)
    
    return overlay

def blend_text_overlay(image, overlay, alpha=0.7):
    """
    将文字覆盖层混合到图像上
    
    参数:
        image: 原始图像
        overlay: 文字覆盖层
        alpha: 混合透明度
    
    返回:
        混合后的图像
    """
    if image is None or overlay is None:
        return image
    
    try:
        # 确保尺寸匹配
        if image.shape[:2] != overlay.shape[:2]:
            overlay = cv2.resize(overlay, (image.shape[1], image.shape[0]))
        
        # 混合图像
        result = cv2.addWeighted(image, 1-alpha, overlay, alpha, 0)
        return result
    except Exception as e:
        logger.warning(f"混合覆盖层失败: {e}")
        return image

# 便捷函数
def quick_add_chinese_text(image, text, position=(10, 30), size="medium", color="green"):
    """
    快速添加中文文字的便捷函数
    
    参数:
        image: 输入图像
        text: 文字内容
        position: 位置
        size: 字体大小 ("small", "medium", "large", "xlarge" 或具体数值)
        color: 颜色 ("red", "green", "blue", "white", "black", "yellow" 或BGR元组)
    
    返回:
        处理后的图像
    """
    # 处理字体大小
    size_map = {
        "small": 16,
        "medium": 24,
        "large": 32,
        "xlarge": 48
    }
    font_size = size_map.get(size, size if isinstance(size, int) else 24)
    
    # 处理颜色
    color_map = {
        "red": (0, 0, 255),
        "green": (0, 255, 0),
        "blue": (255, 0, 0),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (0, 255, 255),
        "cyan": (255, 255, 0),
        "magenta": (255, 0, 255)
    }
    text_color = color_map.get(color, color if isinstance(color, tuple) else (0, 255, 0))
    
    return add_chinese_text(image, text, position, font_size, text_color) 