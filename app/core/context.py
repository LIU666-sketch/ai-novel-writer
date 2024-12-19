from typing import Dict, Any, List, Optional
from ..database.sqlite import DatabaseManager

class ContextManager:
    def __init__(self, db_manager: DatabaseManager):
        """初始化上下文管理器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
        
    def get_novel_context(self, novel_id: int) -> Dict[str, Any]:
        """获取小说的完整上下文
        
        Args:
            novel_id: 小说ID
            
        Returns:
            包含小说信息的上下文字典
        """
        context = {}
        
        # 获取小说基本信息
        novel = self._get_novel_info(novel_id)
        if novel:
            context["outline"] = novel[2]  # outline
            context["current_chapter"] = novel[3]  # current_chapter
            
        # 获取上一章摘要
        if context.get("current_chapter", 0) > 1:
            previous_chapter = self._get_chapter_summary(
                novel_id, 
                context["current_chapter"] - 1
            )
            if previous_chapter:
                context["previous_summary"] = previous_chapter
                
        # 获取角色信息
        characters = self._get_characters(novel_id)
        if characters:
            context["characters"] = characters
            
        return context
        
    def _get_novel_info(self, novel_id: int) -> Optional[tuple]:
        """获取小说基本信息"""
        query = "SELECT * FROM novels WHERE id = ?"
        result = self.db.execute_query(query, (novel_id,))
        return result[0] if result else None
        
    def _get_chapter_summary(self, novel_id: int, chapter_number: int) -> Optional[str]:
        """获取指定章节的摘要"""
        query = """
            SELECT summary 
            FROM chapters 
            WHERE novel_id = ? AND chapter_number = ?
        """
        result = self.db.execute_query(query, (novel_id, chapter_number))
        return result[0][0] if result else None
        
    def _get_characters(self, novel_id: int) -> List[Dict[str, str]]:
        """获取小说中的所有角色信息"""
        query = "SELECT name, description, characteristics FROM characters WHERE novel_id = ?"
        result = self.db.execute_query(query, (novel_id,))
        
        characters = []
        if result:
            for row in result:
                characters.append({
                    "name": row[0],
                    "description": row[1],
                    "characteristics": row[2]
                })
        return characters
        
    def update_chapter_summary(self, novel_id: int, chapter_number: int, summary: str):
        """更新章节摘要
        
        Args:
            novel_id: 小说ID
            chapter_number: 章节号
            summary: 摘要内容
        """
        query = """
            UPDATE chapters 
            SET summary = ?
            WHERE novel_id = ? AND chapter_number = ?
        """
        self.db.execute_query(query, (summary, novel_id, chapter_number))
        
    def add_character(self, novel_id: int, name: str, description: str, 
                     characteristics: Optional[str] = None):
        """添加新角色
        
        Args:
            novel_id: 小说ID
            name: 角色名称
            description: 角色描述
            characteristics: 角色特征
        """
        query = """
            INSERT INTO characters (novel_id, name, description, characteristics)
            VALUES (?, ?, ?, ?)
        """
        self.db.execute_query(query, (novel_id, name, description, characteristics))
        
    def update_novel_progress(self, novel_id: int, current_chapter: int):
        """更新小说进度
        
        Args:
            novel_id: 小说ID
            current_chapter: 当前章节号
        """
        query = "UPDATE novels SET current_chapter = ? WHERE id = ?"
        self.db.execute_query(query, (current_chapter, novel_id)) 