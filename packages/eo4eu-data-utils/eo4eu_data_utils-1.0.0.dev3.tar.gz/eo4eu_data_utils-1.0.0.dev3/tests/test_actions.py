import logging
from pathlib import Path
from eo4eu_data_utils.pipeline import Data, ActionContext
from eo4eu_data_utils.pipeline.actions import TrimNames


logger = logging.getLogger("test")


def test_trim_0():
    paths = Data.homogenous(
        driver = None,
        cwdir = Path.cwd(),
        rel_paths = [
            Path("a/b/c"),
            Path("a/b/d"),
            Path("a/b/e"),
            Path("a/b/f"),
        ]
    )
    ctx = ActionContext(logger = logger, summary = logger)

    out_paths = TrimNames().execute(paths, ctx)
    print(paths)
    print(out_paths)


if __name__ == "__main__":
    logging.basicConfig()
    test_trim_0()
