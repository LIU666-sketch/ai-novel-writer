import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        """初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        logger.info(f"数据库管理器初始化: {db_path}")
        
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
            
    def init_database(self):
        """初始化数据库表结构"""
        try:
            logger.info("开始初始化数据库...")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 创建小说表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS novels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建章节表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    novel_id INTEGER NOT NULL,
                    chapter_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    summary TEXT,
                    outline TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
                )
            """)
            
            # 创建角色表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    novel_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    characteristics TEXT,
                    role_type TEXT,
                    first_appearance INTEGER,
                    status TEXT DEFAULT '活跃',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                    FOREIGN KEY (first_appearance) REFERENCES chapters(id) ON DELETE SET NULL
                )
            """)
            
            # 创建角色关系表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS character_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    novel_id INTEGER NOT NULL,
                    character1_id INTEGER NOT NULL,
                    character2_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    description TEXT,
                    start_chapter INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                    FOREIGN KEY (character1_id) REFERENCES characters(id) ON DELETE CASCADE,
                    FOREIGN KEY (character2_id) REFERENCES characters(id) ON DELETE CASCADE,
                    FOREIGN KEY (start_chapter) REFERENCES chapters(id) ON DELETE SET NULL
                )
            """)
            
            # 创建关系类型表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationship_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 插入预定义的关系类型
            predefined_types = [
                ('家族', '父子', '父亲与儿子的关系'),
                ('家族', '母子', '母亲与儿子的关系'),
                ('家族', '父女', '父亲与女儿的关系'),
                ('家族', '母女', '母亲与女儿的关系'),
                ('家族', '兄弟', '兄弟关系'),
                ('家族', '姐妹', '姐妹关系'),
                ('家族', '夫妻', '已婚夫妻关系'),
                ('家族', '恋人', '恋爱关系'),
                ('社会', '朋友', '朋友关系'),
                ('社会', '敌人', '敌对关系'),
                ('社会', '竞争', '竞争关系'),
                ('社会', '合作', '合作关系'),
                ('师徒', '师傅', '师傅对徒弟的关系'),
                ('师徒', '徒弟', '徒弟对师傅的关系'),
                ('职场', '上级', '工作中的上级关系'),
                ('职场', '下级', '工作中的下级关系'),
                ('职场', '同事', '工作中的平级关系')
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO relationship_types (category, type, description)
                VALUES (?, ?, ?)
            """, predefined_types)
            
            conn.commit()
            logger.info("数据库初始化成功")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
        finally:
            conn.close()
            
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()
                result = cursor.lastrowid if cursor.lastrowid else True
            else:
                result = cursor.fetchall()
                
            return result
            
        except Exception as e:
            logger.error(f"SQL执行失败: {query} - {e}")
            raise
        finally:
            conn.close()
            
    def get_table_structure(self, table_name: str) -> List[str]:
        """获取表结构
        
        Args:
            table_name: 表名
            
        Returns:
            字段名列表
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            logger.info(f"获取表结构成功: {table_name}")
            return columns
            
        except Exception as e:
            logger.error(f"获取表结构失败: {table_name} - {e}")
            raise
        finally:
            conn.close()
            
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> int:
        """插入记录
        
        Args:
            table_name: 表名
            data: 要插入的数据字典
            
        Returns:
            新记录的ID
        """
        try:
            # 过滤掉值为None的字段
            filtered_data = {k: v for k, v in data.items() if v is not None}
            
            # 构建SQL语句
            columns = ', '.join(filtered_data.keys())
            placeholders = ', '.join(['?' for _ in filtered_data])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            # 执行插入
            result = self.execute_query(query, tuple(filtered_data.values()))
            logger.info(f"插入记录成功: {table_name}")
            return result
            
        except Exception as e:
            logger.error(f"插入记录失败: {table_name} - {e}")
            raise
            
    def update_record(self, table_name: str, record_id: int, data: Dict[str, Any]) -> bool:
        """更新记录
        
        Args:
            table_name: 表名
            record_id: 记录ID
            data: 要更新的数据字典
            
        Returns:
            是否更新成功
        """
        try:
            # 过滤掉值为None的字段
            filtered_data = {k: v for k, v in data.items() if v is not None}
            
            # 添加更新时间
            filtered_data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 构建SQL语句
            set_clause = ', '.join([f"{k} = ?" for k in filtered_data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
            
            # 执行更新
            values = list(filtered_data.values()) + [record_id]
            self.execute_query(query, tuple(values))
            logger.info(f"更新记录成功: {table_name} ID={record_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新记录失败: {table_name} ID={record_id} - {e}")
            raise
            
    def delete_record(self, table_name: str, record_id: int) -> bool:
        """删除记录
        
        Args:
            table_name: 表名
            record_id: 记录ID
            
        Returns:
            是否删除成功
        """
        try:
            query = f"DELETE FROM {table_name} WHERE id = ?"
            self.execute_query(query, (record_id,))
            logger.info(f"删除记录成功: {table_name} ID={record_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除记录失败: {table_name} ID={record_id} - {e}")
            raise 