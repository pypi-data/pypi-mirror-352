from pathlib import Path
from pprint import pprint
from eo4eu_data_utils.helpers import (
    format_list, trim_root, shortest_unique,
    strict_distance, simple_distance, group_distance,
    unique_sort_match,
)


def test_methods(input: list[Path]):
    print("\n".join([
        format_list("Before: ", input),
        format_list("Trim:   ", trim_root(input)),
        format_list("Short:  ", shortest_unique(input)),
    ]))


def test_distances(pairs: list[tuple[str,Path]]):
    print(format_list("Strict: ", [
        strict_distance(id_str, path)
        for id_str, path in pairs
    ]))
    print(format_list("Simple: ", [
        simple_distance(id_str, path)
        for id_str, path in pairs
    ]))
    print(format_list("Group:  ", [
        group_distance(id_str, path)
        for id_str, path in pairs
    ]))


def test_match(pairs, distance_func):
    distance_matrix = [
        [
            distance_func(id_str, path)
            for id_str, _ in pairs
        ]
        for _, path in pairs
    ]

    pprint(distance_matrix)
    pprint(unique_sort_match(distance_matrix))


if __name__ == "__main__":
    paths_0 = [
        Path(path_str) for path_str in [
            "dir/another/help/data.csv",
            "dir/another/help/data0.csv",
            "dir/another/help/data1.csv",
            "dir/another/first/data.csv",
            "dir/another/second/data0.csv",
            "dir/another/metainfo.json",
        ]
    ]
    paths_1 = [
        Path(path_str) for path_str in [
            "dir/another/help/data.csv",
            "dir/another/help/data0.csv",
            "dir/another/help/data1.csv",
            "dir/thingy/help/data1.csv",
            "dir/another/first/data.csv",
            "dir/another/second/data0.csv",
            "dir/another/metainfo.json",
        ]
    ]
    paths_2 = [
        Path(path_str) for path_str in [
            "dir/another/help/data.csv",
            "dir/another/help/data0.csv",
            "dir/another/help/data1.csv",
            "dir/thingy/help/data1.csv",
            "further/dir/thingy/help/data1.csv",
            "dir/another/first/data.csv",
            "dir/another/second/data0.csv",
            "dir/another/metainfo.json",
        ]
    ]

    # test_methods(paths_0)
    # test_methods(paths_1)
    # test_methods(paths_2)
    pairs_0 = [
        ["some/test/id.txt", Path("this/is/some/test/id.txt")],
        ["some/test/id.txt00wasv", Path("this/is/some/test/id.txt")],
        ["some/test/id0.txt", Path("this/is/some/test/id.txt")],
        ["some/test/i08635d.txt", Path("this/is/some/test/id.txt")],
    ]

    # test_distances(pairs_0)

    pairs_1 = [
        ["some/test/id0.txt", Path("this/is/some/test/id0.txt")],
        ["some/test/id1.txt", Path("this/is/some/test/id1.txt")],
        ["some/test/id2.txt", Path("this/is/some/test/id2.txt")],
        ["some/test/id3.txt", Path("this/is/some/test/id3.txt")],
    ]
    # test_match(pairs_1, strict_distance)
    # test_match(pairs_1, simple_distance)
    # test_match(pairs_1, group_distance)

    pairs_2 = [
        ["some/test/id0.txt", Path("this/is/some/test/id0.dat")],
        ["some/test/id1.txt", Path("this/is/some/test/id1.dat")],
        ["some/test/id2.txt", Path("this/is/some/test/id2.dat")],
        ["some/test/id3.txt", Path("this/is/some/test/id3.dat")],
    ]
    # test_match(pairs_2, strict_distance)
    # test_match(pairs_2, simple_distance)
    # test_match(pairs_2, group_distance)

    pairs_3 = [
        ["some/test/id0.txt", Path("this/is/some/test/id0.dat")],
        ["some/test/id11.txt", Path("this/is/some/test/id11.dat")],
        ["some/test/id222.txt", Path("this/is/some/test/id222.dat")],
        ["some/test/id3333.txt", Path("this/is/some/test/id3333.dat")],
    ]
    # print("PAIRS 3")
    # test_match(pairs_3, strict_distance)
    # test_match(pairs_3, simple_distance)
    # test_match(pairs_3, group_distance)

    pairs_4 = [
        ["some/test/id0.txt", Path("this/is/some/test/id3333.dat")],
        ["some/test/id11.txt", Path("this/is/some/test/id222.dat")],
        ["some/test/id222.txt", Path("this/is/some/test/id11.dat")],
        ["some/test/id3333.txt", Path("this/is/some/test/id0.dat")],
    ]
    # print("PAIRS 4")
    # test_match(pairs_4, strict_distance)
    # test_match(pairs_4, simple_distance)
    # test_match(pairs_4, group_distance)

    pairs_5 = [
        ["id0.txt", Path("this/is/some/test/_id3333.txt")],
        ["id11.txt", Path("this/is/some/test/_id222.txt")],
        ["id222.txt", Path("this/is/some/test/_id11.txt")],
        ["id3333.txt", Path("this/is/some/test/_id0.txt")],
    ]
    # print("PAIRS 5")
    # test_match(pairs_5, strict_distance)
    # test_match(pairs_5, simple_distance)
    # test_match(pairs_5, group_distance)

    pairs_6 = [
        ["id0.txt", Path("this/is/some/test/id1234_.dat")],
        ["id12.txt", Path("this/is/some/test/id123_.dat")],
        ["id123.txt", Path("this/is/some/test/id12_.dat")],
        ["id1234.txt", Path("this/is/some/test/id0_.dat")],
    ]
    # print("PAIRS 6")
    # test_match(pairs_6, strict_distance)
    # test_match(pairs_6, simple_distance)
    # test_match(pairs_6, group_distance)
