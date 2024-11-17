from collections import deque
from contextlib import contextmanager

from gyver.attrs import mutable
from gyver.exc import FailedFileOperation, InvalidPath
from gyver.utils import merge_dicts

from .interface import AbstractFileTree
from .typedef import File, Folder


@mutable
class VirtualFileTree(AbstractFileTree[Folder]):
    base_dir: Folder

    @property
    def root(self):
        return self.base_dir

    @property
    def name(self):
        return self.root.name

    def from_virtual(
        self, virtual_filetree: "VirtualFileTree", *path: str, strict: bool = True
    ):
        target = self.root
        for item in path:
            if item not in target.contents:
                target.contents[item] = Folder(item)
            target = target.contents[item]
            if isinstance(target, File):
                raise InvalidPath("Foldername conflicts with file")

        current_value = target.contents.get(virtual_filetree.name)
        if current_value is not None:
            if isinstance(current_value, File):
                raise InvalidPath("Foldername conflicts with file")
            elif isinstance(current_value, Folder) and current_value.contents:
                if not strict:
                    self._try_merge(current_value, virtual_filetree.root)
                else:
                    raise InvalidPath("Non-empty folder with same name already exists")

        target.contents[virtual_filetree.name] = current_value or virtual_filetree.root
        return virtual_filetree.root

    def _try_merge(self, current_target: Folder, virtual_folder: Folder):
        stack = deque([(current_target.contents, virtual_folder.contents)])
        while stack:
            current_contents, virtual_contents = stack.pop()
            for value in current_contents.values():
                if (
                    isinstance(value, Folder)
                    and value.name in virtual_contents
                    and isinstance(virtual_contents[value.name], Folder)
                ):
                    stack.append(
                        (value.contents, virtual_contents[value.name].contents)
                    )
            current_contents.update(
                merge_dicts(current_contents, virtual_contents, on_conflict="left")
            )

    @contextmanager
    def virtual_context(self, dirname: str, *path: str):
        try:
            folder = self.get_dir(dirname, *path) or Folder(dirname)
            vt = VirtualFileTree(folder)
            yield vt
        except Exception as e:
            raise FailedFileOperation(
                "unable to complete virtual context after exception", e
            ) from e
        else:
            self.from_virtual(vt, *path, strict=False)
