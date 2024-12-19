import logging
from app.database.sqlite import DatabaseManager
from app.models.novel import Novel

def test_novel_model():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 1. 初始化数据库和模型
        db = DatabaseManager("test_models.db")
        db.init_database()
        novel_model = Novel(db)
        
        # 2. 测试创建小说
        print("\n测试创建小说：")
        novel_id = novel_model.create(
            title="测试小说标题",
            outline="这是一个测试用的小说大纲"
        )
        print(f"创建的小说ID: {novel_id}")
        
        # 3. 测试获取小说信息
        print("\n测试获取小说信息：")
        novel_info = novel_model.get(novel_id)
        print("小说信息:", novel_info)
        
        # 4. 测试更新小说
        print("\n测试更新小说：")
        novel_model.update(
            novel_id,
            title="更新后的标题",
            outline="更新后的大纲"
        )
        updated_info = novel_model.get(novel_id)
        print("更新后的信息:", updated_info)
        
        # 5. 测试获取小说列表
        print("\n测试获取小说列表：")
        novels = novel_model.list_all()
        print(f"小说列表（共{len(novels)}本）:", novels)
        
        # 6. 测试添加章节
        print("\n测试添加章节：")
        query = """
            INSERT INTO chapters (novel_id, chapter_number, title, content, summary)
            VALUES (?, ?, ?, ?, ?)
        """
        db.execute_query(query, (novel_id, 1, "第一章", "章节内容", "章节摘要"))
        
        # 7. 测试获取章节
        print("\n测试获取章节：")
        chapters = novel_model.get_chapters(novel_id)
        print("章节列表:", chapters)
        
        # 8. 测试添加角色
        print("\n测试添加角色：")
        query = """
            INSERT INTO characters (novel_id, name, description, characteristics)
            VALUES (?, ?, ?, ?)
        """
        db.execute_query(query, (novel_id, "测试角色", "角色描述", "角色特征"))
        
        # 9. 测试获取角色
        print("\n测试获取角色：")
        characters = novel_model.get_characters(novel_id)
        print("角色列表:", characters)
        
        # 10. 测试删除小说
        print("\n测试删除小说：")
        novel_model.delete(novel_id)
        deleted_info = novel_model.get(novel_id)
        print(f"删除后查询结果: {deleted_info}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    test_novel_model() 