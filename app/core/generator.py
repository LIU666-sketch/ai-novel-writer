import os
from typing import Optional, Dict, Any
from google import genai
from dotenv import load_dotenv
import logging

class NovelGenerator:
    def __init__(self):
        """初始化小说生成器"""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("未找到 GEMINI_API_KEY 环境变量")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.0-flash-exp'
        
    def generate_content(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """生成内容
        
        Args:
            prompt: 用户提示词
            context: 上下文信息，包含：
                - novel_outline: 小说大纲
                - current_chapter: 当前章节信息
                - previous_summaries: 之前章节的摘要列表
                - characters: 角色列表
                
        Returns:
            生成的内容
        """
        try:
            logging.info("开始生成内容...")
            logging.info(f"原始提示词: {prompt}")
            
            # 构建完整提示词
            base_prompt = """
            你是一个专业的小说创作助手。请基于以下信息创作故事情节：

            1. 写作要求：
               - 保持情节连贯性和人物性格一致性
               - 细腻的描写和自然的对话
               - 符合小说整体风格和主题
               
            2. 标记要求：
               - 新角色首次出场用【角色名：性格特征、外貌特征、身份背景】
               - 已有角色出场用【角色名】
               - 重要情节转折用《情节》标记
               
            3. 上下文信息：
            """
            
            full_prompt = self._build_prompt(base_prompt + "\n" + prompt, context)
            logging.info(f"完整提示词: {full_prompt}")
            
            # 调用 API 生成内容
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            generated_content = response.text
            logging.info(f"内容生成成功，长度: {len(generated_content)}")
            
            return generated_content
            
        except Exception as e:
            logging.error(f"内容生成失败: {str(e)}")
            raise
            
    def _build_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建完整的提示词
        
        Args:
            prompt: 基础提示词
            context: 上下文信息
            
        Returns:
            完整的提示词
        """
        if not context:
            logging.warning("没有提供上下文信息")
            return prompt
            
        # 构建上下文提示词
        context_prompt = []
        
        # 添加小说大纲
        if "novel_outline" in context:
            context_prompt.append(f"小说大纲：\n{context['novel_outline']}")
            logging.info("已添加小说大纲到上下文")
            
        # 添加当前章节信息
        if "current_chapter" in context:
            chapter = context["current_chapter"]
            context_prompt.append(
                f"当前位置：第{chapter['chapter_number']}章 {chapter['title']}\n"
                f"章节大纲：\n{chapter.get('outline', '暂无大纲')}"
            )
            logging.info(f"已添加当前章节信息：第{chapter['chapter_number']}章")
            
        # 添加之前章节的摘要
        if "previous_summaries" in context:
            summaries = context["previous_summaries"]
            if summaries:
                # 按章节号排序
                sorted_summaries = sorted(summaries, key=lambda x: x['chapter_number'])
                context_prompt.append("之前章节摘要：")
                for chapter_summary in sorted_summaries:
                    context_prompt.append(
                        f"第{chapter_summary['chapter_number']}章：{chapter_summary['summary']}"
                    )
                logging.info(f"已添加{len(summaries)}个之前章节的摘要")
            
        # 添加角色信息
        if "characters" in context:
            characters = context["characters"]
            if characters:
                context_prompt.append("已有角色：")
                for char in characters:
                    desc = f"- {char['name']}: {char['description']}"
                    if "characteristics" in char:
                        desc += f" ({char['characteristics']})"
                    context_prompt.append(desc)
                logging.info(f"已添加{len(characters)}个角色信息")
        
        # 组合所有提示词
        full_prompt = "\n\n".join(context_prompt + [prompt])
        return full_prompt
        
    def generate_summary(self, content: str) -> str:
        """生成内容摘要
        
        Args:
            content: 需要总结的内容
            
        Returns:
            生成的摘要
        """
        prompt = f"""请以下内容生成一个简洁的摘要，突出关键情节：

{content}

摘要："""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logging.error(f"摘要生成失败: {e}")
            raise

    def generate_outline(self, novel_title: str = None, chapter_content: str = None, is_chapter: bool = False) -> str:
        """生成大纲
        
        Args:
            novel_title: 小说标题（生成小说大纲时使用）
            chapter_content: 章节内容（生成章节大纲时使用）
            is_chapter: 是否为章节大纲
            
        Returns:
            生成的大纲内容
        """
        try:
            if is_chapter and not chapter_content:
                raise ValueError("生成章节大纲需要提供章节内容")
                
            if not is_chapter and not novel_title:
                raise ValueError("生成小说大纲需要提供小说标题")
                
            if is_chapter:
                prompt = f"""
                请根据以下章节内容生成一个详细的章节大纲。大纲应包含：
                1. 本章的主要内容和目标
                2. 关键场景和对话
                3. 与整体故事的关联
                4. 需要重点描写的细节
                
                章节内容：
                {chapter_content}
                """
            else:
                prompt = f"""
                请为小说《{novel_title}》生成一个详细的整体大纲。大纲应包含：
                1. 小说的整体故事架构
                2. 主要人物及其发展轨迹
                3. 重要的情节转折点
                4. 故事的主题和中心思想
                """
                
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
            
        except Exception as e:
            logging.error(f"生成大纲失败: {str(e)}")
            raise

    def extract_characters(self, content: str) -> list:
        """从内容中提取角色信息"""
        try:
            prompt = f"""
            请分析以下故事中用【】标记的角色信息，并将其转换为严格的JSON格式。

            要求：
            1. 必须返回一个JSON数组
            2. 每个角色必须包含以下字段：
               - name (字符串): 角色名称
               - description (字符串): 性格和外貌特征
               - characteristics (字符串): 身份背景
               - role_type (字符串): 必须是 "主角"、"配角" 或 "反派" 之一

            返回格式必须严格遵循以下示例：
            [
                {{
                    "name": "李明",
                    "description": "性格开朗、正直，身材高大",
                    "characteristics": "刚毕业的大学生",
                    "role_type": "主角"
                }},
                {{
                    "name": "王婆",
                    "description": "头发花白、和蔼可亲",
                    "characteristics": "退休老人",
                    "role_type": "配角"
                }}
            ]

            注意：
            1. 返回的必须是可以直接解析的JSON格式
            2. 不要添加任何额外的说明文字
            3. 确保所有引号和逗号使用正确

            故事内容：
            {content}

            仅返回JSON数组：
            """
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # 清理响应文本，只保留JSON部分
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # 解析JSON响应
            import json
            try:
                characters = json.loads(response_text)
                if not isinstance(characters, list):
                    logging.error("AI返回的不是JSON数组")
                    return []
                    
                # 验证每个角色的字段
                valid_characters = []
                for char in characters:
                    if all(key in char for key in ['name', 'description', 'characteristics', 'role_type']):
                        valid_characters.append(char)
                        logging.info(f"成功提取角色: {char['name']} ({char['role_type']})")
                    else:
                        logging.warning(f"角色信息不完整: {char}")
                
                if valid_characters:
                    logging.info(f"共提取到 {len(valid_characters)} 个角色")
                else:
                    logging.warning("未提取到任何有效角色")
                    
                return valid_characters
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON解析失败: {str(e)}\n响应内容: {response_text}")
                return []
                
        except Exception as e:
            logging.error(f"提取角色信息失败: {str(e)}")
            return []

if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 测试生成器
    generator = NovelGenerator()
    
    # 测试上下文生成
    context = {
        "outline": "这是一个关于冒险的故事",
        "current_chapter": "第一章",
        "characters": [
            {
                "name": "张三",
                "description": "主角，勇敢的冒险家",
                "characteristics": "勇敢，正直"
            }
        ]
    }
    
    result = generator.generate_content("请继续写一个精彩的情节", context)
    print("生成结果:", result) 