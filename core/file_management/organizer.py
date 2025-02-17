import errno
import os
import stat
import shutil
import tempfile
from pathlib import Path

from langchain_core.output_parsers import JsonOutputParser

from core.file_management.classifier import AIClassifier
from core.file_management.parser import FileParser


class FileOrganizer:
    """文件整理器"""
    def __init__(self):
        # self.vector_db = vector_db
        self.classifier = AIClassifier()
        self.parser = FileParser()

    async def generate_dir_tree(self, directory: str, understand_content: bool = False) -> tuple[str, str, dict]:
        """
        生成目录树
        :param directory: 目录路径
        :param understand_content:  是否理解文件内容
        :return:  (原目录树, 推荐目录树, AI分类结果)
        """
        directory = Path(directory)
        dir_tree = [str(directory.name) + "/"] # 保留根目录
        content = []
        file_paths = {}

        # 递归遍历目录
        def _walk_directory(current_path: Path, prefix: str = "", is_last: bool = True) -> None:
            items = sorted(current_path.iterdir(),
                           key=lambda x: (not x.is_dir(), x.name))

            for i, item in enumerate(items):
                is_last = (i == len(items) - 1)
                current_prefix = prefix + ("└── " if is_last else "├── ")
                next_prefix = prefix + ("    " if is_last else "│   ")

                if item.is_dir():
                    dir_tree.append(f"{current_prefix}{item.name}/")
                    _walk_directory(item, next_prefix, is_last)
                else:
                    dir_tree.append(f"{current_prefix}{item.name}")
                    rel_path = item.relative_to(directory)
                    file_paths[item.name] = str(rel_path)
                    if understand_content:
                        summary = self.parser.brief(str(item.resolve()))
                        content.append(f"{item.name}: {summary}")
                    else:
                        content.append(f"{item.name}")

        _walk_directory(directory)

        dir_tree = "\n".join(dir_tree)
        content = "\n".join(content)

        # 异步调用AI分类器
        # classify_out =  await self.classifier.classify(dir_tree, content)
        ai_message = """{\n    "structure": [\n        {\n            "path": "导师相关",\n            "children": [\n                {\n                    "path": "导师双选",\n                    "children": [\n                        {\n                            "path": "国优导师简介0930.pdf"\n                        },\n                        {\n                            "path": "导师双选操作说明（导师端）.pdf"\n                        }\n                    ]\n                }\n            ]\n        },\n        {\n            "path": "校友相关",\n            "children": [\n                {\n                    "path": "校友联络",\n                    "children": [\n                        {\n                            "path": "1_北京理工大学计算机学院2024届校友联络大使名单（本科）.docx"\n                        }\n                    ]\n                }\n            ]\n        },\n        {\n            "path": "奖学金相关",\n            "children": [\n                {\n                    "path": "国家奖学金",\n                    "children": [\n                        {\n                            "path": "附件3：北京理工大学计算机学院2024年国家奖学金证明材料清单.docx"\n                        },\n                        {\n                            "path": "附件4：计算机学院2024年国家奖学金证明材料要求.docx"\n                        },\n                        {\n                            "path": "附件6：硕士研究生国家奖学金学生汇总表.xls"\n                        }\n                    ]\n                },\n                {\n                    "path": "奖学金申报",\n                    "children": [\n                        {\n                            "path": "附件1：学生版：线上申请说明(2024版).docx"\n                        },\n                        {\n                            "path": "附件2：幸福北理【研究生奖学金申报系统】使用说明.docx"\n                        }\n                    ]\n                },\n                {\n                    "path": "附件7：研究生高水平科技创新竞赛列表.pdf"\n                }\n            ]\n        },\n        {\n            "path": "毕业生相关",\n            "children": [\n                {\n                    "path": "本专科",\n                    "children": [\n                        {\n                            "path": "北京地区普通高等教育本专科毕业生登记表.pdf"\n                        },\n                        {\n                            "path": "本专科毕业生登记表填写说明.pdf"\n                        }\n                    ]\n                },\n                {\n                    "path": "团组织关系",\n                    "children": [\n                        {\n                            "path": "团组织关系转出证明_模板.docx"\n                        },\n                        {\n                            "path": "附件5：出国境申请保留团组织关系模板.docx"\n                        }\n                    ]\n                }\n            ]\n        }\n    ],\n    "reasons": "根据文件内容的主题进行分类整理，将导师相关文件归为导师相关目录，校友相关文件归为校友相关目录，奖学金相关文件按不同类型细分到奖学金相关目录下的子目录，毕业生相关文件也按照本专科和团组织关系等不同类型分别归入毕业生相关目录下的子目录，这样的结构便于快速定位和管理文件，也具有较好的可扩展性。"\n}"""
        classify_out = JsonOutputParser().invoke(ai_message)

        proposed_dir_tree = [str(directory.name) + "/"]
        file_mapping = {}

        # 递归处理分类结果
        def _process_structure(structure: dict, current_path: Path, prefix: str = "", is_last: bool = True) -> None:
            path = structure["path"]
            is_dir = "children" in structure

            current_prefix = prefix + ("└── " if is_last else "├── ")
            proposed_dir_tree.append(f"{current_prefix}{path}{'/' if is_dir else ''}")

            new_path = current_path / path
            if not is_dir and path in file_paths:
                file_mapping[file_paths[path]] = str(new_path.relative_to(directory))
            elif is_dir:
                next_prefix = prefix + ("    " if is_last else "│   ")
                for i, child in enumerate(structure["children"]):
                    is_child_last = (i == len(structure["children"]) - 1)
                    _process_structure(child, new_path, next_prefix, is_child_last)

        # 处理一级目录（移动至根目录下）
        for i, structure in enumerate(classify_out["structure"]):
            is_last = (i == len(classify_out["structure"]) - 1)
            _process_structure(structure, directory, "", is_last)

        for file_name, file_path in file_paths.items():
            if file_path not in file_mapping:
                file_mapping[file_path] = file_name

        proposed_dir_tree = "\n".join(proposed_dir_tree)
        classify_out["file_mapping"] = file_mapping
        classify_out["source_dir"] = directory.resolve()

        return dir_tree, proposed_dir_tree, classify_out

    def execute_classify(self, directory: str, classify_out: dict) -> bool:
        """
        执行整理方案
        :param directory:  目录路径
        :param classify_out:  AI分类结果
        :return: bool 是否整理成功
        """
        file_mapping = classify_out["file_mapping"]
        source_dir = Path(directory)
        temp_dir = Path(directory) / f".temp_{source_dir.name}"
        if temp_dir.exists():
            count = 1
            while temp_dir.exists():
                temp_dir = Path(directory) / f".temp_{source_dir.name}_{count}"
                count += 1

        try:
            # 移动文件至临时目录
            os.makedirs(temp_dir, exist_ok=True)
            os.chmod(temp_dir, stat.S_IRWXU)

            # 在临时目录中创建与new_path相同的路径结构
            for old_path, new_path in file_mapping.items():
                old_path = source_dir / old_path
                new_path = temp_dir / new_path
                if os.path.exists(old_path):
                    os.makedirs(new_path.parent, exist_ok=True)
                    try:
                        os.chmod(new_path.parent, stat.S_IRWXU)
                        shutil.move(old_path, new_path)
                    except PermissionError:
                        print(f"无法移动文件: {old_path} - 权限不足，尝试更改权限...")
                        os.chmod(old_path, stat.S_IRWXU)
                        shutil.move(old_path, new_path)

            # 将未映射的文件移动到临时目录的根目录
            for root, dirs, files in os.walk(source_dir):
                if Path(root) == temp_dir:
                    dirs[:] = []
                    continue
                for file in files:
                    file_path = Path(root) / file
                    if file_path.exists() and str(file_path.relative_to(source_dir)) not in file_mapping:
                        new_path = temp_dir / file
                        new_path = self._get_unique_path(new_path)
                        try:
                            shutil.move(file_path, new_path)
                        except PermissionError:
                            print(f"无法移动文件: {file_path} - 权限不足，尝试更改权限...")
                            os.chmod(file_path, stat.S_IRWXU)
                            shutil.copy2(file_path, new_path)

            # 清空原目录
            for item in os.listdir(source_dir):
                item_path = source_dir / item
                if item_path == temp_dir:
                    continue
                if os.path.isdir(item_path):
                    os.chmod(item_path, stat.S_IRWXU)
                    shutil.rmtree(item_path)
                else:
                    os.chmod(item_path, stat.S_IRWXU)
                    os.remove(item_path)

            # 将临时目录中的文件移回原目录，保持结构
            for item in os.listdir(temp_dir):
                temp_path = temp_dir / item
                new_path = source_dir / item
                try:
                    shutil.move(temp_path, new_path)
                except PermissionError:
                    print(f"无法移动路径: {temp_path} - 权限不足，尝试更改权限...")
                    os.chmod(new_path, stat.S_IRWXU)
                    shutil.move(temp_path, new_path)

            shutil.rmtree(temp_dir)
            return True
        except Exception as e:
            print(f"整理失败: {str(e)}")
            return False

    def _get_unique_path(self, path: Path) -> Path:
        """获取唯一的文件路径，通过添加数字后缀避免文件名冲突"""
        if not path.exists():
            return path

        counter = 1
        while True:
            new_path = path.parent / f"{path.stem}_{counter}{path.suffix}"
            if not new_path.exists():
                return new_path
            counter += 1


    # async def process_file(self, file_path: str, dir_tree: str) -> dict:
    #     """文件处理全流程"""
    #     # 解析文件
    #     parsed = self.parser.parse(file_path)
    #
    #     # 存储到向量数据库
    #     self.vector_db.upsert(parsed["content"])
    #
    #     # 获取AI整理方案
    #     ai_response = await self.classifier.generate_new_path(
    #         dir_tree=dir_tree,
    #         content=parsed["content"][0].page_content  # 取第一段内容
    #     )
    #
    #     # 执行文件操作
    #     new_path = self._safe_move(file_path, ai_response["new_path"])
    #
    #     return {
    #         "original": file_path,
    #         "new_path": new_path,
    #         "metadata": parsed["metadata"],
    #         "ai_reason": ai_response["reason"]
    #     }
