from gyver.filetree import FileTree, Folder, TextFile


def test_write_file(tmp_path):
    file_tree = FileTree(base_dir=tmp_path)
    folder = Folder.new("root")
    file = TextFile.new("file.txt")
    file.write("Hello, World!")
    folder.contents[file.name] = file
    file_tree.root = folder

    file_tree.write()

    assert (tmp_path / "file.txt").is_file()
    with open(tmp_path / "file.txt", "r") as f:
        assert f.read() == "Hello, World!"


def test_write_folder(tmp_path):
    file_tree = FileTree(base_dir=tmp_path)
    folder = Folder.new("root")
    file = TextFile.new("file.txt")
    file.write("Hello, World!")
    subfolder = Folder.new("subfolder")
    subfile = TextFile.new("subfile.txt")
    subfile.write("This is a subfile.")
    subfolder.contents[subfile.name] = subfile
    folder.contents[file.name] = file
    folder.contents[subfolder.name] = subfolder
    file_tree.root = folder

    file_tree.write()

    assert (tmp_path / "file.txt").is_file()
    with open(tmp_path / "file.txt", "r") as f:
        assert f.read() == "Hello, World!"

    assert (tmp_path / "subfolder" / "subfile.txt").is_file()
    with open(tmp_path / "subfolder" / "subfile.txt", "r") as f:
        assert f.read() == "This is a subfile."
