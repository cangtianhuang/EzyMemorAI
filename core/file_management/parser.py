import os
from datetime import datetime
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, CSVLoader, \
    UnstructuredExcelLoader, UnstructuredPowerPointLoader, UnstructuredHTMLLoader, JSONLoader, UnstructuredFileLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.config import Config


class FileParser:
    """文件解析器"""

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            add_start_index=True
        )
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            base_url=Config.OPENAI_BASE_URL
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            (
                "system", "你是一个专业的文件摘要助手，请根据以下文件名与文件内容，生成30字以内的摘要",
            ),
            ("human", "{file_name}: {content}"),
        ])

    def parse(self, file_path: str) -> dict:
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
        return {
            "content": self.splitter.split_documents(documents),
            "metadata": {
                "file_type": file_path.split('.')[-1],
                "size": os.path.getsize(file_path),
                "created_time": datetime.fromtimestamp(os.path.getctime(file_path))
            }
        }

    def brief(self, file_path: str) -> str:
        """获取文件摘要"""
        path_suffix = Path(file_path).suffix
        file_name = Path(file_path).name

        if path_suffix in [".pdf"]:
            loader = PyPDFLoader(file_path)
            pages = []
            for doc in loader.lazy_load():
                pages.append(doc)
                break
            summary_content = " ".join(page.page_content for page in pages)
        elif path_suffix in [".doc", ".docx"]:
            loader = Docx2txtLoader(file_path)
            summary_content = loader.load()[0].page_content[:100]
        elif path_suffix in [".txt"]:
            loader = TextLoader(file_path, autodetect_encoding=True)
            summary_content = loader.load()[0].page_content[:100]
        elif path_suffix in [".csv"]:
            loader = CSVLoader(file_path)
            summary_content = loader.load()[0].page_content[:100]
        else:
            print(f"暂不支持的文件类型：{file_path}")
            summary_content = ""

        if not summary_content:
            return "无法解析文件内容"

        prompt = self.prompt_template.format_messages(
            file_name=file_name,
            content=summary_content
        )
        summary = self.llm.invoke(prompt)
        return summary.content