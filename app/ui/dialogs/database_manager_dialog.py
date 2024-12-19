from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
    QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QLabel, QHeaderView, QTabWidget,
    QWidget, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt
import logging
from ...models.character import Character

class DatabaseManagerDialog(QDialog):
    """数据库管理器对话框"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_novel_id = None
        self.modified_data = {}  # 记录修改的数据
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("小说数据管理器")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 顶部控制区
        top_layout = QHBoxLayout()
        
        # 小说选择
        novel_label = QLabel("选择小说:")
        self.novel_combo = QComboBox()
        self.refresh_novel_list()
        self.novel_combo.currentIndexChanged.connect(self.on_novel_selected)
        
        top_layout.addWidget(novel_label)
        top_layout.addWidget(self.novel_combo)
        
        # 新增小说按钮
        self.add_novel_button = QPushButton("新增小说")
        self.add_novel_button.clicked.connect(self.add_novel)
        top_layout.addWidget(self.add_novel_button)
        
        # 删除小说按钮
        self.delete_novel_button = QPushButton("删除小说")
        self.delete_novel_button.clicked.connect(self.delete_novel)
        top_layout.addWidget(self.delete_novel_button)
        
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 章节标签页
        self.chapters_tab = QWidget()
        self.setup_chapters_tab()
        self.tab_widget.addTab(self.chapters_tab, "章节管理")
        
        # 角色标签页
        self.characters_tab = QWidget()
        self.setup_characters_tab()
        self.tab_widget.addTab(self.characters_tab, "角色管理")
        
        # 角色关系标签页
        self.relationships_tab = QWidget()
        self.setup_relationships_tab()
        self.tab_widget.addTab(self.relationships_tab, "角色关系")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_all_data)
        button_layout.addWidget(self.refresh_button)
        
        layout.addLayout(button_layout)
        
    def setup_chapters_tab(self):
        """设置章节标签页"""
        layout = QVBoxLayout(self.chapters_tab)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.add_chapter_button = QPushButton("新增章节")
        self.add_chapter_button.clicked.connect(self.add_chapter)
        toolbar.addWidget(self.add_chapter_button)
        
        self.save_chapters_button = QPushButton("保存修改")
        self.save_chapters_button.clicked.connect(lambda: self.save_changes('chapters'))
        self.save_chapters_button.setEnabled(False)
        toolbar.addWidget(self.save_chapters_button)
        
        self.delete_chapter_button = QPushButton("删除章节")
        self.delete_chapter_button.clicked.connect(self.delete_chapter)
        toolbar.addWidget(self.delete_chapter_button)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 章节表格
        self.chapters_table = QTableWidget()
        self.chapters_table.itemChanged.connect(lambda item: self.on_data_changed(item, 'chapters'))
        layout.addWidget(self.chapters_table)
        
    def setup_characters_tab(self):
        """设置角色标签页"""
        layout = QVBoxLayout(self.characters_tab)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.add_character_button = QPushButton("新增角色")
        self.add_character_button.clicked.connect(self.add_character)
        toolbar.addWidget(self.add_character_button)
        
        self.save_characters_button = QPushButton("保存修改")
        self.save_characters_button.clicked.connect(lambda: self.save_changes('characters'))
        self.save_characters_button.setEnabled(False)
        toolbar.addWidget(self.save_characters_button)
        
        self.delete_character_button = QPushButton("删除角色")
        self.delete_character_button.clicked.connect(self.delete_character)
        toolbar.addWidget(self.delete_character_button)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 角色表格
        self.characters_table = QTableWidget()
        self.characters_table.itemChanged.connect(lambda item: self.on_data_changed(item, 'characters'))
        layout.addWidget(self.characters_table)
        
    def setup_relationships_tab(self):
        """设置角色关系���签页"""
        layout = QVBoxLayout(self.relationships_tab)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.add_relationship_button = QPushButton("新增关系")
        self.add_relationship_button.clicked.connect(self.add_relationship)
        toolbar.addWidget(self.add_relationship_button)
        
        self.save_character_relationships_button = QPushButton("保存修改")
        self.save_character_relationships_button.clicked.connect(
            lambda: self.save_changes('character_relationships')
        )
        self.save_character_relationships_button.setEnabled(False)
        toolbar.addWidget(self.save_character_relationships_button)
        
        self.delete_relationship_button = QPushButton("删除关系")
        self.delete_relationship_button.clicked.connect(self.delete_relationship)
        toolbar.addWidget(self.delete_relationship_button)
        
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # 关系表格
        self.character_relationships_table = QTableWidget()
        self.character_relationships_table.itemChanged.connect(
            lambda item: self.on_data_changed(item, 'character_relationships')
        )
        layout.addWidget(self.character_relationships_table)
        
    def refresh_novel_list(self):
        """刷新小说列表"""
        try:
            # 获取所有小说
            query = "SELECT id, title FROM novels ORDER BY id"
            result = self.db_manager.execute_query(query)
            
            # 清空并重新填充下拉框
            self.novel_combo.clear()
            self.novel_combo.addItem("请选择小说...", None)
            
            for novel_id, title in result:
                self.novel_combo.addItem(title, novel_id)
                
        except Exception as e:
            error_msg = f"加载小说列表失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def on_novel_selected(self, index):
        """小说选择变更处理"""
        self.current_novel_id = self.novel_combo.currentData()
        self.load_all_data()
        
        # 启用/禁用按钮
        has_novel = self.current_novel_id is not None
        self.delete_novel_button.setEnabled(has_novel)
        self.add_chapter_button.setEnabled(has_novel)
        self.add_character_button.setEnabled(has_novel)
        self.add_relationship_button.setEnabled(has_novel)
        
    def load_all_data(self):
        """加载所有数据"""
        logging.info("开始加载所有数据...")
        if self.current_novel_id is None:
            logging.info("当前未选择小说，清空所有表格")
            # 清空所有表格
            self.chapters_table.setRowCount(0)
            self.characters_table.setRowCount(0)
            self.character_relationships_table.setRowCount(0)
            return
            
        logging.info(f"当前选中小说ID: {self.current_novel_id}")
        self.load_chapters_data()
        self.load_characters_data()
        self.load_relationships_data()
        logging.info("所有数据加载完成")
        
    def load_chapters_data(self):
        """加载章节数据"""
        try:
            # 获取表结构
            columns = self.db_manager.get_table_structure('chapters')
            
            # 设置表格
            self.chapters_table.setColumnCount(len(columns))
            self.chapters_table.setHorizontalHeaderLabels(columns)
            
            # 获取数据
            query = "SELECT * FROM chapters WHERE novel_id = ? ORDER BY chapter_number"
            result = self.db_manager.execute_query(query, (self.current_novel_id,))
            
            # 填充数据
            self.chapters_table.setRowCount(0)
            for row_data in result:
                row = self.chapters_table.rowCount()
                self.chapters_table.insertRow(row)
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    if col in [0, 1]:  # ID和novel_id列不可编辑
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.chapters_table.setItem(row, col, item)
                    
            # 调整列宽
            self.chapters_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            
        except Exception as e:
            error_msg = f"加载章节数据失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def load_characters_data(self):
        """加载角色数据"""
        try:
            # 获取表结构
            columns = self.db_manager.get_table_structure('characters')
            
            # 设置表格
            self.characters_table.setColumnCount(len(columns))
            self.characters_table.setHorizontalHeaderLabels(columns)
            
            # 获取数据
            query = "SELECT * FROM characters WHERE novel_id = ? ORDER BY id"
            result = self.db_manager.execute_query(query, (self.current_novel_id,))
            
            # 填充数据
            self.characters_table.setRowCount(0)
            for row_data in result:
                row = self.characters_table.rowCount()
                self.characters_table.insertRow(row)
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    if col in [0, 1]:  # ID和novel_id列不可编辑
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.characters_table.setItem(row, col, item)
                    
            # 调整列宽
            self.characters_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            
        except Exception as e:
            error_msg = f"加载角色数据失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def load_relationships_data(self):
        """加载角色关系数据"""
        try:
            logging.info("开始加载角色关系数据...")
            if not self.current_novel_id:
                logging.info("当前未选择小说，清空关系表格")
                self.character_relationships_table.setRowCount(0)
                return
                
            logging.info(f"创建Character模型实例，小说ID={self.current_novel_id}")
            # 使用Character模型获取关系数据
            character_model = Character(self.db_manager)
            logging.info("开始调用get_character_relationships_for_novel方法")
            relationships = character_model.get_character_relationships_for_novel(self.current_novel_id)
            logging.info(f"获取到{len(relationships) if relationships else 0}个关系数据")
            
            # 设置表格列
            headers = ["ID", "角色1", "角色2", "关系类型", "描述", "起始章节"]
            self.character_relationships_table.setColumnCount(len(headers))
            self.character_relationships_table.setHorizontalHeaderLabels(headers)
            
            # 填充数据
            self.character_relationships_table.setRowCount(0)
            if relationships:
                for relation in relationships:
                    row = self.character_relationships_table.rowCount()
                    self.character_relationships_table.insertRow(row)
                    
                    # 填充各列数据
                    items = [
                        str(relation['id']),           # ID
                        relation['character1_name'],   # 角色1名称
                        relation['character2_name'],   # 角色2名称
                        relation['relationship_type'], # 关系类型
                        relation['description'] or "", # 描述
                        relation['start_chapter'] or "" # 起始章节
                    ]
                    
                    for col, item_text in enumerate(items):
                        item = QTableWidgetItem(str(item_text))
                        if col in [0, 1, 2]:  # ID和角色名称列不可编辑
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.character_relationships_table.setItem(row, col, item)
                        
                logging.info("关系数据填充完成")
            else:
                logging.info("没有找到任何关系数据")
                
            # 调整列宽
            self.character_relationships_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            logging.info("角色关系数据加载完成")
            
        except Exception as e:
            error_msg = f"加载角色关系数据失败: {str(e)}"
            logging.error(error_msg)
            logging.exception("详细错误信息：")
            QMessageBox.critical(self, "错误", error_msg)
            
    def on_data_changed(self, item, table_name):
        """数据修改处理"""
        if not item or not self.current_novel_id:
            return
            
        try:
            row = item.row()
            col = item.column()
            new_value = item.text()
            
            # 获取该行的ID（第一列）
            table_widget = None
            if table_name == 'chapters':
                table_widget = self.chapters_table
            elif table_name == 'characters':
                table_widget = self.characters_table
            elif table_name == 'character_relationships':
                table_widget = self.character_relationships_table
            else:
                return
                
            id_item = table_widget.item(row, 0)
            if not id_item:
                return
                
            record_id = int(id_item.text())
            display_column_name = table_widget.horizontalHeaderItem(col).text()
            
            # 表头显示名称到数据库字段名的映射
            column_name_mapping = {
                # 章节表
                'id': 'id',
                'novel_id': 'novel_id',
                'chapter_number': 'chapter_number',
                'title': 'title',
                'content': 'content',
                'summary': 'summary',
                'outline': 'outline',
                'created_at': 'created_at',
                
                # 角色表
                'name': 'name',
                'description': 'description',
                'characteristics': 'characteristics',
                'role_type': 'role_type',
                'first_appearance': 'first_appearance',
                'status': 'status',
                
                # 角色关系表
                'ID': 'id',
                '角色1': 'character1_id',
                '角色2': 'character2_id',
                '关系类型': 'relationship_type',
                '描述': 'description',
                '起始章节': 'start_chapter'
            }
            
            # 获取实际的数据库字段名
            column_name = column_name_mapping.get(display_column_name)
            if not column_name:
                logging.warning(f"未找到字段名映射: {display_column_name}")
                return
                
            # 对于角色关系表的特殊处理
            if table_name == 'character_relationships':
                # 只允许修改关系类型和描述
                if column_name not in ['relationship_type', 'description']:
                    return
                    
            # 记录修改
            if table_name not in self.modified_data:
                self.modified_data[table_name] = {}
            if record_id not in self.modified_data[table_name]:
                self.modified_data[table_name][record_id] = {}
                
            self.modified_data[table_name][record_id][column_name] = new_value
            
            # 启用相应的保存按钮
            if table_name == 'chapters':
                self.save_chapters_button.setEnabled(True)
            elif table_name == 'characters':
                self.save_characters_button.setEnabled(True)
            elif table_name == 'character_relationships':
                self.save_character_relationships_button.setEnabled(True)
            
            logging.info(f"数据已修改: 表={table_name}, ID={record_id}, {column_name}={new_value}")
            
        except Exception as e:
            error_msg = f"处理数据修改失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def save_changes(self, table_name):
        """保存修改"""
        try:
            if table_name not in self.modified_data or not self.modified_data[table_name]:
                return
                
            # 确认保存
            reply = QMessageBox.question(
                self,
                "确认保存",
                f"确定要保存对{table_name}表的修改吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            # 保存修改
            for record_id, changes in self.modified_data[table_name].items():
                self.db_manager.update_record(table_name, record_id, changes)
                
            # 清除修改记录
            self.modified_data[table_name].clear()
            
            # 禁用保存按钮
            if table_name == 'chapters':
                self.save_chapters_button.setEnabled(False)
            elif table_name == 'characters':
                self.save_characters_button.setEnabled(False)
            elif table_name == 'character_relationships':
                self.save_character_relationships_button.setEnabled(False)
            
            # 重新加载数据
            self.load_all_data()
            
            QMessageBox.information(self, "成功", "修改已保存")
            
        except Exception as e:
            error_msg = f"保存修改失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def add_novel(self):
        """添加新小说"""
        try:
            title, ok = QMessageBox.getText(
                self,
                "新增小说",
                "请输入小说标题："
            )
            
            if ok and title:
                # 检查是否已存在同名小说
                query = "SELECT 1 FROM novels WHERE title = ?"
                if self.db_manager.execute_query(query, (title,)):
                    raise ValueError("已存在同名小说")
                    
                # 插入新小说
                query = "INSERT INTO novels (title) VALUES (?)"
                result = self.db_manager.execute_query(query, (title,))
                
                if result:
                    self.refresh_novel_list()
                    QMessageBox.information(self, "成功", "小说创建成功")
                    
        except Exception as e:
            error_msg = f"创建小说失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def delete_novel(self):
        """删除当前小说"""
        try:
            if not self.current_novel_id:
                return
                
            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                "确定要删除当前小说吗？这将同时删除所有相关的章节、角色和关系数据！",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            # 删除小说及相关数据
            self.db_manager.delete_record('novels', self.current_novel_id)
            
            # 刷新界面
            self.refresh_novel_list()
            self.current_novel_id = None
            self.load_all_data()
            
            QMessageBox.information(self, "成功", "小说已删除")
            
        except Exception as e:
            error_msg = f"删除小说失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def add_chapter(self):
        """添加新章节"""
        try:
            if not self.current_novel_id:
                return
                
            # 获取当前最大章节号
            query = "SELECT MAX(chapter_number) FROM chapters WHERE novel_id = ?"
            result = self.db_manager.execute_query(query, (self.current_novel_id,))
            max_chapter = result[0][0] if result and result[0][0] else 0
            
            # 创建新章节
            new_chapter = {
                'novel_id': self.current_novel_id,
                'chapter_number': max_chapter + 1,
                'title': f'第{max_chapter + 1}章',
                'content': '',
                'summary': ''
            }
            
            self.db_manager.insert_record('chapters', new_chapter)
            
            # 刷新数据
            self.load_chapters_data()
            
        except Exception as e:
            error_msg = f"添加章节失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def delete_chapter(self):
        """删除选中的章节"""
        self.delete_selected_rows('chapters', self.chapters_table)
        
    def add_character(self):
        """添加新角色"""
        try:
            if not self.current_novel_id:
                return
                
            # 创建新角色
            new_character = {
                'novel_id': self.current_novel_id,
                'name': '新角色',
                'description': '',
                'characteristics': '',
                'role_type': '配角',
                'status': '活跃'
            }
            
            self.db_manager.insert_record('characters', new_character)
            
            # 刷新数据
            self.load_characters_data()
            
        except Exception as e:
            error_msg = f"添加角色失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def delete_character(self):
        """删除选中的角色"""
        self.delete_selected_rows('characters', self.characters_table)
        
    def add_relationship(self):
        """添加新角色关系"""
        try:
            if not self.current_novel_id:
                return
                
            # 获取当前小说的所有角色
            query = "SELECT id, name FROM characters WHERE novel_id = ? ORDER BY name"
            characters = self.db_manager.execute_query(query, (self.current_novel_id,))
            
            if not characters or len(characters) < 2:
                QMessageBox.warning(self, "警告", "需要至少两个角色才能创建关系")
                return
                
            # 获取所有关系类型
            query = """
                SELECT category, type, description 
                FROM relationship_types 
                ORDER BY category, type
            """
            relationship_types = self.db_manager.execute_query(query)
            
            if not relationship_types:
                QMessageBox.warning(self, "警告", "未找到预定义的关系类型")
                return
                
            # 创建角色选择对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("新增角色关系")
            dialog.setModal(True)
            dialog.setMinimumWidth(400)
            
            layout = QVBoxLayout(dialog)
            
            # 角色1选择
            char1_label = QLabel("选择角色1:")
            char1_combo = QComboBox()
            for char_id, char_name in characters:
                char1_combo.addItem(char_name, char_id)
            layout.addWidget(char1_label)
            layout.addWidget(char1_combo)
            
            # 角色2选择
            char2_label = QLabel("选择角色2:")
            char2_combo = QComboBox()
            for char_id, char_name in characters:
                char2_combo.addItem(char_name, char_id)
            layout.addWidget(char2_label)
            layout.addWidget(char2_combo)
            
            # 关系类型选择
            type_group = QGroupBox("关系类型")
            type_layout = QVBoxLayout()
            
            # 分类下拉框
            category_label = QLabel("选择分类:")
            category_combo = QComboBox()
            categories = sorted(set(t[0] for t in relationship_types))
            for category in categories:
                category_combo.addItem(category)
            type_layout.addWidget(category_label)
            type_layout.addWidget(category_combo)
            
            # 关系类型下拉框
            type_label = QLabel("选择关系:")
            type_combo = QComboBox()
            type_combo.setMinimumWidth(200)
            
            # 关系描述标签
            desc_label = QLabel()
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: gray;")
            
            def update_types():
                """更新关系类型下拉框"""
                type_combo.clear()
                current_category = category_combo.currentText()
                for cat, type_, desc in relationship_types:
                    if cat == current_category:
                        type_combo.addItem(type_)
                        
            def update_description():
                """更新关系描述"""
                current_type = type_combo.currentText()
                for cat, type_, desc in relationship_types:
                    if type_ == current_type:
                        desc_label.setText(desc)
                        break
                        
            category_combo.currentTextChanged.connect(update_types)
            type_combo.currentTextChanged.connect(update_description)
            
            type_layout.addWidget(type_label)
            type_layout.addWidget(type_combo)
            type_layout.addWidget(desc_label)
            
            type_group.setLayout(type_layout)
            layout.addWidget(type_group)
            
            # 自定义描述输入
            custom_desc_label = QLabel("补充描述:")
            custom_desc_edit = QLineEdit()
            layout.addWidget(custom_desc_label)
            layout.addWidget(custom_desc_edit)
            
            # 按钮
            button_box = QHBoxLayout()
            ok_button = QPushButton("确定")
            cancel_button = QPushButton("取消")
            button_box.addWidget(ok_button)
            button_box.addWidget(cancel_button)
            layout.addLayout(button_box)
            
            # 绑定按钮事件
            ok_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)
            
            # 初始化关系类型列表
            update_types()
            if type_combo.count() > 0:
                update_description()
            
            # 显示对话框
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 获取选择的值
                char1_id = char1_combo.currentData()
                char2_id = char2_combo.currentData()
                
                if char1_id == char2_id:
                    QMessageBox.warning(self, "警告", "不能选择相同的角色")
                    return
                    
                # 创建新关系
                new_relationship = {
                    'novel_id': self.current_novel_id,
                    'character1_id': char1_id,
                    'character2_id': char2_id,
                    'relationship_type': type_combo.currentText(),
                    'description': custom_desc_edit.text(),
                    'start_chapter': None
                }
                
                self.db_manager.insert_record('character_relationships', new_relationship)
                
                # 刷新数据
                self.load_relationships_data()
                
        except Exception as e:
            error_msg = f"添加角色关系失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def delete_relationship(self):
        """删除选中的角色关系"""
        try:
            selected_items = self.character_relationships_table.selectedItems()
            if not selected_items:
                return
                
            # 获取选中的行的ID
            selected_rows = set()
            for item in selected_items:
                row = item.row()
                id_item = self.character_relationships_table.item(row, 0)
                if id_item and id_item.text():
                    selected_rows.add((row, int(id_item.text())))
                    
            if not selected_rows:
                return
                
            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除选中的 {len(selected_rows)} 条关系记录吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            # 删除记录
            for _, record_id in selected_rows:
                self.db_manager.delete_record('character_relationships', record_id)
                
            # 重新加载数据
            self.load_relationships_data()
            
        except Exception as e:
            error_msg = f"删除角色关系失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def delete_selected_rows(self, table_name, table_widget):
        """删除选中的行"""
        try:
            selected_items = table_widget.selectedItems()
            if not selected_items:
                return
                
            # 获取选中的行的ID
            selected_rows = set()
            for item in selected_items:
                row = item.row()
                id_item = table_widget.item(row, 0)
                if id_item and id_item.text():
                    selected_rows.add((row, int(id_item.text())))
                    
            if not selected_rows:
                return
                
            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除选中的 {len(selected_rows)} 条记录吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
            # 删除记录
            for _, record_id in selected_rows:
                self.db_manager.delete_record(table_name, record_id)
                
            # 重新加载数据
            self.load_all_data()
            
        except Exception as e:
            error_msg = f"删除记录失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
            
    def refresh_all_data(self):
        """刷新所有数据"""
        if any(self.modified_data.values()):
            reply = QMessageBox.question(
                self,
                "确认刷新",
                "有未保存的修改，确定要刷新吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        # 清除所有修改记录
        self.modified_data.clear()
        
        # 禁用所有保存按钮
        self.save_chapters_button.setEnabled(False)
        self.save_characters_button.setEnabled(False)
        self.save_character_relationships_button.setEnabled(False)
        
        # 刷新数据
        self.refresh_novel_list()
        self.load_all_data()
        
    @classmethod
    def show_dialog(cls, db_manager, parent=None):
        """显示数据库管理器对话框"""
        dialog = cls(db_manager, parent)
        dialog.exec() 