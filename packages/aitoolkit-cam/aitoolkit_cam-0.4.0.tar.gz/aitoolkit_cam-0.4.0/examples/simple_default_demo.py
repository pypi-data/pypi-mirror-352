#!/usr/bin/env python3
"""
最简单的Camera使用演示
展示默认500帧自动停止功能
"""

from aitoolkit_cam import Camera

def main():
    print("🎥 最简单的Camera使用演示")
    print("=" * 40)
    print()
    
    print("💡 默认特性:")
    print("   - 自动检测摄像头")
    print("   - 默认500帧后自动停止")
    print("   - 自动释放资源")
    print("   - 无需手动调用 stop()")
    print()
    
    # 最简单的使用方式
    print("📹 创建摄像头 (默认500帧后自动停止)...")
    cam = Camera(web_enabled=True)
    cam.start()
    
    print(f"🌐 打开浏览器访问: {cam.get_web_url()}")
    print("📺 开始显示，500帧后自动停止...")
    print()
    
    # 显示进度
    for frame in cam:
        cam.cv_show(frame, "web")
        
        # 每50帧显示一次进度
        if cam.frame_count % 50 == 0:
            remaining = cam.max_frames - cam.frame_count
            progress = (cam.frame_count / cam.max_frames) * 100
            print(f"  📊 进度: {cam.frame_count}/{cam.max_frames} 帧 ({progress:.1f}%) - 还剩 {remaining} 帧")
    
    print()
    print("✅ 摄像头已自动停止并释放资源")
    print("💡 无需调用 cam.stop()，自动管理!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    
    print("\n👋 演示结束") 