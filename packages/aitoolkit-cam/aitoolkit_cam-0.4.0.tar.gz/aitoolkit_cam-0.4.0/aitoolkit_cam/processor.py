"""
图像处理模块 - 提供图像处理功能
"""
import cv2
import numpy as np
from typing import Optional, Any, Dict, List, Tuple, Union
from .camera import Camera

class Processor:
    """
    图像处理类，提供各种图像效果处理
    
    使用方法:
    ```
    from aitoolkit_cam import Processor
    
    # 创建处理器
    processor = Processor(effect_type="gray")  # 创建灰度处理器
    
    # 处理图像
    gray_image = processor.process(image)
    
    # 切换效果
    processor.set_effect("edge")
    edge_image = processor.process(image)
    
    # 获取当前效果和支持的所有效果
    current_effect = processor.get_effect()
    all_effects = processor.get_supported_effects()
    ```
    """
    
    def __init__(self, effect_type: str = "original"):
        """
        初始化图像处理器
        
        参数:
            effect_type: 效果类型, 可选值包括:
                - "original": 原始图像
                - "gray": 灰度图像
                - "edge": 边缘检测
                - "blur": 高斯模糊
                - "sketch": 素描效果
                - "cartoon": 卡通效果
                - "vintage": 复古效果
                - "night_vision": 夜视效果
                - "thermal": 热成像效果
                - "oil_painting": 油画效果
                - "emboss": 浮雕效果
                - "sepia": 棕褐色效果
                - "negative": 负片效果
                - "mirror": 镜像效果
        """
        self.effect_type = effect_type
        # 支持的效果列表
        self.SUPPORTED_EFFECTS = [
            "original", "gray", "edge", "blur", "sketch", "cartoon",
            "vintage", "night_vision", "thermal", "oil_painting", 
            "emboss", "sepia", "negative", "mirror"
        ]
        # 验证效果类型
        if self.effect_type not in self.SUPPORTED_EFFECTS:
            print(f"警告: 不支持的效果类型 '{effect_type}'，已设置为 'original'")
            self.effect_type = "original"

    def set_effect(self, effect_type: str) -> None:
        """
        设置效果类型
        
        参数:
            effect_type: 效果类型
        """
        if effect_type not in self.SUPPORTED_EFFECTS:
            print(f"警告: 不支持的效果类型 '{effect_type}'，保持当前设置")
            return
        self.effect_type = effect_type
    
    def get_effect(self) -> str:
        """
        获取当前效果类型
        
        返回:
            当前效果类型
        """
        return self.effect_type
    
    def get_supported_effects(self) -> List[str]:
        """
        获取所有支持的效果列表
        
        返回:
            支持的效果列表
        """
        return self.SUPPORTED_EFFECTS
    
    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        处理图像帧
        
        参数:
            frame: 输入图像帧
        
        返回:
            处理后的图像帧
        """
        if frame is None:
            return None
        
        # 根据效果类型处理图像
        if self.effect_type == "original":
            return frame
        elif self.effect_type == "gray":
            return self._convert_to_gray(frame)
        elif self.effect_type == "edge":
            return self._detect_edges(frame)
        elif self.effect_type == "blur":
            return self._apply_blur(frame)
        elif self.effect_type == "sketch":
            return self._create_sketch(frame)
        elif self.effect_type == "cartoon":
            return self._create_cartoon(frame)
        elif self.effect_type == "vintage":
            return self._create_vintage(frame)
        elif self.effect_type == "night_vision":
            return self._create_night_vision(frame)
        elif self.effect_type == "thermal":
            return self._create_thermal(frame)
        elif self.effect_type == "oil_painting":
            return self._create_oil_painting(frame)
        elif self.effect_type == "emboss":
            return self._create_emboss(frame)
        elif self.effect_type == "sepia":
            return self._create_sepia(frame)
        elif self.effect_type == "negative":
            return self._create_negative(frame)
        elif self.effect_type == "mirror":
            return self._create_mirror(frame)
        else:
            return frame  # 默认返回原始帧

    def _convert_to_gray(self, frame: np.ndarray) -> np.ndarray:
        """将图像转换为灰度"""
        if frame is None:
            return None
            
        try:
            # 检查是否已经是灰度图
            if len(frame.shape) == 2:
                return frame
                
            # 转换为灰度图
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(f"灰度转换错误: {e}")
            return frame
    
    def _detect_edges(self, frame: np.ndarray) -> np.ndarray:
        """边缘检测效果"""
        if frame is None:
            return None
            
        try:
            # 如果是彩色图像，先转为灰度
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # 使用Canny算法进行边缘检测
            return cv2.Canny(gray, 50, 150)
        except Exception as e:
            print(f"边缘检测错误: {e}")
            return frame
    
    def _apply_blur(self, frame: np.ndarray) -> np.ndarray:
        """高斯模糊效果"""
        if frame is None:
            return None
            
        try:
            return cv2.GaussianBlur(frame, (15, 15), 0)
        except Exception as e:
            print(f"高斯模糊错误: {e}")
            return frame
    
    def _create_sketch(self, frame: np.ndarray) -> np.ndarray:
        """素描效果"""
        if frame is None:
            return None
            
        try:
            # 如果是彩色图像，先转为灰度
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # 对灰度图像进行高斯模糊
            inv = 255 - gray
            blur = cv2.GaussianBlur(inv, (21, 21), 0)
            
            # 叠加模糊图像和灰度图像，模拟素描效果
            return cv2.divide(gray, 255 - blur, scale=256)
        except Exception as e:
            print(f"素描效果错误: {e}")
            return frame
    
    def _create_cartoon(self, frame: np.ndarray) -> np.ndarray:
        """卡通效果"""
        if frame is None:
            return None
            
        try:
            # 降噪处理
            color = cv2.bilateralFilter(frame, 9, 300, 300)
            
            # 边缘检测
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
                color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            # 使用自适应阈值处理
            edge = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                        cv2.THRESH_BINARY, 9, 3)
            
            # 如果是灰度图，则转回彩色图以便合并
            if len(frame.shape) == 2:
                edge = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
            
            # 合并边缘和颜色图像
            return cv2.bitwise_and(color, color, mask=edge)
        except Exception as e:
            print(f"卡通效果错误: {e}")
            return frame

    def _create_vintage(self, frame: np.ndarray) -> np.ndarray:
        """复古效果"""
        if frame is None:
            return None
            
        try:
            # 创建复古色调矩阵
            vintage_matrix = np.array([[0.393, 0.769, 0.189],
                                     [0.349, 0.686, 0.168],
                                     [0.272, 0.534, 0.131]])
            
            # 应用色调变换
            vintage = cv2.transform(frame, vintage_matrix)
            
            # 限制像素值范围
            vintage = np.clip(vintage, 0, 255).astype(np.uint8)
            
            # 添加暖色调
            vintage[:, :, 0] = np.clip(vintage[:, :, 0] * 0.9, 0, 255)  # 减少蓝色
            vintage[:, :, 2] = np.clip(vintage[:, :, 2] * 1.1, 0, 255)  # 增加红色
            
            return vintage
        except Exception as e:
            print(f"复古效果错误: {e}")
            return frame
    
    def _create_night_vision(self, frame: np.ndarray) -> np.ndarray:
        """夜视效果"""
        if frame is None:
            return None
            
        try:
            # 转换为灰度
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # 增强对比度
            enhanced = cv2.equalizeHist(gray)
            
            # 创建绿色夜视效果
            night_vision = np.zeros((enhanced.shape[0], enhanced.shape[1], 3), dtype=np.uint8)
            night_vision[:, :, 1] = enhanced  # 绿色通道
            
            # 添加噪点效果
            noise = np.random.randint(0, 50, enhanced.shape, dtype=np.uint8)
            night_vision[:, :, 1] = np.clip(night_vision[:, :, 1] + noise, 0, 255)
            
            return night_vision
        except Exception as e:
            print(f"夜视效果错误: {e}")
            return frame
    
    def _create_thermal(self, frame: np.ndarray) -> np.ndarray:
        """热成像效果"""
        if frame is None:
            return None
            
        try:
            # 转换为灰度
            if len(frame.shape) == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray = frame
            
            # 应用热成像色彩映射
            thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            
            return thermal
        except Exception as e:
            print(f"热成像效果错误: {e}")
            return frame
    
    def _create_oil_painting(self, frame: np.ndarray) -> np.ndarray:
        """油画效果"""
        if frame is None:
            return None
            
        try:
            # 使用双边滤波器创建油画效果
            oil = cv2.bilateralFilter(frame, 15, 80, 80)
            oil = cv2.bilateralFilter(oil, 15, 80, 80)
            
            # 减少颜色数量
            data = oil.reshape((-1, 3))
            data = np.float32(data)
            
            # K-means聚类减少颜色
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, 8, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # 重建图像
            centers = np.uint8(centers)
            segmented_data = centers[labels.flatten()]
            oil_painting = segmented_data.reshape(oil.shape)
            
            return oil_painting
        except Exception as e:
            print(f"油画效果错误: {e}")
            return frame
    
    def _create_emboss(self, frame: np.ndarray) -> np.ndarray:
        """浮雕效果"""
        if frame is None:
            return None
            
        try:
            # 浮雕卷积核
            emboss_kernel = np.array([[-2, -1, 0],
                                    [-1, 1, 1],
                                    [0, 1, 2]])
            
            # 应用卷积
            embossed = cv2.filter2D(frame, -1, emboss_kernel)
            
            # 调整亮度
            embossed = cv2.add(embossed, 128)
            
            return embossed
        except Exception as e:
            print(f"浮雕效果错误: {e}")
            return frame
    
    def _create_sepia(self, frame: np.ndarray) -> np.ndarray:
        """棕褐色效果"""
        if frame is None:
            return None
            
        try:
            # 棕褐色变换矩阵
            sepia_matrix = np.array([[0.272, 0.534, 0.131],
                                   [0.349, 0.686, 0.168],
                                   [0.393, 0.769, 0.189]])
            
            # 应用变换
            sepia = cv2.transform(frame, sepia_matrix)
            
            # 限制像素值范围
            sepia = np.clip(sepia, 0, 255).astype(np.uint8)
            
            return sepia
        except Exception as e:
            print(f"棕褐色效果错误: {e}")
            return frame
    
    def _create_negative(self, frame: np.ndarray) -> np.ndarray:
        """负片效果"""
        if frame is None:
            return None
            
        try:
            # 简单的负片效果：255 - 像素值
            negative = 255 - frame
            return negative
        except Exception as e:
            print(f"负片效果错误: {e}")
            return frame
    
    def _create_mirror(self, frame: np.ndarray) -> np.ndarray:
        """镜像效果"""
        if frame is None:
            return None
            
        try:
            # 水平镜像
            mirrored = cv2.flip(frame, 1)
            return mirrored
        except Exception as e:
            print(f"镜像效果错误: {e}")
            return frame


def apply_effect(frame: np.ndarray, effect_type: str, **kwargs) -> np.ndarray:
    """
    对图像应用指定效果
    
    参数:
        frame: 输入图像帧
        effect_type: 效果类型
        **kwargs: 附加参数，依效果类型而定
    
    返回:
        处理后的图像帧
        
    示例:
    ```python
    import cv2
    from aitoolkit_cam import apply_effect
    
    # 读取图像
    image = cv2.imread('image.jpg')
    
    # 应用不同效果
    gray = apply_effect(image, 'gray')
    edge = apply_effect(image, 'edge', threshold1=100, threshold2=200)
    blur = apply_effect(image, 'blur', ksize=(21, 21))
    sketch = apply_effect(image, 'sketch')
    cartoon = apply_effect(image, 'cartoon')
    
    # 显示结果
    cv2.imshow('原图', image)
    cv2.imshow('灰度', gray)
    cv2.imshow('边缘', edge)
    cv2.imshow('模糊', blur)
    cv2.imshow('素描', sketch)
    cv2.imshow('卡通', cartoon)
    cv2.waitKey(0)
    ```
    """
    # 创建临时处理器
    processor = Processor(effect_type)
    # 处理并返回
    return processor.process(frame)


class ProcessedCamera(Camera):
    """
    具有实时图像处理效果的摄像头类
    
    在标准Camera类的基础上添加了图像处理功能
    
    使用方法:
    ```python
    from aitoolkit_cam import ProcessedCamera
    
    # 创建带有图像处理效果的摄像头对象
    cam = ProcessedCamera(source=0, effect_type="sketch")
    
    # 启动网页服务器
    url = cam.start()
    print(f"请访问: {url}")
    
    # 迭代获取处理后的帧
    for frame in cam:
        # frame已经应用了指定效果
        pass
    
    # 随时切换效果
    cam.set_effect("cartoon")
    
    # 关闭资源
    cam.stop()
    ```
    """
    
    def __init__(self, source=0, host="localhost", port=8000, reduction=30, 
                 effect_type="original", effect_params=None, **kwargs):
        """
        初始化具有图像处理效果的摄像头
        
        参数:
            source: 视频源，可以是摄像头索引(0,1...)或视频文件路径
            host: 服务器主机地址，使用"0.0.0.0"可从网络访问，"localhost"仅本机访问
            port: 服务器端口号
            reduction: 图像尺寸减少百分比，用于提高性能，设为0则不减少
            effect_type: 效果类型，可选值包括"original", "gray", "edge", "blur", "sketch", "cartoon"
            effect_params: 效果参数，根据effect_type不同而变化
            **kwargs: 其他传递给Camera初始化的参数
        """
        # 初始化基类
        super().__init__(source, host, port, reduction, **kwargs)
        
        # 创建图像处理器
        self.processor = Processor(effect_type)
        
        # 存储效果参数
        self.effect_params = effect_params or {}
    
    def set_effect(self, effect_type):
        """
        设置图像处理效果
        
        参数:
            effect_type: 效果类型
        """
        self.processor.set_effect(effect_type)
    
    def get_effect(self):
        """
        获取当前效果类型
        
        返回:
            当前效果类型
        """
        return self.processor.get_effect()
    
    def get_supported_effects(self):
        """
        获取所有支持的效果列表
        
        返回:
            支持的效果列表
        """
        return self.processor.get_supported_effects()
    
    def __iter__(self):
        """
        重写迭代器方法，返回处理后的帧
        """
        # 使用基类的迭代器
        self._iterator = super().__iter__()
        return self
    
    def __next__(self):
        """
        获取下一帧并应用当前效果
        
        返回:
            处理后的帧
        """
        # 获取原始帧
        frame = next(self._iterator)
        
        # 应用效果处理
        processed_frame = self.processor.process(frame)
        
        # 在网页端显示处理后的帧
        self.set_current_frame(processed_frame)
        
        return processed_frame 