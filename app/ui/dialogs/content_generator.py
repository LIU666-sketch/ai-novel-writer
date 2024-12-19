from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QProgressBar, QMessageBox,
    QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging

class ContentGeneratorDialog(QDialog):
    """内容生成对话框"""
    
    # 自定义信号
    contentGenerated = pyqtSignal(str)  # 内容生成完成信号
    
    def __init__(self, generator, parent=None, context=None):
        super().__init__(parent)
        self.generator = generator
        self.context = context or {}
        self.generated_content = ""
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("AI 内容生成")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 提示词输入区域
        prompt_group = QGroupBox("提示词")
        prompt_layout = QVBoxLayout(prompt_group)
        
        # 提示词说明
        prompt_help = QLabel(
            "提示：\n"
            "1. 描述你想要生成的内容\n"
            "2. 指定写作风格和语气\n"
            "3. 设定情节发展方向\n"
            "4. 提供关键的背景信息\n"
            "\n"
            "系统已自动收集以下上下文信息：\n"
            f"- {'已有' if 'novel_outline' in self.context else '未有'}小说大纲\n"
            f"- {'已有' if 'current_chapter' in self.context else '未有'}当前章节信息\n"
            f"- {'已有' if 'previous_summaries' in self.context else '未有'}之前章节摘要\n"
            f"- {'已有' + str(len(self.context.get('characters', []))) + '个' if 'characters' in self.context else '未有'}角色信息"
        )
        prompt_help.setWordWrap(True)
        prompt_layout.addWidget(prompt_help)
        
        # 提示词输入框
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("在这里输入提示词...")
        self.prompt_edit.setMaximumHeight(100)
        prompt_layout.addWidget(self.prompt_edit)
        
        layout.addWidget(prompt_group)
        
        # 生成选项
        options_layout = QHBoxLayout()
        
        # 字数控制
        word_count_layout = QHBoxLayout()
        word_count_layout.addWidget(QLabel("生成字数："))
        self.word_count_spin = QSpinBox()
        self.word_count_spin.setRange(100, 2000)
        self.word_count_spin.setValue(2000)
        self.word_count_spin.setSingleStep(100)
        word_count_layout.addWidget(self.word_count_spin)
        options_layout.addLayout(word_count_layout)
        
        options_layout.addStretch()
        
        # 生成按钮
        self.generate_button = QPushButton("开始生成")
        self.generate_button.clicked.connect(self._on_generate)
        options_layout.addWidget(self.generate_button)
        
        layout.addLayout(options_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # 预览区域
        preview_group = QGroupBox("内容预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setPlaceholderText("生成的内容将在这里显示...")
        preview_layout.addWidget(self.preview_edit)
        
        layout.addWidget(preview_group)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self._on_apply)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def _on_generate(self):
        """生成内容处理"""
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "提示", "请输入提示词")
            return
            
        try:
            # 显示进度条
            self.progress_bar.setRange(0, 0)  # 显示忙碌状态
            self.progress_bar.show()
            self.generate_button.setEnabled(False)
            self.prompt_edit.setEnabled(False)
            self.word_count_spin.setEnabled(False)
            
            logging.info("开始生成内容...")
            
            # 调用生成器
            content = self.generator.generate_content(
                prompt=prompt,
                context=self.context
            )
            
            # 显示生成的内容
            self.preview_edit.setPlainText(content)
            self.generated_content = content
            
            # 更新UI状态
            self.progress_bar.hide()
            self.apply_button.setEnabled(True)
            self.generate_button.setEnabled(True)
            self.prompt_edit.setEnabled(True)
            self.word_count_spin.setEnabled(True)
            
            logging.info("内容生成完成")
            
        except Exception as e:
            error_msg = f"生成内容失败：{str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            self.progress_bar.hide()
            self.generate_button.setEnabled(True)
            self.prompt_edit.setEnabled(True)
            self.word_count_spin.setEnabled(True)
            
    def _on_apply(self):
        """应用生成的内容"""
        if self.generated_content:
            self.contentGenerated.emit(self.generated_content)
            self.accept()
            
    @classmethod
    def generate_content(cls, generator, parent=None, context=None) -> str:
        """显示内容生成对话框
        
        Args:
            generator: 生成器实例
            parent: 父窗口
            context: 上下文信息
            
        Returns:
            生成的内容，如果取消则返回空字符串
        """
        dialog = cls(generator, parent, context)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.generated_content
        return "" 