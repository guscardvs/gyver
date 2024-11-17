from typing import Protocol, TypeVar, cast

from lazyfields import lazyfield

from gyver.exc import InvalidPath

from .helpers import python_filename
from .typedef import BaseFile, File, Folder, TextFile

FileT = TypeVar("FileT", bound=BaseFile)

T = TypeVar("T")


class AbstractFileTree(Protocol[T]):
    base_dir: T

    @lazyfield
    def root(self) -> Folder:
        raise NotImplementedError

    def create_dir(self, dirname: str, *path: str) -> Folder:
        target = self.root
        for item in path:
            if item not in target.contents:
                target.contents[item] = Folder(item)
            target = target.contents[item]
            if isinstance(target, File):
                raise InvalidPath("Foldername conflicts with file")
        if dirname not in target.contents:
            target.contents[dirname] = Folder(dirname)
        if not isinstance(target.contents[dirname], Folder):
            raise InvalidPath("foldername conflicts with filename")
        return cast(Folder, target.contents[dirname])

    def create_file(
        self, filename: str, *path: str, fileclass: type[FileT] = File
    ) -> FileT:
        if path:
            dirname, *restpath = path
            directory = self.create_dir(dirname, *restpath)
        else:
            directory = self.root
        target = directory.contents.get(filename) or fileclass(filename)
        if not isinstance(target, fileclass):
            raise InvalidPath(
                "filename conflicts with other folder, or different fileclass"
            )
        directory.contents[filename] = target
        return target

    def create_text_file(self, filename: str, *path: str) -> TextFile:
        return self.create_file(filename, *path, fileclass=TextFile)

    def get_file(self, filename: str, *path: str) -> File:
        if path:
            dirname, *restpath = path
            directory = self.get_dir(dirname, *restpath)
        else:
            directory = self.root
        if not directory:
            raise InvalidPath("file not found")
        target = directory.contents.get(filename)
        if not target:
            raise InvalidPath("file not found")
        if not isinstance(target, File):
            raise InvalidPath("filename conflicts with folder")
        return target

    def get_dir(self, dirname: str, *path: str) -> Folder | None:
        target = self.root
        for item in path:
            if item not in target.contents:
                return None
            target = target.contents[item]
            if isinstance(target, File):
                raise InvalidPath("Foldername conflicts with file")
        return cast(Folder | None, target.contents.get(dirname))

    def create_py_file(
        self,
        filename: str,
        *path: str,
        private: bool = False,
        dunder: bool = False,
    ) -> TextFile:
        return self.create_file(
            python_filename(filename, private, dunder),
            *path,
            fileclass=TextFile,
        )

    def dunder_init(self, *path: str):
        return self.create_py_file("init", *path, dunder=True)
