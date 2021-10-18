import pathlib


def create_directory(path: str) -> None:
    directory = pathlib.Path(path)
    if directory.exists():
        raise FileExistsError(f"{path} is exist")

    directory.mkdir()


def create_file(path: str, content: str = None) -> None:
    file = pathlib.Path(path)
    if file.exists():
        raise FileExistsError(f"{path} is exist")

    file.touch()
    if content:
        with file.open(mode="w") as f:
            f.write(content)
