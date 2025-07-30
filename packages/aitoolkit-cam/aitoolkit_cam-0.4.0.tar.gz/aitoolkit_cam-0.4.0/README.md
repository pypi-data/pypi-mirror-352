# AIToolkit Camera 0.4.0 - Jupyter优化版

简单易用的摄像头工具包，完美支持 Jupyter Notebook 和教育编程场景。

## 🎯 核心特性

- **🚀 开箱即用**：`Camera()` 一行代码启动摄像头
- **🎓 Jupyter优化**：默认500帧自动停止，无需手动释放资源
- **🌐 网页显示**：自动启动本地Web服务器
- **⚡ 智能简写**：`Camera(1000)` 直接指定显示帧数
- **🔧 自动资源管理**：解决Jupyter中摄像头占用问题

## 📦 快速安装

```bash
pip install aitoolkit-cam
```

## 🚀 快速开始

### 最简使用（推荐）
```python
from aitoolkit_cam import Camera

# 默认显示500帧后自动停止
cam = Camera()
url = cam.start()
print(f"请访问: {url}")
```

### 自定义帧数
```python
from aitoolkit_cam import Camera

# 显示1000帧后自动停止
cam = Camera(1000)
url = cam.start()
print(f"请访问: {url}")
```

### 传统循环方式
```python
from aitoolkit_cam import Camera

cam = Camera()
url = cam.start()
print(f"请访问: {url}")

for frame in cam:
    # 自动在500帧后停止
    pass
```

## 🎯 主要优势

- **教育友好**：适合编程教学和Jupyter演示
- **资源安全**：自动释放摄像头，避免占用问题
- **简化API**：最少代码实现最多功能
- **向后兼容**：支持所有原有功能

## 📚 完整文档

访问我们的[完整文档](https://github.com/yourusername/aitoolkit-cam)了解更多功能。

## 🆕 v0.4.0 新功能

- 默认500帧自动停止
- 智能参数解析
- Jupyter专用优化
- 自动资源管理
- 积木化编程支持

---

适用于 Python 3.7+ | 支持 Windows, macOS, Linux | 兼容 Jupyter Notebook 