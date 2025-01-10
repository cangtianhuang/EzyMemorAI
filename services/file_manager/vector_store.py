from typing import List
from uuid import uuid4

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models

from config.config import Config


class VectorStore:
    """向量存储管理"""

    def __init__(self, vector_store_path: str, collection_name: str):

        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_base=Config.OPENAI_BASE_URL,
            tiktoken_enabled=False,
            tiktoken_model_name=Config.TIKTOKEN_MODEL,
            check_embedding_ctx_length=False)

        self.client = QdrantClient(path=vector_store_path, prefer_grpc=True)
        self.collection_name = collection_name

        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=4096,
                    distance=models.Distance.COSINE,
                    on_disk=True),
                )

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings)

    def reset(self):
        """清除所有向量数据"""
        try:
            # 删除集合
            self.client.delete_collection(collection_name=self.collection_name)

            # 重新创建集合
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=4096,
                    distance=models.Distance.COSINE,
                    on_disk=True
                )
            )

            # 重新初始化vector_store
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=self.embeddings
            )
            return True
        except Exception as e:
            print(f"VectorStore reset failed: {str(e)}")
            return False

    def add_documents(self, documents: List[Document], document_ids: List[str] | None = None) -> List[str]:
        """添加文档到向量数据库"""
        if document_ids is None:
            for document in documents:
                if not document.id:
                    document.id = str(uuid4())

            document_ids = [doc.id for doc in documents]
        else:
            if len(documents) != len(document_ids):
                raise ValueError("The length of 'documents' and 'document_ids' must be the same.")

            for document, document_id in zip(documents, document_ids):
                document.id = document_id

        self.vector_store.add_documents(documents=documents)
        return document_ids

    def update_documents(self, documents: List[Document], document_ids: List[str]):
        """更新向量"""
        if len(documents) != len(document_ids):
            print("Mismatch between number of documents and ids")
            return
        self.delete_documents(document_ids)
        self.add_documents(documents=documents, document_ids=document_ids)
        return

    def delete_documents(self, document_ids: List[str]) -> bool:
        """删除向量"""
        if not self.vector_store.delete(ids=document_ids):
            print(f"Failed to delete documents with IDs: {document_ids}")
            return False
        return True

    def search(self, query: str, k: int = 1) -> List[Document]:
        """语义搜索"""
        return self.vector_store.similarity_search(query=query, k=k)

    def get_retriever(self, search_k: int = 3):
        return self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={'k': search_k, 'fetch_k': 10}
        )
