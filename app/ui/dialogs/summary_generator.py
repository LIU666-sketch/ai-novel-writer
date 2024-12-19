from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QProgressBar, QMessageBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging

class SummaryGeneratorDialog(QDialog):
    """摘要生成对话框"""
    
    # 自定义信号
    summaryGenerated = pyqtSignal(str)  # 摘要生成完成信号
    autoSummaryChanged = pyqtSignal(bool)  # 自动摘要设置变更信号
    
    def __init__(self, summary_system, content: str, current_summary: str = "", parent=None):
        super().__init__(parent)
        self.summary_system = summary_system
        self.content = content
        self.generated_summary = ""
        self.init_ui()
        
        # 如果有现有摘要，显示在预览区域
        if current_summary:
            self.summary_preview.setPlainText(current_summary)
            self.generated_summary = current_summary
            self.apply_button.setEnabled(True)
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("生成章节摘要")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 原文预览区域
        content_label = QLabel("章节内容：")
        layout.addWidget(content_label)
        
        self.content_preview = QTextEdit()
        self.content_preview.setPlainText(self.content)
        self.content_preview.setReadOnly(True)
        self.content_preview.setMaximumHeight(150)
        layout.addWidget(self.content_preview)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # 摘要预览区域
        summary_label = QLabel("摘要内容：")
        layout.addWidget(summary_label)
        
        self.summary_preview = QTextEdit()
        self.summary_preview.setPlaceholderText("在这里编辑或生成摘要...")
        layout.addWidget(self.summary_preview)
        
        # 自动生成选项
        self.auto_summary_check = QCheckBox("保存时自动生成摘要")
        self.auto_summary_check.stateChanged.connect(self._on_auto_summary_changed)
        layout.addWidget(self.auto_summary_check)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.generate_button = QPushButton("生成摘要")
        self.generate_button.clicked.connect(self._on_generate)
        button_layout.addWidget(self.generate_button)
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._on_apply)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 状态提示
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        # 连接摘要编辑信号
        self.summary_preview.textChanged.connect(self._on_summary_edited)
        
    def _on_generate(self):
        """生成摘要处理"""
        try:
            # 更新UI状态
            self.progress_bar.setRange(0, 0)
            self.progress_bar.show()
            self.generate_button.setEnabled(False)
            self.status_label.setText("正在分析章节内容...")
            
            # 生成摘要
            summary = self.summary_system.generate_chapter_summary(self.content)
            
            # 显示摘要
            self.summary_preview.setPlainText(summary)
            self.generated_summary = summary
            
            # 更新UI状态
            self.progress_bar.hide()
            self.apply_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.status_label.setText("摘要生成完成")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成摘要失败：{str(e)}")
            self.progress_bar.hide()
            self.generate_button.setEnabled(True)
            self.status_label.setText("生成失败")
            
    def _on_apply(self):
        """应用摘要"""
        summary = self.summary_preview.toPlainText().strip()
        if summary:
            self.generated_summary = summary
            self.summaryGenerated.emit(summary)
            self.accept()
            
    def _on_summary_edited(self):
        """摘要编辑处理"""
        # 只要有内容就启用应用按钮
        self.apply_button.setEnabled(bool(self.summary_preview.toPlainText().strip()))
        
    def _on_auto_summary_changed(self, state: int):
        """自动摘要设置变更处理"""
        self.autoSummaryChanged.emit(state == Qt.CheckState.Checked)
            
    @classmethod
    def generate_summary(cls, summary_system, content: str, current_summary: str = "", parent=None) -> str:
        """显示摘要生成对话框
        
        Args:
            summary_system: 摘要系统实例
            content: 章节内容
            current_summary: 当前摘要
            parent: 父窗口
            
        Returns:
            生成的摘要，如果取消则返回空字符串
        """
        dialog = cls(summary_system, content, current_summary, parent)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.generated_summary
        return "" 