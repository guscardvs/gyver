from contextlib import contextmanager
from pathlib import Path

from gyver.attrs import mutable

from gyver.exc import FailedFileOperation
from gyver.utils import lazyfield

from .interface import AbstractFileTree
from .typedef import File
from .typedef import Folder
from .virtual import VirtualFileTree


@mutable
class FileTree(AbstractFileTree[Path]):
    base_dir: Path

    @lazyfield
    def root(self):
        return Folder.new(self.base_dir.name)

    @lazyfield
    def virtual(self):
        return VirtualFileTree(self.root)

    def write(self):
        if not self.base_dir.exists():
            self.base_dir.mkdir()
        self.write_folder(self.base_dir, self.root)

    @contextmanager
    def context(self):
        try:
            yield self
        except Exception as e:
            raise FailedFileOperation(
                "unable to write to disk after exception", e
            ) from e
        else:
            self.write()

    def write_file(self, path: Path, file: File):
        with open(path, "wb") as stream:
            stream.write(file.contents.getvalue())

    def write_folder(self, path: Path, folder: Folder):
        if not path.exists():
            path.mkdir()
        for value in folder.contents.values():
            inner_path = path / value.name
            if isinstance(value, File):
                self.write_file(inner_path, value)
            elif isinstance(value, Folder):
                self.write_folder(inner_path, value)

    def from_virtual(self, virtual_filetree: VirtualFileTree, *path: str):
        return self.virtual.from_virtual(virtual_filetree, *path)

    def virtual_context(self, dirname: str, *path: str):
        return self.virtual.virtual_context(dirname, *path)
