import logging
import re
import threading
from pathlib import Path
from typing import Optional, List, Set, Tuple

from watchdog.events import FileSystemEventHandler
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff, EmptyDirectorySnapshot

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.file_management.snapshoter import Snapshoter

logger = logging.getLogger(__name__)

class FileWatcher(FileSystemEventHandler):
    """文件系统变化处理器，监控特定目录下的文件变化并进行处理"""

    IGNORED_PATTERNS: Set[str] = {
        r'^~\$.*',  # Word临时文件
        r'.*\.tmp$',  # 临时文件
        r'.*\.temp$',
        r'^\.',      # 隐藏文件
        r'.*~$',     # 备份文件
        r'.*\.swp$'  # vim临时文件
    }

    def __init__(self, path: str, snapshoter: 'Snapshoter', debounce_seconds: float = 0.2):
        """
        初始化文件扫描处理器

        Args:
            indexer: 文件索引器
            parser: 文件解析器
            vector_store: 向量存储
            path: 监控目录路径
            snapshoter: 快照管理器
            debounce_seconds: 防抖延迟时间(秒)
        """
        super().__init__()
        logger.info(f"初始化Watcher: {path}")

        self.path = Path(path)
        self.debounce_seconds = debounce_seconds
        self.timer: Optional[threading.Timer] = None
        self.snapshoter = snapshoter
        self.snapshot = self._load_snapshot()

    def _load_snapshot(self) -> DirectorySnapshot:
        """加载或创建初始快照"""
        logger.info(f"加载快照: {self.path}")
        snapshot = self.snapshoter.load_snapshot(str(self.path))
        if snapshot is None:
            logger.info("快照不存在，创建新快照")
            snapshot = EmptyDirectorySnapshot()
        return snapshot


    def on_any_event(self, event):
        """处理文件系统事件"""
        if self._is_ignore(event.src_path):
            logger.info(f"忽略文件: {event.src_path}")
            return

        self._start_debounce_timer()

    def _start_debounce_timer(self):
        """启动防抖计时器"""
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.debounce_seconds, self._process_changes)
        self.timer.start()

    def _process_changes(self):
        """处理文件变化"""
        new_snapshot = DirectorySnapshot(str(self.path))
        diff = DirectorySnapshotDiff(self.snapshot, new_snapshot)

        if not any([diff.files_created, diff.files_modified, diff.files_moved, diff.files_deleted,
                    diff.dirs_created, diff.dirs_modified, diff.dirs_moved, diff.dirs_deleted]):
            logger.info("快照一致，无文件变化")
            return

        logger.info("快照不一致，开始处理文件索引...")
        self._handle_created_files(diff.files_created)
        self._handle_modified_files(diff.files_modified)
        self._handle_moved_files(diff.files_moved)
        self._handle_deleted_files(diff.files_deleted)
        logger.info("文件索引处理完毕！")

        self.snapshot = new_snapshot
        snapshot_path = self.snapshoter.update_snapshot(str(self.path), new_snapshot)
        if snapshot_path:
            logger.info(f"已保存快照: {snapshot_path}")

        self.timer = None

    def _handle_created_files(self, created_files):
        """处理新创建的文件"""
        # for file_path in created_files:
        #     if self._should_ignore_file(file_path):
        #         continue
        #     try:
        #         file_path = FileInfo.normalize_path(file_path)
        #         file_info = FileInfo(path=file_path)
        #         self.process_file(file_info)
        #         logger.info(f"Created: {file_path}")
        #     except Exception as e:
        #         logger.error(f"Created Failed: {file_path}, {str(e)}", exc_info=True)

    def _handle_modified_files(self, modified_files):
        """处理修改的文件"""
        # for file_path in modified_files:
        #     if self._should_ignore_file(file_path):
        #         continue
        #     try:
        #         file_path = FileInfo.normalize_path(file_path)
        #         file_info = self.indexer.search_by_path(file_path)
        #         if len(file_info) > 1:
        #             logger.error(f"文件索引异常：{file_path}, 建议重置索引！")
        #         elif len(file_info) == 1:
        #             self.delete_file(file_info[0])
        #             self.process_file(file_info[0])
        #             logger.info(f"Modified: {file_path}")
        #     except Exception as e:
        #         logger.error(f"Modified Failed: {file_path}, {str(e)}", exc_info=True)

    def _handle_moved_files(self, moved_files):
        """处理移动的文件"""
        # for src_path, dest_path in moved_files:
        #     if self._should_ignore_file(src_path) or self._should_ignore_file(dest_path):
        #         continue
        #     try:
        #         src_path = FileInfo.normalize_path(src_path)
        #         dest_path = FileInfo.normalize_path(dest_path)
        #         file_id = self.indexer.get_id_by_path(src_path)
        #         self.indexer.update_file_path(file_id, dest_path)
        #         logger.info(f"Moved: {src_path} to {dest_path}")
        #     except Exception as e:
        #         logger.error(f"Moved Failed: {src_path} to {dest_path}, {str(e)}", exc_info=True)

    def _handle_deleted_files(self, deleted_files):
        """处理删除的文件"""
        # for file_path in deleted_files:
        #     if self._should_ignore_file(file_path):
        #         continue
        #     try:
        #         file_path = FileInfo.normalize_path(file_path)
        #         file_info = self.indexer.search_by_path(file_path)
        #         if len(file_info) > 1:
        #             logger.error(f"文件索引异常：{file_path}，建议重置索引！")
        #         elif len(file_info) == 1:
        #             self.delete_file(file_info[0])
        #             logger.info(f"Deleted: {file_path}")
        #     except Exception as e:
        #         logger.error(f"Deleted Failed: {file_path}, {str(e)}", exc_info=True)

    def _is_ignore(self, file_path: str) -> bool:
        """检查文件是否应该被忽略"""
        file_name = Path(file_path).name
        return any(re.match(pattern, file_name) for pattern in self.IGNORED_PATTERNS)

    # def process_file(self, file_info: FileInfo):
    #     """
    #     处理文件:解析内容并存储向量
    #
    #     Args:
    #         file_info: 文件信息对象
    #     """
    #     documents = self.parser.parse_file_with_info(file_info)
    #     document_ids = self.vector_store.add_documents(documents)
    #     logger.info(f"Added vectors for: {file_info.path}")
    #     file_info.document_ids = document_ids
    #     self.indexer.create_indexes([file_info])
    #
    # def delete_file(self, file_info: FileInfo):
    #     """
    #     删除文件相关的向量和索引
    #
    #     Args:
    #         file_info: 文件信息对象
    #     """
    #     if file_info.document_ids:
    #         self.vector_store.delete_documents(file_info.document_ids)
    #         logger.info(f"Deleted vectors for: {file_info.path}")
    #     self.indexer.delete_index(file_info.id)
    #
    # def dispose(self):
    #     """释放资源"""
    #     if self.timer:
    #         self.timer.cancel()
    #     self.timer = None