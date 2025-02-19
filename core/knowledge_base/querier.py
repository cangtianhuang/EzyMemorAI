from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSerializable, RunnablePassthrough, RunnableLambda
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI

from config.config import Config


class Querier:
    """问答助手类，提供问答功能"""
    def __init__(self, vector_store):
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            base_url=Config.OPENAI_BASE_URL
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的文档问答助手，请基于检索到的文档内容，准确简洁地回答用户问题。
        回答要求：
        1. 保持简洁，尽量不超过3句话
        2. 直接给出答案，无需重复问题
        3. 引用信息来源（具体文件名与页码）
        4. 严格基于检索内容回答，不添加任何其他信息
        5. 如果找不到答案，请明确告知无法回答"""),

            ("human", "检索内容：\n{context}\n\n用户问题：\n{question}")
        ])
        self.vector_store = vector_store
        self.qa_chain = self.create_chain(self.vector_store.get_retriever())

    def create_chain(self, retriever: VectorStoreRetriever) -> RunnableSerializable:
        def runnable_print(x):
            print(x)
            return x

        self.qa_chain = (
                {
                    "question": RunnablePassthrough(),
                    "context": retriever
                }
                | RunnableLambda(runnable_print)
                | self.prompt_template
                | self.llm
                | StrOutputParser()
        )
        return self.qa_chain

    async def search(self, question: str) -> str:
        return await self.qa_chain.ainvoke(question)

    async def stream_search(self, question: str):
        async for chunk in self.qa_chain.astream(question):
            yield chunk