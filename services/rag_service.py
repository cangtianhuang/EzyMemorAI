from typing import Optional

from core.knowledge_base.querier import Querier
from core.knowledge_base.vector_db import VectorDB


class RagService:
    """RAG 服务类，提供问答功能"""
    def __init__(self, vector_db: Optional[VectorDB] = None):
        self.vector_db = VectorDB() if vector_db is None else vector_db
        self.querier = None
        self.file_service = None

    def set_file_service(self, file_service):
        self.file_service = file_service

    async def chat(self):
        if self.querier is None:
            self.querier = Querier(self.vector_db)
        while True:
            question = input("请输入问题（quit退出）：")
            if question == "quit":
                break
            answer = await self.querier.search(question)
            print(f"回答：{answer}")

    async def chat_stream(self):
        if self.querier is None:
            self.querier = Querier(self.vector_db)
        while True:
            question = input("请输入问题（quit退出）：")
            if question == "quit":
                break
            print("回答：", end="", flush=True)
            async for chunk in self.querier.stream_search(question):
                print(chunk, end="", flush=True)
            print()

    def load_directory(self, folder_path: str):
        if self.file_service:
            self.file_service.load_directory(folder_path)

    def generate_response(self, question: str):
        if self.querier is None:
            self.querier = Querier(self.vector_db)
        return self.querier.search(question)