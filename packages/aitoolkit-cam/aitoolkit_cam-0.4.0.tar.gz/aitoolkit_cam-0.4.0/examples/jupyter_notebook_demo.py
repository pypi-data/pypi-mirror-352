#!/usr/bin/env python3
"""
🎯 aitoolkit_cam Jupyter Notebook 完整演示
适用于 Jupyter Notebook/Lab 环境的摄像头工具包演示

功能特点:
- 🔧 自动资源管理，解决重启内核时摄像头占用问题
- 🎥 多种显示模式：网页流、本地窗口
- 🖼️ 图像处理演示：滤镜、效果
- 📊 性能监控：FPS统计
- 🛑 安全控制：超时保护、异常处理
"""

from aitoolkit_cam import Camera
import atexit
import time
import cv2
import numpy as np
from IPython.display import clear_output
import threading

# ==================== 全局变量 ====================
cam = None
is_demo_running = False
demo_stats = {"frames": 0, "start_time": None}

# ==================== 资源管理 ====================

def cleanup_camera():
    """清理摄像头资源 - 自动注册的清理函数"""
    global cam, is_demo_running
    is_demo_running = False
    if cam is not None:
        try:
            print("🔧 正在释放摄像头资源...")
            cam.stop()
            print("✅ 摄像头资源已释放")
        except Exception as e:
            print(f"⚠️ 释放摄像头资源时出错: {e}")
        finally:
            cam = None

# 注册程序退出时的清理函数
atexit.register(cleanup_camera)

# ==================== 基础摄像头控制 ====================

def init_camera(source='auto', port=9000, width=640, height=480, fps=30):
    """初始化摄像头
    
    参数:
        source: 摄像头源 ('auto', 0, 1, 或视频文件路径)
        port: 网页流端口
        width: 画面宽度
        height: 画面高度
        fps: 帧率
    """
    global cam
    
    # 如果已有摄像头在运行，先停止
    if cam is not None:
        print("🛑 检测到摄像头已在运行，先停止旧的摄像头...")
        cleanup_camera()
    
    try:
        print("📹 正在初始化摄像头...")
        cam = Camera(
            source=source, 
            web_enabled=True, 
            port=port,
            width=width,
            height=height,
            fps=fps
        )
        
        # 启动摄像头
        cam.start()
        
        # 获取网页地址
        web_url = cam.get_web_url()
        if web_url:
            print(f"🌐 摄像头已启动！")
            print(f"   网页地址: {web_url}")
            print(f"   分辨率: {width}x{height}")
            print(f"   帧率: {fps}fps")
            print(f"   端口: {port}")
        else:
            print("⚠️ 网页服务未正确启动")
            
        return True
        
    except Exception as e:
        print(f"❌ 启动摄像头失败: {e}")
        cleanup_camera()
        return False

def stop_camera():
    """停止摄像头"""
    global is_demo_running
    is_demo_running = False
    cleanup_camera()

def get_camera_info():
    """获取摄像头状态信息"""
    global cam
    if cam is None:
        print("📹 摄像头状态: 未启动")
        return False
    elif cam.is_running:
        print("📹 摄像头状态信息:")
        print(f"   运行状态: ✅ 运行中")
        print(f"   网页地址: {cam.get_web_url()}")
        print(f"   端口: {cam.port}")
        print(f"   分辨率: {cam.width}x{cam.height}")
        return True
    else:
        print("📹 摄像头状态: 已停止")
        return False

# ==================== 演示模式 ====================

def demo_basic_stream(duration=30):
    """基础摄像头流演示
    
    参数:
        duration: 运行时长(秒)，0表示无限制
    """
    global cam, is_demo_running, demo_stats
    
    if cam is None:
        print("❌ 摄像头未启动，请先运行 init_camera()")
        return
    
    print("🎥 开始基础摄像头流演示...")
    print(f"⏱️ 运行时长: {duration}秒 (0=无限制)")
    print("💡 停止方法:")
    print("   - Jupyter: 点击 'Interrupt' 按钮")
    print("   - 代码: 运行 stop_demo() 或 stop_camera()")
    
    # 重置统计
    is_demo_running = True
    demo_stats = {"frames": 0, "start_time": time.time()}
    
    try:
        start_time = time.time()
        
        for frame in cam:
            if not is_demo_running:
                break
                
            # 发送到网页显示
            cam.cv_show(frame, "web")
            
            # 更新统计
            demo_stats["frames"] += 1
            
            # 检查时长限制
            if duration > 0 and (time.time() - start_time) > duration:
                print(f"⏹️ 达到设定时长 {duration}秒，自动停止")
                break
                
    except KeyboardInterrupt:
        print("\n⏹️ 检测到中断信号，停止演示")
    except Exception as e:
        print(f"❌ 演示过程发生错误: {e}")
    finally:
        is_demo_running = False
        show_demo_stats()

def demo_with_effects(duration=30):
    """带图像效果的摄像头演示
    
    参数:
        duration: 运行时长(秒)
    """
    global cam, is_demo_running, demo_stats
    
    if cam is None:
        print("❌ 摄像头未启动，请先运行 init_camera()")
        return
    
    print("🎨 开始图像效果演示...")
    print("🔄 效果循环: 原图 -> 灰度 -> 边缘 -> 模糊 -> 重复")
    
    # 重置统计
    is_demo_running = True
    demo_stats = {"frames": 0, "start_time": time.time()}
    
    effects = ["original", "gray", "edge", "blur"]
    effect_index = 0
    effect_duration = 3  # 每种效果持续3秒
    effect_start_time = time.time()
    
    try:
        start_time = time.time()
        
        for frame in cam:
            if not is_demo_running:
                break
            
            # 切换效果
            current_time = time.time()
            if current_time - effect_start_time > effect_duration:
                effect_index = (effect_index + 1) % len(effects)
                effect_start_time = current_time
                print(f"🎨 切换效果: {effects[effect_index]}")
            
            # 应用效果
            processed_frame = apply_effect(frame, effects[effect_index])
            
            # 发送到网页显示
            cam.cv_show(processed_frame, "web")
            
            # 更新统计
            demo_stats["frames"] += 1
            
            # 检查时长限制
            if duration > 0 and (current_time - start_time) > duration:
                print(f"⏹️ 达到设定时长 {duration}秒，自动停止")
                break
                
    except KeyboardInterrupt:
        print("\n⏹️ 检测到中断信号，停止演示")
    except Exception as e:
        print(f"❌ 演示过程发生错误: {e}")
    finally:
        is_demo_running = False
        show_demo_stats()

def apply_effect(frame, effect_name):
    """应用图像效果"""
    if effect_name == "original":
        return frame
    elif effect_name == "gray":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    elif effect_name == "edge":
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    elif effect_name == "blur":
        return cv2.GaussianBlur(frame, (15, 15), 0)
    else:
        return frame

def stop_demo():
    """停止当前演示"""
    global is_demo_running
    is_demo_running = False
    print("⏹️ 演示已停止")

def show_demo_stats():
    """显示演示统计信息"""
    global demo_stats
    if demo_stats["start_time"]:
        duration = time.time() - demo_stats["start_time"]
        fps = demo_stats["frames"] / duration if duration > 0 else 0
        print(f"📊 演示统计:")
        print(f"   运行时长: {duration:.1f}秒")
        print(f"   总帧数: {demo_stats['frames']}")
        print(f"   平均FPS: {fps:.1f}")

# ==================== 快速开始函数 ====================

def quick_start(port=9000):
    """一键快速开始演示"""
    print("🚀 快速开始演示...")
    
    # 初始化摄像头
    if init_camera(port=port):
        print("\n⏱️ 等待3秒让摄像头稳定...")
        time.sleep(3)
        
        # 开始基础演示
        demo_basic_stream(duration=0)  # 无限制运行
    else:
        print("❌ 快速开始失败")

def quick_effects_demo(port=9001):
    """一键效果演示"""
    print("🎨 快速效果演示...")
    
    # 初始化摄像头
    if init_camera(port=port):
        print("\n⏱️ 等待3秒让摄像头稳定...")
        time.sleep(3)
        
        # 开始效果演示
        demo_with_effects(duration=60)  # 运行60秒
    else:
        print("❌ 效果演示启动失败")

# ==================== 使用指南 ====================

def show_usage():
    """显示使用指南"""
    print("🎯 aitoolkit_cam Jupyter 演示工具")
    print("=" * 60)
    print()
    print("🚀 快速开始:")
    print("   quick_start()                    # 一键开始基础演示")
    print("   quick_effects_demo()             # 一键开始效果演示")
    print()
    print("🔧 分步控制:")
    print("   init_camera()                    # 初始化摄像头")
    print("   demo_basic_stream(duration=30)   # 基础流演示")
    print("   demo_with_effects(duration=30)   # 效果演示")
    print("   stop_demo()                      # 停止当前演示")
    print("   stop_camera()                    # 停止摄像头")
    print()
    print("📊 监控:")
    print("   get_camera_info()                # 获取摄像头状态")
    print("   show_demo_stats()                # 显示演示统计")
    print()
    print("💡 提示:")
    print("   - 在Jupyter中按 'Interrupt' 按钮可停止演示")
    print("   - 建议在不同的cell中运行不同的函数")
    print("   - 重启内核时会自动释放摄像头资源")
    print()
    print("🌐 网页访问:")
    print("   演示开始后会显示网页地址，在浏览器中打开即可查看画面")

# ==================== 自动运行 ====================

if __name__ == "__main__":
    show_usage()
    
    print("\n" + "="*60)
    print("🎬 准备开始演示...")
    print("在Jupyter中运行以下代码开始:")
    print("   show_usage()      # 查看完整使用指南")
    print("   quick_start()     # 快速开始") 