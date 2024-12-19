import logging
from app.database.sqlite import DatabaseManager
from app.models.novel import Novel
from app.models.chapter import Chapter
from app.models.character import Character

def test_character_model():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 1. 初始化数据库和模型
        db = DatabaseManager("test_models.db")
        db.init_database()
        novel_model = Novel(db)
        chapter_model = Chapter(db)
        character_model = Character(db)
        
        # 2. 创建测试小说
        print("\n创建测试小说：")
        novel_id = novel_model.create(
            title="测试小说",
            outline="测试用小说大纲"
        )
        print(f"小说ID: {novel_id}")
        
        # 3. 创建测试章节
        print("\n创建测试章节：")
        chapter_id = chapter_model.create(
            novel_id=novel_id,
            chapter_number=1,
            title="第一章",
            content="这是第一章的内容",
            summary="第一章的摘要"
        )
        print(f"章节ID: {chapter_id}")
        
        # 4. 测试创建角色
        print("\n测试创建角色：")
        # 创建主角
        protagonist_id = character_model.create(
            novel_id=novel_id,
            name="张三",
            description="主角，一个普通人",
            characteristics="勇敢，正直",
            role_type="主角",
            first_appearance=chapter_id
        )
        print(f"主角ID: {protagonist_id}")
        
        # 创建配角
        supporting_id = character_model.create(
            novel_id=novel_id,
            name="李四",
            description="主角的好友",
            characteristics="聪明，谨慎",
            role_type="配角",
            first_appearance=chapter_id
        )
        print(f"配角ID: {supporting_id}")
        
        # 5. 测试获取角色信息
        print("\n测试获取角色信息：")
        protagonist_info = character_model.get(protagonist_id)
        print("主角信息:", protagonist_info)
        
        # 6. 测试更新角色
        print("\n测试更新角色：")
        character_model.update(
            protagonist_id,
            description="主角，一个觉醒了超能力的普通人",
            characteristics="勇敢，正直，善良"
        )
        updated_info = character_model.get(protagonist_id)
        print("更新后的信息:", updated_info)
        
        # 7. 测试添加角色关系
        print("\n测试添加角色关系：")
        relationship_id = character_model.add_relationship(
            novel_id=novel_id,
            character1_id=protagonist_id,
            character2_id=supporting_id,
            relationship_type="挚友",
            description="青梅竹马的好友",
            start_chapter=chapter_id
        )
        print(f"关系ID: {relationship_id}")
        
        # 8. 测试获取角色关系
        print("\n测试获取角色关系：")
        relationships = character_model.get_relationships(protagonist_id)
        print("角色关系:", relationships)
        
        # 9. 测试更新关系
        print("\n测试更新关系：")
        character_model.update_relationship(
            relationship_id,
            relationship_type="盟友",
            description="共同对抗邪恶势力的伙伴"
        )
        updated_relationships = character_model.get_relationships(protagonist_id)
        print("更新后的关系:", updated_relationships)
        
        # 10. 测试删除关系
        print("\n测试删除关系：")
        character_model.delete_relationship(relationship_id)
        remaining_relationships = character_model.get_relationships(protagonist_id)
        print(f"剩余关系数量: {len(remaining_relationships)}")
        
        # 11. 测试删除角色
        print("\n测试删除角色：")
        character_model.delete(supporting_id)
        deleted_info = character_model.get(supporting_id)
        print(f"删除后查询结果: {deleted_info}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        raise

if __name__ == "__main__":
    test_character_model() 