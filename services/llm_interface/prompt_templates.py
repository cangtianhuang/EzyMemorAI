from langchain_core.prompts import PromptTemplate

_search_prompt_template = """你是一个专业的智能助手，专门用于回答基于文档的问题。请仔细阅读以下从文档中检索到的相关内容，并用它来回答用户的问题。如果无法从给定信息中找到答案，请诚实地说明你无法回答。回答时请注意以下几点：
    1.保持简洁，最多使用三个句子。
    2.直接回答问题，不需要重复问题内容。
    3.如果可能，请指出信息来自哪个具体文件。
    4.仅使用检索到的内容回答，不要添加其他信息。

    问题：{question}
    检索到的内容：{context}
    回答："""

SEARCH_TEMPLATE = PromptTemplate(template=_search_prompt_template)
