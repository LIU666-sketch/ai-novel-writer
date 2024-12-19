import logging
from app.database.sqlite import DatabaseManager
from app.models.novel import Novel
from app.models.chapter import Chapter

def test_chapter_model():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 1. 初始化数据库和模型
        db = DatabaseManager("test_models.db")
        db.init_database()
        novel_model = Novel(db)
        chapter_model = Chapter(db)
        
        # 2. 创建测试小说
        print("\n创建测试小说：")
        novel_id = novel_model.create(
            title="测试小说",
            outline="测试用小说大纲"
        )
        print(f"小说ID: {novel_id}")
        
        # 3. 测试创建章节
        print("\n测试创建章节：")
        chapter_id = chapter_model.create(
            novel_id=novel_id,
            chapter_number=1,
            title="第一章 测试",
            content="这是第一章的内容",
            summary="第一章的摘要"
        )
        print(f"章节ID: {chapter_id}")
        
        # 4. 测试获取章节信息
        print("\n测试获取章���信息：")
        chapter_info = chapter_model.get(chapter_id)
        print("章节信息:", chapter_info)
        
        # 5. 测试更新章节
        print("\n测试更新章节：")
        chapter_model.update(
            chapter_id,
            title="第一章 修改后的标题",
            content="这是更新后的内容"
        )
        updated_info = chapter_model.get(chapter_id)
        print("更新后的信息:", updated_info)
        
        # 6. 测试获取版本历史
        print("\n测试获取版本历史：")
        versions = chapter_model.get_versions(chapter_id)
        print(f"版本历史（共{len(versions)}个版本）:")
        for version in versions:
            print(f"- 版本ID: {version['id']}")
            print(f"  内容: {version['content']}")
            print(f"  备注: {version['comment']}")
            print(f"  创建时间: {version['created_at']}")
        
        # 7. 测试恢复版本
        if versions:
            print("\n测试恢复版本：")
            first_version_id = versions[-1]['id']  # 获取最早的版本
            chapter_model.restore_version(first_version_id)
            restored_info = chapter_model.get(chapter_id)
            print("恢复后的信息:", restored_info)
        
        # 8. 测试删��章节
        print("\n测试删除章节：")
        chapter_model.delete(chapter_id)
        deleted_info = chapter_model.get(chapter_id)
        print(f"删除后查询结果: {deleted_info}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    test_chapter_model() 