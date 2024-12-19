from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QInputDialog, QMessageBox,
    QMenu
)
from PyQt6.QtCore import pyqtSignal, Qt

class ChapterList(QWidget):
    """章节列表组件"""
    
    # 自定义信号
    chapterSelected = pyqtSignal(int)  # 章节选择信号，参数为章节ID
    chapterCreated = pyqtSignal(int)   # 章节创建信号，参数为章节ID
    chapterDeleted = pyqtSignal(int)   # 章节删除信号，参数为章节ID
    chapterRenamed = pyqtSignal(int, str)  # 章节重命名信号，参数为章节ID和新标题
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_novel_id = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 添加章节按钮
        self.add_button = QPushButton("添加章节")
        self.add_button.clicked.connect(self._on_add_chapter)
        button_layout.addWidget(self.add_button)
        
        # 删除章节按钮
        self.delete_button = QPushButton("删除章节")
        self.delete_button.clicked.connect(self._on_delete_chapter)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # 创建章节列表
        self.chapter_list = QListWidget()
        self.chapter_list.currentItemChanged.connect(self._on_chapter_selected)
        self.chapter_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.chapter_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.chapter_list)
        
        # 初始状态下禁用按钮
        self.add_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
    def set_novel(self, novel_id: int, chapters: list):
        """设置当前小说
        
        Args:
            novel_id: 小说ID
            chapters: 章节列表，每个元素应该包含 id 和 title
        """
        self.current_novel_id = novel_id
        self.add_button.setEnabled(True)
        self.chapter_list.clear()
        
        for chapter in chapters:
            item = QListWidgetItem(f"{chapter['title']}")
            item.setData(Qt.ItemDataRole.UserRole, {
                'id': chapter['id'],
                'chapter_number': chapter['chapter_number']
            })
            self.chapter_list.addItem(item)
            
    def _show_context_menu(self, position):
        """显示上下文菜单"""
        item = self.chapter_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        rename_action = menu.addAction("重命名")
        action = menu.exec(self.chapter_list.mapToGlobal(position))
        
        if action == rename_action:
            self._rename_chapter(item)
            
    def _rename_chapter(self, item: QListWidgetItem):
        """重命名章节"""
        chapter_data = item.data(Qt.ItemDataRole.UserRole)
        old_title = item.text()
        
        title, ok = QInputDialog.getText(
            self,
            "重命名章节",
            "请输入新的章节标题：",
            text=old_title
        )
        
        if ok and title and title != old_title:
            # 发送重命名信号
            self.chapterRenamed.emit(chapter_data['id'], title)
            # 更新列表项
            item.setText(title)
            
    def clear_novel(self):
        """清除当前小说"""
        self.current_novel_id = None
        self.add_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.chapter_list.clear()
        
    def _on_chapter_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """章节选择处理"""
        self.delete_button.setEnabled(current is not None)
        if current:
            chapter_data = current.data(Qt.ItemDataRole.UserRole)
            self.chapterSelected.emit(chapter_data['id'])
            
    def _on_add_chapter(self):
        """添加章节处理"""
        if not self.current_novel_id:
            return
            
        title, ok = QInputDialog.getText(
            self,
            "添加章节",
            "请输入章节标题："
        )
        
        if ok and title:
            # 发送创建信号，让父组件处理创建逻辑
            self.chapterCreated.emit(self.current_novel_id)
            
    def _on_delete_chapter(self):
        """删除章节处理"""
        current_item = self.chapter_list.currentItem()
        if not current_item:
            return
            
        chapter_data = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除章节 '{current_item.text()}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 发送删除信号，让父组件处理删除逻辑
            self.chapterDeleted.emit(chapter_data['id'])
            
    def select_chapter(self, chapter_id: int):
        """选择指定章节
        
        Args:
            chapter_id: 要选择的章节ID
        """
        for i in range(self.chapter_list.count()):
            item = self.chapter_list.item(i)
            chapter_data = item.data(Qt.ItemDataRole.UserRole)
            if chapter_data['id'] == chapter_id:
                self.chapter_list.setCurrentItem(item)
                break