"""
AIToolkit Camera - 简单易用的摄像头工具包
===========================================

提供本地显示和网页显示功能，支持图像处理

此包提供了使用OpenCV的摄像头工具，它具有以下特点：
1. 简单的API，易于使用
2. 支持本地窗口显示和网页浏览器显示
3. 提供多种图像处理效果
4. 兼容迭代器协议，可用于for循环
5. 自动处理摄像头连接和断开

快速示例:
```python
from aitoolkit_cam import Camera

# 创建摄像头对象
cam = Camera(0)

# 启动网页服务器
url = cam.start()
print(f"请访问: {url}")

# 在网页模式下显示
for frame in cam:
    # 可以进行额外的处理
    pass

try:
    cam.wait_for_exit()
except KeyboardInterrupt:
    pass

# 释放资源
cam.stop()
```
"""

# 版本信息
__version__ = '0.4.0'
__author__ = "aitoolkit_cam"

# 导入主要类和函数
from .camera import Camera
from .processor import Processor, ProcessedCamera, apply_effect
from .web_streamer import WebStreamer
from .text_utils import (
    add_chinese_text, 
    add_text_with_background, 
    add_multiline_text,
    quick_add_chinese_text
)

# 导出的公共接口
__all__ = [
    'Camera',
    'Processor', 
    'ProcessedCamera',
    'apply_effect',
    'WebStreamer',
    'cv_show',
    'add_chinese_text',
    'add_text_with_background', 
    'add_multiline_text',
    'quick_add_chinese_text',
    '__version__',
    '__author__'
]

# 兼容性函数
def cv_show(frame, window_name="预览", wait_key=1):
    """兼容性函数：显示图像"""
    import cv2
    try:
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(wait_key) & 0xFF
        return key == ord('q') or key == 27
    except:
        print("无法显示图像，可能缺少GUI支持")
        return False 