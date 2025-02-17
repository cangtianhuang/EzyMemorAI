from typing import Any

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable
from langchain_core.vectorstores import VectorStoreRetriever


class RagService:

    search_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的文档问答助手，请基于检索到的文档内容，准确简洁地回答用户问题。
回答要求：
1. 保持简洁，尽量不超过3句话
2. 直接给出答案，无需重复问题
3. 引用信息来源（具体文件名与页码）
4. 严格基于检索内容回答，不添加任何其他信息
5. 如果找不到答案，请明确告知无法回答"""),

        ("human", "检索内容：\n{context}\n\n用户问题：\n{question}")
    ])

    def __init__(self):
        self.qa_chain = None
        self.llm = None
        self.prompt = None

    def create_chain(self, retriever: VectorStoreRetriever) -> RunnableSerializable:
        self.qa_chain = (
                {
                    "question": RunnablePassthrough(),
                    "context": retriever
                }
                | (lambda x: print(x) or x)
                | self.prompt
                | self.llm
                | StrOutputParser()
        )
        return self.qa_chain

    def search(self, question: str) -> Any:
        return self.qa_chain.invoke(question)