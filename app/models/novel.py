from typing import List, Dict, Optional
from datetime import datetime
from ..database.sqlite import DatabaseManager
import json
import logging

class Novel:
    def __init__(self, db_manager: DatabaseManager):
        """初始化小说模型
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
        
    def create(self, title: str, outline: str = "") -> int:
        """创建新小说
        
        Args:
            title: 小说标题
            outline: 小说大纲（可选）
            
        Returns:
            新创建的小说ID
        """
        try:
            query = """
                INSERT INTO novels (title, outline, current_chapter)
                VALUES (?, ?, ?)
            """
            result = self.db.execute_query(query, (title, outline, 1))
            
            if not result:
                raise ValueError("创建小说失败")
                
            novel_id = result[0][0]
            logging.info(f"创建小说成功，ID: {novel_id}")
            return novel_id
            
        except Exception as e:
            logging.error(f"创建小说失败: {e}")
            raise
            
    def get(self, novel_id: int) -> Optional[Dict]:
        """获取小说信息
        
        Args:
            novel_id: 小说ID
            
        Returns:
            小说信息字典
        """
        try:
            query = "SELECT * FROM novels WHERE id = ?"
            result = self.db.execute_query(query, (novel_id,))
            
            if not result:
                logging.warning(f"未找到小说: {novel_id}")
                return None
                
            novel_info = {
                "id": result[0][0],
                "title": result[0][1],
                "outline": result[0][2],
                "current_chapter": result[0][3]
            }
            logging.info(f"获取小说信息成功: {novel_id}")
            return novel_info
            
        except Exception as e:
            logging.error(f"获取小说信息失败: {e}")
            raise
            
    def update(self, novel_id: int, **kwargs) -> bool:
        """更新小说信息
        
        Args:
            novel_id: 小说ID
            **kwargs: 要更新的字段和值
            
        Returns:
            是否更新成功
        """
        try:
            # 检查小说是否存在
            if not self.get(novel_id):
                raise ValueError(f"小说不存在: {novel_id}")
            
            # 构建更新语句
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ["title", "outline", "current_chapter"]:
                    fields.append(f"{key} = ?")
                    values.append(value)
                    
            if not fields:
                return False
                
            query = f"""
                UPDATE novels 
                SET {', '.join(fields)}
                WHERE id = ?
            """
            values.append(novel_id)
            
            self.db.execute_query(query, tuple(values))
            logging.info(f"更新小说成功: {novel_id}")
            return True
            
        except Exception as e:
            logging.error(f"更新小说信息失败: {e}")
            raise
            
    def delete(self, novel_id: int) -> bool:
        """删除小说
        
        Args:
            novel_id: 小说ID
            
        Returns:
            是否删除成功
        """
        try:
            # 检查小说是否存在
            if not self.get(novel_id):
                raise ValueError(f"小说不存在: {novel_id}")
            
            # 首先删除相关的章节和角色
            self.db.execute_query("DELETE FROM chapters WHERE novel_id = ?", (novel_id,))
            self.db.execute_query("DELETE FROM characters WHERE novel_id = ?", (novel_id,))
            
            # 删除小说
            self.db.execute_query("DELETE FROM novels WHERE id = ?", (novel_id,))
            logging.info(f"删除小说成功: {novel_id}")
            return True
            
        except Exception as e:
            logging.error(f"删除小说失败: {e}")
            raise
            
    def list_all(self) -> List[Dict]:
        """获取所有小说列表
        
        Returns:
            小说信息列表
        """
        try:
            query = "SELECT * FROM novels ORDER BY id DESC"
            result = self.db.execute_query(query)
            
            novels = [{
                "id": row[0],
                "title": row[1],
                "outline": row[2],
                "current_chapter": row[3]
            } for row in result] if result else []
            
            logging.info(f"获取小说列表成功，共{len(novels)}本")
            return novels
            
        except Exception as e:
            logging.error(f"获取小说列表失败: {e}")
            raise
            
    def get_chapters(self, novel_id: int) -> List[Dict]:
        """获取小说的所有章节
        
        Args:
            novel_id: 小说ID
            
        Returns:
            章节信息列表
        """
        try:
            # 检查小说是否存在
            if not self.get(novel_id):
                raise ValueError(f"小说不存在: {novel_id}")
            
            query = """
                SELECT id, chapter_number, title, summary, created_at
                FROM chapters
                WHERE novel_id = ?
                ORDER BY chapter_number
            """
            result = self.db.execute_query(query, (novel_id,))
            
            chapters = [{
                "id": row[0],
                "chapter_number": row[1],
                "title": row[2],
                "summary": row[3],
                "created_at": row[4]
            } for row in result] if result else []
            
            logging.info(f"获取章节列表成功: {novel_id}, 共{len(chapters)}章")
            return chapters
            
        except Exception as e:
            logging.error(f"获取章节列表失败: {e}")
            raise
            
    def get_characters(self, novel_id: int) -> List[Dict]:
        """获取小说的所有角色
        
        Args:
            novel_id: 小说ID
            
        Returns:
            角色信息列表
        """
        try:
            # 检查小说是否存在
            if not self.get(novel_id):
                raise ValueError(f"小说不存在: {novel_id}")
            
            query = """
                SELECT id, name, description, characteristics
                FROM characters
                WHERE novel_id = ?
            """
            result = self.db.execute_query(query, (novel_id,))
            
            characters = [{
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "characteristics": row[3]
            } for row in result] if result else []
            
            logging.info(f"获取角色列表成功: {novel_id}, 共{len(characters)}个角色")
            return characters
            
        except Exception as e:
            logging.error(f"获取角色列表失败: {e}")
            raise
            
    def get_by_title(self, title: str) -> Optional[Dict]:
        """根据标题获取小说信息
        
        Args:
            title: 小说标题
            
        Returns:
            小说信息字典，如果不存在返回 None
        """
        try:
            query = """
                SELECT id, title, outline, current_chapter
                FROM novels
                WHERE title = ?
            """
            result = self.db.execute_query(query, (title,))
            
            if not result:
                return None
                
            return {
                "id": result[0][0],
                "title": result[0][1],
                "outline": result[0][2],
                "current_chapter": result[0][3]
            }
        except Exception as e:
            logging.error(f"根据标题获取小说失败: {e}")
            raise 