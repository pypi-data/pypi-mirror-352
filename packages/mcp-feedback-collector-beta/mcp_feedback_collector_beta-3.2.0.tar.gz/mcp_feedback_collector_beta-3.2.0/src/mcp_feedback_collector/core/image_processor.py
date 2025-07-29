"""
图片处理模块
统一处理图片相关的所有操作，包括加载、转换、压缩等
"""

import io
import base64
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Union
from PIL import Image
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

from .config import config


class ImageProcessor:
    """图片处理器"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'PNG', 'JPEG', 'JPG', 'GIF', 'BMP', 'WEBP'}
    
    @staticmethod
    def load_from_file(file_path: Union[str, Path]) -> Optional[Dict]:
        """从文件加载图片"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 验证文件
            is_valid, message = config.validate_file_upload(path.name, path.stat().st_size)
            if not is_valid:
                raise ValueError(message)
            
            # 读取图片数据
            with open(path, 'rb') as f:
                image_data = f.read()
            
            # 打开图片获取信息
            img = Image.open(io.BytesIO(image_data))
            
            return {
                'data': image_data,
                'source': f'文件: {path.name}',
                'size': img.size,
                'format': img.format,
                'mode': img.mode,
                'image': img,
                'filename': path.name
            }
            
        except Exception as e:
            raise Exception(f"加载图片失败: {str(e)}")
    
    @staticmethod
    def load_from_clipboard() -> Optional[Dict]:
        """从剪贴板加载图片"""
        if ImageGrab is None:
            raise Exception("当前系统不支持剪贴板图片功能")
        
        try:
            img = ImageGrab.grabclipboard()
            if not img:
                raise Exception("剪贴板中没有图片数据")
            
            # 转换为PNG格式
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_data = buffer.getvalue()
            
            return {
                'data': image_data,
                'source': '剪贴板',
                'size': img.size,
                'format': 'PNG',
                'mode': img.mode,
                'image': img,
                'filename': 'clipboard.png'
            }
            
        except Exception as e:
            raise Exception(f"从剪贴板获取图片失败: {str(e)}")
    
    @staticmethod
    def load_from_bytes(image_data: bytes, source: str = "未知") -> Dict:
        """从字节数据加载图片"""
        try:
            img = Image.open(io.BytesIO(image_data))
            
            return {
                'data': image_data,
                'source': source,
                'size': img.size,
                'format': img.format,
                'mode': img.mode,
                'image': img,
                'filename': f'{source}.{img.format.lower()}'
            }
            
        except Exception as e:
            raise Exception(f"解析图片数据失败: {str(e)}")
    
    @staticmethod
    def create_thumbnail(img_info: Dict, max_size: Tuple[int, int] = (100, 80)) -> bytes:
        """创建缩略图"""
        try:
            img = img_info['image'].copy()
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"创建缩略图失败: {str(e)}")
    
    @staticmethod
    def resize_for_preview(img_info: Dict, max_size: int = 800) -> bytes:
        """调整图片大小用于预览"""
        try:
            img = img_info['image']
            
            # 如果图片太大，缩放显示
            if img.width > max_size or img.height > max_size:
                img_copy = img.copy()
                img_copy.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            else:
                img_copy = img
            
            buffer = io.BytesIO()
            img_copy.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"调整图片大小失败: {str(e)}")
    
    @staticmethod
    def to_base64(img_info: Dict) -> str:
        """转换为Base64编码"""
        try:
            image_data = img_info['data']
            format_name = img_info.get('format', 'PNG').lower()
            
            # 确保格式名称正确
            if format_name == 'jpeg':
                format_name = 'jpg'
            
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/{format_name};base64,{base64_data}"
            
        except Exception as e:
            raise Exception(f"转换Base64失败: {str(e)}")
    
    @staticmethod
    def from_base64(base64_string: str) -> Dict:
        """从Base64字符串解码图片"""
        try:
            # 解析data URL格式
            if base64_string.startswith('data:image/'):
                header, data = base64_string.split(',', 1)
                format_info = header.split(';')[0].split('/')[1]
            else:
                data = base64_string
                format_info = 'png'
            
            # 解码Base64数据
            image_data = base64.b64decode(data)
            
            return ImageProcessor.load_from_bytes(image_data, f"base64.{format_info}")
            
        except Exception as e:
            raise Exception(f"Base64解码失败: {str(e)}")
    
    @staticmethod
    def get_image_info(img_info: Dict) -> Dict:
        """获取图片详细信息"""
        try:
            return {
                "文件名": img_info.get('filename', '未知'),
                "来源": img_info.get('source', '未知'),
                "格式": img_info.get('format', '未知'),
                "尺寸": f"{img_info['size'][0]} x {img_info['size'][1]}",
                "模式": img_info.get('mode', '未知'),
                "数据大小": f"{len(img_info['data']) / 1024:.1f} KB"
            }
        except Exception as e:
            return {"错误": str(e)}
    
    @staticmethod
    def validate_images(images: List[Dict], max_count: int = 5) -> Tuple[bool, str]:
        """验证图片列表"""
        if len(images) > max_count:
            return False, f"图片数量超过限制: {len(images)} > {max_count}"
        
        total_size = sum(len(img['data']) for img in images)
        max_total_size = config.max_file_size * max_count
        
        if total_size > max_total_size:
            return False, f"图片总大小超过限制: {total_size / 1024 / 1024:.1f}MB > {max_total_size / 1024 / 1024:.1f}MB"
        
        return True, "验证通过"
