import logging
import os
import threading

from watchdog.events import FileSystemEventHandler
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff, EmptyDirectorySnapshot

from services.file_manager import FileInfo

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from services.file_manager import FileIndexer, FileParser, VectorStore
    from utils.SnapshotManager import SnapshotManager


class FileScannerHandler(FileSystemEventHandler):
    """文件系统变化处理器，监控特定目录下的文件变化并进行相应处理"""

    IGNORED_PATTERNS = {
        r'^~\$.*',  # Word临时文件
        r'.*\.tmp$',  # 临时文件
        r'.*\.temp$',
        r'^\.',      # 隐藏文件
        r'.*~$',     # 备份文件
        r'.*\.swp$'  # vim临时文件
    }

    def __init__(self, indexer: 'FileIndexer', parser: 'FileParser', vector_store: 'VectorStore',
                 aim_path: str, snapshot_manager: 'SnapshotManager', debounce_seconds: float = 0.2):
        """
        初始化文件扫描处理器

        Args:
            indexer: 文件索引器
            parser: 文件解析器
            vector_store: 向量存储
            aim_path: 监控目录路径
            snapshot_manager: 快照管理器
            debounce_seconds: 防抖延迟时间(秒)
        """
        super(FileScannerHandler, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"初始化FileScannerHandler: {aim_path}")

        self.indexer = indexer
        self.parser = parser
        self.vector_store = vector_store
        self.aim_path = aim_path
        self.debounce_seconds = debounce_seconds
        self.timer: Optional[threading.Timer] = None

        self.snapshot_manager = snapshot_manager
        # 尝试加载该路径的最新快照
        print(f"尝试加载快照: {aim_path}")
        self.snapshot = self.snapshot_manager.load_latest_snapshot(self.aim_path)
        if self.snapshot is None:
            self.logger.info("未找到快照，开始新建快照...")
            self.snapshot = EmptyDirectorySnapshot()

        self.check_snapshot()

    def on_any_event(self, event):
        if self._should_ignore_file(event.src_path):
            self.logger.debug(f"忽略文件: {event.src_path}")
            return

        if self.timer:
            self.timer.cancel()

        self.timer = threading.Timer(self.debounce_seconds, self.check_snapshot)
        self.timer.start()

    def check_snapshot(self):
        new_snapshot = DirectorySnapshot(self.aim_path)
        diff = DirectorySnapshotDiff(self.snapshot, new_snapshot)

        changed = diff.files_created or diff.files_modified or diff.files_moved or diff.files_deleted
        if not changed:
            self.logger.debug("快照一致，无文件变化")
            return

        self.logger.info("开始处理文件索引...")
        # 处理文件变化
        self._handle_created_files(diff.files_created)
        self._handle_modified_files(diff.files_modified)
        self._handle_moved_files(diff.files_moved)
        self._handle_deleted_files(diff.files_deleted)
        self.logger.info("文件索引处理完毕！")

        self.snapshot = new_snapshot
        snapshot_path = self.snapshot_manager.save_snapshot(self.aim_path, new_snapshot)
        if snapshot_path:
            self.logger.info(f"已保存快照: {snapshot_path}")

        self.timer = None

    def _handle_created_files(self, created_files):
        """处理新创建的文件"""
        for file_path in created_files:
            if self._should_ignore_file(file_path):
                continue
            try:
                file_path = FileInfo.normalize_path(file_path)
                file_info = FileInfo(path=file_path)
                self.process_file(file_info)
                self.logger.info(f"Created: {file_path}")
            except Exception as e:
                self.logger.error(f"Created Failed: {file_path}, {str(e)}", exc_info=True)

    def _handle_modified_files(self, modified_files):
        """处理修改的文件"""
        for file_path in modified_files:
            if self._should_ignore_file(file_path):
                continue
            try:
                file_path = FileInfo.normalize_path(file_path)
                file_info = self.indexer.search_by_path(file_path)
                if len(file_info) > 1:
                    self.logger.error(f"文件索引异常：{file_path}, 建议重置索引！")
                elif len(file_info) == 1:
                    self.delete_file(file_info[0])
                    self.process_file(file_info[0])
                    self.logger.info(f"Modified: {file_path}")
            except Exception as e:
                self.logger.error(f"Modified Failed: {file_path}, {str(e)}", exc_info=True)

    def _handle_moved_files(self, moved_files):
        """处理移动的文件"""
        for src_path, dest_path in moved_files:
            if self._should_ignore_file(src_path) or self._should_ignore_file(dest_path):
                continue
            try:
                src_path = FileInfo.normalize_path(src_path)
                dest_path = FileInfo.normalize_path(dest_path)
                file_id = self.indexer.get_id_by_path(src_path)
                self.indexer.update_file_path(file_id, dest_path)
                self.logger.info(f"Moved: {src_path} to {dest_path}")
            except Exception as e:
                self.logger.error(f"Moved Failed: {src_path} to {dest_path}, {str(e)}", exc_info=True)

    def _handle_deleted_files(self, deleted_files):
        """处理删除的文件"""
        for file_path in deleted_files:
            if self._should_ignore_file(file_path):
                continue
            try:
                file_path = FileInfo.normalize_path(file_path)
                file_info = self.indexer.search_by_path(file_path)
                if len(file_info) > 1:
                    self.logger.error(f"文件索引异常：{file_path}，建议重置索引！")
                elif len(file_info) == 1:
                    self.delete_file(file_info[0])
                    self.logger.info(f"Deleted: {file_path}")
            except Exception as e:
                self.logger.error(f"Deleted Failed: {file_path}, {str(e)}", exc_info=True)

    def _should_ignore_file(self, file_path: str) -> bool:
        """检查文件是否应该被忽略"""
        import re
        file_name = os.path.basename(file_path)
        return any(re.match(pattern, file_name) for pattern in self.IGNORED_PATTERNS)

    def process_file(self, file_info: FileInfo):
        """
        处理文件:解析内容并存储向量

        Args:
            file_info: 文件信息对象
        """
        documents = self.parser.parse_file_with_info(file_info)
        # print("文件解析完毕，解析结果如下：")
        # for document in documents:
        #     print(document.page_content)
        #     print(document.metadata)
        #     print("===")
        documents_ids = self.vector_store.add_documents(documents)
        self.logger.info(f"Added vectors for: {file_info.path}")
        file_info.document_ids = documents_ids
        self.indexer.create_indexes([file_info])

    def delete_file(self, file_info: FileInfo):
        """
        删除文件相关的向量和索引

        Args:
            file_info: 文件信息对象
        """
        if file_info and file_info.document_ids:
            self.vector_store.delete_documents(file_info.document_ids)
            self.logger.info(f"Deleted vectors for: {file_info.path}")
        self.indexer.delete_index(file_info.id)

    def _dispose_error(self):
        if self.timer:
            self.timer.cancel()
        self.timer = None