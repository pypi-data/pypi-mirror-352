"""
反馈处理模块
处理用户反馈的收集、验证和格式化
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from .image_processor import ImageProcessor


class FeedbackHandler:
    """反馈处理器"""
    
    @staticmethod
    def create_feedback_result(text_content: str = "", 
                             images: List[Dict] = None,
                             success: bool = True,
                             message: str = "") -> Dict[str, Any]:
        """创建反馈结果"""
        images = images or []
        
        # 验证图片
        if images:
            is_valid, validation_message = ImageProcessor.validate_images(images)
            if not is_valid:
                return {
                    "success": False,
                    "message": f"图片验证失败: {validation_message}",
                    "timestamp": datetime.now().isoformat()
                }
        
        # 构建结果
        result = {
            "success": success,
            "message": message or ("反馈提交成功" if success else "反馈提交失败"),
            "timestamp": datetime.now().isoformat(),
            "feedback": {
                "text": text_content.strip(),
                "has_text": bool(text_content.strip()),
                "image_count": len(images),
                "has_images": len(images) > 0
            }
        }
        
        # 添加图片信息
        if images:
            result["feedback"]["images"] = []
            for i, img_info in enumerate(images):
                try:
                    # 获取图片基本信息
                    img_data = {
                        "index": i,
                        "source": img_info.get('source', '未知'),
                        "filename": img_info.get('filename', f'image_{i}.png'),
                        "size": img_info.get('size', [0, 0]),
                        "format": img_info.get('format', '未知'),
                        "data_size": len(img_info.get('data', b'')),
                        "base64": ImageProcessor.to_base64(img_info)
                    }
                    result["feedback"]["images"].append(img_data)
                except Exception as e:
                    # 如果某张图片处理失败，记录错误但继续处理其他图片
                    result["feedback"]["images"].append({
                        "index": i,
                        "error": str(e),
                        "source": img_info.get('source', '未知')
                    })
        
        return result
    
    @staticmethod
    def validate_feedback(text_content: str, images: List[Dict]) -> tuple[bool, str]:
        """验证反馈内容"""
        # 检查是否有任何内容
        has_text = bool(text_content.strip())
        has_images = len(images) > 0
        
        if not has_text and not has_images:
            return False, "请提供文字反馈或图片反馈"
        
        # 验证图片
        if has_images:
            is_valid, message = ImageProcessor.validate_images(images)
            if not is_valid:
                return False, message
        
        # 验证文本长度
        if has_text and len(text_content.strip()) > 10000:  # 10K字符限制
            return False, "文字反馈过长，请控制在10000字符以内"
        
        return True, "验证通过"
    
    @staticmethod
    def format_feedback_summary(feedback_result: Dict) -> str:
        """格式化反馈摘要"""
        if not feedback_result.get("success", False):
            return f"❌ {feedback_result.get('message', '反馈失败')}"
        
        feedback = feedback_result.get("feedback", {})
        summary_parts = []
        
        # 文字反馈摘要
        if feedback.get("has_text", False):
            text = feedback.get("text", "")
            if len(text) > 100:
                text_summary = text[:100] + "..."
            else:
                text_summary = text
            summary_parts.append(f"📝 文字反馈: {text_summary}")
        
        # 图片反馈摘要
        if feedback.get("has_images", False):
            image_count = feedback.get("image_count", 0)
            summary_parts.append(f"🖼️ 图片反馈: {image_count}张图片")
        
        if not summary_parts:
            summary_parts.append("📝 空反馈")
        
        timestamp = feedback_result.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%H:%M:%S")
                summary_parts.append(f"⏰ {time_str}")
            except:
                pass
        
        return " | ".join(summary_parts)
    
    @staticmethod
    def create_sample_work_summary() -> str:
        """创建示例工作汇报"""
        return """✅ MCP Feedback Collector v3.2.0 升级完成

🔧 核心架构重构:
  • 抽离核心业务逻辑为独立模块
  • 实现GUI和Web双重界面支持
  • 统一配置管理和API接口

🌐 新增Web界面:
  • Flask Web服务器支持远程访问
  • 完整复刻Cherry Studio设计风格
  • 支持所有现有功能（图片上传、AI聊天等）

🎯 保持向后兼容:
  • 所有MCP工具函数接口不变
  • 现有GUI界面完全保留
  • 配置文件格式兼容

📱 技术特性:
  • 响应式Web设计，支持移动端
  • WebSocket实时通信
  • 多模态图片处理
  • 安全认证机制"""
    
    @staticmethod
    def extract_feedback_data(feedback_result: Dict) -> tuple[str, List[str]]:
        """提取反馈数据用于进一步处理"""
        if not feedback_result.get("success", False):
            return "", []
        
        feedback = feedback_result.get("feedback", {})
        
        # 提取文字内容
        text_content = feedback.get("text", "")
        
        # 提取图片Base64数据
        image_data = []
        for img in feedback.get("images", []):
            if "base64" in img:
                image_data.append(img["base64"])
        
        return text_content, image_data
    
    @staticmethod
    def merge_feedback_results(results: List[Dict]) -> Dict:
        """合并多个反馈结果"""
        if not results:
            return FeedbackHandler.create_feedback_result(success=False, message="没有反馈数据")
        
        # 统计成功和失败的数量
        success_count = sum(1 for r in results if r.get("success", False))
        total_count = len(results)
        
        # 合并所有文字内容
        all_text = []
        all_images = []
        
        for result in results:
            if result.get("success", False):
                feedback = result.get("feedback", {})
                if feedback.get("text"):
                    all_text.append(feedback["text"])
                if feedback.get("images"):
                    all_images.extend(feedback["images"])
        
        # 创建合并结果
        merged_text = "\n\n".join(all_text)
        success = success_count > 0
        
        if success_count == total_count:
            message = f"所有{total_count}个反馈都提交成功"
        elif success_count > 0:
            message = f"{success_count}/{total_count}个反馈提交成功"
        else:
            message = f"所有{total_count}个反馈都提交失败"
        
        return {
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "feedback": {
                "text": merged_text,
                "has_text": bool(merged_text),
                "image_count": len(all_images),
                "has_images": len(all_images) > 0,
                "images": all_images
            },
            "statistics": {
                "total_count": total_count,
                "success_count": success_count,
                "failure_count": total_count - success_count
            }
        }
