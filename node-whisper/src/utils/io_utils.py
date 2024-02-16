import pathlib


def read_binary_file(fpath: str):
    with open(fpath, mode="rb") as f:
        return f.read()

def write_binary_file(fpath: str, data):
    with open(fpath, mode="wb") as f:
        f.write(data)

def delete_file(fpath: str):
    f = pathlib.Path(fpath)
    if f.exists() and f.is_file():
        f.unlink(missing_ok=True)
