"""
MCP工具函数模块
定义所有MCP工具函数的核心逻辑，与界面无关
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from .config import config
from .image_processor import ImageProcessor
from .chat_api import ChatAPI
from .feedback_handler import FeedbackHandler


class MCPTools:
    """MCP工具函数的核心实现"""
    
    @staticmethod
    def collect_feedback_core(work_summary: str = "", 
                            timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
        """
        反馈收集的核心逻辑
        返回需要传递给界面的数据
        """
        if timeout_seconds is None:
            timeout_seconds = config.dialog_timeout
        
        return {
            "work_summary": work_summary or FeedbackHandler.create_sample_work_summary(),
            "timeout_seconds": timeout_seconds,
            "interface_mode": config.interface_mode,
            "config": {
                "max_images": 5,
                "allowed_formats": list(config.allowed_extensions),
                "max_file_size": config.max_file_size
            }
        }
    
    @staticmethod
    def open_chat_interface_core() -> Dict[str, Any]:
        """
        聊天界面的核心逻辑
        返回需要传递给界面的数据
        """
        # 验证配置
        if not config.enable_chat:
            return {
                "success": False,
                "message": "AI聊天功能已禁用。请在环境变量中设置 MCP_ENABLE_CHAT=true 启用。"
            }
        
        if not config.has_api_key:
            return {
                "success": False,
                "message": "请在环境变量中设置 MCP_API_KEY 以使用AI聊天功能。",
                "need_api_key": True
            }
        
        return {
            "success": True,
            "interface_mode": config.interface_mode,
            "api_info": {
                "base_url": config.api_base_url,
                "model": config.default_model,
                "has_api_key": config.has_api_key
            },
            "config": {
                "max_images": 5,
                "allowed_formats": list(config.allowed_extensions),
                "max_file_size": config.max_file_size
            }
        }
    
    @staticmethod
    def pick_image_core() -> Dict[str, Any]:
        """
        图片选择的核心逻辑
        返回需要传递给界面的数据
        """
        return {
            "interface_mode": config.interface_mode,
            "config": {
                "allowed_formats": list(config.allowed_extensions),
                "max_file_size": config.max_file_size
            }
        }
    
    @staticmethod
    def get_image_info_core(image_path: str) -> Dict[str, Any]:
        """
        获取图片信息的核心逻辑
        """
        try:
            path = Path(image_path)
            if not path.exists():
                return {
                    "success": False,
                    "message": f"文件不存在: {image_path}"
                }
            
            # 加载图片
            img_info = ImageProcessor.load_from_file(path)
            
            # 获取详细信息
            info = ImageProcessor.get_image_info(img_info)
            
            return {
                "success": True,
                "image_info": info,
                "file_path": str(path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"获取图片信息失败: {str(e)}"
            }
    
    @staticmethod
    def process_feedback_submission(text_content: str, 
                                  images: List[Dict]) -> Dict[str, Any]:
        """
        处理反馈提交的核心逻辑
        """
        try:
            # 验证反馈内容
            is_valid, message = FeedbackHandler.validate_feedback(text_content, images)
            if not is_valid:
                return FeedbackHandler.create_feedback_result(
                    success=False, 
                    message=message
                )
            
            # 创建反馈结果
            result = FeedbackHandler.create_feedback_result(
                text_content=text_content,
                images=images,
                success=True
            )
            
            return result
            
        except Exception as e:
            return FeedbackHandler.create_feedback_result(
                success=False,
                message=f"处理反馈时发生错误: {str(e)}"
            )
    
    @staticmethod
    def process_chat_message(text: str, 
                           images: List[Dict],
                           message_history: List[Dict]) -> Dict[str, Any]:
        """
        处理聊天消息的核心逻辑
        """
        try:
            # 验证API配置
            chat_api = ChatAPI()
            is_valid, message = chat_api.validate_api_config()
            if not is_valid:
                return {
                    "success": False,
                    "message": message
                }
            
            # 构建消息
            if images:
                user_message = chat_api.build_multimodal_message(text, images)
            else:
                user_message = chat_api.build_text_message(text)
            
            # 添加到历史记录
            messages = message_history + [user_message]
            
            return {
                "success": True,
                "user_message": user_message,
                "messages": messages,
                "api_ready": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"处理聊天消息失败: {str(e)}"
            }
    
    @staticmethod
    def load_images_from_paths(file_paths: List[str]) -> List[Dict]:
        """
        从文件路径列表加载图片
        """
        images = []
        errors = []
        
        for file_path in file_paths:
            try:
                img_info = ImageProcessor.load_from_file(file_path)
                images.append(img_info)
            except Exception as e:
                errors.append(f"{Path(file_path).name}: {str(e)}")
        
        return images, errors
    
    @staticmethod
    def load_image_from_clipboard() -> Optional[Dict]:
        """
        从剪贴板加载图片
        """
        try:
            return ImageProcessor.load_from_clipboard()
        except Exception as e:
            raise Exception(str(e))
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        获取系统信息
        """
        # 显示API密钥的前10位和后4位，中间用*遮盖
        api_key_display = ""
        if config.has_api_key and config.api_key:
            if len(config.api_key) > 14:
                api_key_display = config.api_key[:10] + "..." + config.api_key[-4:]
            else:
                api_key_display = config.api_key[:6] + "..."

        return {
            "version": "3.2.0",
            "interface_mode": config.interface_mode,
            "gui_available": config.is_gui_mode,
            "web_available": config.is_web_mode,
            "chat_enabled": config.enable_chat,
            "has_api_key": config.has_api_key,
            "api_base_url": config.api_base_url,
            "api_key_display": api_key_display,
            "default_model": config.default_model,
            "web_config": {
                "host": config.web_host,
                "port": config.web_port,
                "debug": config.web_debug
            } if config.is_web_mode else None
        }
