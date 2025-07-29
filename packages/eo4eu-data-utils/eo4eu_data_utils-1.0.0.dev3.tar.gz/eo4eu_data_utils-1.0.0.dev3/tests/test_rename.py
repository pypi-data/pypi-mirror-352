from pprint import pprint
from pathlib import Path
from eo4eu_data_utils.settings.format import remove_duplicates


def test_0():
    paths = [
        Path(path_str) for path_str in [
            "dir0/dir1/dir2/filename.zip/filename.png",
            "dir0/dir1/dir3/filename.zip/filename.png",
            "dir0/dir1/dir4/filename.zip/filename.png",
            "dir0/dir1/dir5/filename.zip/filename.png",
            "dir0/dir1/dir5/filename.tgz/filename.png",
            "dir0/dir1/dir5/filename.txt/filename.png",
        ]
    ]

    pprint(remove_duplicates(paths))


if __name__ == "__main__":
    test_0()
