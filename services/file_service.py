import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

from core.file_management.organizer import FileOrganizer


class FileService:
    def __init__(self):
        self.organizer = FileOrganizer()


    async def organize(self, folder_path: str, deep_understanding: bool = False):
        task = asyncio.create_task(self.organizer.generate_dir_tree(folder_path, deep_understanding))
        old_tree, new_tree, out = await task

        print("\n当前目录结构：")
        print(old_tree)

        if not out["structure"]:
            print("\nAI文件整理失败，请重试。")
            return False
        else:
            print("\n推荐目录结构：")
            print(new_tree)

            print("\n更新理由：")
            reasons = out["reasons"]
            print(f"{reasons}\n")

        while True:
            response = input("\n你希望应用新的目录结构吗？（是/否）：").lower()
            if response in ['是', 'yes', 'y']:
                if self.organizer.execute_classify(folder_path, out):
                    print("\n目录整理成功！")
                    return True
                else:
                    print("\n目录整理失败，请重试。")
            elif response in ['否', 'no', 'n']:
                print("\n取消目录整理。")
                return False
            else:
                print("请输入'是'或'否'。")