"""
GUI界面管理器
管理PyQt6界面的创建和显示
"""

import sys
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QApplication

from ..core import config, MCPTools


class GUIInterface:
    """GUI界面管理器"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
    
    def ensure_application(self) -> QApplication:
        """确保QApplication存在"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        return self.app
    
    def show_feedback_dialog(self, work_summary: str = "",
                           timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
        """显示反馈收集对话框"""
        try:
            # 延迟导入避免循环依赖
            from .dialogs import FeedbackDialog

            self.ensure_application()

            # 获取核心数据
            core_data = MCPTools.collect_feedback_core(work_summary, timeout_seconds)

            # 创建并显示对话框
            dialog = FeedbackDialog(
                work_summary=core_data["work_summary"],
                timeout_seconds=core_data["timeout_seconds"]
            )

            return dialog.show_dialog()

        except ImportError as e:
            return {"success": False, "message": f"GUI模块导入失败: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"显示反馈对话框失败: {str(e)}"}
    
    def show_main_window(self, initial_page: int = 0) -> str:
        """显示主窗口"""
        try:
            # 延迟导入避免循环依赖
            from .windows import MainWindow

            self.ensure_application()

            # 创建主窗口
            self.main_window = MainWindow()

            # 切换到指定页面
            if initial_page == 1:  # 聊天页面
                chat_data = MCPTools.open_chat_interface_core()
                if not chat_data["success"]:
                    return chat_data["message"]
                self.main_window.navigation.select_page(1)
            else:  # 反馈页面
                self.main_window.navigation.select_page(0)

            # 显示窗口
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()

            # 强制刷新界面
            self.app.processEvents()

            try:
                # 运行事件循环
                self.app.exec()
                return "GUI界面已关闭"
            except Exception as e:
                return f"GUI界面运行出错: {str(e)}"

        except ImportError as e:
            return f"GUI模块导入失败: {str(e)}"
        except Exception as e:
            return f"显示主窗口失败: {str(e)}"
    
    def show_image_picker(self) -> Optional[bytes]:
        """显示图片选择对话框"""
        try:
            # 延迟导入避免循环依赖
            from .dialogs import ImagePickerDialog

            self.ensure_application()

            dialog = ImagePickerDialog()
            result = dialog.exec()

            if result and dialog.selected_image:
                return dialog.selected_image
            else:
                return None

        except ImportError as e:
            raise Exception(f"GUI模块导入失败: {str(e)}")
        except Exception as e:
            raise Exception(f"显示图片选择对话框失败: {str(e)}")
    
    def is_available(self) -> bool:
        """检查GUI是否可用"""
        try:
            # 尝试导入PyQt6
            from PyQt6.QtWidgets import QApplication
            return True
        except ImportError:
            return False
