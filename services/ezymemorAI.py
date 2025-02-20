import asyncio

from core.knowledge_base.document_db import DocumentDB
from core.knowledge_base.vector_db import VectorDB
from services.file_service import FileService
from services.rag_service import RagService


class EzyMemorAI():
    def __init__(self):
        vector_db = VectorDB()
        document_db = DocumentDB()
        self.file_service = FileService(vector_db=vector_db, document_db=document_db)
        self.rag_service = RagService(vector_db=vector_db)

        self.file_service.set_rag_service(self.rag_service)
        self.rag_service.set_file_service(self.file_service)


    async def run(self):
        await WelcomePage.run(self.file_service, self.rag_service)

class WelcomePage:
    @staticmethod
    def show():
            print("\n=== 欢迎使用 EzyMemorAI —— 您的个人文件助手AI ===")
            print("1. 智能聊天")
            print("2. 智能文件整理")
            print("3. 文件夹监听")
            print("4. 设置")
            print("q. 退出")

    @staticmethod
    async def run(file_service, rag_service):
        while True:
            WelcomePage.show()
            choice = input("请输入选项：")

            if choice == "1":
                await ChatPage.run(rag_service)
            elif choice == "2":
                await FileSortingPage.run(file_service)
            elif choice == "3":
                await MonitoringPage.run(file_service)
            elif choice == "4":
                await SettingsPage.run(file_service)
            elif choice == "q":
                print("退出程序。")
                break
            else:
                print("无效选项，请重新选择。")

class ChatPage:
    @staticmethod
    async def run(rag_service):
        while True:
            print("\n=== 智能聊天 ===")
            print("1. 载入文件夹")
            print("2. 启动RAG聊天")
            print("3. 启动RAG流式聊天")
            print("b. 返回上一级")

            choice = input("请输入选项：")

            if choice == "1":
                path = input("请输入要加载的文件夹路径：")
                rag_service.load_directory(path)
            elif choice == "2":
                await rag_service.chat()
            elif choice == "3":
                await rag_service.chat_stream()
            elif choice == "b":
                break
            else:
                print("无效选项，请重新选择。")

class FileSortingPage:
    @staticmethod
    async def run(file_service):
        while True:
            print("\n=== 智能文件整理 ===")
            print("1. 显示文件树")
            print("2. 快速整理文件夹")
            print("3. 深度整理文件夹")
            print("b. 返回上一级")

            choice = input("请输入选项：")

            if choice == "1":
                path = input("请输入要显示文件树的文件夹路径：")
                file_service.show_directory_tree(path)
            elif choice == "2":
                path = input("请输入要整理的文件夹路径：")
                await file_service.organize(path, False)
                print("文件整理完成。")
            elif choice == "3":
                path = input("请输入要组织的文件夹路径：")
                await file_service.organize(path, True)
                print("文件整理完成。")
            elif choice == "b":
                break
            else:
                print("无效选项，请重新选择。")

class MonitoringPage:
    @staticmethod
    async def run(file_service):
        while True:
            print("\n=== 文件夹监听 ===")
            print("1. 列出所有监听文件夹")
            print("2. 开始监听文件夹")
            print("3. 停止监听文件夹")
            print("b. 返回上一级")

            choice = input("请输入选项：")

            if choice == "1":
                file_service.show_monitored_paths()
            elif choice == "2":
                path = input("请输入要监听的文件夹路径：")
                file_service.start_watching(path)
                print("文件夹监听已启动。")
            elif choice == "3":
                path = input("请输入要停止监听的文件夹路径：")
                file_service.stop_watching(path)
                print("文件夹监听已停止。")
            elif choice == "b":
                break
            else:
                print("无效选项，请重新选择。")

class SettingsPage:
    @staticmethod
    async def run(file_service):
        while True:
            print("\n=== 设置 ===")
            print("1. 显示文档数据库")
            print("2. 设置文件夹路径")
            print("3. 设置模型")
            print("b. 返回上一级")

            choice = input("请输入选项：")

            if choice == "1":
                file_service.show_document_db()
            elif choice == "2":
                print("未实现。")
            elif choice == "3":
                print("未实现。")
            elif choice == "b":
                break
            else:
                print("无效选项，请重新选择。")