import json
import sqlite3
from typing import List

from tabulate import tabulate


class DocumentDB:
    def __init__(self, db_file: str = "./core/knowledge_base/docs.db"):
        self.db_file = db_file
        self._create_tables()

    def _create_tables(self):
        """创建表结构"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            # 创建文件索引表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_index (
                    id TEXT PRIMARY KEY,
                    path TEXT UNIQUE,
                    name TEXT,
                    is_directory INTEGER,
                    file_type TEXT,
                    size INTEGER,
                    document_ids TEXT
                )
            ''')
            # 创建文档ID与文件ID的关联表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS doc_file_mapping (
                    document_id TEXT,
                    file_id TEXT,
                    FOREIGN KEY(file_id) REFERENCES file_index(id),
                    PRIMARY KEY(document_id, file_id)
                )
            ''')
            # 为document_id创建索引以提高查询效率
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_document_id 
                ON doc_file_mapping(document_id)
            ''')
            conn.commit()

    def add_file(self, file_id: str, path: str, name: str, is_directory: bool,
                 file_type: str, size: int, document_ids: List[str]):
        """添加文件索引"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO file_index (id, path, name, is_directory, file_type, size, document_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, path, name, int(is_directory), file_type, size, json.dumps(document_ids)))
            for doc_id in document_ids:
                cursor.execute('''
                    INSERT INTO doc_file_mapping (document_id, file_id)
                    VALUES (?, ?)
                ''', (doc_id, file_id))
            conn.commit()

    def update_file(self, file_id: str, path: str = None, name: str = None, is_directory: str = None,
                    file_type: str = None, size: int = None, document_ids: List[str] = None):
        """更新文件索引"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            if path is not None:
                updates.append("path = ?")
                params.append(path)
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if is_directory is not None:
                updates.append("is_directory = ?")
                params.append(int(is_directory))
            if file_type is not None:
                updates.append("file_type = ?")
                params.append(file_type)
            if size is not None:
                updates.append("size = ?")
                params.append(size)
            if document_ids is not None:
                updates.append("document_ids = ?")
                params.append(document_ids)
            params.append(file_id)
            cursor.execute(f'''
                UPDATE file_index
                SET {', '.join(updates)}
                WHERE id = ?
            ''', params)

            if document_ids is not None:
                # 删除旧的映射
                cursor.execute('''
                    DELETE FROM doc_file_mapping
                    WHERE file_id = ?
                ''', (file_id,))
                # 添加新的映射
                for doc_id in document_ids:
                    cursor.execute('''
                        INSERT INTO doc_file_mapping (document_id, file_id)
                        VALUES (?, ?)
                    ''', (doc_id, file_id))
            conn.commit()

    def delete_file(self, file_id: str):
        """删除文件索引"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM file_index
                WHERE id = ?
            ''', (file_id,))
            cursor.execute('''
                DELETE FROM doc_file_mapping
                WHERE file_id = ?
            ''', (file_id,))
            conn.commit()

    def check_file_exists(self, file_id: str):
        """检查文件是否存在"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM file_index
                WHERE id = ?
            ''', (file_id,))
            return cursor.fetchone()[0] > 0

    def check_document_exists(self, document_id: str):
        """检查文档是否存在"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM doc_file_mapping
                WHERE document_id = ?
            ''', (document_id,))
            return cursor.fetchone()[0] > 0

    def get_files_by_document_id(self, document_id: str):
        """根据文档ID获取文件列表"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_id FROM doc_file_mapping
                WHERE document_id = ?
            ''', (document_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_documents_by_file_id(self, file_id: str):
        """根据文件ID获取文档列表"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT document_id FROM doc_file_mapping
                WHERE file_id = ?
            ''', (file_id,))
            return [row[0] for row in cursor.fetchall()]

    def print_all_tables(self):
        """打印所有表的内容"""
        with sqlite3.connect(self.db_file) as conn:
            # 设置行工厂以返回字典格式的结果
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 打印 file_index 表内容
            print("\n=== 文件索引表 ===")
            cursor.execute("SELECT * FROM file_index")
            rows = cursor.fetchall()
            self._print_table(rows)

            # 打印 doc_file_mapping 表内容
            print("\n=== 文档-文件映射表 ===")
            cursor.execute("SELECT * FROM doc_file_mapping")
            rows = cursor.fetchall()
            self._print_table(rows)

    def _print_table(self, rows):
        """辅助函数：打印表格内容"""
        if not rows:
            print("无记录")
        else:
            try:
                print(tabulate([dict(row) for row in rows], headers='keys', tablefmt='grid'))
            except ImportError:
                for row in rows:
                    for key, value in dict(row).items():
                        print(f"{key}: {value}")

    def print_table_stats(self):
        """获取表的统计信息"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            # 获取 file_index 表的记录数
            cursor.execute("SELECT COUNT(*) FROM file_index")
            file_count = cursor.fetchone()[0]
            # 获取 doc_file_mapping 表的记录数
            cursor.execute("SELECT COUNT(*) FROM doc_file_mapping")
            mapping_count = cursor.fetchone()[0]
            # 获取唯一文档ID的数量
            cursor.execute("SELECT COUNT(DISTINCT document_id) FROM doc_file_mapping")
            unique_docs = cursor.fetchone()[0]

            print("\n=== 数据统计 ===")
            print(f"文件索引数: {file_count}")
            print(f"文档映射数: {mapping_count}")
            print(f"唯一文档数: {unique_docs}")