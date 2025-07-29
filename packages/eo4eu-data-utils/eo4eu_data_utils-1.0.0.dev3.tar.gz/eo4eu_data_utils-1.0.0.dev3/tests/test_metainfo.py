import json
from pathlib import Path
from eo4eu_data_utils.metainfo import DSMetainfo


def test_metainfo_0():
    metainfo = json.loads(Path("data/ds_meta.json").read_text())

    ds_meta = DSMetainfo.parse(metainfo[0])
    print(ds_meta.to_json())
    print(len(ds_meta.products))
    for prod in ds_meta.products:
        print(prod)


if __name__ == "__main__":
    test_metainfo_0()
