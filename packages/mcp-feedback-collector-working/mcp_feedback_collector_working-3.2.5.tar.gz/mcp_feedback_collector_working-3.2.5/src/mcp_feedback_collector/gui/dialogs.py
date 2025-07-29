"""
GUI对话框模块
包含反馈收集对话框和图片选择对话框
"""

import io
import sys
from typing import Optional, Dict, List, Any
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QScrollArea, QFrame, QLabel, QPushButton,
                            QFileDialog, QMessageBox, QWidget, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent

from ..core import config, MCPTools, ImageProcessor, FeedbackHandler


class FeedbackDialog(QDialog):
    """Cherry Studio风格的反馈收集对话框"""

    def __init__(self, work_summary: str = "", timeout_seconds: int = None):
        super().__init__()
        self.work_summary = work_summary
        self.timeout_seconds = timeout_seconds or config.dialog_timeout
        self.selected_images = []
        self.result = None

        # 确保QApplication存在
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        self.init_ui()
        self.setup_timeout()

    def init_ui(self):
        """初始化Cherry Studio风格界面"""
        self.setWindowTitle("🎯 AI工作汇报与反馈收集")
        self.setFixedSize(900, 700)
        self.setModal(True)

        # 居中显示
        self.center_window()

        # 主布局 - 垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 上部分：可滚动的汇报内容区域
        self.create_report_area(main_layout)

        # 下部分：悬浮固定的输入区域
        self.create_input_area(main_layout)

        # 设置Cherry Studio风格样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
        """)

        # 启用拖拽
        self.setAcceptDrops(True)

    def center_window(self):
        """窗口居中"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

    def setup_timeout(self):
        """设置超时机制"""
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self.handle_timeout)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.start(self.timeout_seconds * 1000)

    def handle_timeout(self):
        """处理超时"""
        self.result = None
        self.reject()

    def create_report_area(self, main_layout):
        """创建Cherry Studio风格的汇报内容区域"""
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1a1a1a;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
        """)

        # 滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(16)

        # AI汇报标题
        title_label = QLabel("🤖 AI工作汇报")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                padding: 12px 0;
                border-bottom: 2px solid #333333;
                margin-bottom: 8px;
            }
        """)
        scroll_layout.addWidget(title_label)

        # 汇报内容
        self.create_report_content(scroll_layout)

        # 添加弹性空间
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

    def create_report_content(self, layout):
        """创建汇报内容"""
        if self.work_summary:
            # 显示具体的工作汇报
            report_frame = QFrame()
            report_frame.setStyleSheet("""
                QFrame {
                    background-color: #252525;
                    border: 1px solid #333333;
                    border-radius: 8px;
                    padding: 4px;
                    margin: 4px 0;
                }
            """)

            report_layout = QVBoxLayout(report_frame)
            report_layout.setContentsMargins(16, 12, 16, 12)
            report_layout.setSpacing(8)

            # 标题
            title_label = QLabel("📋 工作内容")
            title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #4CAF50; margin-bottom: 4px;")
            report_layout.addWidget(title_label)

            # 内容
            content_label = QLabel(self.work_summary)
            content_label.setFont(QFont("Microsoft YaHei", 10))
            content_label.setStyleSheet("color: #cccccc; margin-left: 12px;")
            content_label.setWordWrap(True)
            report_layout.addWidget(content_label)

            layout.addWidget(report_frame)
        else:
            # 显示示例内容
            sample_summary = FeedbackHandler.create_sample_work_summary()
            content_label = QLabel(sample_summary)
            content_label.setFont(QFont("Microsoft YaHei", 10))
            content_label.setStyleSheet("color: #cccccc; margin-left: 12px;")
            content_label.setWordWrap(True)
            layout.addWidget(content_label)

    def create_input_area(self, main_layout):
        """创建Cherry Studio风格的悬浮固定输入区域"""
        # 输入区域容器
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-top: 1px solid #333333;
                padding: 4px;
            }
        """)

        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(20, 20, 20, 20)
        input_layout.setSpacing(16)

        # 反馈标题
        feedback_title = QLabel("💬 您的反馈（可选）")
        feedback_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        feedback_title.setStyleSheet("color: #ffffff; margin-bottom: 8px;")
        input_layout.addWidget(feedback_title)

        # 文字输入区域
        self.text_widget = QTextEdit()
        self.text_widget.setPlaceholderText("请输入您的反馈意见...")
        self.text_widget.setFixedHeight(120)
        self.text_widget.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 12px;
                color: #e0e0e0;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
        input_layout.addWidget(self.text_widget)

        # 图片区域
        self.create_image_area(input_layout)

        # 工具栏
        toolbar = self.create_toolbar()
        input_layout.addWidget(toolbar)

        main_layout.addWidget(input_container)

    def create_image_area(self, layout):
        """创建图片区域"""
        # 图片标题和计数
        image_header = QHBoxLayout()
        image_title = QLabel("🖼️ 图片反馈（可选）")
        image_title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        image_title.setStyleSheet("color: #ffffff;")

        self.image_count_label = QLabel("0/5")
        self.image_count_label.setStyleSheet("color: #0078d4; font-weight: bold;")

        image_header.addWidget(image_title)
        image_header.addStretch()
        image_header.addWidget(self.image_count_label)
        layout.addLayout(image_header)

        # 图片标签容器
        self.image_tags_container = QFrame()
        self.image_tags_container.setMinimumHeight(80)
        self.image_tags_container.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 2px dashed #404040;
                border-radius: 8px;
                margin: 8px 0;
            }
        """)

        self.image_tags_layout = QHBoxLayout(self.image_tags_container)
        self.image_tags_layout.setContentsMargins(10, 10, 10, 10)
        self.image_tags_layout.setSpacing(10)
        self.image_tags_layout.addStretch()

        layout.addWidget(self.image_tags_container)

    def create_toolbar(self):
        """创建Cherry Studio风格的工具栏"""
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: transparent;")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        # 图片操作按钮
        select_btn = self.create_tool_button("📁 选择文件", "选择图片文件")
        select_btn.clicked.connect(self.select_images)

        paste_btn = self.create_tool_button("📋 粘贴图片", "从剪贴板粘贴图片")
        paste_btn.clicked.connect(self.paste_image)

        # 主要操作按钮
        submit_btn = QPushButton("✅ 提交反馈")
        submit_btn.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        submit_btn.setFixedHeight(35)
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        submit_btn.clicked.connect(self.submit_feedback)

        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.setFont(QFont("Microsoft YaHei", 10))
        cancel_btn.setFixedHeight(35)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        # 布局
        toolbar_layout.addWidget(select_btn)
        toolbar_layout.addWidget(paste_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(submit_btn)
        toolbar_layout.addWidget(cancel_btn)

        return toolbar

    def create_tool_button(self, text, tooltip):
        """创建工具按钮"""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)
        btn.setFont(QFont("Microsoft YaHei", 9))
        btn.setFixedHeight(35)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        return btn

    def select_images(self):
        """选择图片文件"""
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self,
                "选择图片文件",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;所有文件 (*)"
            )

            if file_paths:
                images, errors = MCPTools.load_images_from_paths(file_paths)

                for img_info in images:
                    if len(self.selected_images) >= 5:
                        QMessageBox.warning(self, "提示", "最多只能选择5张图片")
                        break
                    self.add_image(img_info)

                if errors:
                    error_msg = "\n".join(errors)
                    QMessageBox.warning(self, "部分图片加载失败", error_msg)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"选择图片失败: {str(e)}")

    def paste_image(self):
        """从剪贴板粘贴图片"""
        try:
            if len(self.selected_images) >= 5:
                QMessageBox.warning(self, "提示", "最多只能选择5张图片")
                return

            img_info = MCPTools.load_image_from_clipboard()
            if img_info:
                self.add_image(img_info)
            else:
                QMessageBox.information(self, "提示", "剪贴板中没有图片数据")

        except Exception as e:
            QMessageBox.warning(self, "提示", str(e))

    def add_image(self, img_info):
        """添加图片到界面"""
        self.selected_images.append(img_info)
        self.update_image_display()

    def remove_image(self, index):
        """移除图片"""
        if 0 <= index < len(self.selected_images):
            self.selected_images.pop(index)
            self.update_image_display()

    def update_image_display(self):
        """更新图片显示"""
        # 清除现有的图片标签
        for i in reversed(range(self.image_tags_layout.count())):
            child = self.image_tags_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # 更新计数
        self.image_count_label.setText(f"{len(self.selected_images)}/5")

        # 添加新的图片标签
        for i, img_info in enumerate(self.selected_images):
            image_tag = self.create_image_tag(img_info, i)
            self.image_tags_layout.insertWidget(i, image_tag)

        # 添加弹性空间
        self.image_tags_layout.addStretch()

    def create_image_tag(self, img_info, index):
        """创建图片标签"""
        tag_frame = QFrame()
        tag_frame.setFixedSize(100, 80)
        tag_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 4px;
            }
            QFrame:hover {
                border-color: #0078d4;
            }
        """)

        tag_layout = QVBoxLayout(tag_frame)
        tag_layout.setContentsMargins(4, 4, 4, 4)
        tag_layout.setSpacing(2)

        # 图片预览
        try:
            thumbnail_data = ImageProcessor.create_thumbnail(img_info, (80, 60))
            pixmap = QPixmap()
            pixmap.loadFromData(thumbnail_data)

            image_label = QLabel()
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setStyleSheet("border: none; border-radius: 4px;")
            tag_layout.addWidget(image_label)
        except Exception:
            # 如果缩略图创建失败，显示占位符
            placeholder = QLabel("🖼️")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: #888888; font-size: 24px; border: none;")
            tag_layout.addWidget(placeholder)

        # 文件名
        filename = img_info.get('filename', '未知')
        if len(filename) > 12:
            filename = filename[:9] + "..."

        name_label = QLabel(filename)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #cccccc; font-size: 10px; border: none;")
        tag_layout.addWidget(name_label)

        # 删除按钮
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(16, 16)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b52d30;
            }
        """)
        delete_btn.clicked.connect(lambda: self.remove_image(index))

        # 将删除按钮放在右上角
        delete_btn.setParent(tag_frame)
        delete_btn.move(80, 4)

        return tag_frame

    def submit_feedback(self):
        """提交反馈"""
        try:
            text_content = self.text_widget.toPlainText().strip()

            # 处理反馈
            result = MCPTools.process_feedback_submission(text_content, self.selected_images)

            if result["success"]:
                self.result = result
                self.accept()
            else:
                QMessageBox.warning(self, "提交失败", result["message"])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"提交反馈时发生错误: {str(e)}")

    def show_dialog(self):
        """显示对话框并返回结果"""
        try:
            self.show()
            self.raise_()
            self.activateWindow()

            # 强制刷新界面
            self.app.processEvents()

            # 运行对话框
            result = self.exec()

            if result == QDialog.DialogCode.Accepted and self.result:
                return self.result
            else:
                return {"success": False, "message": "用户取消了操作"}

        except Exception as e:
            return {"success": False, "message": f"对话框显示失败: {str(e)}"}

    # 拖拽支持
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.image_tags_container.setStyleSheet("""
                QFrame {
                    background-color: #252525;
                    border: 2px dashed #0078d4;
                    border-radius: 8px;
                    margin: 8px 0;
                }
            """)

    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.image_tags_container.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 2px dashed #404040;
                border-radius: 8px;
                margin: 8px 0;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        self.image_tags_container.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 2px dashed #404040;
                border-radius: 8px;
                margin: 8px 0;
            }
        """)

        try:
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]

            if file_paths:
                images, errors = MCPTools.load_images_from_paths(file_paths)

                for img_info in images:
                    if len(self.selected_images) >= 5:
                        QMessageBox.warning(self, "提示", "最多只能选择5张图片")
                        break
                    self.add_image(img_info)

                if errors:
                    error_msg = "\n".join(errors)
                    QMessageBox.warning(self, "部分图片加载失败", error_msg)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"拖拽图片失败: {str(e)}")


class ImagePickerDialog(QDialog):
    """图片选择对话框"""

    def __init__(self):
        super().__init__()
        self.selected_image = None
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("🖼️ 选择图片")
        self.setFixedSize(400, 300)
        self.setModal(True)

        # 居中显示
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # 标题
        title = QLabel("请选择图片来源")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff; margin: 20px 0;")
        layout.addWidget(title)

        # 按钮
        file_btn = QPushButton("📁 选择文件")
        file_btn.setFixedHeight(50)
        file_btn.clicked.connect(self.select_file)

        clipboard_btn = QPushButton("📋 从剪贴板粘贴")
        clipboard_btn.setFixedHeight(50)
        clipboard_btn.clicked.connect(self.paste_from_clipboard)

        cancel_btn = QPushButton("❌ 取消")
        cancel_btn.setFixedHeight(50)
        cancel_btn.clicked.connect(self.reject)

        # 设置按钮样式
        for btn in [file_btn, clipboard_btn, cancel_btn]:
            btn.setFont(QFont("Microsoft YaHei", 12))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    color: #e0e0e0;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
            """)

        layout.addWidget(file_btn)
        layout.addWidget(clipboard_btn)
        layout.addWidget(cancel_btn)

        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #e0e0e0;
            }
        """)

    def select_file(self):
        """选择文件"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择图片文件",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;所有文件 (*)"
            )

            if file_path:
                img_info = ImageProcessor.load_from_file(file_path)
                self.selected_image = img_info['data']
                self.accept()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"选择图片失败: {str(e)}")

    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        try:
            img_info = ImageProcessor.load_from_clipboard()
            if img_info:
                self.selected_image = img_info['data']
                self.accept()
            else:
                QMessageBox.information(self, "提示", "剪贴板中没有图片数据")

        except Exception as e:
            QMessageBox.warning(self, "提示", str(e))
