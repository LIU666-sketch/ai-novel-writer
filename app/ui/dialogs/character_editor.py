from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QComboBox, QPushButton, QDialogButtonBox
)

class CharacterEditorDialog(QDialog):
    """角色编辑对话框"""
    
    def __init__(self, character=None, parent=None):
        """初始化对话框
        
        Args:
            character: 角色信息字典，如果为None则为新建角色
            parent: 父窗口
        """
        super().__init__(parent)
        self.character = character
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑角色" if self.character else "新建角色")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 创建表单
        form_layout = QFormLayout()
        
        # 角色名称
        self.name_edit = QLineEdit()
        if self.character:
            self.name_edit.setText(self.character.get('name', ''))
        form_layout.addRow("角色名称：", self.name_edit)
        
        # 角色描述
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        if self.character:
            self.description_edit.setText(self.character.get('description', ''))
        form_layout.addRow("角色描述：", self.description_edit)
        
        # 角色特征
        self.characteristics_edit = QTextEdit()
        self.characteristics_edit.setMaximumHeight(100)
        if self.character:
            self.characteristics_edit.setText(self.character.get('characteristics', ''))
        form_layout.addRow("角色特征：", self.characteristics_edit)
        
        # 角色类型
        self.role_type = QComboBox()
        self.role_type.addItems(["主角", "配角", "反派"])
        if self.character:
            self.role_type.setCurrentText(self.character.get('role_type', '配角'))
        form_layout.addRow("角色类型：", self.role_type)
        
        # 角色状态
        self.status = QComboBox()
        self.status.addItems(["活跃", "已退场", "已死亡"])
        if self.character:
            self.status.setCurrentText(self.character.get('status', '活跃'))
        form_layout.addRow("角色状态：", self.status)
        
        layout.addLayout(form_layout)
        
        # 添加按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_character_data(self) -> dict:
        """获取角色数据
        
        Returns:
            角色信息字典
        """
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'characteristics': self.characteristics_edit.toPlainText().strip(),
            'role_type': self.role_type.currentText(),
            'status': self.status.currentText()
        } 