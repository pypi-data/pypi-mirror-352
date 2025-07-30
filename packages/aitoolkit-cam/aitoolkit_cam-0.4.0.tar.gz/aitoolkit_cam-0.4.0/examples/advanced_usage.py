#!/usr/bin/env python3
"""
高级使用示例 - 展示AIToolkit Camera的高级功能
"""
from aitoolkit_cam import Camera, Processor
import cv2
import time
import threading
import numpy as np

def multi_camera_example():
    """多摄像头同时使用示例"""
    print("=== 多摄像头示例 ===")
    
    # 检测可用摄像头
    available_cameras = Camera.find_available_cameras()
    print(f"检测到可用摄像头: {available_cameras}")
    
    if len(available_cameras) < 2:
        print("⚠️ 需要至少2个摄像头才能运行此示例")
        return
    
    # 创建多个摄像头实例
    cam1 = Camera(source=available_cameras[0], web_enabled=True, port=9010)
    cam2 = Camera(source=available_cameras[1], web_enabled=True, port=9011)
    
    try:
        # 启动摄像头
        print("启动摄像头1...")
        cam1.start()
        url1 = cam1.get_web_url()
        
        print("启动摄像头2...")
        cam2.start()
        url2 = cam2.get_web_url()
        
        print(f"🌐 摄像头1地址: {url1}")
        print(f"🌐 摄像头2地址: {url2}")
        
        # 同时读取两个摄像头的数据
        for i in range(5):
            ret1, frame1 = cam1.read()
            ret2, frame2 = cam2.read()
            
            if ret1 and ret2:
                print(f"帧 {i+1}: 摄像头1={frame1.shape}, 摄像头2={frame2.shape}")
            
            time.sleep(1)
        
        print("✅ 多摄像头示例完成")
        
    except Exception as e:
        print(f"❌ 多摄像头错误: {e}")
    finally:
        cam1.stop()
        cam2.stop()

def custom_processing_example():
    """自定义图像处理示例"""
    print("\n=== 自定义图像处理示例 ===")
    
    def custom_effect(frame):
        """自定义效果：彩虹边框"""
        if frame is None:
            return frame
        
        h, w = frame.shape[:2]
        
        # 创建彩虹边框
        border_size = 20
        colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), 
                 (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]
        
        result = frame.copy()
        
        for i, color in enumerate(colors):
            thickness = border_size - i * 2
            if thickness > 0:
                cv2.rectangle(result, (i, i), (w-i-1, h-i-1), color, 2)
        
        return result
    
    cam = Camera(source='auto', web_enabled=True, port=9012)
    
    try:
        cam.start()
        url = cam.get_web_url()
        print(f"🌐 自定义效果地址: {url}")
        
        # 应用自定义效果
        for i, frame in enumerate(cam):
            processed_frame = custom_effect(frame)
            cam.cv_show(processed_frame, "web")
            
            if i >= 50:  # 处理50帧后退出
                break
        
        print("✅ 自定义处理示例完成")
        
    except Exception as e:
        print(f"❌ 自定义处理错误: {e}")
    finally:
        cam.stop()

def performance_monitoring_example():
    """性能监控示例"""
    print("\n=== 性能监控示例 ===")
    
    cam = Camera(source='auto', width=640, height=480)
    
    try:
        cam.start()
        
        # 性能统计
        frame_count = 0
        start_time = time.time()
        processing_times = []
        
        print("开始性能监控...")
        
        for frame in cam:
            frame_start = time.time()
            
            # 模拟一些处理
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            frame_end = time.time()
            processing_time = frame_end - frame_start
            processing_times.append(processing_time)
            
            frame_count += 1
            
            # 每10帧输出一次统计
            if frame_count % 10 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                avg_processing = np.mean(processing_times[-10:]) * 1000
                
                print(f"帧数: {frame_count}, FPS: {fps:.1f}, "
                      f"平均处理时间: {avg_processing:.1f}ms")
            
            if frame_count >= 50:
                break
        
        # 最终统计
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        avg_processing = np.mean(processing_times) * 1000
        
        print(f"\n📊 性能统计:")
        print(f"   总帧数: {frame_count}")
        print(f"   总时间: {total_time:.2f}秒")
        print(f"   平均FPS: {avg_fps:.1f}")
        print(f"   平均处理时间: {avg_processing:.1f}ms")
        
    except Exception as e:
        print(f"❌ 性能监控错误: {e}")
    finally:
        cam.stop()

def threaded_processing_example():
    """多线程处理示例"""
    print("\n=== 多线程处理示例 ===")
    
    cam = Camera(source='auto')
    processed_frames = []
    processing_lock = threading.Lock()
    
    def processing_worker(frame_queue):
        """处理线程工作函数"""
        processor = Processor('cartoon')
        
        while True:
            try:
                frame = frame_queue.get(timeout=1.0)
                if frame is None:  # 结束信号
                    break
                
                # 处理帧
                processed = processor.process(frame)
                
                with processing_lock:
                    processed_frames.append(processed)
                
                frame_queue.task_done()
                
            except:
                break
    
    try:
        cam.start()
        
        # 创建帧队列和处理线程
        import queue
        frame_queue = queue.Queue(maxsize=10)
        
        # 启动处理线程
        worker_thread = threading.Thread(target=processing_worker, args=(frame_queue,))
        worker_thread.daemon = True
        worker_thread.start()
        
        print("开始多线程处理...")
        
        # 主线程负责读取帧
        for i, frame in enumerate(cam):
            try:
                frame_queue.put(frame, timeout=0.1)
            except queue.Full:
                print("队列满，跳过帧")
            
            # 检查处理结果
            with processing_lock:
                if processed_frames:
                    processed = processed_frames.pop(0)
                    print(f"处理完成帧 {i}: {processed.shape}")
            
            if i >= 20:
                break
        
        # 发送结束信号
        frame_queue.put(None)
        worker_thread.join(timeout=2.0)
        
        print("✅ 多线程处理示例完成")
        
    except Exception as e:
        print(f"❌ 多线程处理错误: {e}")
    finally:
        cam.stop()

def context_manager_example():
    """上下文管理器使用示例"""
    print("\n=== 上下文管理器示例 ===")
    
    try:
        # 使用with语句自动管理资源
        with Camera(source='auto', web_enabled=True, port=9013) as cam:
            url = cam.get_web_url()
            print(f"🌐 上下文管理器地址: {url}")
            
            # 读取一些帧
            for i in range(5):
                ret, frame = cam.read()
                if ret:
                    print(f"帧 {i+1}: {frame.shape}")
                time.sleep(0.5)
        
        print("✅ 上下文管理器示例完成（资源自动清理）")
        
    except Exception as e:
        print(f"❌ 上下文管理器错误: {e}")

if __name__ == "__main__":
    multi_camera_example()
    custom_processing_example()
    performance_monitoring_example()
    threaded_processing_example()
    context_manager_example() 