import os
import logging
import logging.config
from pathlib import Path
from eo4eu_data_utils.stream import Stream, PathSpec, S3Driver
from eo4eu_data_utils.helpers import select
from eo4eu_comm_utils.format import get_default_logging_config

# logging.basicConfig()
logging.config.dictConfig(get_default_logging_config(verbosity = 0))

boto_config = {
    "region_name": "us-east-1",
    "endpoint_url": os.environ["S3_ENDPOINT_URL"],
    "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
    "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
}


def basic_test_0():
    input_dir = Path("input")
    unpack_dir = Path("unpack")

    result = (Stream()
        .ls(input_dir)
        .filter(lambda ps: ps.path.suffix == ".zip")
        .unpack(unpack_dir)
        .exec()
    )

def basic_test_1():
    input_dir = Path("input")
    output_dir = Path("output")
    unpack_dir = Path("unpack")

    result = (Stream()
        .ls(input_dir)
        .ifelse(
            lambda item: item.path.suffix == ".zip",
            Stream().unpack(unpack_dir),  # if case
            Stream().move(output_dir),    # else case
        )
        .report()
        .exec()
    )

def basic_test_2():
    input_dir = Path("input")
    output_dir = Path("output")

    result = (Stream()
        .raw([
            "file0.txt",
            "file1.txt",
            "file4.txt", # these do not
            "file5.txt", # exist
        ])
        .map(lambda filename: PathSpec(         # this is the datatype used
            name = filename,                    # for files; the name field
            path = input_dir.joinpath(filename) # is used by methods to determine
         ))                                     # where the file should be moved, etc
        .move(output_dir)
        .warn("Failed to move {}/{} files")
        .report()
        .exec()
    )

def s3_test_0():
    output_dir = Path("output")
    s3_driver = S3Driver(
        config = boto_config,
        bucket = "test_pre_pro-base"
    )

    result = (Stream()
        .ls(s3_driver, "source")
        .download(
            s3_driver,
            output_dir,
            post_callback = lambda input, passed, failed, item: logging.warning(f"{passed}, {failed}, {item}")
        )
        .exec()
    )

if __name__ == "__main__":
    # basic_test_0()
    # basic_test_1()
    # basic_test_2()
    s3_test_0()
