import logging
from app.database.sqlite import DatabaseManager
from app.core.generator import NovelGenerator
from app.core.context import ContextManager

def test_basic_workflow():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 1. 初始化数据库
        db = DatabaseManager("test.db")
        db.init_database()
        
        # 2. 创建小说
        query = """
            INSERT INTO novels (title, outline, current_chapter)
            VALUES (?, ?, ?)
        """
        db.execute_query(query, ("测试小说", "这是一个测试用的武侠小说", 1))
        
        # 获取新创建的小说ID
        result = db.execute_query("SELECT last_insert_rowid()")
        novel_id = result[0][0]
        
        # 3. 添加角色
        context_manager = ContextManager(db)
        context_manager.add_character(
            novel_id=novel_id,
            name="李白",
            description="主角，潇洒不羁的剑客",
            characteristics="豪放，善饮，武艺高超"
        )
        
        # 4. 获取上下文
        context = context_manager.get_novel_context(novel_id)
        print("\n当前上下文：")
        print(context)
        
        # 5. 生成内容
        generator = NovelGenerator()
        prompt = "请以李白为主角，写一个江湖场景的开篇，要求有诗意，300字左右"
        content = generator.generate_content(prompt, context)
        print("\n生成的内容：")
        print(content)
        
        # 6. 生成摘要
        summary = generator.generate_summary(content)
        print("\n内容摘要：")
        print(summary)
        
        # 7. 保存章节
        query = """
            INSERT INTO chapters (novel_id, chapter_number, title, content, summary)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute_query(query, (novel_id, 1, "第一章", content, summary))
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    test_basic_workflow() 