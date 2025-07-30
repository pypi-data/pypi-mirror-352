#!/usr/bin/env python3
"""
SimpleWebStream 模块 - 简单的Web视频流实现
不依赖vidgear，使用Flask实现MJPEG流服务器
"""
import threading
import time
import socket
import queue
import cv2
import numpy as np
import logging
from flask import Flask, Response, render_template_string
import sys

# 配置日志
logger = logging.getLogger("aitoolkit_cam.simple_web_stream")
# 不再设置日志级别，让上层决定

class WebStreamer:
    """
    简单的Web视频流服务器
    使用Flask实现MJPEG流，支持局域网访问
    """
    
    def __init__(self, host="0.0.0.0", port=8000):
        """
        初始化SimpleWebStream
        
        参数:
            host: 服务器主机地址，"0.0.0.0"可从网络访问
            port: 服务器端口号
        """
        self.host = host
        self.port = port
        self.is_running = False
        
        # Flask应用
        self.app = Flask(__name__)
        self.app.logger.setLevel(logging.ERROR)  # 减少Flask日志输出
        
        # 帧队列，用于接收来自Camera的帧
        self.frame_queue = queue.Queue(maxsize=10)
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        
        # 服务器线程
        self.server_thread = None
        
        # 设置路由
        self._setup_routes()
    
    def _setup_routes(self):
        """设置Flask路由"""
        
        @self.app.route('/')
        def index():
            """主页面"""
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camera Stream</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background-color: #1a1a1a;
            color: white;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            width: 100%;
            text-align: center;
        }
        h1 {
            color: #4CAF50;
            margin-bottom: 30px;
        }
        .video-container {
            background: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .video-stream {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }
        .status {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        .info {
            background: #333;
            border-radius: 5px;
            padding: 15px;
            margin-top: 20px;
            text-align: left;
        }
        .error {
            background: #d32f2f;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>摄像头实时流 <span class="status" id="status"></span></h1>
        
        <div class="video-container">
            <img src="/video" class="video-stream" alt="视频流" id="videoStream">
        </div>
        
        <div class="info">
            <h3>连接信息</h3>
            <p><strong>服务器地址:</strong> {{ request.host }}</p>
            <p><strong>视频流地址:</strong> {{ request.host_url }}video</p>
            <p><strong>状态:</strong> <span id="statusText">连接中...</span></p>
        </div>
    </div>

    <script>
        const video = document.getElementById('videoStream');
        const status = document.getElementById('status');
        const statusText = document.getElementById('statusText');
        
        video.onload = function() {
            status.style.background = '#4CAF50';
            statusText.textContent = '正常运行';
        };
        
        video.onerror = function() {
            status.style.background = '#f44336';
            statusText.textContent = '连接失败';
            // 尝试重新连接
            setTimeout(() => {
                video.src = '/video?' + new Date().getTime();
            }, 2000);
        };
        
        // 定期检查连接状态
        setInterval(() => {
            if (video.complete && video.naturalWidth === 0) {
                video.src = '/video?' + new Date().getTime();
            }
        }, 5000);
    </script>
</body>
</html>
            """
            return render_template_string(html_template)
        
        @self.app.route('/video')
        def video_feed():
            """视频流端点"""
            return Response(
                self._generate_frames(),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        @self.app.route('/status')
        def status():
            """状态检查端点"""
            return {
                'status': 'running' if self.is_running else 'stopped',
                'has_frame': self.latest_frame is not None,
                'queue_size': self.frame_queue.qsize()
            }
    
    def _generate_frames(self):
        """生成MJPEG帧流"""
        # logger.info("开始生成视频帧流")  # 删除这个日志
        
        # JPEG编码参数
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
        frame_count = 0
        
        while self.is_running:
            frame = None
            
            # 尝试从队列获取最新帧
            try:
                # 非阻塞获取最新帧
                frame = self.frame_queue.get(timeout=0.1)
                
                # 清空队列中的旧帧，只保留最新的
                while not self.frame_queue.empty():
                    try:
                        newer_frame = self.frame_queue.get_nowait()
                        frame = newer_frame  # 使用更新的帧
                    except queue.Empty:
                        break
                        
            except queue.Empty:
                # 队列为空时，使用最后一帧
                with self.frame_lock:
                    frame = self.latest_frame
            except Exception as e:
                logger.error(f"获取帧时出错: {e}")
                frame = None
            
            # 如果没有帧，生成占位帧
            if frame is None:
                frame = self._create_placeholder_frame()
            else:
                frame_count += 1
                # 更新最新帧（不复制，直接引用）
                with self.frame_lock:
                    self.latest_frame = frame
            
            try:
                # 编码为JPEG
                success, buffer = cv2.imencode('.jpg', frame, encode_params)
                if not success:
                    logger.warning("帧编码失败")
                    continue
                
                # 生成MJPEG流格式
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                if frame_count % 100 == 0:
                    logger.debug(f"已发送 {frame_count} 帧")
                    
            except Exception as e:
                logger.error(f"帧编码或发送时出错: {e}")
                continue
            
            # 控制帧率
            time.sleep(0.033)  # 约30fps
        
        logger.info("视频帧流生成结束")
    
    def _create_placeholder_frame(self, width=640, height=480):
        """创建占位帧"""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 添加文字
        text = "Waiting for camera..."
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, 1, 2)[0]
        
        # 居中显示
        x = (width - text_size[0]) // 2
        y = (height + text_size[1]) // 2
        
        cv2.putText(frame, text, (x, y), font, 1, (255, 255, 255), 2)
        
        # 添加时间戳
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, height - 20), font, 0.5, (128, 128, 128), 1)
        
        return frame
    
    def update_frame(self, frame):
        """更新帧数据"""
        if frame is None:
            return
            
        try:
            # 非阻塞方式放入队列
            if not self.frame_queue.full():
                self.frame_queue.put(frame, block=False)
            else:
                # 队列满时，丢弃旧帧，保留新帧
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put(frame, block=False)
                except queue.Empty:
                    pass
        except Exception as e:
            logger.debug(f"更新帧时出错: {e}")
    
    def _find_available_port(self, start_port=9000, max_attempts=50):
        """查找可用端口，使用更高端口范围避免权限问题"""
        # 如果原始端口小于9000，从9000开始查找
        if start_port < 9000:
            start_port = 9000
            
        for offset in range(max_attempts):
            test_port = start_port + offset
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(0.5)
                sock.bind(('0.0.0.0', test_port))
                sock.close()
                logger.info(f"找到可用端口: {test_port}")
                return test_port
            except OSError:
                continue
            except Exception as e:
                logger.debug(f"检测端口 {test_port} 时出错: {e}")
                continue
        
        logger.warning(f"未找到可用端口，使用原始端口 {start_port}")
        return start_port
    
    def _get_local_ip(self):
        """获取本机局域网IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
    
    def start(self):
        """启动Web服务器"""
        if self.is_running:
            return self.get_url()
        
        # 查找可用端口
        original_port = self.port
        self.port = self._find_available_port(self.port)
        if self.port != original_port:
            logger.info(f"端口从 {original_port} 更改为 {self.port}")
        
        self.is_running = True
        
        # 启动Flask服务器线程
        def run_server():
            try:
                # 禁用Flask的启动信息
                import logging as flask_logging
                flask_log = flask_logging.getLogger('werkzeug')
                flask_log.setLevel(flask_logging.ERROR)
                
                self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                logger.error(f"Flask服务器启动失败: {e}")
                self.is_running = False
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动
        max_wait = 5.0
        waited = 0
        while waited < max_wait:
            if self._test_connection():
                url = self.get_url()
                logger.info(f"Web服务器启动成功: {url}")
                return url
            time.sleep(0.2)
            waited += 0.2
        
        logger.error("Web服务器启动超时")
        self.is_running = False
        return None
    
    def _test_connection(self):
        """测试服务器连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((self.host if self.host != "0.0.0.0" else "127.0.0.1", self.port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def get_url(self):
        """获取访问URL"""
        if self.host == "0.0.0.0":
            # 返回局域网IP
            local_ip = self._get_local_ip()
            return f"http://{local_ip}:{self.port}/"
        else:
            return f"http://{self.host}:{self.port}/"
    
    def stop(self):
        """停止服务器"""
        if not self.is_running:
            logger.info("Web服务器已经停止")
            return
            
        logger.info("正在停止Web服务器...")
        self.is_running = False
        
        # 等待服务器线程结束
        if self.server_thread and self.server_thread.is_alive():
            logger.info("等待服务器线程结束...")
            self.server_thread.join(timeout=3.0)
            if self.server_thread.is_alive():
                logger.warning("服务器线程未能在3秒内结束")
        
        # 强制清理Flask应用
        try:
            # 尝试关闭Flask的内置服务器
            import requests
            try:
                # 发送shutdown请求（如果Flask支持）
                requests.post(f"http://127.0.0.1:{self.port}/shutdown", timeout=1)
            except:
                pass
        except:
            pass
        
        # 清理资源
        self.server_thread = None
        logger.info("Web服务器已停止") 