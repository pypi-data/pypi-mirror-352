"""
BOFS
----------------------------------------------------------------
A pythonic file-systems interface to BOS (BAIDU Object Storage)
"""

from .core import BOSFileSystem
from .file import BOSFile

__all__ = ["BOSFile", "BOSFileSystem"]