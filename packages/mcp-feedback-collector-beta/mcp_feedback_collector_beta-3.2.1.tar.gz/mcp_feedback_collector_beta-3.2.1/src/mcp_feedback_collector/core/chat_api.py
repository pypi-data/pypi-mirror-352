"""
AI聊天API模块
封装AI API调用逻辑，支持流式和非流式响应
"""

import json
import requests
import threading
from typing import List, Dict, Callable, Optional
from .config import config
from .image_processor import ImageProcessor


class ChatAPI:
    """AI聊天API接口封装"""
    
    def __init__(self):
        """初始化API客户端"""
        self.base_url = config.api_base_url
        self.api_key = config.api_key
        self.model = config.default_model
        self.session = requests.Session()
    
    def send_message_sync(self, messages: List[Dict]) -> str:
        """同步发送消息（非流式）"""
        try:
            headers = config.get_api_headers()
            payload = config.get_api_payload(messages, stream=False)
            url = f"{self.base_url}/v1/chat/completions"
            
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
        except KeyError as e:
            raise Exception(f"API响应格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"发送消息失败: {str(e)}")
    
    def send_message_stream(self, messages: List[Dict], 
                          on_message: Callable[[str], None],
                          on_error: Callable[[str], None],
                          on_complete: Callable[[], None] = None):
        """流式发送消息（异步）"""
        def _send():
            try:
                headers = config.get_api_headers()
                payload = config.get_api_payload(messages, stream=True)
                url = f"{self.base_url}/v1/chat/completions"
                
                response = self.session.post(url, headers=headers, json=payload, 
                                           stream=True, timeout=30)
                response.raise_for_status()
                
                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            data_text = line_text[6:]  # 移除 'data: ' 前缀
                            
                            if data_text.strip() == '[DONE]':
                                if on_complete:
                                    on_complete()
                                break
                            
                            try:
                                data = json.loads(data_text)
                                if 'choices' in data and len(data['choices']) > 0:
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        on_message(delta['content'])
                            except json.JSONDecodeError:
                                continue  # 忽略无效的JSON行
                
            except requests.exceptions.RequestException as e:
                on_error(f"API请求失败: {str(e)}")
            except Exception as e:
                on_error(f"发送消息失败: {str(e)}")
        
        # 在新线程中执行
        thread = threading.Thread(target=_send, daemon=True)
        thread.start()
        return thread
    
    def build_text_message(self, text: str, role: str = "user") -> Dict:
        """构建纯文本消息"""
        return {
            "role": role,
            "content": text
        }
    
    def build_multimodal_message(self, text: str, images: List[Dict], role: str = "user") -> Dict:
        """构建多模态消息（文字+图片）"""
        content = []
        
        # 添加文本内容
        if text.strip():
            content.append({
                "type": "text",
                "text": text
            })
        
        # 添加图片内容
        for img_info in images:
            try:
                base64_url = ImageProcessor.to_base64(img_info)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": base64_url
                    }
                })
            except Exception as e:
                # 如果某张图片处理失败，跳过但不影响其他图片
                print(f"处理图片失败: {e}")
                continue
        
        return {
            "role": role,
            "content": content
        }
    
    def validate_api_config(self) -> tuple[bool, str]:
        """验证API配置"""
        if not config.enable_chat:
            return False, "AI聊天功能已禁用"
        
        if not config.has_api_key:
            return False, "请配置API密钥"
        
        if not self.base_url:
            return False, "请配置API端点"
        
        return True, "配置验证通过"
    
    def test_connection(self) -> tuple[bool, str]:
        """测试API连接"""
        try:
            is_valid, message = self.validate_api_config()
            if not is_valid:
                return False, message
            
            # 发送测试消息
            test_messages = [self.build_text_message("Hello")]
            response = self.send_message_sync(test_messages)
            
            if response:
                return True, "API连接正常"
            else:
                return False, "API返回空响应"
                
        except Exception as e:
            return False, f"API连接测试失败: {str(e)}"
    
    def get_api_info(self) -> Dict:
        """获取API配置信息"""
        return {
            "base_url": self.base_url,
            "model": self.model,
            "has_api_key": bool(self.api_key),
            "chat_enabled": config.enable_chat
        }
