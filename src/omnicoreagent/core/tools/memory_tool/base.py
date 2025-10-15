from abc import ABC, abstractmethod
from typing import Optional


class AbstractMemoryBackend(ABC):
    """
    Abstract base class for a memory storage backend.

    Defines the contract that all backends (local dir, cloud, DB, etc.)
    must follow. The MemoryTool uses this interface only — never the concrete
    implementation directly.
    """

    @abstractmethod
    def view(self, path: Optional[str] = None) -> str:
        """Show directory listing or file contents."""
        pass

    @abstractmethod
    def create_update(self, path: str, file_text: str, mode: str = "create") -> str:
        """Create, append, or overwrite a file."""
        pass

    @abstractmethod
    def str_replace(self, path: str, old_str: str, new_str: str) -> str:
        """Replace all occurrences of old_str with new_str in a file."""
        pass

    @abstractmethod
    def insert(self, path: str, insert_line: int, insert_text: str) -> str:
        """Insert text at a specific line number in a file."""
        pass

    @abstractmethod
    def delete(self, path: str) -> str:
        """Delete a file or directory."""
        pass

    @abstractmethod
    def rename(self, old_path: str, new_path: str) -> str:
        """Rename or move a file/directory."""
        pass

    @abstractmethod
    def clear_all_memory(self) -> str:
        """Clear all memory storage."""
        pass
