from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeView, QDockWidget, QMenuBar, QTextEdit,
    QStatusBar, QMessageBox, QFileDialog, QInputDialog
)
from PyQt6.QtCore import Qt
from app.models.novel import Novel
from app.models.chapter import Chapter
from app.core.generator import NovelGenerator
from app.ui.widgets.editor import Editor
from app.ui.widgets.chapter_list import ChapterList
from app.ui.widgets.outline_editor import OutlineEditor
from app.ui.widgets.character_list import CharacterList
from app.ui.dialogs.content_generator import ContentGeneratorDialog
from app.ui.dialogs.summary_generator import SummaryGeneratorDialog
from app.core.summary import SummarySystem
from app.ui.dialogs.character_editor import CharacterEditorDialog
from app.models.character import Character
from app.ui.dialogs.database_manager_dialog import DatabaseManagerDialog
import logging

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.novel_model = Novel(db_manager)
        self.chapter_model = Chapter(db_manager)
        self.generator = NovelGenerator()
        self.summary_system = SummarySystem(db_manager, self.generator)
        self.character_model = Character(db_manager)
        
        self.current_novel_id = None
        self.current_chapter_id = None
        self.auto_summary = False  # 自动摘要标志
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置窗口基本属性
        self.setWindowTitle('AI 小说生成器')
        self.setMinimumSize(1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QHBoxLayout(central_widget)
        
        # 创建左侧面板（大纲和章节列表）
        self.create_left_panel()
        
        # 创建中央编辑区
        self.create_editor()
        layout.addWidget(self.editor)
        
        # 创建右侧面板（角色���摘要）
        self.create_right_panel()
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('就绪')
        
    def create_left_panel(self):
        """创建左侧面板"""
        # 创建大纲面板
        outline_dock = QDockWidget("小说大纲", self)
        outline_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        
        # 创建大纲编辑器
        self.outline_editor = OutlineEditor()
        self.outline_editor.outlineChanged.connect(self._on_outline_changed)
        self.outline_editor.generateRequested.connect(self._on_generate_outline)
        outline_dock.setWidget(self.outline_editor)
        
        # 创建章节列表面板
        chapter_dock = QDockWidget("章节列表", self)
        chapter_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        
        # 创建章节列表
        self.chapter_list = ChapterList()
        self.chapter_list.chapterSelected.connect(self._on_chapter_selected)
        self.chapter_list.chapterCreated.connect(self._on_chapter_created)
        self.chapter_list.chapterDeleted.connect(self._on_chapter_deleted)
        self.chapter_list.chapterRenamed.connect(self._on_chapter_renamed)
        chapter_dock.setWidget(self.chapter_list)
        
        # 添加到主窗口
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, outline_dock)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, chapter_dock)
        
    def _on_outline_changed(self, content: str):
        """大纲内容变更处理"""
        try:
            if not self.current_novel_id:
                raise ValueError('请先创建或打开小说')
                
            if self.outline_editor.is_chapter_outline():
                # 保存章节大纲
                if not self.current_chapter_id:
                    raise ValueError('请先选择章节')
                self.chapter_model.update(
                    self.current_chapter_id,
                    outline=content
                )
                self.statusBar.showMessage('章节大纲已保存')
            else:
                # 保存小说大纲
                self.novel_model.update(
                    self.current_novel_id,
                    outline=content
                )
                self.statusBar.showMessage('小说大纲已保存')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存大纲失败：{str(e)}')
            
    def _load_novel_outline(self):
        """加载小说大纲"""
        try:
            if self.current_novel_id:
                novel = self.novel_model.get(self.current_novel_id)
                if novel:
                    self.outline_editor.set_content(novel.get('outline', ''), is_chapter=False)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载大纲失败：{str(e)}')
            
    def _load_chapter_outline(self):
        """加载章节大纲"""
        try:
            if self.current_chapter_id:
                chapter = self.chapter_model.get(self.current_chapter_id)
                if chapter:
                    self.outline_editor.set_content(chapter.get('outline', ''), is_chapter=True)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载章节大纲失败：{str(e)}')
            
    def _on_chapter_selected(self, chapter_id: int):
        """章节选择处理"""
        try:
            # 如果当前有修改，先保存
            if self.editor.is_modified():
                self.save_novel()
                
            # 加载选中的章节
            chapter = self.chapter_model.get(chapter_id)
            if chapter:
                self.current_chapter_id = chapter_id
                self.editor.load_content(chapter['content'])
                # 显示摘要
                self.summary_text.setPlainText(chapter['summary'] or "暂无摘要")
                # 加载章节大纲
                self._load_chapter_outline()
                self.statusBar.showMessage(f'当前章节：第{chapter["chapter_number"]}章 {chapter["title"]}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载章节失败：{str(e)}')
            
    def _on_chapter_created(self, novel_id: int):
        """章节创建处理"""
        try:
            # 获取当前章节数
            chapters = self.chapter_model.get_by_novel(novel_id)
            chapter_number = len(chapters) + 1
            
            # 创建新章节
            chapter_id = self.chapter_model.create(
                novel_id=novel_id,
                chapter_number=chapter_number,
                title=f'第{chapter_number}章',
                content=''
            )
            
            # 刷新章节列表
            self._refresh_chapter_list()
            
            # 选择新创建的章节
            self.chapter_list.select_chapter(chapter_id)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建章节失败：{str(e)}')
            
    def _on_chapter_deleted(self, chapter_id: int):
        """章节删除处理"""
        try:
            self.chapter_model.delete(chapter_id)
            self.current_chapter_id = None
            self.editor.clear()
            self.editor.clear_modified()
            
            # 刷新章节列表
            self._refresh_chapter_list()
            
            self.statusBar.showMessage('章节已删除')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'删除章节失败：{str(e)}')
            
    def _refresh_chapter_list(self):
        """刷新章节列表"""
        if self.current_novel_id:
            chapters = self.chapter_model.get_by_novel(self.current_novel_id)
            self.chapter_list.set_novel(self.current_novel_id, chapters)
            
    def new_novel(self):
        """创建新小说"""
        try:
            title, ok = QInputDialog.getText(
                self,
                "新建小说",
                "请输入小说标题："
            )
            
            if ok and title:
                # 检查标题是否已存在
                existing_novel = self.novel_model.get_by_title(title)
                if existing_novel:
                    raise ValueError(f'已存在同名小说：{title}')
                
                # 创建新小说
                novel_id = self.novel_model.create(title=title)
                self.current_novel_id = novel_id
                self.current_chapter_id = None
                
                # 清空编辑器
                self.editor.clear()
                self.editor.clear_modified()
                self.outline_editor.clear()
                
                # 刷新章节列表
                self._refresh_chapter_list()
                
                # 刷新角色列表
                self.character_list.clear_novel()
                
                self.statusBar.showMessage(f'创建新小说：{title}')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建小说失败：{str(e)}')
            
    def open_novel(self):
        """打开小说"""
        try:
            # 获取所有小说列表
            novels = self.novel_model.list_all()
            if not novels:
                QMessageBox.information(self, "提示", "还没有创建任何小说")
                return
                
            # 创建选择话框
            items = [novel['title'] for novel in novels]
            title, ok = QInputDialog.getItem(
                self,
                "打开小说",
                "请选择要打开的小说：",
                items,
                0,
                False
            )
            
            if ok and title:
                # 获取小说信息
                novel = self.novel_model.get_by_title(title)
                if not novel:
                    raise ValueError(f'找不到小说：{title}')
                    
                self.current_novel_id = novel['id']
                self.current_chapter_id = None
                
                # 清空编辑器
                self.editor.clear()
                self.editor.clear_modified()
                
                # 加载大纲
                self._load_novel_outline()
                
                # 刷新章节列表
                self._refresh_chapter_list()
                
                # 刷新角色列表
                self._refresh_character_list()
                
                self.statusBar.showMessage(f'打开小说：{title}')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'打开小说失败：{str(e)}')
            
    def create_editor(self):
        """创建中央编辑器"""
        self.editor = Editor()
        # 连接编辑器信号
        self.editor.contentChanged.connect(self._on_editor_content_changed)
        self.editor.saveRequested.connect(self._on_editor_save_requested)
        
    def create_right_panel(self):
        """创建右侧面板"""
        # 创建角色面板
        character_dock = QDockWidget("角色", self)
        character_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # 创建角色列表
        self.character_list = CharacterList()
        self.character_list.characterSelected.connect(self._on_character_selected)
        self.character_list.characterCreated.connect(self._on_character_created)
        self.character_list.characterDeleted.connect(self._on_character_deleted)
        self.character_list.characterEdited.connect(self._on_character_edited)
        character_dock.setWidget(self.character_list)
        
        # 创建摘要面板
        summary_dock = QDockWidget("摘要", self)
        summary_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # 创建摘要显示
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_dock.setWidget(self.summary_text)
        
        # 添加到主窗口
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, character_dock)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, summary_dock)
        
    def _refresh_character_list(self):
        """刷新角色列表"""
        if self.current_novel_id:
            characters = self.character_model.get_by_novel(self.current_novel_id)
            self.character_list.set_novel(self.current_novel_id, characters)
            
    def _on_character_selected(self, character_id: int):
        """角色选择处理"""
        try:
            character = self.character_model.get(character_id)
            if character:
                # TODO: 显示角色详细信息
                self.statusBar.showMessage(f'当前角色：{character["name"]}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载角色失败：{str(e)}')
            
    def _on_character_created(self, novel_id: int):
        """角色创建处理"""
        try:
            dialog = CharacterEditorDialog(parent=self)
            if dialog.exec():
                character_data = dialog.get_character_data()
                character_data['novel_id'] = novel_id
                
                # 创建角色
                self.character_model.create(**character_data)
                
                # 刷新角色列表
                self._refresh_character_list()
                self.statusBar.showMessage('角色创建成功')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建角色失败：{str(e)}')
            
    def _on_character_edited(self, character_id: int):
        """角色编辑处理"""
        try:
            character = self.character_model.get(character_id)
            if not character:
                raise ValueError('找不到角色')
                
            dialog = CharacterEditorDialog(character, parent=self)
            if dialog.exec():
                character_data = dialog.get_character_data()
                
                # 更新角色
                self.character_model.update(character_id, **character_data)
                
                # 刷新角色列表
                self._refresh_character_list()
                self.statusBar.showMessage('角色更新成功')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'编辑角色失败：{str(e)}')
            
    def _on_character_deleted(self, character_id: int):
        """角色删除处理"""
        try:
            self.character_model.delete(character_id)
            
            # 刷新角色列表
            self._refresh_character_list()
            self.statusBar.showMessage('角色已删除')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'删除角色失败：{str(e)}')
            
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        file_menu.addAction('新建', self.new_novel)
        file_menu.addAction('打开', self.open_novel)
        file_menu.addAction('保存', self.save_novel)
        file_menu.addSeparator()
        
        # 添加导出子菜单
        export_menu = file_menu.addMenu('导出')
        export_menu.addAction('导出当前章节', self.export_current_chapter)
        export_menu.addAction('导出整本小说', self.export_novel)
        export_menu.addAction('导出人物关系图', self.export_character_network)
        export_menu.addAction('导出章节大纲', self.export_outlines)
        
        file_menu.addSeparator()
        file_menu.addAction('退出', self.close)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        edit_menu.addAction('生成内容', self.generate_content)
        edit_menu.addAction('更新摘要', self.update_summary)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        view_menu.addAction('版本历史', self.show_history)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具')
        tools_menu.addAction('数据库管理', self.show_database_manager)

    def show_database_manager(self):
        """显示数据库管理器"""
        try:
            DatabaseManagerDialog.show_dialog(self.db_manager, self)
        except Exception as e:
            error_msg = f"打开数据库管理器失败: {str(e)}"
            logging.error(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def export_current_chapter(self):
        """导出当前章节"""
        try:
            if not self.current_chapter_id:
                raise ValueError('请先选择要导出的章节')
                
            chapter = self.chapter_model.get(self.current_chapter_id)
            if not chapter:
                raise ValueError('找不到章节信息')
                
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出章节",
                f"第{chapter['chapter_number']}章_{chapter['title']}.txt",
                "文本文件 (*.txt)"
            )
            
            if file_path:
                # 构建导出内容
                content = [
                    f"第{chapter['chapter_number']}章 {chapter['title']}",
                    "-" * 40,
                    "章节大纲：",
                    chapter.get('outline', '暂无大纲'),
                    "-" * 40,
                    "正文：",
                    chapter['content'],
                    "-" * 40,
                    "摘要：",
                    chapter.get('summary', '暂无摘要')
                ]
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(content))
                    
                self.statusBar.showMessage(f'章节已导出到：{file_path}')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出章节失败：{str(e)}')
            
    def export_novel(self):
        """导出整本小说"""
        try:
            if not self.current_novel_id:
                raise ValueError('请先打开小说')
                
            novel = self.novel_model.get(self.current_novel_id)
            if not novel:
                raise ValueError('找不到小说信息')
                
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出小说",
                f"{novel['title']}.txt",
                "文本文件 (*.txt)"
            )
            
            if file_path:
                # 获取所有章节
                chapters = self.chapter_model.get_by_novel(self.current_novel_id)
                
                # 构建导出内容
                content = [
                    novel['title'],
                    "=" * 40,
                    "小说大纲：",
                    novel.get('outline', '暂无大纲'),
                    "=" * 40,
                    ""
                ]
                
                # 添加每个章节
                for chapter in chapters:
                    content.extend([
                        f"第{chapter['chapter_number']}章 {chapter['title']}",
                        "-" * 40,
                        "章节大纲：",
                        chapter.get('outline', '暂无大纲'),
                        "-" * 40,
                        chapter['content'],
                        "\n" + "=" * 40 + "\n"
                    ])
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n\n'.join(content))
                    
                self.statusBar.showMessage(f'小说已导出到：{file_path}')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出小说失败：{str(e)}')
            
    def export_character_network(self):
        """导出人物关系图"""
        try:
            if not self.current_novel_id:
                raise ValueError('请先打开小说')
                
            # 获取所有角色
            characters = self.character_model.get_by_novel(self.current_novel_id)
            if not characters:
                raise ValueError('当前小说没有角色信息')
                
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出人物关系图",
                "人物关系图.html",
                "HTML文件 (*.html)"
            )
            
            if file_path:
                # 构建关系图数据
                nodes = []
                for char in characters:
                    nodes.append({
                        'name': char['name'],
                        'role_type': char['role_type'],
                        'status': char['status']
                    })
                
                # 使用 pyecharts 生成关系图
                from pyecharts import options as opts
                from pyecharts.charts import Graph
                
                # 创建图表
                graph = Graph()
                graph.add(
                    "",
                    [{'name': node['name'], 'symbolSize': 50} for node in nodes],
                    [],  # 暂时不添加关系连线
                    categories=[
                        {'name': '主角'},
                        {'name': '配角'},
                        {'name': '反派'}
                    ],
                    layout='circular',
                    is_rotate_label=True,
                    label_opts=opts.LabelOpts(position='right'),
                )
                graph.set_global_opts(
                    title_opts=opts.TitleOpts(title="人物关系图")
                )
                
                # 保存图表
                graph.render(file_path)
                self.statusBar.showMessage(f'人物关系图已导出到：{file_path}')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出人物关系图失败：{str(e)}')
            
    def export_outlines(self):
        """导出章节大纲"""
        try:
            if not self.current_novel_id:
                raise ValueError('请先打开小说')
                
            novel = self.novel_model.get(self.current_novel_id)
            if not novel:
                raise ValueError('找不到小说信息')
                
            # 获取保存路径
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出大纲",
                f"{novel['title']}_大纲.txt",
                "文本文件 (*.txt)"
            )
            
            if file_path:
                # 获取所有章节
                chapters = self.chapter_model.get_by_novel(self.current_novel_id)
                
                # 构建导出内容
                content = [
                    novel['title'] + " - 大纲",
                    "=" * 40,
                    "小说整体大纲：",
                    novel.get('outline', '暂无大纲'),
                    "=" * 40,
                    "\n章节大纲：\n"
                ]
                
                # 添加每个章节的大纲
                for chapter in chapters:
                    content.extend([
                        f"第{chapter['chapter_number']}章 {chapter['title']}",
                        "-" * 40,
                        chapter.get('outline', '暂无大纲'),
                        ""
                    ])
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(content))
                    
                self.statusBar.showMessage(f'大纲已导出到：{file_path}')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出大纲失败：{str(e)}')
            
    def _on_editor_content_changed(self, content: str):
        """编辑器内容变更处理"""
        if self.current_chapter_id:
            self.statusBar.showMessage('正在编辑...')
            
    def _on_editor_save_requested(self, content: str):
        """编辑器保存请求处理"""
        try:
            if self.current_chapter_id:
                # 保存内容
                self.chapter_model.update(
                    self.current_chapter_id,
                    content=content
                )
                
                # 自动提取和更新角色
                self.character_model.auto_update_characters(
                    self.generator,
                    self.current_novel_id,
                    self.current_chapter_id,
                    content
                )
                self._refresh_character_list()
                
                # 如果启用了自动摘要，生成并保存摘要
                if self.auto_summary:
                    try:
                        summary = self.summary_system.generate_chapter_summary(content)
                        self.chapter_model.update(
                            self.current_chapter_id,
                            summary=summary
                        )
                        self.summary_text.setPlainText(summary)
                        self.statusBar.showMessage('内容、角色和摘要已自动保存')
                    except Exception as e:
                        logging.error(f"自动生成摘要失败: {e}")
                        self.statusBar.showMessage('内容和角色已保存，但自动摘要失败')
                else:
                    self.statusBar.showMessage('内容和角色已自动保存')
                    
                logging.info(f"章节 {self.current_chapter_id} 已自动保存")
        except Exception as e:
            self.statusBar.showMessage('自动保存失败')
            logging.error(f"自动保存失败: {str(e)}")
            
    def save_novel(self):
        """保存小说"""
        try:
            if self.current_novel_id and self.current_chapter_id:
                content = self.editor.save_content()
                
                # 保存内容
                self.chapter_model.update(
                    self.current_chapter_id,
                    content=content
                )
                
                # 如果启用了自动摘要，生成并保存摘要
                if self.auto_summary:
                    try:
                        summary = self.summary_system.generate_chapter_summary(content)
                        self.chapter_model.update(
                            self.current_chapter_id,
                            summary=summary
                        )
                        self.summary_text.setPlainText(summary)
                        self.statusBar.showMessage('内容和摘要已保存')
                    except Exception as e:
                        logging.error(f"自动生成摘要失败: {e}")
                        self.statusBar.showMessage('内容已保存，但自动摘要失败')
                else:
                    self.statusBar.showMessage('保存成功')
            else:
                self.new_novel()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存失败：{str(e)}')
            
    def generate_content(self):
        """生成内容"""
        try:
            if not self.current_novel_id:
                raise ValueError('请先创建或打开小说')
                
            # 收集上下文信息
            context = {}
            
            # 获取小说信息和大纲
            novel = self.novel_model.get(self.current_novel_id)
            if novel:
                context['novel_outline'] = novel.get('outline', '')
                logging.info(f"已获取小说《{novel['title']}》的大纲")
            
            # 获取当前章节信息
            if self.current_chapter_id:
                current_chapter = self.chapter_model.get(self.current_chapter_id)
                if current_chapter:
                    context['current_chapter'] = current_chapter
                    logging.info(f"已获取当前章节信息：第{current_chapter['chapter_number']}章")
                    
                    # 获取之前所有章节的摘要
                    previous_chapters = self.chapter_model.get_by_novel(
                        self.current_novel_id,
                        before_chapter=current_chapter['chapter_number']
                    )
                    if previous_chapters:
                        context['previous_summaries'] = [
                            {
                                'chapter_number': chapter['chapter_number'],
                                'summary': chapter.get('summary', '')
                            }
                            for chapter in previous_chapters
                        ]
                        logging.info(f"已获取{len(previous_chapters)}个之前章节的摘要")
            
            # 获取角色信息
            characters = self.character_model.get_by_novel(self.current_novel_id)
            if characters:
                context['characters'] = characters
                logging.info(f"已获取{len(characters)}个角色信息")
                
            logging.info("开始调用内容生成对话框...")
            
            # 显示内容生成对话框
            content = ContentGeneratorDialog.generate_content(
                self.generator,
                self,
                context
            )
            
            # 如果生成了内容，插入到当前位置并提取角色
            if content:
                cursor = self.editor.textCursor()
                cursor.insertText(content)
                
                # 自动提取和更新角色
                self.character_model.auto_update_characters(
                    self.generator,
                    self.current_novel_id,
                    self.current_chapter_id,
                    content
                )
                self._refresh_character_list()
                
                self.statusBar.showMessage('内容已插入，角色已更新')
                logging.info("内容生成和插入完成，角色已更新")
                
        except Exception as e:
            error_msg = f'生成内容失败：{str(e)}'
            logging.error(error_msg)
            QMessageBox.critical(self, '错误', error_msg)
            
    def update_summary(self):
        """更新摘要"""
        try:
            if not self.current_chapter_id:
                raise ValueError('请先选择章节')
                
            content = self.editor.toPlainText()
            if not content:
                raise ValueError('当前章节没有内容')
                
            # 获取当前摘要
            chapter = self.chapter_model.get(self.current_chapter_id)
            current_summary = chapter.get('summary', '')
                
            # 显示摘要生成对话框
            dialog = SummaryGeneratorDialog(
                self.summary_system,
                content,
                current_summary,
                self
            )
            # 连接自动摘要信号
            dialog.autoSummaryChanged.connect(self._on_auto_summary_changed)
            
            summary = dialog.generate_summary(
                self.summary_system,
                content,
                current_summary
            )
            
            # 如果生成了摘要，更新数据库
            if summary:
                self.chapter_model.update(
                    self.current_chapter_id,
                    summary=summary
                )
                self.summary_text.setPlainText(summary)
                self.statusBar.showMessage('摘要已更新')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'更新摘要失败：{str(e)}')
            
    def _on_auto_summary_changed(self, enabled: bool):
        """自动摘要设置变更处理"""
        self.auto_summary = enabled
        self.statusBar.showMessage(f'自动摘要已{"启用" if enabled else "禁用"}')
        
    def show_history(self):
        """显示版本历史"""
        try:
            if not self.current_chapter_id:
                raise ValueError('请先选择章节')
                
            # TODO: 实现显示版本历史功能
            self.statusBar.showMessage('正在加载版本历史...')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载版本历史失败：{str(e)}')
            
    def closeEvent(self, event):
        """关闭窗口事件"""
        if self.editor.is_modified():
            reply = QMessageBox.question(
                self, '确认退出',
                '是否保存当前更改？',
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_novel()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept() 

    def _on_chapter_renamed(self, chapter_id: int, new_title: str):
        """章节重命名处理"""
        try:
            # 更新章节标题
            self.chapter_model.update(
                chapter_id,
                title=new_title
            )
            self.statusBar.showMessage(f'章节已重命名为：{new_title}')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'重命名章节失败：{str(e)}')
            
    def _on_generate_outline(self):
        """AI生成大纲处理"""
        try:
            if not self.current_novel_id:
                raise ValueError('请先创建或打开小说')
                
            if self.outline_editor.is_chapter_outline():
                # 生成章节大纲
                if not self.current_chapter_id:
                    raise ValueError('请先选择章节')
                    
                chapter = self.chapter_model.get(self.current_chapter_id)
                if not chapter['content']:
                    raise ValueError('当前章节没有内容')
                    
                self.statusBar.showMessage('正在生成章节大纲...')
                outline = self.generator.generate_outline(
                    chapter_content=chapter['content'],
                    is_chapter=True
                )
                
            else:
                # 生成小说大纲
                novel = self.novel_model.get(self.current_novel_id)
                self.statusBar.showMessage('正在生成小说大纲...')
                outline = self.generator.generate_outline(
                    novel_title=novel['title'],
                    is_chapter=False
                )
                
            # 更新编辑器内容
            self.outline_editor.set_content(
                outline,
                is_chapter=self.outline_editor.is_chapter_outline()
            )
            self.statusBar.showMessage('大纲生成完成')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成大纲失败：{str(e)}') 