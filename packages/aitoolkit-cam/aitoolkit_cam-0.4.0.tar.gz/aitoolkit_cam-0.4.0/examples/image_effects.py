#!/usr/bin/env python3
"""
中学生图像特效教程 - 学会给照片添加酷炫效果
"""
from aitoolkit_cam import Camera, Processor, ProcessedCamera, apply_effect
import cv2
import time

def lesson1_simple_effects():
    """第1课：给照片添加简单特效"""
    print("🎨 第1课：给照片添加简单特效")
    print("=" * 50)
    
    # 创建摄像头
    cam = Camera(source='auto')
    
    try:
        cam.start()
        print("📸 先拍一张原始照片...")
        
        # 拍摄原始照片
        ret, original_photo = cam.read()
        if not ret:
            print("❌ 无法拍摄照片")
            return
        
        print(f"✅ 拍摄成功！照片尺寸: {original_photo.shape[1]}x{original_photo.shape[0]} 像素")
        
        # 尝试几种简单特效
        simple_effects = ['gray', 'edge', 'blur', 'negative', 'mirror']
        effect_names = {
            'gray': '黑白照片',
            'edge': '边缘检测', 
            'blur': '模糊效果',
            'negative': '底片效果',
            'mirror': '镜像翻转'
        }
        
        print("\n🎭 开始添加特效...")
        for effect in simple_effects:
            print(f"   🔄 正在添加 {effect_names[effect]} 效果...")
            
            # 使用apply_effect函数快速添加效果
            processed_photo = apply_effect(original_photo, effect)
            
            print(f"   ✅ {effect_names[effect]} 效果添加完成！")
            time.sleep(0.5)  # 短暂停顿，让学生看到进度
        
        print("\n💡 解释：")
        print("   - 原始照片就像一张白纸")
        print("   - 特效就像不同的滤镜或画笔")
        print("   - 程序把滤镜应用到照片上，产生新的效果")
        
    except Exception as e:
        print(f"❌ 特效处理出错: {e}")
    finally:
        cam.stop()

def lesson2_real_time_effects():
    """第2课：实时特效（理解画面同步）"""
    print("\n⚡ 第2课：实时特效")
    print("=" * 50)
    print("💡 这一课我们学习如何给实时画面添加特效")
    
    # 创建带特效的摄像头
    cam = ProcessedCamera(source='auto', effect_type='cartoon', 
                         web_enabled=True, port=9002)
    
    try:
        cam.start()
        url = cam.get_web_url()
        
        if url:
            print(f"🌐 实时特效地址: {url}")
            print("👀 请在浏览器中打开，观察实时特效")
            print("🎭 我们将每3秒切换一种特效...")
            
            # 准备几种酷炫特效
            cool_effects = ['cartoon', 'sketch', 'thermal', 'night_vision', 'vintage']
            effect_names = {
                'cartoon': '卡通效果',
                'sketch': '素描效果',
                'thermal': '热成像效果',
                'night_vision': '夜视效果',
                'vintage': '复古效果'
            }
            
            for i, effect in enumerate(cool_effects, 1):
                print(f"\n🎨 第{i}种特效: {effect_names[effect]}")
                cam.set_effect(effect)
                
                # 每种特效显示3秒，同时处理画面
                start_time = time.time()
                frame_count = 0
                
                while time.time() - start_time < 3:
                    # 获取处理后的画面
                    processed_frame = next(cam)
                    frame_count += 1
                    
                    # 每秒报告一次处理进度
                    if frame_count % 30 == 0:
                        print(f"   ⚡ 已处理 {frame_count} 帧画面")
                
                print(f"   ✅ {effect_names[effect]} 完成，共处理 {frame_count} 帧")
            
            print("\n🔄 画面同步原理解释：")
            print("1. 摄像头不断拍摄新照片（每秒30张）")
            print("2. 程序对每张照片应用特效处理")
            print("3. 处理后的照片立即发送到网页显示")
            print("4. 这样就形成了实时特效视频！")
            
        else:
            print("❌ 实时特效启动失败")
            
    except Exception as e:
        print(f"❌ 实时特效出错: {e}")
    finally:
        cam.stop()

def lesson3_effect_comparison():
    """第3课：特效对比实验"""
    print("\n🔬 第3课：特效对比实验")
    print("=" * 50)
    print("🧪 我们来做个实验，比较不同特效的处理速度")
    
    cam = Camera(source='auto')
    
    try:
        cam.start()
        
        # 拍摄测试照片
        ret, test_photo = cam.read()
        if not ret:
            print("❌ 无法拍摄测试照片")
            return
        
        print(f"📸 测试照片准备完成: {test_photo.shape[1]}x{test_photo.shape[0]} 像素")
        
        # 测试不同特效的处理速度
        effects_to_test = ['gray', 'cartoon', 'thermal', 'oil_painting']
        effect_names = {
            'gray': '黑白效果（简单）',
            'cartoon': '卡通效果（中等）',
            'thermal': '热成像效果（中等）',
            'oil_painting': '油画效果（复杂）'
        }
        
        print("\n⏱️  特效处理速度测试：")
        for effect in effects_to_test:
            print(f"\n🎨 测试 {effect_names[effect]}...")
            
            # 测试处理10次的时间
            start_time = time.time()
            for i in range(10):
                processed = apply_effect(test_photo, effect)
                if i == 0:  # 只在第一次显示结果
                    print(f"   ✅ 处理成功，输出尺寸: {processed.shape[1]}x{processed.shape[0]}")
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 10 * 1000  # 转换为毫秒
            
            print(f"   ⚡ 平均处理时间: {avg_time:.1f} 毫秒/张")
            
            # 根据速度给出评价
            if avg_time < 10:
                print("   🚀 超快速！适合实时处理")
            elif avg_time < 30:
                print("   ⚡ 快速！可以实时处理")
            elif avg_time < 100:
                print("   🐌 较慢，实时处理可能有延迟")
            else:
                print("   🐢 很慢，不适合实时处理")
        
        print("\n💡 学到的知识：")
        print("   - 简单特效处理速度快，适合实时应用")
        print("   - 复杂特效处理速度慢，但效果更酷炫")
        print("   - 选择特效时要考虑速度和效果的平衡")
        
    except Exception as e:
        print(f"❌ 对比实验出错: {e}")
    finally:
        cam.stop()

def lesson4_custom_effect_demo():
    """第4课：自定义特效演示"""
    print("\n🛠️  第4课：自定义特效演示")
    print("=" * 50)
    print("🎯 学会创建自己的特效！")
    
    def rainbow_border_effect(photo):
        """彩虹边框特效 - 给照片加上彩色边框"""
        if photo is None:
            return photo
        
        # 获取照片尺寸
        height, width = photo.shape[:2]
        
        # 彩虹颜色（红橙黄绿蓝靛紫）
        rainbow_colors = [
            (255, 0, 0),    # 红色
            (255, 127, 0),  # 橙色
            (255, 255, 0),  # 黄色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
            (75, 0, 130),   # 靛色
            (148, 0, 211)   # 紫色
        ]
        
        # 复制原始照片
        result = photo.copy()
        
        # 画彩虹边框
        border_width = 15
        for i, color in enumerate(rainbow_colors):
            thickness = border_width - i * 2
            if thickness > 0:
                cv2.rectangle(result, (i, i), (width-i-1, height-i-1), color, 2)
        
        return result
    
    cam = Camera(source='auto', web_enabled=True, port=9003)
    
    try:
        cam.start()
        url = cam.get_web_url()
        
        if url:
            print(f"🌐 自定义特效地址: {url}")
            print("🌈 我们创建了一个彩虹边框特效！")
            print("👀 请在浏览器中观察效果...")
            
            print("\n🎨 开始应用彩虹边框特效...")
            
            # 应用自定义特效10秒
            start_time = time.time()
            frame_count = 0
            
            while time.time() - start_time < 10:
                # 获取原始画面
                ret, frame = cam.read()
                if ret:
                    # 应用自定义特效
                    rainbow_frame = rainbow_border_effect(frame)
                    
                    # 在网页上显示
                    cam.cv_show(rainbow_frame, "web")
                    
                    frame_count += 1
                    
                    # 每3秒报告一次
                    if frame_count % 90 == 0:
                        elapsed = int(time.time() - start_time)
                        print(f"   🌈 已应用彩虹特效 {elapsed} 秒")
                
                time.sleep(0.033)  # 约30帧每秒
            
            print(f"✅ 自定义特效演示完成！共处理 {frame_count} 帧")
            
            print("\n🎓 自定义特效原理：")
            print("1. 获取原始照片")
            print("2. 编写特效处理函数")
            print("3. 对照片进行像素级修改")
            print("4. 返回处理后的照片")
            print("💡 你也可以创造自己的特效！")
        
    except Exception as e:
        print(f"❌ 自定义特效出错: {e}")
    finally:
        cam.stop()

if __name__ == "__main__":
    print("🎨 欢迎来到图像特效编程课堂！")
    print("🌟 我们将学习如何给照片和视频添加酷炫特效")
    print("📚 同时理解画面处理和同步的原理")
    print()
    
    # 依次进行4个课程
    lesson1_simple_effects()
    
    input("\n按回车键继续下一课...")
    lesson2_real_time_effects()
    
    input("\n按回车键继续下一课...")
    lesson3_effect_comparison()
    
    input("\n按回车键继续下一课...")
    lesson4_custom_effect_demo()
    
    print("\n🎉 恭喜！你已经掌握了图像特效编程！")
    print("🎯 现在你知道了：")
    print("   ✅ 如何给照片添加特效")
    print("   ✅ 实时特效的工作原理")
    print("   ✅ 不同特效的处理速度差异")
    print("   ✅ 如何创建自定义特效")
    print("   ✅ 画面同步和处理的秘密")
    print()
    print("🚀 继续探索更多创意特效吧！") 