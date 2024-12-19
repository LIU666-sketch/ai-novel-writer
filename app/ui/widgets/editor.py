from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QTimer, pyqtSignal
import logging

class Editor(QTextEdit):
    """自定义编辑器组件"""
    
    # 自定义信号
    contentChanged = pyqtSignal(str)  # 内容变更信号
    saveRequested = pyqtSignal(str)   # 保存请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化自动保存定时器
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(30000)  # 30秒自动保存
        self._auto_save_timer.timeout.connect(self._auto_save)
        
        # 连接信号
        self.textChanged.connect(self._on_text_changed)
        
        # 设置占位符文本
        self.setPlaceholderText("在这里开始写作...")
        
        # 状态标记
        self._content_modified = False
        
    def _on_text_changed(self):
        """文本变更处理"""
        self._content_modified = True
        content = self.toPlainText()
        self.contentChanged.emit(content)
        
        # 重启自动保存定时器
        self._auto_save_timer.start()
        
    def _auto_save(self):
        """自动保存"""
        if self._content_modified:
            content = self.toPlainText()
            self.saveRequested.emit(content)
            self._content_modified = False
            logging.info("编辑器内容已自动保存")
            
    def load_content(self, content: str):
        """加载内容
        
        Args:
            content: 要加载的内容
        """
        # 暂时断开信号连接，避免触发变更
        self.blockSignals(True)
        self.setPlainText(content)
        self.blockSignals(False)
        self._content_modified = False
        
    def save_content(self) -> str:
        """保存内容
        
        Returns:
            当前内容
        """
        content = self.toPlainText()
        self.saveRequested.emit(content)
        self._content_modified = False
        return content
        
    def is_modified(self) -> bool:
        """检查内容是否被修改
        
        Returns:
            是否被修改
        """
        return self._content_modified
        
    def clear_modified(self):
        """清除修改标记"""
        self._content_modified = False