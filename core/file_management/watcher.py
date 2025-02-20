from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.observers import Observer

from core.file_management.watcher_handler import WatcherHandler

if TYPE_CHECKING:
    from core.file_management.processor import FileProcessor

class FileWatcher:
    """文件监控类，监控特定目录下的文件变化"""
    def __init__(self):
        self.observer = Observer()
        self.watchers = {}

    def start_watching(self, path: str, processor: 'FileProcessor') -> bool:
        path = Path(path).resolve()
        if str(path) not in self.watchers:
            event_handler = WatcherHandler(str(path), processor)
            self.watchers[str(path)] = self.observer.schedule(event_handler, str(path), recursive=True)
        else:
            return False
        if not self.observer.is_alive():
            self.observer.start()
        return True

    def stop_watching(self, path: str) -> bool:
        path = Path(path).resolve()
        watcher = self.watchers.pop(str(path), None)
        if watcher:
            self.observer.unschedule(watcher)
        else:
            return False
        if not self.watchers and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        return True

    def check_watching(self, path: str):
        path = Path(path).resolve()
        return str(path) in self.watchers

    def stop_all(self):
        self.observer.stop()
        self.observer.join()
        self.watchers.clear()

    def get_all_watched_paths(self):
        return sorted(list(self.watchers.keys()))

    def __del__(self):
        self.stop_all()
