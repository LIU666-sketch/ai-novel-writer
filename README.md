# AI 小说生成器 (AI Novel Writer)

基于 Gemini API 开发的智能小说创作助手，支持文风模仿、智能写作和长篇小说创作。这是一个面向小说创作者的智能写作工具，添加了数据库进行长文记录。它能帮助作者更高效地进行创作，同时保持文章的连贯性和人物的一致性。

## 项目特点

- 🤖 **AI 驱动**：基于 Google Gemini API，提供智能写作建议和内容生成
- 📝 **专业编辑器**：集成现代化的文本编辑器，支持实时保存和版本控制
- 👥 **角色管理**：智能角色提取和关系管理，自动维护角色信息的一致性
- 📊 **数据可视化**：直观的数据管理界面，支持表格化展示和关系图可视化
- 🔄 **版本控制**：内置版本控制系统，支持内容回滚和历史追踪
- 🎯 **场景规划**：支持大纲创作和章节规划，帮助把控整体剧情走向
- 💾 **数据安全**：本地数据存储，支持数据备份和恢复

## 技术栈

- **前端框架**：PyQt6
- **数据存储**：SQLite
- **AI 模型**：Google Gemini API
- **开发语言**：Python 3.8+

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- pip 包管理器
- Google Gemini API 密钥

### 安装步骤

1. 克隆项目到本地：
```bash
git clone https://github.com/yourusername/ai-novel-writer.git
cd ai-novel-writer
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并添加以下内容：
```
GEMINI_API_KEY=your_api_key_here
```

4. 运行应用：
```bash
python main.py
```

## 功能特点

### 已实现功能
- [x] 基础编辑器功能
  - 创建和管理小说
  - 章节管理（添加、删除、切换章节）
  - 自动保存（每30秒）
  - 内容修改状态跟踪
  - 版本历史记录

- [x] AI 内容生成
  - 基于 Gemini API 的智能内容生成
  - 可自定义提示词
  - 内容预览和确认
  - 支持生成 2000 字的内容
  - 智能文风模仿
  - 上下文关联分析

- [x] 数据管理
  - SQLite 数据库存储
  - 小说基本信息管理
  - 章节内容管理
  - 版本历史记录
  - 数据库管理界面
    - 表格化展示和编辑数据
    - 角色关系可视化
    - 预定义关系类型管理
    - 数据备份和恢复

### 计划实现功能
- [] 实现多模型生成

- [ ] 大纲管理
  - 小说整体大纲
  - 章节大纲
  - 大纲智能生成
  - 情节线索追踪
  - 冲突设置建议

- [ ] 角色管理
  - 角色信息管理
  - 角色关系图
  - 角色特征追踪
  - 角色成长曲线
  - 性格特征分析

- [ ] 智能摘要系统
  - 章节自动摘要
  - 情节发展追踪
  - 上下文关联分析
  - 关键事件提取
  - 伏笔追踪系统

- [ ] 写作辅助功能
  - 智能写作建议
  - 情节连贯性检查
  - 人物性格一致性检查
  - 文风分析与建议
  - 写作质量评估

## 使用方法

### 基本界面
- 左侧面板：写作设置和角色管理
- 中央区域：文本编辑
- 右侧面板：大纲和摘要
- 数据库管理：工具菜单 -> 数据库管理

### 常用操作
- 新建文档：文件 -> 新建
- 保存文档：文件 -> 保存
- 生成内容：编辑 -> 生成
- 查看历史：视图 -> 版本历史
- 管理数据：工具 -> 数据库管理


## 开发说明

### 项目结构
```
novel-writer/
├── app/                  # 核心功能模块
│   ├── core/            # 核心功能
│   │   ├── generator.py # AI 生成器
│   │   ├── context.py   # 上下文管理
│   │   └── summary.py   # 摘要系统
│   ├── models/          # 数据模型
│   │   ├── novel.py     # 小说模型
│   │   ├── chapter.py   # 章节模型
│   │   └── character.py # 角色模型
│   ├── database/        # 数据库管理
│   │   ├── sqlite.py    # SQLite 管理器
│   │   └── queries.py   # SQL 查询
│   └── utils/           # 工具函数
├── ui/                  # Qt界面模块
│   ├── windows/        # 窗口类
│   ├── widgets/        # 自定义组件
│   └── resources/      # UI资源文件
└── tests/              # 测试用例
```

### 数据库结构

#### 小说表 (novels)
```sql
CREATE TABLE novels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 章节表 (chapters)
```sql
CREATE TABLE chapters (
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
);
```

#### 角色表 (characters)
```sql
CREATE TABLE characters (
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
);
```

#### 角色关系表 (character_relationships)
```sql
CREATE TABLE character_relationships (
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
);
```

#### 关系类型表 (relationship_types)
```sql
CREATE TABLE relationship_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 章节版本表 (chapter_versions)
```sql
CREATE TABLE chapter_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter_id INTEGER,
    content TEXT,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chapter_id) REFERENCES chapters(id)
);
```

### 模型功能说明

#### Novel 模型
- 小说基本信息管理
- 章节管理
- 版本控制
- 导出功能
- 数据备份

#### Chapter 模型
- 章节内容管理
- 版本历史
- 自动摘要生成
- 大纲关联
- 角色追踪

#### Character 模型
- 角色信息管理
- 角色关系管理
- 角色发展追踪
- 状态管理
- 自动角色提取
- 关系类型预定义
- 角色图谱生成

## 贡献指南

我们欢迎所有形式的贡献，包括但不限于：

- 提交问题和建议
- 改进文档
- 修复 bug
- 添加新功能
- 优化代码

### 贡献步骤

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目作者：[Liufenyi]
- 邮箱：[liufy696@gmail.com]
- GitHub：[LIU666-sketch]

## 致谢

感谢所有为这个项目做出贡献的开发者们！

- Google Gemini API 团队
- PyQt 开发团队
- 所有项目贡献者
```

