import pytest
from gyver.attrs import asdict

from gyver.exc import FailedFileOperation
from gyver.exc import InvalidPath
from gyver.filetree import File
from gyver.filetree import Folder
from gyver.filetree import TextFile
from gyver.filetree import VirtualFileTree


def test_create_dir():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        folder = inner_tree.create_dir("subfolder")
        assert folder.name == "subfolder"
        assert folder.contents == {}


def test_create_dir_existing_folder():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        folder1 = inner_tree.create_dir("subfolder")
        folder2 = inner_tree.create_dir("subfolder")
        assert folder1 is folder2


def test_create_dir_existing_file():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_file("file")
        with pytest.raises(InvalidPath):
            inner_tree.create_dir("file")


def test_create_file():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        file = inner_tree.create_file("file")
        assert file.name == "file"
        assert file.contents.getvalue() == "".encode(file.get_encoding())


def test_create_file_existing_folder():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_dir("subfolder")
        with pytest.raises(InvalidPath):
            inner_tree.create_file("subfolder")


def test_create_file_existing_file():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        file1 = inner_tree.create_file("file")
        file2 = inner_tree.create_file("file")
        assert file1 is file2


def test_get_file():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_file("file")
        file = inner_tree.get_file("file")
        assert file.name == "file"


def test_get_file_nonexistent_folder():
    file_tree = VirtualFileTree(Folder.new("root"))
    with pytest.raises(InvalidPath):
        file_tree.get_file("file", "invalid")


def test_get_file_nonexistent_file():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        with pytest.raises(InvalidPath):
            inner_tree.get_file("file")


def test_get_dir():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_dir("folder")
        folder = inner_tree.get_dir("folder")
        assert folder is not None
        assert folder.name == "folder"


def test_get_dir_nonexistent_folder():
    file_tree = VirtualFileTree(Folder.new("root"))
    folder = file_tree.get_dir("folder")
    assert folder is None


def test_create_py_file():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder"):
        file = file_tree.create_py_file("script")
        assert file.name == "script.py"


def test_dunder_init():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder"):
        file = file_tree.dunder_init()
        assert file.name == "__init__.py"


def test_from_virtual():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_dir("subfolder")
        inner_tree.create_file("file")

        new_tree = VirtualFileTree(Folder.new("new_root"))
        new_root = new_tree.from_virtual(inner_tree, "folder")
        assert new_root.name == "folder"
        assert isinstance(new_root, Folder)
        assert new_root.contents["subfolder"].name == "subfolder"
        assert isinstance(new_root.contents["subfolder"], Folder)
        assert new_root.contents["file"].name == "file"
        assert isinstance(new_root.contents["file"], File)


def test_from_virtual_existing_file():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_file("file")

    new_tree = VirtualFileTree(Folder.new("file"))
    with pytest.raises(InvalidPath):
        file_tree.from_virtual(new_tree, "folder")


def test_from_virtual_foldername_conflict():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_file("subfolder")

    new_tree = VirtualFileTree(Folder.new("subfolder"))
    with pytest.raises(InvalidPath):
        file_tree.from_virtual(new_tree, "folder")


def test_virtual_context():
    file_tree = VirtualFileTree(Folder.new("root"))
    with file_tree.virtual_context("folder") as inner_tree:
        folder = inner_tree.create_dir("subfolder")
        file = inner_tree.create_file("file")
        text_file = inner_tree.create_file("text_file", fileclass=TextFile)
        text_file.write("Hello")
        assert folder.name == "subfolder"
        assert file.name == "file"
        assert inner_tree.root.contents["subfolder"].name == "subfolder"
        assert inner_tree.root.contents["file"].name == "file"

    assert asdict(file_tree.root) == {
        "name": "root",
        "contents": {
            "folder": {
                "name": "folder",
                "contents": {
                    "subfolder": {"name": "subfolder", "contents": {}},
                    "file": {
                        "name": "file",
                        "contents": file.contents,
                    },
                    "text_file": {
                        "name": "text_file",
                        "contents": text_file.contents,
                        "encoding": text_file.encoding,
                    },
                },
            }
        },
    }


def test_virtual_context_exception():  # sourcery skip: raise-specific-error
    file_tree = VirtualFileTree(Folder.new("root"))
    with pytest.raises(FailedFileOperation):
        with file_tree.virtual_context("folder"):
            raise Exception("Something went wrong")

    assert file_tree.root.contents == {}


def test_from_virtual_merge_strict():
    file_tree = VirtualFileTree(Folder.new("root"))

    # Create a file with the same name as the folder we want to merge
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_file("file.txt")

    another = VirtualFileTree(Folder.new("folder"))
    another.create_file("another_file.txt")
    another.create_dir("subfolder")

    with pytest.raises(InvalidPath):
        file_tree.from_virtual(another, strict=True)


def test_from_virtual_merge_non_strict():
    file_tree = VirtualFileTree(Folder.new("root"))

    # Create a file with the same name as the folder we want to merge
    with file_tree.virtual_context("folder") as inner_tree:
        inner_tree.create_file("file.txt")

    another = VirtualFileTree(Folder.new("folder"))
    another.create_file("another_file.txt")
    another.create_dir("subfolder")

    file_tree.from_virtual(another, strict=False)
    merged_file = file_tree.get_file("file.txt", "folder")
    assert merged_file.name == "file.txt"

    # Verify that the subfolder is not merged
    subfolder = file_tree.get_dir("subfolder", "folder")
    assert subfolder is not None
    assert subfolder.name == "subfolder"

    # Verify that the new file is added
    another_file = file_tree.get_file("another_file.txt", "folder")
    assert another_file.name == "another_file.txt"
