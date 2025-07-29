from eo4eu_data_utils.stream import Stream, S3Driver
from eo4eu_data_utils.config import ConfigBuilder, Try
from eo4eu_data_utils.metainfo import DSMetainfo
from eo4eu_data_utils.helpers import attach, select
from eo4eu_comm_utils.format import get_default_logging_config
from pprint import pprint, pformat
from pathlib import Path
from enum import Enum
import traceback
import logging
import logging.config
import re
import os

logger = logging.getLogger("app.logger")
logging.config.dictConfig(get_default_logging_config(verbosity = 2))
logger.setLevel(logging.INFO)

config = {
    "boto": {
        "region_name": "us-east-1",
        "endpoint_url": os.environ["S3_ENDPOINT_URL"],
        "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
    },
    "bucket": "apollo-test"
}


class FileKind(Enum):
    ARCH = 0
    DATA = 1
    META = 2
    TIFF = 3
    OTHER = 4

    @classmethod
    def from_pathspec(cls, pathspec):
        path = pathspec.path
        extension = path.suffix
        # handle cases such as .tar.gz
        if len(path.suffixes) > 1 and path.suffixes[-2] == ".tar":
            extension = "".join(path.suffixes[-2:])

        if extension in {".tar", ".tar.gz", ".tar.br", ".tar.xz"}:
            return cls.ARCH

        if extension in {
            ".json", ".csv", ".xml", ".xls", ".xlsx", ".xlsb",
            ".xlsm", ".odf", ".ods", ".odt", ".dbf"
        }:
            if re.match(r"(.*\-)?meta.*\.json", path.name):
                return cls.META
            return cls.DATA

        if extension in {".tiff", ".tif"}:
            return cls.TIFF

        return cls.OTHER


def basic_test(s3_driver: S3Driver):
    result = (Stream()
        .ls(s3_driver)
        .report()
        .download(
            s3_driver, "download",
            err_callback = lambda item, e: print(traceback.format_exc())
        )
        .report()
        .unpack("download/unpack")
        .report()
        # .warn(
        #     lambda passed, failed: logger.warning(f"Failed to get {passed}/{failed} files!")
        # )
        # .filter(lambda pathspec: pathspec.path.suffix == ".csv")
        # .report()
        # .warn(
        #     lambda passed, failed: logger.warning(f"Failed to get {passed}/{failed} files!")
        # )
        .rename()
        .report()
        .do(lambda: print("hello!!"))
        .report()
        .exec()
    )


def meta_test(s3_driver: S3Driver):
    metainfo = [
        {"id": id_str, "filetype": "image/tiff"}
        for id_str in [
            "T32SQF_resampled_B02B03B04.tiff",
            "T32SQG_resampled_B02B03B04.tiff",
            "T32SQH_resampled_B02B03B04.tiff",
            "T32STA_resampled_B02B03B04.tiff",
            "T32STB_resampled_B02B03B04.tiff",
            "T32STC_resampled_B02B03B04.tiff",
            "T32SUA_resampled_B02B03B04.tiff",
            "T32SUB_resampled_B02B03B04.tiff",
            "T32SUC_resampled_B02B03B04.tiff",
            "T32SVA_resampled_B02B03B04.tiff",
            "T32SVB_resampled_B02B03B04.tiff",
            "T32SVC_resampled_B02B03B04.tiff",
            "T32SWA_resampled_B02B03B04.tiff",
            "T32SWB_resampled_B02B03B04.tiff",
            # "T32SWC_resampled_B02B03B04.tiff",
        ]
    ] + [{"extraInfo": {"datasetName": "ivi_fusion"}}]
    return (Stream()
        .ls(s3_driver, "ivi_fusion_folder/")
        .rename()
        .report()
        .fill_metainfo(
            DSMetainfo.parse(metainfo),
            err_callback = lambda item, e: print(f"WARNING: {traceback.format_exc()}")
        )
        .apply(lambda data: print("\n".join([
            f"{pathspec.name}: {pformat(pathspec.meta)}"
            for pathspec in data
        ])))
        .exec()
    )


def filter_test(s3_driver: S3Driver):
    return (Stream()
        .ls(s3_driver)
        .rename()
        .map(attach(kind = FileKind.from_pathspec))
        .report()
        # .filter(select(kind = {FileKind.DATA, FileKind.ARCH}))
        .branch(
            select(kind = FileKind.TIFF),
            Stream().do(lambda: logger.info("TIFFS")).report()
        )
        .branch(
            select(kind = {FileKind.DATA, FileKind.ARCH}),
            Stream().do(lambda: logger.info("DATA")).report()
        )
        .switch(
            cases = [
                (select(kind = FileKind.META),
                    Stream().do(lambda: logger.info(".META"))
                        .report().drop()
                ),
                (select(kind = FileKind.DATA),
                    Stream().do(lambda: logger.info(".DATA")).report()
                ),
            ],
            default = Stream().do(lambda: logger.info(".REST")).report()
        )
        .report()
        .exec()
    )


if __name__ == "__main__":
    s3_driver = S3Driver(
        config = config["boto"],
        bucket = config["bucket"]
    )

    # basic_test(s3_driver)
    # meta_test(s3_driver)
    filter_test(s3_driver)
