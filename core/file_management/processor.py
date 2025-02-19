import hashlib
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Set, Optional

from watchdog.utils.dirsnapshot import DirectorySnapshot, EmptyDirectorySnapshot, DirectorySnapshotDiff

from core.file_management.snapshoter import Snapshoter
from core.file_management.parser import FileParser

if TYPE_CHECKING:
    from core.knowledge_base.document_db import DocumentDB
    from core.knowledge_base.vector_db import VectorDB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileProcessor:

    IGNORED_PATTERNS: Set[str] = {
        r'^~\$.*',  # Word临时文件
        r'.*\.tmp$',  # 临时文件
        r'.*\.temp$',
        r'^\.',      # 隐藏文件
        r'.*~$',     # 备份文件
        r'.*\.swp$'  # vim临时文件
    }

    def __init__(self, vector_db: 'VectorDB', document_db: 'DocumentDB',
                 snapshoter: Optional['Snapshoter'] = None, parser: Optional['FileParser'] = None, ):
        self.vector_db = vector_db
        self.document_db = document_db
        self.snapshoter = Snapshoter() if snapshoter is None else snapshoter
        self.parser = FileParser() if parser is None else parser

    def load_directory(self, path: str):
        # 加载快照
        logger.info(f"加载快照: {path}")
        old_snapshot = self.load_snapshot(path)
        self.process_snapshot_diff(path, old_snapshot)

    def load_snapshot(self, path: str) -> DirectorySnapshot:
        """加载或创建初始快照"""
        logger.info(f"加载快照: {path}")
        snapshot = self.snapshoter.load_latest_snapshot(path)
        if snapshot is None:
            logger.info("快照不存在，创建空白快照")
            snapshot = EmptyDirectorySnapshot()
        return snapshot

    def process_snapshot_diff(self, path: str, old_snapshot: DirectorySnapshot) -> DirectorySnapshot:
        """处理文件变化"""
        new_snapshot = DirectorySnapshot(path)
        diff = DirectorySnapshotDiff(old_snapshot, new_snapshot)

        if not any([diff.files_created, diff.files_modified, diff.files_moved, diff.files_deleted,
                    diff.dirs_created, diff.dirs_modified, diff.dirs_moved, diff.dirs_deleted]):
            logger.info("快照一致，无文件变化")
            return new_snapshot

        logger.info("快照不一致，开始处理文件索引...")
        self._handle_created_files(diff.files_created)
        self._handle_modified_files(diff.files_modified)
        self._handle_moved_files(diff.files_moved)
        self._handle_deleted_files(diff.files_deleted)
        logger.info("文件索引处理完毕！")

        snapshot_path = self.snapshoter.update_snapshot(path, new_snapshot)
        if snapshot_path:
            logger.info(f"已保存快照：{snapshot_path}")
        return new_snapshot

    def _handle_created_files(self, created_files):
        """处理新创建的文件"""
        for file_path in created_files:
            if self.is_ignore(file_path):
                continue
            try:
                self.process_file(file_path)
                logger.info(f"已处理新建文件：{file_path}")
            except Exception as e:
                logger.error(f"处理新建文件失败：{file_path}, {str(e)}", exc_info=True)

    def _handle_modified_files(self, modified_files):
        """处理修改的文件"""
        for file_path in modified_files:
            if self.is_ignore(file_path):
                continue
            try:
                self.delete_file(file_path)
                self.process_file(file_path)
                logger.info(f"已处理修改文件：{file_path}")
            except Exception as e:
                logger.error(f"处理修改文件失败：{file_path}, {str(e)}", exc_info=True)

    def _handle_moved_files(self, moved_files):
        """处理移动的文件"""
        for src_path, dest_path in moved_files:
            if self.is_ignore(src_path) or self.is_ignore(dest_path):
                continue
            try:
                abs_src_path = str(Path(src_path).resolve())
                file_id = hashlib.md5(abs_src_path.encode()).hexdigest()
                self.document_db.update_file(file_id, dest_path)
                logger.info(f"已处理文件移动：{src_path} 至 {dest_path}")
            except Exception as e:
                logger.error(f"处理文件移动失败：{src_path} 至 {dest_path}, {str(e)}", exc_info=True)

    def _handle_deleted_files(self, deleted_files):
        """处理删除的文件"""
        for file_path in deleted_files:
            if self.is_ignore(file_path):
                continue
            try:
                self.delete_file(file_path)
                logger.info(f"已处理文件删除：{file_path}")
            except Exception as e:
                logger.error(f"处理文件删除失败：{file_path}, {str(e)}", exc_info=True)

    def is_ignore(self, file_path: str) -> bool:
        """检查文件是否应该被忽略"""
        file_name = Path(file_path).name
        return any(re.match(pattern, file_name) for pattern in self.IGNORED_PATTERNS)

    def process_file(self, file_path: str):
        """处理文件：解析、向量化、存储"""
        file_path = Path(file_path)
        abs_path = str(file_path.resolve())
        file_id = hashlib.md5(abs_path.encode()).hexdigest()

        if self.document_db.check_file_exists(file_id):
            logger.info(f"文件 {file_path} 已存在，清理旧文件……")
            self.delete_file(str(file_path))

        documents = self.parser.parse(str(file_path))
        document_ids = self.vector_db.add_documents(documents)
        if not document_ids:
            logger.error(f"文件 {file_path} 无法向量化")
            return

        logger.info(f"将文件 {file_path} 添加至向量数据库")
        self.document_db.add_file(file_id, abs_path, file_path.name, file_path.is_dir(),
                                  file_path.suffix, file_path.stat().st_size, document_ids)
        logger.info(f"将文件 {file_path} 添加至文档数据库")

    def delete_file(self, file_path: str):
        """删除文件：从向量数据库和文档数据库中删除"""
        file_path = Path(file_path)
        abs_path = str(file_path.resolve())
        file_id = hashlib.md5(abs_path.encode()).hexdigest()

        if not self.document_db.check_file_exists(file_id):
            logger.info(f"文件 {file_path} 不存在，无需删除")
            return

        document_ids = self.document_db.get_documents_by_file_id(file_id)
        if document_ids:
            self.vector_db.delete_documents(document_ids)
            logger.info(f"将文件 {file_path} 从向量数据库中删除")

        self.document_db.delete_file(file_id)
        logger.info(f"将文件 {file_path} 从文档数据库中删除")