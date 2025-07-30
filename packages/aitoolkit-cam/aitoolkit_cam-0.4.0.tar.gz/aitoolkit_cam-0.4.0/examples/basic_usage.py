#!/usr/bin/env python3
"""
中学生摄像头入门教程 - 最简单的实时显示测试
"""
from aitoolkit_cam import Camera
import cv2
import time

def simple_test():
    """最简单的摄像头测试"""
    print("🎥 最简单的摄像头测试")
    print("=" * 40)
    
    # 创建摄像头 - 使用极速检测
    print("📱 创建摄像头（极速模式）...")
    cam = Camera(source='auto', web_enabled=True, port=9000)
    
    try:
        # 启动摄像头
        print("🔄 启动摄像头...")
        success = cam.start()
        if not success:
            print("❌ 摄像头启动失败")
            return
        
        # 获取网页地址
        url = cam.get_web_url()
        print(f"🌐 网页地址: {url}")
        print("💡 在浏览器中打开上面的地址观看实时画面")
        print()
        
        # 简单测试 - 只显示原始画面
        print("📺 开始5秒实时显示测试...")
        frame_count = 0
        
        for i in range(5):
            ret, frame = cam.read(timeout=2.0)
            if ret and frame is not None:
                frame_count += 1
                # 只发送到Web显示，避免cv2.imshow错误
                cam.cv_show(frame, "web")
                print(f"   📡 第{i+1}秒: 画面已更新")
            time.sleep(1)
        
        print(f"✅ 测试完成！成功处理了 {frame_count} 帧")
        
    except Exception as e:
        print(f"❌ 出现错误: {e}")
    finally:
        print("🔒 关闭摄像头...")
        cam.stop()
        print("✅ 测试完成")

if __name__ == "__main__":
    simple_test()