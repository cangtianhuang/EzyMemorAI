from pathlib import Path
from typing import List, Dict

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document

from config.config import Config
from langchain.text_splitter import RecursiveCharacterTextSplitter

from services.file_manager import FileInfo


class FileParser:
    """文件解析器"""

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            add_start_index=True
        )

    def parse_file(self, file_path: str) -> List[Document]:
        """解析文件内容并分割成documents"""
        documents = []
        path_suffix = Path(file_path).suffix
        if path_suffix.endswith(".pdf"):
            loader = PyPDFLoader(file_path)  # 存在跨页信息丢失的问题，考虑自定义pdf加载器。
            documents.extend(loader.load())
        elif path_suffix.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            documents.extend(loader.load())
        else:
            loader = TextLoader(file_path, autodetect_encoding=True)
            documents.extend(loader.load())
        chunked_documents = self.splitter.split_documents(documents)
        return chunked_documents

    def parse_file_with_info(self, info: FileInfo) -> List[Document]:
        documents = self.parse_file(info.path)
        for document in documents:
            document.metadata["file_id"] = info.id
        return documents

    def extract_metadata(self, file_path: str) -> Dict:
        """提取文件元数据"""
        # 实现文件元数据提取逻辑
        pass
