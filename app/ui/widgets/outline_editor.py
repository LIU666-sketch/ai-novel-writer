from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QComboBox
)
from PyQt6.QtCore import pyqtSignal

class OutlineEditor(QWidget):
    """大纲编辑器组件"""
    
    # 自定义信号
    outlineChanged = pyqtSignal(str)  # 大纲内容变更信号
    generateRequested = pyqtSignal()  # AI生成请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._modified = False
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建工具栏
        toolbar = QHBoxLayout()
        
        # 大纲类型选择
        self.outline_type = QComboBox()
        self.outline_type.addItems(["小说大纲", "章节大纲"])
        toolbar.addWidget(self.outline_type)
        
        # 保存按钮
        self.save_button = QPushButton("保存大纲")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setEnabled(False)
        toolbar.addWidget(self.save_button)
        
        # AI生成按钮
        self.generate_button = QPushButton("AI生成")
        self.generate_button.clicked.connect(self._on_generate)
        toolbar.addWidget(self.generate_button)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 创建编辑区域
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("在这里编写大纲...")
        self.editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.editor)
        
        # 创建提示标签
        self.hint_label = QLabel()
        self.hint_label.setStyleSheet("color: gray;")
        layout.addWidget(self.hint_label)
        
        # 连接大纲类型变更信号
        self.outline_type.currentIndexChanged.connect(self._update_hint)
        self._update_hint()
        
    def _update_hint(self):
        """更新提示信息"""
        if self.outline_type.currentText() == "小说大纲":
            self.hint_label.setText(
                "小说大纲提示：\n"
                "1. 描述小说的整体故事架构\n"
                "2. 设定主要人物及其发展轨迹\n"
                "3. 规划重要的情节转折点\n"
                "4. 确定故事的主题和中心思想"
            )
        else:
            self.hint_label.setText(
                "章节大纲提示：\n"
                "1. 描述本章的主要内容和目标\n"
                "2. 列出关键场景和对话\n"
                "3. 说明与整体故事的关联\n"
                "4. 注明需要重点描写的细节"
            )
        
    def _on_text_changed(self):
        """文本变更处理"""
        self._modified = True
        self.save_button.setEnabled(True)
        
    def _on_save(self):
        """保存处理"""
        content = self.editor.toPlainText().strip()
        self.outlineChanged.emit(content)
        self._modified = False
        self.save_button.setEnabled(False)
        
    def _on_generate(self):
        """AI生成处理"""
        self.generateRequested.emit()
        
    def set_content(self, content: str, is_chapter: bool = False):
        """设置内容
        
        Args:
            content: 大纲内容
            is_chapter: 是否为章节大纲
        """
        self.outline_type.setCurrentText("章节大纲" if is_chapter else "小说大纲")
        self.editor.setPlainText(content or "")
        self._modified = False
        self.save_button.setEnabled(False)
        
    def get_content(self) -> str:
        """获取内容
        
        Returns:
            当前大纲内容
        """
        return self.editor.toPlainText().strip()
        
    def is_modified(self) -> bool:
        """是否已修改
        
        Returns:
            是否已修改
        """
        return self._modified
        
    def is_chapter_outline(self) -> bool:
        """是否为章节大纲
        
        Returns:
            是否为章节大纲
        """
        return self.outline_type.currentText() == "章节大纲"
        
    def clear(self):
        """清空内容"""
        self.editor.clear()
        self._modified = False
        self.save_button.setEnabled(False) 