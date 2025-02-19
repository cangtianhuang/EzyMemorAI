import asyncio
from typing import Optional

from core.file_management.organizer import FileOrganizer
from core.file_management.parser import FileParser
from core.file_management.processor import FileProcessor
from core.file_management.watcher import FileWatcher
from core.knowledge_base.document_db import DocumentDB
from core.knowledge_base.vector_db import VectorDB


class FileService:
    """文件服务类，提供文件整理功能"""
    def __init__(self, vector_db: Optional[VectorDB] = None, document_db: Optional[DocumentDB] = None):
        self.parser = FileParser()
        self.organizer = FileOrganizer()
        self.watcher = FileWatcher()
        self.vector_db = VectorDB() if vector_db is None else vector_db
        self.document_db = DocumentDB() if document_db is None else document_db
        self.processor = FileProcessor(vector_db=self.vector_db, document_db=self.document_db, parser=self.parser)
        self.rag_service = None

    def set_rag_service(self, rag_service):
        self.rag_service = rag_service


    async def organize(self, folder_path: str, deep_understanding: bool = False):
        task = asyncio.create_task(self.organizer.generate_classify(folder_path, deep_understanding))
        old_tree, new_tree, classify_out = await task

        print("\n当前目录结构：")
        print(old_tree)

        if not classify_out["structure"]:
            print("\nAI文件整理失败，请重试。")
            return False
        else:
            print("\n推荐目录结构：")
            print(new_tree)

            print("\n更新理由：")
            reasons = classify_out["reasons"]
            print(f"{reasons}\n")

        while True:
            response = input("\n你希望应用新的目录结构吗？（是/否）：").lower()
            if response in ['是', 'yes', 'y']:
                # 检查是否正在监控, 如果是, 先停止监控
                is_watching =  self.check_watching(folder_path)
                if is_watching:
                    self.stop_watching(folder_path)
                succeed = self.organizer.execute_classify(folder_path, classify_out)
                if is_watching:
                    self.start_watching(folder_path)
                if succeed:
                    print("\n目录整理成功！")
                    return True
                else:
                    print("\n目录整理失败，请重试。")
            elif response in ['否', 'no', 'n']:
                print("\n取消目录整理。")
                return False
            else:
                print("请输入'是'或'否'。")

    def show_directory_tree(self, folder_path: str):
        dir_tree, file_paths = self.organizer.get_dir_tree(folder_path)
        print(dir_tree)
        return dir_tree

    def organize_directory_tree(self, folder_path: str, deep_understanding: bool = False):
        old_tree, new_tree, classify_out = asyncio.run(self.organizer.generate_classify(folder_path, deep_understanding))
        return old_tree, new_tree, classify_out

    def apply_directory_tree(self, folder_path: str, classify_out):
        return self.organizer.execute_classify(folder_path, classify_out)

    def get_monitored_paths(self):
        return self.watcher.get_all_watched_paths()

    def add_monitored_path(self, folder_path: str):
        return self.watcher.start_watching(folder_path, self.processor)

    def remove_monitored_path(self, folder_path: str):
        return self.watcher.stop_watching(folder_path)

    def start_watching(self, folder_path: str):
        self.watcher.start_watching(folder_path, self.processor)

    def stop_watching(self, folder_path: str):
        self.watcher.stop_watching(folder_path)

    def check_watching(self, folder_path: str) -> bool:
        return self.watcher.check_watching(folder_path)

    def show_document_db(self):
        self.document_db.print_all_tables()
        self.document_db.print_table_stats()

    def load_directory(self, folder_path: str):
        self.processor.load_directory(folder_path)