import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

from config.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VectorDB:
    """向量数据库，用于存储文档向量并执行语义搜索"""
    def __init__(self, vector_path: str = "./core/knowledge_base/.vector", collection_name: str = "my_collection"):
        # 初始化嵌入模型
        self.embedding = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_base=Config.OPENAI_BASE_URL,
            tiktoken_enabled=False,
            tiktoken_model_name=Config.TIKTOKEN_MODEL,
            check_embedding_ctx_length=False)

        # 初始化 Qdrant 客户端
        logger.info(f"初始化向量存储 '{collection_name}'")
        self.client = QdrantClient(path=vector_path, prefer_grpc=True)
        self.collection_name = collection_name

        # 检查并创建集合
        if not self.client.collection_exists(collection_name=self.collection_name):
            logger.info(f"集合 '{self.collection_name}' 不存在，正在创建新集合。")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=4096,
                    distance=Distance.COSINE,
                    on_disk=True
                )
            )

        # 初始化 QdrantVectorStore
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embedding
        )
        logger.info(f"向量存储 '{collection_name}' 初始化成功")

    def add_documents(self, documents: List[Document], document_ids: Optional[List[str]] = None) -> List[str]:
        """添加文档到向量数据库"""
        logger.info(f"添加 {len(documents)} 个文档至集合 {self.collection_name}")
        if document_ids:
            if len(documents) != len(document_ids):
                logger.error("文档和文档ID的长度必须相同")
                raise ValueError("文档和文档ID的长度必须相同")
            self.vector_store.add_documents(documents=documents, ids=document_ids)
        else:
            document_ids = self.vector_store.add_documents(documents=documents)
        logger.info(f"成功添加 {len(documents)} 个文档至集合 {self.collection_name}")
        return document_ids

    def update_documents(self, documents: List[Document], document_ids: List[str]):
        """更新向量"""
        logger.info(f"更新 {len(documents)} 个文档至集合 {self.collection_name}")
        if len(documents) != len(document_ids):
            logger.error("文档和文档ID的长度必须相同")
            raise ValueError("文档和文档ID的长度必须相同")
        # 删除旧文档并添加新文档
        self.delete_documents(document_ids)
        self.vector_store.add_documents(documents=documents, ids=document_ids)
        logger.info(f"成功更新 {len(documents)} 个文档至集合 {self.collection_name}")
        return

    def delete_documents(self, document_ids: List[str]) -> bool:
        """删除向量"""
        logger.info(f"删除集合 {self.collection_name} 中的 {len(document_ids)} 个文档")
        if not self.vector_store.delete(ids=document_ids):
            logger.error(f"删除集合 {self.collection_name} 中的文档失败")
            return False
        logger.info(f"成功删除集合 {self.collection_name} 中的 {len(document_ids)} 个文档")
        return True

    def search(self, query: str, k: int = 1) -> List[Document]:
        """语义搜索"""
        logger.info(f"为查询 '{query}' 执行语义搜索，k={k}")
        results = self.vector_store.similarity_search(query=query, k=k)
        logger.info(f"为查询 '{query}' 找到 {len(results)} 个结果")
        return results

    def get_retriever(self, search_type: str = "mmr", search_k: int = 3, fetch_k: int = 10,
                      score_threshold: Optional[float] = None, filter: Optional[dict] = None, **kwargs):
        """获取检索器"""
        logger.info(f"创建检索器，search_type='{search_type}', search_k={search_k}, fetch_k={fetch_k}, score_threshold={score_threshold}, filter={filter}")
        # 构造搜索参数
        search_kwargs = {
            'k': search_k,
            'fetch_k': fetch_k if search_type == "mmr" else None,
            'score_threshold': score_threshold,
            'filter': filter,
            **kwargs  # 合并其他自定义参数
        }
        # 根据检索类型返回检索器
        if search_type == "mmr":
            return self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs=search_kwargs
            )
        elif search_type == "similarity":
            return self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs
            )
        else:
            raise ValueError(f"不支持的 search_type: {search_type}。支持的类型为 'mmr' 和 'similarity'。")