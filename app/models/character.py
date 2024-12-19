from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..database.sqlite import DatabaseManager
import logging

# 配置日志
logger = logging.getLogger(__name__)

class Character:
    def __init__(self, db_manager: DatabaseManager):
        """初始化角色模型
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
        logger.info("角色模型初始化完成")
        
    def create(self, novel_id: int, name: str, description: str = None,
               characteristics: str = None, role_type: str = "配角",
               first_appearance: int = None, status: str = "活跃") -> int:
        """创建角色"""
        query = """
            INSERT INTO characters (
                novel_id, name, description, characteristics,
                role_type, first_appearance, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        result = self.db.execute_query(
            query,
            (novel_id, name, description, characteristics, 
             role_type, first_appearance, status)
        )
        return result[0][0] if result else None
        
    def extract_characters_from_content(self, generator, content: str) -> List[Dict]:
        """从内容中提取角色信息
        
        Args:
            generator: NovelGenerator实例
            content: 章节内容
            
        Returns:
            角色信息列表，每个角色包含name和description
        """
        return generator.extract_characters(content)
        
    def auto_update_characters(self, generator, novel_id: int, chapter_id: int, content: str):
        """自动更新角色信息
        
        Args:
            generator: NovelGenerator实例
            novel_id: 小说ID
            chapter_id: 章节ID
            content: 章节内容
        """
        try:
            # 提取新角色
            new_characters = self.extract_characters_from_content(generator, content)
            logger.info(f"从内容中提取到 {len(new_characters)} 个角色")
            
            # 获取现有角色
            existing_characters = self.get_by_novel(novel_id)
            existing_names = {char['name'] for char in existing_characters}
            logger.info(f"当前小说已有 {len(existing_names)} 个角色")
            
            # 添加新角色
            added_count = 0
            for char in new_characters:
                if char['name'] not in existing_names:
                    self.create(
                        novel_id=novel_id,
                        name=char['name'],
                        description=char.get('description'),
                        characteristics=char.get('characteristics'),
                        role_type=char.get('role_type', '配角'),
                        first_appearance=chapter_id,
                        status='活跃'
                    )
                    added_count += 1
                    logger.info(f"添加新角色: {char['name']}")
                    
            if added_count > 0:
                logger.info(f"成功添加 {added_count} 个新角色")
            else:
                logger.info("没有新角色需要添加")
                
        except Exception as e:
            logger.error(f"自动更新角色失败: {str(e)}")
            raise
        
    def get_character_by_name(self, novel_id: int, name: str) -> Optional[Dict]:
        """根据名称获取角色
        
        Args:
            novel_id: 小说ID
            name: 角色名称
            
        Returns:
            角色信息字典
        """
        query = "SELECT * FROM characters WHERE novel_id = ? AND name = ?"
        result = self.db.execute_query(query, (novel_id, name))
        if result:
            row = result[0]
            return {
                'id': row[0],
                'novel_id': row[1],
                'name': row[2],
                'description': row[3],
                'characteristics': row[4],
                'role_type': row[5],
                'status': row[6],
                'first_appearance': row[7]
            }
        return None
        
    def get(self, character_id: int) -> Optional[Dict]:
        """获取角色信息
        
        Args:
            character_id: 角色ID
            
        Returns:
            角色信息字典
        """
        try:
            query = """
                SELECT id, novel_id, name, description, characteristics,
                       role_type, first_appearance, status
                FROM characters
                WHERE id = ?
            """
            result = self.db.execute_query(query, (character_id,))
            
            if not result:
                logger.warning(f"未找到角色: {character_id}")
                return None
                
            character_info = {
                "id": result[0][0],
                "novel_id": result[0][1],
                "name": result[0][2],
                "description": result[0][3],
                "characteristics": result[0][4],
                "role_type": result[0][5],
                "first_appearance": result[0][6],
                "status": result[0][7]
            }
            logger.info(f"获取角色信息成功: {character_id}")
            return character_info
            
        except Exception as e:
            logger.error(f"获取角色信息失败: {e}")
            raise
            
    def update(self, character_id: int, **kwargs) -> bool:
        """更新角色信息
        
        Args:
            character_id: 角色ID
            **kwargs: 要更新的字段和值
            
        Returns:
            是否更新成功
        """
        try:
            # 检查角色是否存在
            if not self.get(character_id):
                raise ValueError(f"角色不存在: {character_id}")
            
            # 构建更新语句
            fields = []
            values = []
            valid_fields = [
                "name", "description", "characteristics",
                "role_type", "first_appearance", "status"
            ]
            
            for key, value in kwargs.items():
                if key in valid_fields:
                    fields.append(f"{key} = ?")
                    values.append(value)
                    
            if not fields:
                return False
                
            query = f"""
                UPDATE characters 
                SET {', '.join(fields)}
                WHERE id = ?
            """
            values.append(character_id)
            
            self.db.execute_query(query, tuple(values))
            logger.info(f"更新角色成功: {character_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新角色失败: {e}")
            raise
            
    def delete(self, character_id: int) -> bool:
        """删除角色
        
        Args:
            character_id: 角色ID
            
        Returns:
            是否删除成功
        """
        try:
            # 检查角色是否存在
            if not self.get(character_id):
                raise ValueError(f"角色不存在: {character_id}")
            
            # 删除角色关系
            self.db.execute_query(
                "DELETE FROM character_relationships WHERE character1_id = ? OR character2_id = ?",
                (character_id, character_id)
            )
            
            # 删除角色
            self.db.execute_query(
                "DELETE FROM characters WHERE id = ?",
                (character_id,)
            )
            logger.info(f"删除角色成功: {character_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            raise
            
    def add_relationship(self, novel_id: int, character1_id: int, character2_id: int,
                        relationship_type: str, description: str = "",
                        start_chapter: Optional[int] = None) -> int:
        """添加角色关系
        
        Args:
            novel_id: 小说ID
            character1_id: 角色1 ID
            character2_id: 角色2 ID
            relationship_type: 关系类型
            description: 关系描述
            start_chapter: 关系开始的章节ID
            
        Returns:
            新创建的关系ID
        """
        try:
            # 检查角色是否存在
            if not self.get(character1_id):
                raise ValueError(f"角色1不存在: {character1_id}")
            if not self.get(character2_id):
                raise ValueError(f"角色2不存在: {character2_id}")
            
            # 检查章节是否存在
            if start_chapter:
                chapter_check = self.db.execute_query(
                    "SELECT 1 FROM chapters WHERE id = ?",
                    (start_chapter,)
                )
                if not chapter_check:
                    raise ValueError(f"章节不存在: {start_chapter}")
            
            query = """
                INSERT INTO character_relationships (
                    novel_id, character1_id, character2_id,
                    relationship_type, description, start_chapter
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """
            result = self.db.execute_query(
                query,
                (novel_id, character1_id, character2_id,
                 relationship_type, description, start_chapter)
            )
            
            if not result:
                raise ValueError("创建角色关系失败")
                
            relationship_id = result[0][0]
            logger.info(f"创建角色关系成功，ID: {relationship_id}")
            return relationship_id
            
        except Exception as e:
            logger.error(f"创建角色关系失败: {e}")
            raise
            
    def get_relationships(self, character_id: int) -> List[Dict]:
        """获取角色的所有关系
        
        Args:
            character_id: 角色ID
            
        Returns:
            关系列表
        """
        try:
            query = """
                SELECT r.id, r.relationship_type, r.description,
                       r.start_chapter, r.character1_id, r.character2_id,
                       c1.name as character1_name, c2.name as character2_name
                FROM character_relationships r
                JOIN characters c1 ON r.character1_id = c1.id
                JOIN characters c2 ON r.character2_id = c2.id
                WHERE r.character1_id = ? OR r.character2_id = ?
            """
            result = self.db.execute_query(query, (character_id, character_id))
            
            relationships = []
            if result:
                for row in result:
                    # 确保当前角色始终是 character1
                    if row[5] == character_id:  # 如果当前角色是 character2
                        char1_id, char2_id = row[5], row[4]
                        char1_name, char2_name = row[7], row[6]
                    else:
                        char1_id, char2_id = row[4], row[5]
                        char1_name, char2_name = row[6], row[7]
                        
                    relationships.append({
                        "id": row[0],
                        "relationship_type": row[1],
                        "description": row[2],
                        "start_chapter": row[3],
                        "character1_id": char1_id,
                        "character2_id": char2_id,
                        "character1_name": char1_name,
                        "character2_name": char2_name
                    })
            
            logger.info(f"获取角色关系成功: {character_id}, 共{len(relationships)}个关系")
            return relationships
            
        except Exception as e:
            logger.error(f"获取角色关系失败: {e}")
            raise
            
    def update_relationship(self, relationship_id: int, **kwargs) -> bool:
        """更新角色关系
        
        Args:
            relationship_id: 关系ID
            **kwargs: 要更新的字段和值
            
        Returns:
            是否更新成功
        """
        try:
            # 检查关系是否存在
            query = "SELECT 1 FROM character_relationships WHERE id = ?"
            if not self.db.execute_query(query, (relationship_id,)):
                raise ValueError(f"关系不存在: {relationship_id}")
            
            # 构建更新语句
            fields = []
            values = []
            valid_fields = ["relationship_type", "description", "start_chapter"]
            
            for key, value in kwargs.items():
                if key in valid_fields:
                    fields.append(f"{key} = ?")
                    values.append(value)
                    
            if not fields:
                return False
                
            query = f"""
                UPDATE character_relationships 
                SET {', '.join(fields)}
                WHERE id = ?
            """
            values.append(relationship_id)
            
            self.db.execute_query(query, tuple(values))
            logger.info(f"更新角色关系成功: {relationship_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新角色关系失败: {e}")
            raise
            
    def delete_relationship(self, relationship_id: int) -> bool:
        """删除角色关系
        
        Args:
            relationship_id: 关系ID
            
        Returns:
            是否删除成功
        """
        try:
            query = "DELETE FROM character_relationships WHERE id = ?"
            self.db.execute_query(query, (relationship_id,))
            logger.info(f"删除角色关系成功: {relationship_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除角色关系失败: {e}")
            raise
            
    def get_by_novel(self, novel_id: int) -> list:
        """获取小说的所有角色
        
        Args:
            novel_id: 小说ID
            
        Returns:
            角色列表
        """
        query = "SELECT * FROM characters WHERE novel_id = ? ORDER BY id"
        result = self.db.execute_query(query, (novel_id,))
        return [
            {
                'id': row[0],
                'novel_id': row[1],
                'name': row[2],
                'description': row[3],
                'characteristics': row[4],
                'role_type': row[5],
                'status': row[6],
                'first_appearance': row[7]
            }
            for row in result
        ] if result else []
        
    def get_character_relationships_for_novel(self, novel_id: int) -> List[Dict]:
        """获取小说中所有的角色关系信息"""
        try:
            logger.info(f"开始获取小说(ID={novel_id})的角色关系...")
            
            query = """
                SELECT r.id, 
                       c1.name as character1_name, 
                       c2.name as character2_name,
                       r.relationship_type,
                       r.description,
                       r.start_chapter,
                       ch.chapter_number
                FROM character_relationships r
                JOIN characters c1 ON r.character1_id = c1.id
                JOIN characters c2 ON r.character2_id = c2.id
                LEFT JOIN chapters ch ON r.start_chapter = ch.id
                WHERE r.novel_id = ?
                ORDER BY r.id
            """
            result = self.db.execute_query(query, (novel_id,))
            
            relationships = []
            if result:
                for row in result:
                    chapter_info = f"第{row[6]}章" if row[6] else None
                    relationships.append({
                        'id': row[0],
                        'character1_name': row[1],
                        'character2_name': row[2],
                        'relationship_type': row[3],
                        'description': row[4],
                        'start_chapter': chapter_info
                    })
                
                # 按关系类型统计
                relation_types = {}
                for r in relationships:
                    r_type = r['relationship_type']
                    relation_types[r_type] = relation_types.get(r_type, 0) + 1
                    
                # 生成关系类型统计信息
                type_summary = ", ".join(
                    f"{t}:{c}组" for t, c in sorted(relation_types.items())
                )
                
                logger.info(f"成功获取{len(relationships)}个角色关系")
                logger.info(f"关系类型统计: {type_summary}")
                
                # 输出每个关系的详细信息
                for relation in relationships:
                    char1 = relation['character1_name']
                    char2 = relation['character2_name']
                    rel_type = relation['relationship_type']
                    desc = relation['description']
                    
                    log_msg = f"- {char1} 与 {char2}: {rel_type}"
                    if desc:
                        log_msg += f" ({desc})"
                    logger.info(log_msg)
            else:
                logger.warning("未找到任何角色关系")
            
            return relationships
            
        except Exception as e:
            error_msg = f"获取小说角色关系失败: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    def get_character_context(self, novel_id: int, character_name: str = None) -> Dict:
        """获取角色相关的上下文信息，用于AI生成内容
        
        Args:
            novel_id: 小说ID
            character_name: 角色名称（可选，如果提供则只返回该角色的信息）
            
        Returns:
            角色上下文信息：
            {
                'characters': [
                    {
                        'name': 角色名称,
                        'description': 角色描述,
                        'characteristics': 角色特征,
                        'role_type': 角色类型,
                        'status': 角色状态
                    }
                ],
                'relationships': [
                    {
                        'character1_name': 角色1名称,
                        'character2_name': 角色2名称,
                        'relationship_type': 关系类型,
                        'description': 关系描述
                    }
                ]
            }
        """
        try:
            # 获取角色信息
            if character_name:
                # 获取指定角色
                character = self.get_character_by_name(novel_id, character_name)
                characters = [character] if character else []
                if characters:
                    logger.info(f"已获取角色 '{character_name}' 的信息")
                else:
                    logger.warning(f"未找到角色: {character_name}")
            else:
                # 获取所有角色
                characters = self.get_by_novel(novel_id)
                if characters:
                    role_types = {}
                    for char in characters:
                        role_type = char['role_type']
                        role_types[role_type] = role_types.get(role_type, 0) + 1
                    role_summary = ", ".join(f"{role}:{count}人" for role, count in role_types.items())
                    logger.info(f"已获取{len(characters)}个角色信息 ({role_summary})")
                else:
                    logger.warning("未找到任何角色信息")
            
            # 获取角色关系
            relationships = self.get_character_relationships_for_novel(novel_id)
            
            # 如果指定了角色名称，只返回与该角色相关的关系
            if character_name:
                relationships = [
                    r for r in relationships
                    if character_name in (r['character1_name'], r['character2_name'])
                ]
                if relationships:
                    logger.info(f"已获取角色 '{character_name}' 的{len(relationships)}个关系")
                else:
                    logger.info(f"角色 '{character_name}' 暂无任何关系")
            else:
                if relationships:
                    # 统计关系类型
                    relation_types = {}
                    for r in relationships:
                        r_type = r['relationship_type']
                        relation_types[r_type] = relation_types.get(r_type, 0) + 1
                    type_summary = ", ".join(f"{t}:{c}组" for t, c in relation_types.items())
                    logger.info(f"已获取{len(relationships)}个角色关系 ({type_summary})")
                else:
                    logger.info("暂无任何角色关系")
            
            # 构建上下文信息
            context = {
                'characters': [
                    {
                        'name': char['name'],
                        'description': char['description'],
                        'characteristics': char['characteristics'],
                        'role_type': char['role_type'],
                        'status': char['status']
                    }
                    for char in characters
                ],
                'relationships': [
                    {
                        'character1_name': r['character1_name'],
                        'character2_name': r['character2_name'],
                        'relationship_type': r['relationship_type'],
                        'description': r['description']
                    }
                    for r in relationships
                ]
            }
            
            return context
            
        except Exception as e:
            logger.error(f"获取角色上下文失败: {e}")
            raise
        