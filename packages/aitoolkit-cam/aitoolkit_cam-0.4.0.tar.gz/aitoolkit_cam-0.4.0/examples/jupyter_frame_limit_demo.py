#!/usr/bin/env python3
"""
Jupyter 帧数限制演示
展示如何使用新的max_frames参数实现自动停止功能
"""

from aitoolkit_cam import Camera
import time

def demo_basic_frame_limit():
    """基础帧数限制演示"""
    print("🎯 基础帧数限制演示")
    print("=" * 50)
    
    # 方式1: 使用max_frames参数
    print("📹 创建摄像头(最多显示30帧)...")
    cam = Camera(max_frames=30, web_enabled=True, port=9001)
    cam.start()
    
    print(f"🌐 网页地址: {cam.get_web_url()}")
    print("📺 开始显示，30帧后自动停止...")
    
    for frame in cam:
        cam.cv_show(frame, "web")
        time.sleep(0.1)  # 稍微放慢速度便于观察
    
    print("✅ 摄像头已自动停止")
    print()

def demo_jupyter_shorthand():
    """Jupyter简写模式演示"""
    print("🚀 Jupyter简写模式演示")
    print("=" * 50)
    
    # 方式2: 简写模式 - 直接传入数字作为帧数
    print("📹 创建摄像头(Jupyter简写: 20帧)...")
    cam = Camera(20, web_enabled=True, port=9002)  # 数字>100会被识别为max_frames
    cam.start()
    
    print(f"🌐 网页地址: {cam.get_web_url()}")
    print("📺 开始显示，20帧后自动停止...")
    
    for frame in cam:
        cam.cv_show(frame, "web")
        time.sleep(0.1)
    
    print("✅ 摄像头已自动停止")
    print()

def demo_manual_read():
    """手动读取模式演示"""
    print("📖 手动读取模式演示")
    print("=" * 50)
    
    print("📹 创建摄像头(最多读取15帧)...")
    cam = Camera(max_frames=15, web_enabled=True, port=9003)
    cam.start()
    
    print(f"🌐 网页地址: {cam.get_web_url()}")
    print("📺 手动读取模式，15帧后自动停止...")
    
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        
        should_exit = cam.cv_show(frame, "web")
        if should_exit:
            break
        
        time.sleep(0.1)
    
    print("✅ 摄像头已自动停止")
    print()

def demo_large_number_shorthand():
    """大数字简写演示"""
    print("💫 大数字简写演示")
    print("=" * 50)
    
    # 超过100的数字会被自动识别为max_frames
    print("📹 创建摄像头(简写: 500帧)...")
    cam = Camera(500, web_enabled=True, port=9004)
    cam.start()
    
    print(f"🌐 网页地址: {cam.get_web_url()}")
    print("📺 开始快速显示500帧...")
    
    for frame in cam:
        cam.cv_show(frame, "web")
        time.sleep(0.02)  # 快速显示
    
    print("✅ 摄像头已自动停止")
    print()

def demo_status_monitoring():
    """状态监控演示"""
    print("📊 状态监控演示")
    print("=" * 50)
    
    cam = Camera(max_frames=25, web_enabled=True, port=9005)
    cam.start()
    
    print(f"🌐 网页地址: {cam.get_web_url()}")
    print("📈 实时监控帧数状态...")
    
    for frame in cam:
        cam.cv_show(frame, "web")
        
        # 每5帧显示一次状态
        if cam.frame_count % 5 == 0:
            remaining = cam.max_frames - cam.frame_count
            print(f"  📊 已显示: {cam.frame_count} / {cam.max_frames} 帧 (还剩 {remaining} 帧)")
        
        time.sleep(0.1)
    
    print("✅ 摄像头已自动停止")
    print()

if __name__ == "__main__":
    print("🎪 aitoolkit_cam Jupyter 帧数限制演示")
    print("=" * 60)
    print()
    
    print("💡 这个演示展示了如何在Jupyter中使用帧数限制功能")
    print("   Camera类默认500帧后自动停止，无需手动调用 stop()")
    print()
    
    try:
        # 1. 基础演示
        demo_basic_frame_limit()
        time.sleep(1)
        
        # 2. 简写模式
        demo_jupyter_shorthand() 
        time.sleep(1)
        
        # 3. 手动读取
        demo_manual_read()
        time.sleep(1)
        
        # 4. 大数字简写
        demo_large_number_shorthand()
        time.sleep(1)
        
        # 5. 状态监控
        demo_status_monitoring()
        
        print("🎉 所有演示完成！")
        print()
        print("💡 Jupyter使用技巧:")
        print("   1. Camera() - 默认500帧后自动停止")
        print("   2. Camera(100) - 显示100帧后自动停止")
        print("   3. Camera(max_frames=None) - 无限制，需手动停止")
        print("   4. 无需手动调用 stop()，自动资源管理")
        print("   5. 适合教学和实验场景")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
    
    print("\n👋 演示结束") 