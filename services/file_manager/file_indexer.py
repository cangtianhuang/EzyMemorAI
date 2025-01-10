import json
import os
import sqlite3
from datetime import datetime
from enum import Enum
from typing import List, Tuple, Optional, Dict

from services.file_manager import FileInfo
from services.file_manager.file_info import FileType


class SearchType(Enum):
    """搜索类型枚举"""
    FILENAME = "filename"  # 按文件名搜索
    CONTENT_TYPE = "content_type"  # 按文件类型搜索
    DATE_RANGE = "date_range"  # 按日期范围搜索
    SIZE_RANGE = "size_range"  # 按文件大小范围搜索
    DOCUMENT_ID = "document_id"  # 按文档ID搜索
    FILE_ID = "file_id"  # 按文件ID搜索
    PATH = "path"  # 按路径搜索
    METADATA = "metadata"  # 按元数据搜索


class FileIndexer:
    """文件索引管理"""

    def __init__(self, db_file: str):
        self.db_file = db_file
        self._initialize_db()

    def _initialize_db(self):
        """初始化数据库"""
        if not os.path.exists(self.db_file):
            # 数据库文件不存在，创建新表
            self._create_table()
        else:
            # 检查数据库的合法性
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT 1 FROM file_index LIMIT 1')
            except sqlite3.Error:
                # 如果有任何错误，重新创建表
                self._create_table()

    def _create_table(self):
        """创建表结构"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            # 创建文件索引表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_index (
                    id TEXT PRIMARY KEY,
                    path TEXT,
                    name TEXT,
                    is_directory INTEGER,
                    file_type TEXT,
                    size INTEGER,
                    created_at TEXT,
                    modified_at TEXT,
                    metadata TEXT,
                    document_ids TEXT
                )
            ''')

            # 创建文档ID与文件ID的关联表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS doc_file_mapping (
                    document_id TEXT,
                    file_id TEXT,
                    FOREIGN KEY(file_id) REFERENCES file_index(id),
                    PRIMARY KEY(document_id, file_id)
                )
            ''')

            # 为document_id创建索引以提高查询效率
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_document_id 
                ON doc_file_mapping(document_id)
            ''')
            conn.commit()

    def reset(self):
        """清除所有数据,保留表结构"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                # 先删除doc_file_mapping表中的数据
                cursor.execute('DELETE FROM doc_file_mapping')
                # 然后删除file_index表中的数据
                cursor.execute('DELETE FROM file_index')
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"FileIndexer reset failed: {str(e)}")
            return False

    def create_indexes(self, files: List[FileInfo]):
        """创建文件索引"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            # 开始事务
            conn.execute('BEGIN')
            try:
                for file in files:
                    # 插入文件信息
                    cursor.execute('''
                        INSERT OR REPLACE INTO file_index 
                        (id, path, name, is_directory, file_type, size, created_at, modified_at, metadata, document_ids)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (file.id, file.path, file.name, int(file.is_directory), file.file_type.value,
                          file.size, file.created_at.isoformat(), file.modified_at.isoformat(),
                          json.dumps(file.metadata), json.dumps(file.document_ids)))

                    # 更新文档ID映射
                    if file.document_ids:
                        # 删除旧的映射关系
                        cursor.execute('DELETE FROM doc_file_mapping WHERE file_id = ?', (file.id,))
                        # 插入新的映射关系
                        for doc_id in file.document_ids:
                            cursor.execute('''
                                INSERT OR REPLACE INTO doc_file_mapping (document_id, file_id)
                                VALUES (?, ?)
                            ''', (doc_id, file.id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def update_indexes(self, files: List[FileInfo]):
        """批量更新文件索引"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN')
            try:
                for file in files:
                    # 更新文件信息
                    cursor.execute('''
                        UPDATE file_index 
                        SET path=?, name=?, is_directory=?, file_type=?, 
                            size=?, created_at=?, modified_at=?, 
                            metadata=?, document_ids=?
                        WHERE id=?
                    ''', (file.path, file.name, int(file.is_directory),
                          file.file_type.value, file.size,
                          file.created_at.isoformat(),
                          file.modified_at.isoformat(),
                          json.dumps(file.metadata),
                          json.dumps(file.document_ids),
                          file.id))

                    # 更新文档ID映射
                    if file.document_ids:
                        cursor.execute('DELETE FROM doc_file_mapping WHERE file_id = ?',
                                       (file.id,))
                        cursor.executemany('''
                            INSERT INTO doc_file_mapping (document_id, file_id)
                            VALUES (?, ?)
                        ''', [(doc_id, file.id) for doc_id in file.document_ids])
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def update_file_paths(self, path_updates: List[Tuple[str, str]]):
        """
        仅更新文件的路径
        Args:
            path_updates: List[Tuple[str, str]] - 列表of (file_id, new_path) 元组
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN')
            try:
                # 批量更新路径和文件名
                cursor.executemany('''
                    UPDATE file_index 
                    SET path = ?,
                        name = ?
                    WHERE id = ?
                ''', [(new_path, os.path.basename(new_path), file_id)
                      for file_id, new_path in path_updates])

                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def update_file_path(self, file_id: str, new_path: str):
        """
        更新单个文件的路径
        Args:
            file_id: str - 文件ID
            new_path: str - 新的文件路径
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN')
            try:
                # 更新路径和文件名
                cursor.execute('''
                    UPDATE file_index 
                    SET path = ?,
                        name = ?
                    WHERE id = ?
                ''', (new_path, os.path.basename(new_path), file_id))

                if cursor.rowcount == 0:
                    raise ValueError(f"File ID {file_id} not found")

                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def delete_indexes(self, files: List[FileInfo]):
        """批量删除文件索引"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN')
            try:
                # 批量删除文件索引
                file_ids = [file.id for file in files]
                # 使用参数化查询构建IN子句
                placeholders = ','.join('?' * len(file_ids))

                # 删除文档ID映射
                cursor.execute(f'''
                    DELETE FROM doc_file_mapping 
                    WHERE file_id IN ({placeholders})
                ''', file_ids)

                # 删除文件索引
                cursor.execute(f'''
                    DELETE FROM file_index 
                    WHERE id IN ({placeholders})
                ''', file_ids)

                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def delete_index(self, file_id: str) -> List[str]:
        """
        删除单个文件的索引
        Args:
            file_id: str - 文件ID
        Returns:
            List[str] - 被删除的文档ID列表
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            conn.execute('BEGIN')
            try:
                # 首先获取关联的文档ID
                cursor.execute('''
                    SELECT document_id 
                    FROM doc_file_mapping 
                    WHERE file_id = ?
                ''', (file_id,))
                document_ids = [row[0] for row in cursor.fetchall()]

                # 删除文档ID映射
                cursor.execute('''
                    DELETE FROM doc_file_mapping 
                    WHERE file_id = ?
                ''', (file_id,))

                # 删除文件索引
                cursor.execute('''
                    DELETE FROM file_index 
                    WHERE id = ?
                ''', (file_id,))

                if cursor.rowcount == 0:
                    raise ValueError(f"File ID {file_id} not found")

                conn.commit()
                return document_ids
            except Exception as e:
                conn.rollback()
                raise e

    def _rows_to_file_infos(self, rows: List[Tuple]) -> List[FileInfo]:
        """将数据库结果行转换为FileInfo对象列表"""
        file_infos = []
        for row in rows:
            file_info = self._row_to_file_info(row)
            if file_info:
                file_infos.append(file_info)
        return file_infos

    def _row_to_file_info(self, row: Tuple) -> Optional[FileInfo]:
        """将数据库结果行转换为FileInfo对象"""
        if not row:
            return None
        try:
            file_info = FileInfo(
                path=row[1],
                id=row[0],
                name=row[2],
                is_directory=bool(row[3]),
                file_type=FileType(row[4]),
                size=row[5],
                created_at=datetime.fromisoformat(row[6]) if row[6] else None,
                modified_at=datetime.fromisoformat(row[7]) if row[7] else None,
                metadata=json.loads(row[8]) if row[8] else {},
                document_ids=json.loads(row[9]) if row[9] else [],
                _skip_existence_check=True
            )
            return file_info
        except Exception as e:
            print(f"Error converting row to FileInfo: {e}")
            return None

    def get_file_ids_by_document_ids(self, document_ids: List[str]) -> List[str]:
        """快速获取与文档ID关联的文件ID列表"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(document_ids))
            cursor.execute(f'''
                SELECT DISTINCT file_id 
                FROM doc_file_mapping 
                WHERE document_id IN ({placeholders})
            ''', document_ids)
            return [row[0] for row in cursor.fetchall()]

    def get_document_ids_by_file_id(self, file_id: str) -> List[str]:
        """获取指定文件ID关联的所有文档ID"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT document_id 
                FROM doc_file_mapping 
                WHERE file_id = ?
            ''', (file_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_id_by_path(self, path: str) -> str:
        """根据文件路径返回对应的文件ID"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM file_index WHERE path = ?', (path,))
            result = cursor.fetchone()
            return result[0] if result else None

    def search_by_document_ids(self, document_ids: List[str]) -> List[FileInfo]:
        """按文档ID搜索文件信息"""
        file_ids = self.get_file_ids_by_document_ids(document_ids)
        return self.search_by_file_ids(file_ids)

    def search_by_file_ids(self, file_ids: List[str]) -> List[FileInfo]:
        """按文件ID搜索文件信息"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(file_ids))
            cursor.execute(f'''
                SELECT * FROM file_index 
                WHERE id IN ({placeholders})
            ''', file_ids)
            return self._rows_to_file_infos(cursor.fetchall())

    def search_by_filename(self, pattern: str, exact_match: bool = False) -> List[FileInfo]:
        """按文件名搜索

        Args:
            pattern: 搜索模式
            exact_match: 是否精确匹配
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            if exact_match:
                cursor.execute('SELECT * FROM file_index WHERE name = ?', (pattern,))
            else:
                cursor.execute('SELECT * FROM file_index WHERE name LIKE ?', (f'%{pattern}%',))
            return self._rows_to_file_infos(cursor.fetchall())

    def search_by_type(self, file_type: str) -> List[FileInfo]:
        """按文件类型搜索"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM file_index WHERE file_type = ?', (file_type,))
            return self._rows_to_file_infos(cursor.fetchall())

    def search_by_date_range(self,
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             date_field: str = 'modified_at') -> List[FileInfo]:
        """按日期范围搜索

        Args:
            start_date: 开始日期
            end_date: 结束日期
            date_field: 日期字段 ('created_at' 或 'modified_at')
        """
        if date_field not in ['created_at', 'modified_at']:
            raise ValueError("date_field must be either 'created_at' or 'modified_at'")

        query = f'SELECT * FROM file_index WHERE 1=1'
        params = []

        if start_date:
            query += f' AND {date_field} >= ?'
            params.append(start_date.isoformat())
        if end_date:
            query += f' AND {date_field} <= ?'
            params.append(end_date.isoformat())

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return self._rows_to_file_infos(cursor.fetchall())

    def search_by_size_range(self,
                             min_size: Optional[int] = None,
                             max_size: Optional[int] = None) -> List[FileInfo]:
        """按文件大小范围搜索（单位：字节）"""
        query = 'SELECT * FROM file_index WHERE 1=1'
        params = []

        if min_size is not None:
            query += ' AND size >= ?'
            params.append(min_size)
        if max_size is not None:
            query += ' AND size <= ?'
            params.append(max_size)

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return self._rows_to_file_infos(cursor.fetchall())

    def search_by_path(self, path_pattern: str, recursive: bool = True) -> List[FileInfo]:
        """按路径搜索

        Args:
            path_pattern: 路径模式
            recursive: 是否递归搜索子目录
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            if recursive:
                cursor.execute('SELECT * FROM file_index WHERE path LIKE ?', (f'{path_pattern}%',))
            else:
                cursor.execute('SELECT * FROM file_index WHERE path = ?', (path_pattern,))
            return self._rows_to_file_infos(cursor.fetchall())

    def search_by_metadata(self, metadata_filters: Dict) -> List[FileInfo]:
        """按元数据搜索"""
        query = 'SELECT * FROM file_index WHERE 1=1'
        params = []

        for key, value in metadata_filters.items():
            query += f" AND json_extract(metadata, '$.{key}') = ?"
            params.append(str(value))

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return self._rows_to_file_infos(cursor.fetchall())

    def advanced_search(self,
                        search_criteria: Dict[SearchType, any],
                        sort_by: Optional[str] = None,
                        sort_order: str = 'ASC',
                        limit: Optional[int] = None) -> List[FileInfo]:
        """高级搜索，支持多条件组合"""
        query = 'SELECT * FROM file_index WHERE 1=1'
        params = []

        for search_type, value in search_criteria.items():
            if search_type == SearchType.FILENAME:
                query += ' AND name LIKE ?'
                params.append(f'%{value}%')
            elif search_type == SearchType.CONTENT_TYPE:
                query += ' AND type = ?'
                params.append(value)
            elif search_type == SearchType.DATE_RANGE:
                start_date, end_date = value
                if start_date:
                    query += ' AND modified_at >= ?'
                    params.append(start_date.isoformat())
                if end_date:
                    query += ' AND modified_at <= ?'
                    params.append(end_date.isoformat())
            # ... 其他条件的处理

        if sort_by:
            query += f' ORDER BY {sort_by} {sort_order}'
        if limit:
            query += ' LIMIT ?'
            params.append(limit)

        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return self._rows_to_file_infos(cursor.fetchall())

    def get_all_files(self) -> List[FileInfo]:
        """获取所有文件信息"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM file_index')
            return self._rows_to_file_infos(cursor.fetchall())

    def print_all_tables(self):
        """打印所有表的内容"""
        with sqlite3.connect(self.db_file) as conn:
            # 设置行工厂以返回字典格式的结果
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 打印 file_index 表内容
            print("\n=== File Index Table ===")
            cursor.execute("SELECT * FROM file_index")
            rows = cursor.fetchall()
            if not rows:
                print("No records in file_index")
            else:
                # 获取列名
                columns = rows[0].keys()
                # 使用 tabulate 打印表格（如果已安装）
                try:
                    from tabulate import tabulate
                    print(tabulate([dict(row) for row in rows], headers='keys', tablefmt='grid'))
                except ImportError:
                    # 如果没有安装 tabulate，使用简单的格式打印
                    for row in rows:
                        print("\nFile Record:")
                        for column in columns:
                            print(f"{column}: {row[column]}")

            # 打印 doc_file_mapping 表内容
            print("\n=== Document-File Mapping Table ===")
            cursor.execute("SELECT * FROM doc_file_mapping")
            rows = cursor.fetchall()
            if not rows:
                print("No records in doc_file_mapping")
            else:
                try:
                    from tabulate import tabulate
                    print(tabulate([dict(row) for row in rows], headers='keys', tablefmt='grid'))
                except ImportError:
                    for row in rows:
                        print(f"\nMapping: document_id={row['document_id']}, file_id={row['file_id']}")

    def get_table_stats(self):
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

            print("\n=== Database Statistics ===")
            print(f"Total files indexed: {file_count}")
            print(f"Total document-file mappings: {mapping_count}")
            print(f"Unique document IDs: {unique_docs}")
