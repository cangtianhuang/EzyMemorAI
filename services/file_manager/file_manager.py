from typing import List

from langchain_core.documents import Document

from services.file_manager import FileIndexer, FileParser, FileScanner, VectorStore


class FileManager:
    """文件管理器"""

    def __init__(self, store_path: str, collection_name: str):
        self.scanner = FileScanner()
        print("FileScanner初始化完成！")
        self.parser = FileParser()
        print("FileParser初始化完成！")
        self.vector_store = VectorStore(store_path, collection_name)
        print("VectorStore初始化完成！")
        self.indexer = FileIndexer(store_path + "\\file_index.db")
        print("FileIndexer初始化完成！")

    def load_directory(self, path: str):
        """加载目录并检查一致性"""
        print("开始加载目录...")
        self.scanner.initialize_handler(path, self.indexer, self.parser, self.vector_store)
        self.scanner.start_watching(path)

        print(f"目录加载完成: {path}")

        print("所有文件索引如下：")
        print(self.indexer.print_all_tables())

    def release_directory(self):
        self.scanner.stop_watching()

    def reset(self):
        """重置"""
        self.indexer.reset()
        self.vector_store.reset()
        self.scanner.reset()

    def search(self, query: str) -> List[Document]:
        """搜索接口"""
        return self.vector_store.search(query)
