"""
GUI主窗口模块
包含主窗口和各个页面组件
"""

import sys
from typing import Optional, Dict, List, Any
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QStackedWidget, QPushButton, QLabel,
                            QTextEdit, QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon

from ..core import config, MCPTools, ChatAPI, FeedbackHandler


class MainWindow(QMainWindow):
    """Cherry Studio风格的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.chat_api = ChatAPI()
        self.message_history = []
        self.current_ai_message = None
        
        # 确保QApplication存在
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化Cherry Studio风格界面"""
        self.setWindowTitle("🎯 MCP Feedback Collector v3.2.0")
        self.setFixedSize(1200, 800)
        
        # 居中显示
        self.center_window()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 左侧导航栏
        self.navigation = NavigationPanel()
        self.navigation.page_changed.connect(self.switch_page)
        main_layout.addWidget(self.navigation)
        
        # 右侧内容区域
        self.content_stack = QStackedWidget()
        
        # 创建页面
        self.feedback_page = FeedbackPage()
        self.chat_page = ChatPage()
        
        self.content_stack.addWidget(self.feedback_page)
        self.content_stack.addWidget(self.chat_page)
        
        main_layout.addWidget(self.content_stack)
        
        # 设置Cherry Studio风格样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
        """)
    
    def center_window(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def switch_page(self, page_index):
        """切换页面"""
        self.content_stack.setCurrentIndex(page_index)
        
        # 如果切换到聊天页面，检查API配置
        if page_index == 1:  # 聊天页面
            chat_data = MCPTools.open_chat_interface_core()
            if not chat_data["success"]:
                QMessageBox.warning(self, "配置错误", chat_data["message"])
                # 切换回反馈页面
                self.navigation.select_page(0)
                return
            
            # 初始化聊天页面
            self.chat_page.initialize_chat()


class NavigationPanel(QWidget):
    """左侧导航栏"""
    
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_page = 0
        self.init_ui()
    
    def init_ui(self):
        """初始化导航栏"""
        self.setFixedWidth(80)
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border-right: 1px solid #404040;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # Logo区域
        logo_label = QLabel("🎯")
        logo_label.setFixedSize(60, 60)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                background-color: #0078d4;
                border-radius: 12px;
                font-size: 24px;
                font-weight: bold;
                color: white;
            }
        """)
        layout.addWidget(logo_label)
        
        layout.addSpacing(15)
        
        # 导航按钮
        self.feedback_btn = self.create_nav_button("💬", "AI汇报反馈收集")
        self.chat_btn = self.create_nav_button("🤖", "AI智能聊天")
        
        self.nav_buttons = [self.feedback_btn, self.chat_btn]
        
        layout.addWidget(self.feedback_btn)
        layout.addWidget(self.chat_btn)
        
        layout.addStretch()
        
        # 默认选中第一个
        self.select_page(0)
    
    def create_nav_button(self, icon, tooltip):
        """创建导航按钮"""
        btn = QPushButton(icon)
        btn.setFixedSize(60, 60)
        btn.setToolTip(tooltip)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: #cccccc;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #404040;
                color: #ffffff;
            }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
    
    def select_page(self, page_index):
        """选择页面"""
        if 0 <= page_index < len(self.nav_buttons):
            # 重置所有按钮样式
            for btn in self.nav_buttons:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        border-radius: 12px;
                        color: #cccccc;
                        font-size: 20px;
                    }
                    QPushButton:hover {
                        background-color: #404040;
                        color: #ffffff;
                    }
                """)
            
            # 设置选中按钮样式
            selected_btn = self.nav_buttons[page_index]
            selected_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    border: none;
                    border-radius: 12px;
                    color: #ffffff;
                    font-size: 20px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                    color: #ffffff;
                }
            """)
            
            self.current_page = page_index
            
            # 连接点击事件
            for i, btn in enumerate(self.nav_buttons):
                try:
                    btn.clicked.disconnect()  # 断开之前的连接
                except TypeError:
                    pass  # 如果没有连接，忽略错误
                btn.clicked.connect(lambda checked, idx=i: self.on_button_clicked(idx))
            
            self.page_changed.emit(page_index)
    
    def on_button_clicked(self, page_index):
        """按钮点击事件"""
        if page_index != self.current_page:
            self.select_page(page_index)


class FeedbackPage(QWidget):
    """反馈收集页面"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化反馈页面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 页面标题
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333333;
                padding: 4px;
            }
        """)
        header.setFixedHeight(80)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel("💬 AI工作汇报与反馈收集")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        
        subtitle = QLabel("查看AI工作汇报，提供您的宝贵反馈")
        subtitle.setFont(QFont("Microsoft YaHei", 12))
        subtitle.setStyleSheet("color: #cccccc;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # 内容区域
        content_label = QLabel("反馈收集功能")
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 16px;
                padding: 40px;
            }
        """)
        
        layout.addWidget(content_label)


class ChatPage(QWidget):
    """AI聊天页面"""
    
    def __init__(self):
        super().__init__()
        self.chat_api = ChatAPI()
        self.message_history = []
        self.init_ui()
    
    def init_ui(self):
        """初始化聊天页面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 页面标题
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333333;
                padding: 4px;
            }
        """)
        header.setFixedHeight(80)
        
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        title = QLabel("🤖 AI智能聊天")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff;")
        
        subtitle = QLabel("与AI进行多模态智能对话")
        subtitle.setFont(QFont("Microsoft YaHei", 12))
        subtitle.setStyleSheet("color: #cccccc;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # 聊天区域
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch()
        
        self.chat_area.setWidget(self.chat_content)
        layout.addWidget(self.chat_area)
        
        # 输入区域
        input_area = QFrame()
        input_area.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-top: 1px solid #333333;
                padding: 4px;
            }
        """)
        input_area.setFixedHeight(120)
        
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(20, 20, 20, 20)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.setFixedHeight(80)
        self.message_input.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 12px;
                color: #e0e0e0;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
        
        send_btn = QPushButton("🚀")
        send_btn.setFixedSize(80, 80)
        send_btn.setToolTip("发送消息")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_area)
    
    def initialize_chat(self):
        """初始化聊天"""
        # 清空聊天记录
        for i in reversed(range(self.chat_layout.count())):
            child = self.chat_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加欢迎消息
        welcome_msg = QLabel("🎯 欢迎使用AI智能聊天！\n支持文字对话，实时流式响应。")
        welcome_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_msg.setStyleSheet("""
            QLabel {
                background-color: #252525;
                color: #cccccc;
                padding: 20px;
                border-radius: 8px;
                font-style: italic;
                margin: 20px 0;
            }
        """)
        
        self.chat_layout.insertWidget(0, welcome_msg)
        self.chat_layout.addStretch()
    
    def send_message(self):
        """发送消息"""
        text = self.message_input.toPlainText().strip()
        if not text:
            return
        
        # 验证API配置
        is_valid, message = self.chat_api.validate_api_config()
        if not is_valid:
            QMessageBox.warning(self, "配置错误", message)
            return
        
        # 清空输入框
        self.message_input.clear()
        
        # 添加用户消息
        self.add_message(text, "user")
        
        # 发送到AI
        try:
            user_message = self.chat_api.build_text_message(text)
            self.message_history.append(user_message)
            
            # 添加AI回复占位符
            ai_placeholder = self.add_typing_indicator()
            
            # 发送流式请求
            def on_message(content):
                self.update_ai_message(ai_placeholder, content)
            
            def on_error(error_msg):
                self.show_error_message(error_msg)
                ai_placeholder.setParent(None)
            
            def on_complete():
                self.complete_ai_message(ai_placeholder)
            
            self.chat_api.send_message_stream(
                self.message_history,
                on_message,
                on_error,
                on_complete
            )
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发送消息失败: {str(e)}")
    
    def add_message(self, text, sender):
        """添加消息到聊天区域"""
        message_frame = QFrame()
        message_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {'#0078d4' if sender == 'user' else '#2a2a2a'};
                border-radius: 12px;
                padding: 4px;
                margin: 4px 0;
                max-width: 80%;
            }}
        """)
        
        if sender == "user":
            message_frame.setStyleSheet(message_frame.styleSheet() + """
                QFrame {
                    margin-left: 20%;
                }
            """)
        else:
            message_frame.setStyleSheet(message_frame.styleSheet() + """
                QFrame {
                    margin-right: 20%;
                }
            """)
        
        layout = QVBoxLayout(message_frame)
        layout.setContentsMargins(12, 8, 12, 8)
        
        content_label = QLabel(text)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"""
            QLabel {{
                color: {'white' if sender == 'user' else '#e0e0e0'};
                font-size: 14px;
                line-height: 1.4;
                border: none;
            }}
        """)
        
        layout.addWidget(content_label)
        
        # 插入到倒数第二个位置（最后一个是stretch）
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_frame)
        
        # 滚动到底部
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def add_typing_indicator(self):
        """添加打字指示器"""
        indicator = QLabel("AI正在回复...")
        indicator.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                color: #888888;
                padding: 12px;
                border-radius: 12px;
                font-style: italic;
                margin: 4px 0;
                margin-right: 20%;
            }
        """)
        
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, indicator)
        self.scroll_to_bottom()
        
        return indicator
    
    def update_ai_message(self, placeholder, content):
        """更新AI消息"""
        if hasattr(placeholder, '_content'):
            placeholder._content += content
        else:
            placeholder._content = content
            placeholder.setText("")
            placeholder.setStyleSheet("""
                QLabel {
                    background-color: #2a2a2a;
                    color: #e0e0e0;
                    padding: 12px;
                    border-radius: 12px;
                    margin: 4px 0;
                    margin-right: 20%;
                    font-size: 14px;
                    line-height: 1.4;
                }
            """)
        
        placeholder.setText(placeholder._content)
        placeholder.setWordWrap(True)
        self.scroll_to_bottom()
    
    def complete_ai_message(self, placeholder):
        """完成AI消息"""
        if hasattr(placeholder, '_content'):
            # 添加到历史记录
            ai_message = self.chat_api.build_text_message(placeholder._content, "assistant")
            self.message_history.append(ai_message)
    
    def show_error_message(self, error_msg):
        """显示错误消息"""
        error_label = QLabel(f"❌ {error_msg}")
        error_label.setStyleSheet("""
            QLabel {
                background-color: #d13438;
                color: white;
                padding: 12px;
                border-radius: 8px;
                margin: 4px 0;
                text-align: center;
            }
        """)
        
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_label)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
