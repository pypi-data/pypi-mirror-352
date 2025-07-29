"""
MCP Feedback Collector v3.2.0 - 双重架构版本
支持GUI和Web两种界面模式的统一服务器入口
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image as MCPImage

# 导入核心模块
try:
    # 尝试相对导入（作为包使用时）
    from .core import config, MCPTools, ImageProcessor
    from .core.config import config as global_config
except ImportError:
    # 直接运行时使用绝对导入
    import sys
    from pathlib import Path

    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.mcp_feedback_collector.core import config, MCPTools, ImageProcessor
    from src.mcp_feedback_collector.core.config import config as global_config

# 创建MCP服务器
mcp = FastMCP(
    "MCP Feedback Collector v3.2.0",
    dependencies=["pillow", "PyQt6", "requests", "flask", "flask-socketio"]
)


@mcp.tool()
def collect_feedback(work_summary: str = "", timeout_seconds: int = None) -> List[Dict[str, Any]]:
    """
    收集用户反馈的交互式工具。AI可以汇报完成的工作，用户可以提供文字和/或图片反馈。
    
    Args:
        work_summary: AI完成的工作内容汇报
        timeout_seconds: 对话框超时时间（秒），默认使用配置值
    
    Returns:
        包含用户反馈内容的列表，可能包含文本和图片
    """
    if timeout_seconds is None:
        timeout_seconds = global_config.dialog_timeout
    
    # 根据配置选择界面模式
    if global_config.is_gui_mode and not global_config.is_web_mode:
        # 仅GUI模式
        return _show_gui_feedback(work_summary, timeout_seconds)
    elif global_config.is_web_mode and not global_config.is_gui_mode:
        # 仅Web模式
        return _show_web_feedback(work_summary, timeout_seconds)
    else:
        # 双模式或默认，优先尝试GUI
        try:
            return _show_gui_feedback(work_summary, timeout_seconds)
        except Exception as e:
            print(f"GUI模式失败，尝试Web模式: {e}")
            return _show_web_feedback(work_summary, timeout_seconds)


@mcp.tool()
def open_chat_interface() -> str:
    """
    打开AI聊天界面，提供与AI助手的交互式对话功能。
    支持文字聊天和流式响应，需要配置API密钥。
    
    Returns:
        操作结果信息
    """
    # 验证配置
    chat_data = MCPTools.open_chat_interface_core()
    if not chat_data["success"]:
        return chat_data["message"]
    
    # 根据配置选择界面模式
    if global_config.is_gui_mode and not global_config.is_web_mode:
        # 仅GUI模式
        return _show_gui_chat()
    elif global_config.is_web_mode and not global_config.is_gui_mode:
        # 仅Web模式
        return _show_web_chat()
    else:
        # 双模式或默认，优先尝试GUI
        try:
            return _show_gui_chat()
        except Exception as e:
            print(f"GUI模式失败，尝试Web模式: {e}")
            return _show_web_chat()


@mcp.tool()
def pick_image() -> MCPImage:
    """
    弹出图片选择对话框，让用户选择图片文件或从剪贴板粘贴图片。
    用户可以选择本地图片文件，或者先截图到剪贴板然后粘贴。
    """
    # 优先尝试GUI模式
    if global_config.is_gui_mode:
        try:
            return _show_gui_image_picker()
        except Exception as e:
            if not global_config.is_web_mode:
                raise Exception(f"图片选择失败: {str(e)}")
    
    # Web模式或GUI失败时的处理
    if global_config.is_web_mode:
        return _show_web_image_picker()
    else:
        raise Exception("没有可用的界面模式来选择图片")


@mcp.tool()
def get_image_info(image_path: str) -> str:
    """
    获取指定路径图片的信息（尺寸、格式等）
    
    Args:
        image_path: 图片文件路径
    """
    result = MCPTools.get_image_info_core(image_path)
    
    if result["success"]:
        info = result["image_info"]
        return "\n".join([f"{k}: {v}" for k, v in info.items()])
    else:
        return result["message"]


def _show_gui_feedback(work_summary: str, timeout_seconds: int) -> List[Dict[str, Any]]:
    """显示GUI反馈界面"""
    try:
        try:
            from .gui import GUIInterface
        except ImportError:
            from src.mcp_feedback_collector.gui import GUIInterface
        
        gui = GUIInterface()
        if not gui.is_available():
            raise Exception("PyQt6不可用")
        
        result = gui.show_feedback_dialog(work_summary, timeout_seconds)
        
        if result and result.get("success", False):
            return [result]
        else:
            return [{"success": False, "message": result.get("message", "用户取消了操作")}]
            
    except ImportError as e:
        raise Exception(f"GUI模块导入失败: {str(e)}")
    except Exception as e:
        raise Exception(f"GUI反馈界面失败: {str(e)}")


def _show_web_feedback(work_summary: str, timeout_seconds: int) -> List[Dict[str, Any]]:
    """显示Web反馈界面"""
    try:
        try:
            from .web import WebInterface
        except ImportError:
            from src.mcp_feedback_collector.web import WebInterface
        
        web = WebInterface()
        
        # 启动Web服务器（如果还没启动）
        if not hasattr(web, 'server_thread') or not web.server_thread or not web.server_thread.is_alive():
            web.run_in_thread()
        
        # 构建访问URL
        url = f"http://{global_config.web_host}:{global_config.web_port}/feedback"
        if work_summary:
            import urllib.parse
            url += f"?work_summary={urllib.parse.quote(work_summary)}"
        
        return [{
            "success": True,
            "message": f"Web反馈界面已启动",
            "url": url,
            "instructions": "请在浏览器中访问上述URL来提交反馈"
        }]
        
    except ImportError as e:
        raise Exception(f"Web模块导入失败: {str(e)}")
    except Exception as e:
        raise Exception(f"Web反馈界面失败: {str(e)}")


def _show_gui_chat() -> str:
    """显示GUI聊天界面"""
    try:
        try:
            from .gui import GUIInterface
        except ImportError:
            from src.mcp_feedback_collector.gui import GUIInterface
        
        gui = GUIInterface()
        if not gui.is_available():
            raise Exception("PyQt6不可用")
        
        return gui.show_main_window(initial_page=1)
        
    except ImportError as e:
        raise Exception(f"GUI模块导入失败: {str(e)}")
    except Exception as e:
        raise Exception(f"GUI聊天界面失败: {str(e)}")


def _show_web_chat() -> str:
    """显示Web聊天界面"""
    try:
        try:
            from .web import WebInterface
        except ImportError:
            from src.mcp_feedback_collector.web import WebInterface
        
        web = WebInterface()
        
        # 启动Web服务器（如果还没启动）
        if not hasattr(web, 'server_thread') or not web.server_thread or not web.server_thread.is_alive():
            web.run_in_thread()
        
        url = f"http://{global_config.web_host}:{global_config.web_port}/chat"
        
        return f"Web聊天界面已启动，请访问: {url}"
        
    except ImportError as e:
        raise Exception(f"Web模块导入失败: {str(e)}")
    except Exception as e:
        raise Exception(f"Web聊天界面失败: {str(e)}")


def _show_gui_image_picker() -> MCPImage:
    """显示GUI图片选择器"""
    try:
        try:
            from .gui import GUIInterface
        except ImportError:
            from src.mcp_feedback_collector.gui import GUIInterface
        
        gui = GUIInterface()
        if not gui.is_available():
            raise Exception("PyQt6不可用")
        
        image_data = gui.show_image_picker()
        if image_data:
            return MCPImage(data=image_data, format='png')
        else:
            raise Exception("未选择图片或操作被取消")
            
    except ImportError as e:
        raise Exception(f"GUI模块导入失败: {str(e)}")
    except Exception as e:
        raise Exception(f"GUI图片选择失败: {str(e)}")


def _show_web_image_picker() -> MCPImage:
    """Web模式图片选择（返回说明信息）"""
    url = f"http://{global_config.web_host}:{global_config.web_port}/"
    raise Exception(f"请在Web界面中选择图片: {url}")


def main():
    """主入口函数"""
    # 打印启动信息（避免emoji在Windows控制台的编码问题）
    try:
        print("🎯 MCP Feedback Collector v3.2.0")
        print(f"📋 界面模式: {global_config.interface_mode}")
        print(f"🖥️  GUI支持: {'✅' if global_config.is_gui_mode else '❌'}")
        print(f"🌐 Web支持: {'✅' if global_config.is_web_mode else '❌'}")

        if global_config.is_web_mode:
            print(f"🌐 Web服务: http://{global_config.web_host}:{global_config.web_port}")
    except UnicodeEncodeError:
        # Windows控制台编码问题的备用方案
        print("MCP Feedback Collector v3.2.0")
        print(f"界面模式: {global_config.interface_mode}")
        print(f"GUI支持: {'是' if global_config.is_gui_mode else '否'}")
        print(f"Web支持: {'是' if global_config.is_web_mode else '否'}")

        if global_config.is_web_mode:
            print(f"Web服务: http://{global_config.web_host}:{global_config.web_port}")

    # 启动MCP服务器
    mcp.run()


if __name__ == "__main__":
    main()
