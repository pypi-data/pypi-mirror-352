"""
配置管理模块
统一管理所有配置项，支持环境变量和默认值
"""

import os
from typing import Optional


class Config:
    """配置管理类"""
    
    # 基础配置
    DEFAULT_DIALOG_TIMEOUT = 300  # 5分钟
    DEFAULT_API_BASE_URL = "https://api.ssopen.top"
    DEFAULT_MODEL = "gpt-4o-mini"
    
    # Web服务配置
    DEFAULT_WEB_PORT = 5000
    DEFAULT_WEB_HOST = "0.0.0.0"
    
    def __init__(self):
        """初始化配置"""
        self._load_config()
    
    def _load_config(self):
        """从环境变量加载配置"""
        # 基础配置
        self.dialog_timeout = int(os.getenv("MCP_DIALOG_TIMEOUT", self.DEFAULT_DIALOG_TIMEOUT))
        
        # AI聊天API配置
        self.api_base_url = os.getenv("MCP_API_BASE_URL", self.DEFAULT_API_BASE_URL)
        self.api_key = os.getenv("MCP_API_KEY", "")
        self.default_model = os.getenv("MCP_DEFAULT_MODEL", self.DEFAULT_MODEL)
        self.enable_chat = os.getenv("MCP_ENABLE_CHAT", "true").lower() == "true"
        
        # 界面模式配置
        self.interface_mode = os.getenv("MCP_INTERFACE_MODE", "gui").lower()  # gui, web, both
        
        # Web服务配置
        self.web_port = int(os.getenv("MCP_WEB_PORT", self.DEFAULT_WEB_PORT))
        self.web_host = os.getenv("MCP_WEB_HOST", self.DEFAULT_WEB_HOST)
        self.web_debug = os.getenv("MCP_WEB_DEBUG", "false").lower() == "true"
        
        # 安全配置
        self.web_secret_key = os.getenv("MCP_WEB_SECRET_KEY", "mcp-feedback-collector-secret")
        self.web_auth_token = os.getenv("MCP_WEB_AUTH_TOKEN", "")
        
        # 文件上传配置
        self.max_file_size = int(os.getenv("MCP_MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB
        self.allowed_extensions = set(os.getenv("MCP_ALLOWED_EXTENSIONS", 
                                               "png,jpg,jpeg,gif,bmp,webp").split(","))
    
    @property
    def is_gui_mode(self) -> bool:
        """是否启用GUI模式"""
        return self.interface_mode in ["gui", "both"]
    
    @property
    def is_web_mode(self) -> bool:
        """是否启用Web模式"""
        return self.interface_mode in ["web", "both"]
    
    @property
    def has_api_key(self) -> bool:
        """是否配置了API密钥"""
        return bool(self.api_key.strip())
    
    def get_api_headers(self) -> dict:
        """获取API请求头"""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    def get_api_payload(self, messages: list, stream: bool = True) -> dict:
        """获取API请求负载"""
        return {
            "model": self.default_model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.7,
            "max_tokens": 2000
        }
    
    def validate_file_upload(self, filename: str, file_size: int) -> tuple[bool, str]:
        """验证文件上传"""
        # 检查文件扩展名
        if '.' not in filename:
            return False, "文件没有扩展名"
        
        ext = filename.rsplit('.', 1)[1].lower()
        if ext not in self.allowed_extensions:
            return False, f"不支持的文件格式: {ext}"
        
        # 检查文件大小
        if file_size > self.max_file_size:
            return False, f"文件大小超过限制: {file_size / 1024 / 1024:.1f}MB > {self.max_file_size / 1024 / 1024:.1f}MB"
        
        return True, "验证通过"
    
    def __repr__(self) -> str:
        """配置信息字符串表示"""
        return f"""Config(
    interface_mode={self.interface_mode},
    api_base_url={self.api_base_url},
    has_api_key={self.has_api_key},
    enable_chat={self.enable_chat},
    web_port={self.web_port},
    dialog_timeout={self.dialog_timeout}
)"""


# 全局配置实例
config = Config()
