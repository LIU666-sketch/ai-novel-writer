from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QMenu, QMessageBox,
    QInputDialog
)
from PyQt6.QtCore import pyqtSignal, Qt

class CharacterList(QWidget):
    """角色列表组件"""
    
    # 自定义信号
    characterSelected = pyqtSignal(int)  # 角色选择信号
    characterCreated = pyqtSignal(int)   # 角色创建信号
    characterDeleted = pyqtSignal(int)   # 角色删除信号
    characterEdited = pyqtSignal(int)    # 角色编辑信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_novel_id = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建工具栏
        toolbar = QHBoxLayout()
        
        # 添加角色按钮
        self.add_button = QPushButton("添加角色")
        self.add_button.clicked.connect(self._on_add_character)
        toolbar.addWidget(self.add_button)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 创建角��列表
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemClicked.connect(self._on_character_selected)
        layout.addWidget(self.list_widget)
        
    def set_novel(self, novel_id: int, characters: list):
        """设置当前小说和角色列表
        
        Args:
            novel_id: 小说ID
            characters: 角色列表
        """
        self.current_novel_id = novel_id
        self.list_widget.clear()
        
        for char in characters:
            item = QListWidgetItem(char['name'])
            item.setData(Qt.ItemDataRole.UserRole, char['id'])
            self.list_widget.addItem(item)
            
    def clear_novel(self):
        """清空当前小说"""
        self.current_novel_id = None
        self.list_widget.clear()
        
    def _on_add_character(self):
        """添加角色处理"""
        if not self.current_novel_id:
            QMessageBox.warning(self, "警告", "请先创建或打开小说")
            return
            
        name, ok = QInputDialog.getText(
            self,
            "添加角色",
            "请输入角色名称："
        )
        
        if ok and name:
            self.characterCreated.emit(self.current_novel_id)
            
    def _show_context_menu(self, pos):
        """显示上下文菜单"""
        item = self.list_widget.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        delete_action = menu.addAction("删除")
        
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        
        if action == edit_action:
            self._on_edit_character(item)
        elif action == delete_action:
            self._on_delete_character(item)
            
    def _on_edit_character(self, item):
        """编辑角色处理"""
        character_id = item.data(Qt.ItemDataRole.UserRole)
        self.characterEdited.emit(character_id)
        
    def _on_delete_character(self, item):
        """删除角色处理"""
        character_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除角色\"{item.text()}\"吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.characterDeleted.emit(character_id)
            
    def _on_character_selected(self, item):
        """角色选择处理"""
        character_id = item.data(Qt.ItemDataRole.UserRole)
        self.characterSelected.emit(character_id) 