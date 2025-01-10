from dataclasses import dataclass, asdict, field
from datetime import datetime
import hashlib
import os
from enum import Enum
from typing import Dict, List


class FileType(Enum):
    """文件类型枚举"""
    TEXT = "text"
    PDF = "pdf"
    WORD = "word"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DIRECTORY = "directory"
    OTHER = "other"


@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    id: str = ""
    name: str = ""
    is_directory: bool = False
    file_type: FileType = FileType.OTHER
    size: int = 0
    created_at: datetime = None
    modified_at: datetime = None
    metadata: Dict = field(default_factory=dict)
    document_ids: List[str] = field(default_factory=list)
    _skip_existence_check: bool = field(default=False, repr=False)

    def __post_init__(self):
        # 跳过文件存在性检查
        if self._skip_existence_check:
            return

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"文件不存在: {self.path}")
        # 标准化路径
        self.path = self.normalize_path(self.path)
        self.id = self.generate_id(self.path)
        self.name = os.path.basename(self.path)
        self.is_directory = os.path.isdir(self.path)
        self.file_type = self._determine_file_type()
        self.size = 0 if self.is_directory else os.path.getsize(self.path)
        self.created_at = datetime.fromtimestamp(os.path.getctime(self.path))
        self.modified_at = datetime.fromtimestamp(os.path.getmtime(self.path))
        self.metadata = {}
        self.document_ids = []

    @staticmethod
    def normalize_path(path: str) -> str:
        """标准化文件路径"""
        # 转换为绝对路径
        abs_path = os.path.abspath(path)
        # 标准化路径
        norm_path = os.path.normpath(abs_path)
        # Windows系统下转换为小写
        if os.name == 'nt':
            norm_path = norm_path.lower()
        return norm_path

    @staticmethod
    def generate_id(path: str) -> str:
        """生成文件唯一标识"""
        return hashlib.md5(path.encode()).hexdigest()

    @staticmethod
    def generate_file_id(path: str) -> str:
        """公共接口：生成文件唯一标识"""
        path = FileInfo.normalize_path(path)
        return FileInfo.generate_id(path)

    def _determine_file_type(self) -> FileType:
        """确定文件类型"""
        if self.is_directory:
            return FileType.DIRECTORY

        ext = os.path.splitext(self.path)[1].lower()
        type_mapping = {
            ('.txt', '.md', '.json', '.csv'): FileType.TEXT,
            ('.pdf',): FileType.PDF,
            ('.doc', '.docx'): FileType.WORD,
            ('.jpg', '.jpeg', '.png', '.gif'): FileType.IMAGE,
            ('.mp4', '.avi', '.mov'): FileType.VIDEO,
            ('.mp3', '.wav'): FileType.AUDIO
        }

        for extensions, file_type in type_mapping.items():
            if ext in extensions:
                return file_type
        return FileType.OTHER

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        data = asdict(self)
        data['file_type'] = self.file_type.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['modified_at'] = self.modified_at.isoformat() if self.modified_at else None
        return data
