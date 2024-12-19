from typing import List, Dict, Any, Optional
from .generator import NovelGenerator
from ..database.sqlite import DatabaseManager
import logging

class SummarySystem:
    def __init__(self, db_manager: DatabaseManager, generator: NovelGenerator):
        """初始化摘要系统
        
        Args:
            db_manager: 数据库管理器实例
            generator: AI生成器实例
        """
        self.db = db_manager
        self.generator = generator
        
    def generate_chapter_summary(self, content: str) -> str:
        """生成章节摘要
        
        Args:
            content: 章节内容
            
        Returns:
            章节摘要
        """
        return self.generator.generate_summary(content)
        
    def update_novel_outline(self, novel_id: int) -> str:
        """更新小说大纲
        
        Args:
            novel_id: 小说ID
            
        Returns:
            更新后的大纲
        """
        try:
            # 获取所有章节摘要
            summaries = self._get_all_chapter_summaries(novel_id)
            if not summaries:
                return ""
                
            # 构建提示词
            prompt = self._build_outline_prompt(summaries)
            
            # 生成新大纲
            new_outline = self.generator.generate_content(prompt)
            
            # 更新数据库
            self._update_outline_in_db(novel_id, new_outline)
            
            return new_outline
            
        except Exception as e:
            logging.error(f"更新大纲失败: {e}")
            raise
            
    def extract_key_points(self, chapter_id: int) -> List[str]:
        """提取章节关键情节点
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            关键情节点列表
        """
        try:
            # 获取章节内容
            content = self._get_chapter_content(chapter_id)
            if not content:
                return []
                
            prompt = f"""请从以下内容中提取3-5个关键情节点，每个情节点用一句话描述：

{content}

关键情节："""
            
            result = self.generator.generate_content(prompt)
            # 将结果按行分割并清理
            key_points = [point.strip() for point in result.split('\n') if point.strip()]
            return key_points
            
        except Exception as e:
            logging.error(f"提取关键情节点失败: {e}")
            raise
            
    def _get_all_chapter_summaries(self, novel_id: int) -> List[Dict[str, Any]]:
        """获取小说所有章节的摘要"""
        query = """
            SELECT chapter_number, summary
            FROM chapters
            WHERE novel_id = ?
            ORDER BY chapter_number
        """
        result = self.db.execute_query(query, (novel_id,))
        return [{"chapter": row[0], "summary": row[1]} for row in result] if result else []
        
    def _build_outline_prompt(self, summaries: List[Dict[str, Any]]) -> str:
        """构建更新大纲的提示词"""
        summary_text = "\n".join([
            f"第{s['chapter']}章：{s['summary']}"
            for s in summaries
        ])
        
        return f"""基于以下各章节摘要，生成一个完整的小说大纲，需要：
1. 突出主要情节发展
2. 体现人物关系变化
3. 注意情节的连贯性

章节摘要：
{summary_text}

请生成大纲："""
        
    def _update_outline_in_db(self, novel_id: int, outline: str):
        """更新数据库中的小说大纲"""
        query = "UPDATE novels SET outline = ? WHERE id = ?"
        self.db.execute_query(query, (outline, novel_id))
        
    def _get_chapter_content(self, chapter_id: int) -> Optional[str]:
        """获取章节内容"""
        query = "SELECT content FROM chapters WHERE id = ?"
        result = self.db.execute_query(query, (chapter_id,))
        return result[0][0] if result else None 