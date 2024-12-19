from typing import List, Dict, Optional
from datetime import datetime
from ..database.sqlite import DatabaseManager
import json
import logging

class Chapter:
    def __init__(self, db_manager: DatabaseManager):
        """初始化章节模型
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
        
    def get_by_novel(self, novel_id: int, limit: Optional[int] = None, before_chapter: Optional[int] = None) -> List[Dict]:
        """获取指定小说的章节
        
        Args:
            novel_id: 小说ID
            limit: 限制返回的章节数量
            before_chapter: 只返回此章节号之前的章节
            
        Returns:
            章节列表
        """
        try:
            query = """
                SELECT id, novel_id, chapter_number, title, content, summary, created_at
                FROM chapters
                WHERE novel_id = ?
            """
            params = [novel_id]
            
            if before_chapter is not None:
                query += " AND chapter_number < ?"
                params.append(before_chapter)
                
            query += " ORDER BY chapter_number DESC"
            
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
                
            result = self.db.execute_query(query, tuple(params))
            
            chapters = [{
                "id": row[0],
                "novel_id": row[1],
                "chapter_number": row[2],
                "title": row[3],
                "content": row[4],
                "summary": row[5],
                "created_at": row[6]
            } for row in result] if result else []
            
            logging.info(f"获取小说章节列表成功: novel_id={novel_id}, before_chapter={before_chapter}, limit={limit}, 共{len(chapters)}章")
            return chapters
            
        except Exception as e:
            logging.error(f"获取小说章节列表失败: {e}")
            raise
        
    def create(self, novel_id: int, chapter_number: int, title: str,
               content: str = "", summary: str = "") -> int:
        """创建新章节
        
        Args:
            novel_id: 小说ID
            chapter_number: 章节号
            title: 章节标题
            content: 章节内容
            summary: 章节摘要
            
        Returns:
            新创建的章节ID
        """
        try:
            # 检查章节号是否已存在
            if self._chapter_exists(novel_id, chapter_number):
                raise ValueError(f"章节号 {chapter_number} 已存在")
            
            # 检查小说是否存在
            novel_check = self.db.execute_query(
                "SELECT 1 FROM novels WHERE id = ?", 
                (novel_id,)
            )
            if not novel_check:
                raise ValueError(f"小说ID {novel_id} 不存在")
            
            query = """
                INSERT INTO chapters (novel_id, chapter_number, title, content, summary)
                VALUES (?, ?, ?, ?, ?)
            """
            result = self.db.execute_query(
                query, 
                (novel_id, chapter_number, title, content, summary)
            )
            
            if not result:
                raise ValueError("创建章节失败")
                
            chapter_id = result[0][0]
            logging.info(f"创建章节成功，ID: {chapter_id}")
            
            # 创建初始版本
            self._create_version(chapter_id, content, "初始版本")
            
            return chapter_id
            
        except Exception as e:
            logging.error(f"创建章节失败: {e}")
            raise
            
    def get(self, chapter_id: int) -> Optional[Dict]:
        """获取章节信息
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            章节信息字典
        """
        try:
            query = """
                SELECT id, novel_id, chapter_number, title, content, summary, created_at
                FROM chapters
                WHERE id = ?
            """
            result = self.db.execute_query(query, (chapter_id,))
            
            if not result:
                logging.warning(f"未找到章节: {chapter_id}")
                return None
                
            chapter_info = {
                "id": result[0][0],
                "novel_id": result[0][1],
                "chapter_number": result[0][2],
                "title": result[0][3],
                "content": result[0][4],
                "summary": result[0][5],
                "created_at": result[0][6]
            }
            logging.info(f"获取章节信息成功: {chapter_id}")
            return chapter_info
            
        except Exception as e:
            logging.error(f"获取章节信息失败: {e}")
            raise
            
    def update(self, chapter_id: int, **kwargs) -> bool:
        """更新章节信息
        
        Args:
            chapter_id: 章节ID
            **kwargs: 要更新的字段和值
            
        Returns:
            是否更新成功
        """
        try:
            # 检查章节是否存在
            chapter_info = self.get(chapter_id)
            if not chapter_info:
                raise ValueError(f"章节不存在: {chapter_id}")
            
            # 如果要更新内容，先创建新版本
            if "content" in kwargs:
                self._create_version(chapter_id, chapter_info["content"], "自动保存")
            
            # 构建更新语句
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ["title", "content", "summary"]:
                    fields.append(f"{key} = ?")
                    values.append(value)
                    
            if not fields:
                return False
                
            query = f"""
                UPDATE chapters 
                SET {', '.join(fields)}
                WHERE id = ?
            """
            values.append(chapter_id)
            
            self.db.execute_query(query, tuple(values))
            logging.info(f"更新章节成功: {chapter_id}")
            return True
            
        except Exception as e:
            logging.error(f"更新章节失败: {e}")
            raise
            
    def delete(self, chapter_id: int) -> bool:
        """删除章节
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            是否删除成功
        """
        try:
            # 检查章节是否存在
            if not self.get(chapter_id):
                raise ValueError(f"章节不存在: {chapter_id}")
            
            # 删除版本历史
            self.db.execute_query(
                "DELETE FROM chapter_versions WHERE chapter_id = ?",
                (chapter_id,)
            )
            
            # 删除章节
            self.db.execute_query(
                "DELETE FROM chapters WHERE id = ?",
                (chapter_id,)
            )
            logging.info(f"删除章节成功: {chapter_id}")
            return True
            
        except Exception as e:
            logging.error(f"删除章节失败: {e}")
            raise
            
    def get_versions(self, chapter_id: int) -> List[Dict]:
        """获取章节的版本历史
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            版本历史列表
        """
        try:
            # 检查章节是否存在
            if not self.get(chapter_id):
                raise ValueError(f"章节不存在: {chapter_id}")
            
            query = """
                SELECT id, content, comment, created_at
                FROM chapter_versions
                WHERE chapter_id = ?
                ORDER BY created_at DESC
            """
            result = self.db.execute_query(query, (chapter_id,))
            
            versions = [{
                "id": row[0],
                "content": row[1],
                "comment": row[2],
                "created_at": row[3]
            } for row in result] if result else []
            
            logging.info(f"获取版本历史成功: {chapter_id}, 共{len(versions)}个版本")
            return versions
            
        except Exception as e:
            logging.error(f"获取版本历史失败: {e}")
            raise
            
    def restore_version(self, version_id: int) -> bool:
        """恢复到指定版本
        
        Args:
            version_id: 版本ID
            
        Returns:
            是否恢复成功
        """
        try:
            # 获取版本信息
            query = """
                SELECT chapter_id, content
                FROM chapter_versions
                WHERE id = ?
            """
            result = self.db.execute_query(query, (version_id,))
            
            if not result:
                raise ValueError(f"版本不存在: {version_id}")
                
            chapter_id, content = result[0]
            
            # 更新章节内容
            success = self.update(chapter_id, content=content)
            if success:
                logging.info(f"恢复版本成功: {version_id}")
            return success
            
        except Exception as e:
            logging.error(f"恢复版本失败: {e}")
            raise
            
    def _chapter_exists(self, novel_id: int, chapter_number: int) -> bool:
        """检查章节号是否已存在"""
        query = """
            SELECT 1 FROM chapters
            WHERE novel_id = ? AND chapter_number = ?
        """
        result = self.db.execute_query(query, (novel_id, chapter_number))
        return bool(result)
        
    def _create_version(self, chapter_id: int, content: str, comment: str):
        """创建新版本"""
        query = """
            INSERT INTO chapter_versions (chapter_id, content, comment)
            VALUES (?, ?, ?)
        """
        self.db.execute_query(query, (chapter_id, content, comment))
        logging.info(f"创建版本成功: {chapter_id}") 