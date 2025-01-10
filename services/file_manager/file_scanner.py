import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from watchdog.observers import Observer

from services.file_manager import FileInfo, FileIndexer, FileParser, VectorStore
from utils.SnapshotManager import SnapshotManager


class FileScanner:
    def __init__(self):
        self.event_handlers = {}
        self.observer = None
        self.snapshot_manager = SnapshotManager()

    def reset(self):
        """重置"""
        self.event_handlers.clear()
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        self.observer = None
        self.snapshot_manager.reset()

    def scan_directory(self, aim_path: str) -> List[FileInfo]:
        """扫描指定目录"""
        aim_path = os.path.normpath(os.path.abspath(aim_path))
        files_info = []
        for root, dirs, filenames in os.walk(aim_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                file_info = FileInfo(file_path)
                files_info.append(file_info)
        return files_info

    def initialize_handler(self, aim_path: str, indexer: FileIndexer, parser: FileParser, vector_store: VectorStore):
        from services.file_manager import FileScannerHandler
        self.event_handlers[aim_path] = {
            'handler': FileScannerHandler(indexer, parser, vector_store, aim_path, self.snapshot_manager),
            'watch': None  # 存储 observer.schedule 返回的 watch 对象
        }

    def start_watching(self, aim_path: str = None):
        """
        监控指定路径的文件变化

        Args:
            aim_path: 要监控的目录路径

        Raises:
            Exception: 当指定路径的 handler 未初始化时抛出异常
        """
        if self.observer is None or not self.observer.is_alive():
            self.observer = Observer()
            self.observer.start()

        if aim_path is None:
            for path, handler_info in self.event_handlers.items():
                if handler_info['watch'] is None:
                    handler_info['watch'] = self.observer.schedule(handler_info['handler'], path, recursive=True)
        else:
            handler_info = self.event_handlers[aim_path]
            if handler_info['watch'] is None:  # 避免重复监控
                handler_info['watch'] = self.observer.schedule(handler_info['handler'], aim_path, recursive=True)

    def stop_watching(self, aim_path: str = None):
        """
        停止文件监控

        Args:
            aim_path: 要停止监控的目录路径，如果为None则停止所有监控
        """
        if self.observer is None or not self.observer.is_alive():
            return

        if aim_path is not None:
            # 停止监控指定路径
            if aim_path in self.event_handlers:
                handler_info = self.event_handlers[aim_path]
                if handler_info['watch']:
                    self.observer.unschedule(handler_info['watch'])
                del self.event_handlers[aim_path]

                # 如果没有其他活跃的监控，则停止 observer
                if not self.event_handlers:
                    self.observer.stop()
                    self.observer.join()
        else:
            # 停止所有监控
            self.observer.stop()
            self.observer.join()
            # 清理所有 watch 记录
            self.event_handlers.clear()
