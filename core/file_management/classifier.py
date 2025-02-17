from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI

from config.config import Config


class AIClassifier:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            base_url=Config.OPENAI_BASE_URL,
            model_kwargs = {"response_format": {"type": "json_object"}}
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的文件整理助手，请根据用户提供的目录结构和文件内容，设计符合最佳实践的文件组织方案：
任务目标：
1. 分析文件内容和现有结构，识别文件之间的逻辑关系
2. 创建清晰的目录层级，便于用户快速定位和管理文件
3. 保持文件原始名称，仅调整其位置

目录命名规范：
1. 使用简洁、准确的中文词汇
2. 避免特殊字符，使用下划线(_)代替空格
3. 名称长度建议在2-6个汉字之间

结构限制：
1. 最多允许三级子目录，允许多个一级目录或文件
2. 相似主题的文件应当归入同一目录
3. 避免创建只包含单个文件的目录

输出要求：
1. 使用规范的JSON格式
2. 必须包含以下字段：
   - structure: 完整的目录树结构
   - reasons: 简要说明推荐该整理方案的理由
JSON:
{{
    "structure": [
        {{
            "path": "一级目录名",
            "children": [
                {{
                    "path": "二级目录名",
                    "children": [
                        {{
                            "path": "文件名.扩展名"
                        }}
                    ]
                }},
                {{
                    "path": "文件名.扩展名"
                }}
            ]
        }},
        {{
            "path": "文件名.扩展名"
        }}
    ],
    "reasons": "更新理由"
}}

请确保：
1. 所有文件都被合理归类，不遗漏任何文件
2. 目录名称反映其包含内容的实际主题
3. 整理方案具有可扩展性，便于未来添加相关文件
4. 提供简要清晰的整理理由，向用户推荐整理方案
"""),
            ("human", "当前目录结构：\n{dir_tree}\n\n文件内容：\n{content}")
        ])

    async def classify(self, dir_tree: str, content: str) -> dict:
        """调用AI生成整理方案"""
        print("\n" + dir_tree)
        print("\n" + content)
        chain = self.prompt_template | self.llm | (lambda x: print(x) or x) | JsonOutputParser()
        try:
            return await chain.ainvoke({
                "dir_tree": dir_tree,
                "content": content[:5000]  # 限制输入长度
            })
        except Exception as e:
            print(e)
            return {
                "structure": [],
                "reasons": "AI文件整理失败"
            }
