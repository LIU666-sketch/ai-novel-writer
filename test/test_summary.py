import logging
from app.database.sqlite import DatabaseManager
from app.core.generator import NovelGenerator
from app.core.summary import SummarySystem

def test_summary_system():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 1. 初始化组件
        db = DatabaseManager("test.db")
        generator = NovelGenerator()
        summary_system = SummarySystem(db, generator)
        
        # 2. 创建测试小说和章节
        # 创建小说
        query = """
            INSERT INTO novels (title, outline, current_chapter)
            VALUES (?, ?, ?)
        """
        db.execute_query(query, ("测试小说", "初始大纲", 2))
        
        # 获取小说ID
        result = db.execute_query("SELECT last_insert_rowid()")
        novel_id = result[0][0]
        
        # 创建两个测试章节
        chapters_data = [
            (novel_id, 1, "第一章", "月光如水，李白独坐江畔，手中的酒壶映照着星光。远处传来阵阵琴声，一个蒙面剑客缓步走来...", "李白在江边遇到神秘剑客"),
            (novel_id, 2, "第二章", "剑光如虹，李白与神秘人的对决惊动了整个江湖。那人的剑法竟与传说中的荒古剑派如出一辙...", "李白与神秘剑客的惊天对决")
        ]
        
        for chapter in chapters_data:
            query = """
                INSERT INTO chapters (novel_id, chapter_number, title, content, summary)
                VALUES (?, ?, ?, ?, ?)
            """
            db.execute_query(query, chapter)
            
        # 3. 测试更新大纲
        print("\n测试更新大纲：")
        new_outline = summary_system.update_novel_outline(novel_id)
        print(f"新大纲：\n{new_outline}")
        
        # 4. 测试提取关键情节点
        print("\n测试提取关键情节点：")
        # 获取第二章的ID
        result = db.execute_query(
            "SELECT id FROM chapters WHERE novel_id = ? AND chapter_number = ?",
            (novel_id, 2)
        )
        chapter_id = result[0][0]
        
        key_points = summary_system.extract_key_points(chapter_id)
        print("关键情节点：")
        for i, point in enumerate(key_points, 1):
            print(f"{i}. {point}")
            
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    test_summary_system() 