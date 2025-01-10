from services.file_manager.file_manager import FileManager
from services.llm_interface.query_engine import QueryEngine


class EzyMemorAI:
    def __init__(self, target_dir, vector_store_path):
        self.target_dir = target_dir
        self.vector_store_path = vector_store_path
        self._initialize()

    def _initialize(self):

        self.manager = FileManager(self.vector_store_path, "my_collection")
        print("FileManager初始化完成！")

        self.query_engine = QueryEngine()
        self.query_engine.create_chain(self.manager.vector_store.get_retriever())
        print("QAChain创建完成!")

        self.manager.load_directory(self.target_dir)

    def search(self, question: str) -> str:
        answer = self.query_engine.search(question)
        print(f"回答：{answer}")
        return answer

    def restart(self):
        print("正在重启AI...")
        self._initialize()
        print("AI重启完成！")

    def reload(self):
        print("正在重新加载AI...")
        self.manager.load_directory(self.target_dir)
        print("AI重新加载完成！")

    def reset(self):
        print("正在重置AI...")
        self.manager.reset()
        print("AI重置完成！")

    def run(self):
        """运行主循环"""
        print("AI系统已启动，可以开始提问（exit退出，restart重启，reload重新加载目录，reset重置）")
        try:
            while True:
                question = input("\n请提问：")
                if question.lower() == 'exit':
                    print("正在退出AI系统...")
                    break
                elif question.lower() == 'restart':
                    self.restart()
                    continue
                elif question.lower() == 'reload':
                    self.reload()
                    continue
                elif question.lower() == 'reset':
                    self.reset()
                    continue
                elif not question.strip():
                    print("问题不能为空，请重新输入")
                    continue

                try:
                    result = self.search(question)
                    print(result)
                except Exception as e:
                    print(f"处理问题时发生错误: {str(e)}")
                    print("请尝试重新提问或重启系统")
        except KeyboardInterrupt:
            print("\n检测到中断信号，正在退出AI系统...")

    def __del__(self):
        """析构函数，用于清理资源"""
        try:
            if hasattr(self, 'manager') and self.manager:
                self.manager.release_directory()
                self.manager = None
            if hasattr(self, 'query_engine'):
                self.query_engine = None
            print("AI系统资源已清理完毕")
        except Exception as e:
            print(f"清理资源时发生错误: {str(e)}")
