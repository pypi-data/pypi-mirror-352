import os
from pathlib import Path
from eo4eu_base_utils import if_none
from eo4eu_base_utils.typing import List, Any, Callable

def _get_idx_of_last_common_part(path_parts_list: List[List[str]]) -> int:
    max_len = max([len(parts) for parts in path_parts_list])
    for idx in range(max_len):
        parts = set()
        for path_parts in path_parts_list:
            if len(path_parts) <= idx:  # a path ends before this part
                return idx

            parts.add(path_parts[idx])
            if len(parts) > 1:  # two paths are not the same
                return idx
    return 0


def trim_root(paths: List[Path], **kwargs) -> List[Path]:
    """Returns the given paths, with the largest common
    parent directory removed. For example ``[\"proj/data/data_0.txt\",
    \"proj/data/data_1.txt\", \"proj/data/data_2.txt\"]`` will become
    ``[\"data_0.txt\", \"data_1.txt\", \"data_2.txt\"]``

    :param paths: A list of :class:`pathlib.Path` objects
    :type paths: List[Path]
    :param kwargs: Ignored
    :rtype: List[Path]
    """
    if len(paths) == 0:
        return paths
    if len(paths) == 1:
        return [Path(paths[0].name)]

    path_parts_list = [path.parts for path in paths]
    last_common_part_idx = _get_idx_of_last_common_part(path_parts_list)
    if last_common_part_idx == 0:
        return paths

    return [
        Path("").joinpath(*[
            part for part in path.parts[last_common_part_idx:]
        ])
        for path in paths
    ]


def _get_shortest_unique(
    parts_list: List[tuple[int,List[str]]],
    aggregator: List[str]
) -> List[str]:
    unique_parts = {}
    for idx, (orig_idx, parts) in enumerate(parts_list):
        first_part = parts[0]
        if first_part not in unique_parts:
            unique_parts[first_part] = [idx]
        else:
            unique_parts[first_part].append(idx)

    next_parts_list = []
    for name, indices in unique_parts.items():
        if len(indices) == 1:  # the path is unique, life is good
            orig_idx = parts_list[indices[0]][0]
            aggregator[orig_idx] = name
        else:
            for idx in indices:
                orig_idx, parts = parts_list[idx]
                if len(parts) <= 1:  # give up trying to make them shorter
                    aggregator[orig_idx] = parts[0]
                else:
                    next_parts_list.append((
                        orig_idx,
                        [f"{parts[1]}/{parts[0]}"] + parts[2:]
                    ))

    if len(next_parts_list) > 0:
        _get_shortest_unique(next_parts_list, aggregator)

    return aggregator


def shortest_unique(paths: List[Path], **kwargs) -> List[Path]:
    """Returns the given paths, flattening them as much as
    possible. If all filenames are unique, it will flatten
    the paths to be just filenames. If two or more filenames are the
    same, the function will add their parents. If they are still
    the same, it will keep adding parents until they are all unique.
    If this never happens (i.e. the given paths are identical), they
    will remain unchanged. This function messes up the folder
    structure if it can, so it should not be used if that
    structure matters.

    :param paths: A list of :class:`pathlib.Path` objects
    :type paths: List[Path]
    :param kwargs: Ignored
    :rtype: List[Path]
    """
    parts_list = [list(path.parts)[::-1] for path in paths]
    if min([len(parts) for parts in parts_list]) <= 0:
        return paths

    return [
        Path(path_str)
        for path_str in _get_shortest_unique(
            parts_list = [(idx, part) for idx, part in enumerate(parts_list)],
            aggregator = [None for _ in parts_list]
        )
    ]


def _append_if_unique(items: List[Any], new_item: Any, compare_func: Callable[[Any,Any],bool]):
    for item in items:
        if compare_func(item, new_item):
            return

    items.append(new_item)


def remove_duplicates(
    paths: List[Path],
    path_compare_func: Callable[[Path,Path],bool]|None = None,
    **kwargs
) -> List[Path]:
    """Returns the given paths, but any path elements with
    the same stem will be removed.

    :param paths: A list of :class:`pathlib.Path` objects
    :type paths: List[Path]
    :param path_compare_func: A function that takes in two :class:`pathlib.Path` objects and returns True if they are \"practically the same\" and False if they are not. By default, it compares their ``.stem`` attributes.
    :type path_compare_func: Callable[[Path,Path],bool]|None
    :rtype: List[Path]
    """
    compare = if_none(path_compare_func, lambda p0, p1: p0.stem == p1.stem)

    new_paths = []
    for path in paths:
        new_path_parts = []
        # We invert the parts list because, of all possible duplicates, we
        # want to keep the last one
        for part in path.parts[::-1]:
            _append_if_unique(new_path_parts, Path(part), compare)

        new_paths.append(Path("").joinpath(*new_path_parts[::-1]))

    # The above algorithm may produce identical paths from previously
    # non-identical ones, which would be BAD. We try to detect it
    # and in those cases we simply won't rename any of the paths that
    # were caused to become identical
    new_path_duplicate_indices = set()
    for i, new_path_i in enumerate(new_paths):
        for j, new_path_j in enumerate(new_paths):
            if i == j:
                continue
            if new_path_i == new_path_j:
                new_path_duplicate_indices.add(i)
                new_path_duplicate_indices.add(j)

    return [
        path if (idx in new_path_duplicate_indices) else new_path
        for idx, (path, new_path) in enumerate(zip(paths, new_paths))
    ]


def _preprocess_distance_matrix(
    distance_matrix: List[List[float]],
    offset = 1
) -> tuple[int,List[List[float]]]:
    max_distance = max([max(distances) for distances in distance_matrix])
    invalid_value = int(max_distance + offset)

    return (invalid_value, [
        [
            distance if distance >= 0 else invalid_value
            for distance in distances
        ]
        for distances in distance_matrix
    ])


def unique_sort_match(distance_matrix: List[List[float]]) -> List[int]:
    """Tries to match each path to the id with the least
    distance from it, and each id to the path with the least distance
    from it. It first sorts the ids for each path based on their distance.
    Then, it moves through the list of ids which are the best match
    for at least one path, and matches the id-path pair with the smallest
    distance. Then the list of ids which are the second best match for at
    least one path, etc... Each id is used only once (hence \"unique\").
    If the distance entry between a path and an id is negative, those
    are considered completely incompatible and are not matched no matter
    what.

    :param distance_matrix: The matrix of path-id distances.
    :type distance_matrix: List[List[float]]
    :returns: A list containing, for each path, the index of the matched id. If the index is -1, no id was matched.
    :rtype: List[int]
    """
    if len(distance_matrix) == 0 or len(distance_matrix[0]) == 0:
        return []

    invalid_value, dist_matrix = _preprocess_distance_matrix(distance_matrix)
    result = [-1 for _ in dist_matrix]  # start as unmatched

    sorted_distances = [
        [
            idx,  # each index here represents a path
            sorted(distances),
            sorted(range(len(distances)), key = distances.__getitem__),  # the id indices
        ]
        for idx, distances in enumerate(dist_matrix)
    ]

    # iterate over "levels": Note that we use sorted_distances, so each level
    # does not correspond to a single id: level=0 iterates over the ids
    # that are the closest to at least one path; level=1 the second closest,
    # etc...
    for level in range(len(dist_matrix[0])):
        sorted_distances.sort(key = lambda item: item[1][level])

        for idx, distances, match_indices in sorted_distances:
            if result[idx] >= 0:  # the path entry has already been filled
                continue

            match_idx = match_indices[level]  # index of the id
            distance = distances[level]
            # either the id has been matched to a different path
            # or the distance between the two is incompatible
            # (i.e. the distance method has returned a negative number)
            if match_idx in result or distance == invalid_value:
                continue

            result[idx] = match_idx

    return result


def _get_appropriate_path_part(
    id_str: str,
    path: Path,
    sep: str = os.sep,
    ljust = True
) -> tuple[str,str,bool]:
    num_elem = id_str.count(sep) + 1
    start_idx = len(path.parts) - num_elem
    if start_idx < 0:
        start_idx = 0

    result = sep.join(path.parts[start_idx:])
    if len(result) == len(id_str):
        return (id_str, result, True)

    length = max([len(result), len(id_str)])
    if ljust:
        return (id_str.ljust(length), result.ljust(length), False)
    else:
        return (id_str.rjust(length), result.rjust(length), False)


def _wrap_dist_func(id_str: str, path: Path, sep: str, func, **kwargs):
    id_str, part, same_lengths = _get_appropriate_path_part(id_str, path, sep)
    left_dist = func(id_str, part, **kwargs)
    if same_lengths:
        return left_dist / len(id_str)
    else:
        id_str, part, _ = _get_appropriate_path_part(id_str, path, sep, ljust = False)
        right_dist = func(id_str, part, **kwargs)

        return min(left_dist, right_dist) / len(id_str)


def _char_dist_basic(c0: str, c1: str) -> float:
    if c0 == c1:
        return 0.0
    elif c0.lower() == c1.lower():
        return 0.25
    elif c0.casefold() == c1.casefold():
        return 0.5
    else:
        return 1.0


def strict_distance(id_str: str, path: Path, sep: str = os.sep) -> float:
    """Returns 0 if the path ends with the id string, -1 otherwise.
    This means paths are only matched to ids which correspond to them
    exactly.

    :param id_str: An id string sourced from some sort of metainfo
    :type is_str: str
    :param path: The path we want to compare to the id
    :type path: Path
    :param sep: The filesystem separator (default: :obj:`os.sep`)
    :type sep: str
    :returns: Either 0 (complete match) or -1 (completely incompatible)
    :rtype: float
    """
    id_str, part, _ = _get_appropriate_path_part(id_str, path, sep)
    return 0 if part == id_str else -1


def _simple_distance(
    id_str: str,
    part: str,
    char_dist_func = None
) -> float:
    char_dist_func = if_none(char_dist_func, _char_dist_basic)
    return sum([
        char_dist_func(id_char, path_char)
        for id_char, path_char in zip(id_str, part)
    ])


def _group_distance(
    id_str: str,
    part: str,
    char_dist_func = None,
    tolerance = 1e-6
) -> float:
    char_dist_func = if_none(char_dist_func, _char_dist_basic)

    group_lengths = []
    current_group_length = 0
    total_dist = 0
    for id_char, path_char in zip(id_str, part):
        dist = char_dist_func(id_char, path_char)
        total_dist += dist

        if dist < tolerance:
            current_group_length += 1
        elif current_group_length > 0:
            # larger groups are rewarded
            group_lengths.append(current_group_length ** 2)
            current_group_length = 0

    if current_group_length > 0:
        group_lengths.append(current_group_length ** 2)

    try:
        return 10 * (total_dist ** 0.5) / sum(group_lengths)
    except Exception as e:
        return 10 * (total_dist ** 0.5)


def simple_distance(id_str: str, path: Path, sep = os.sep, **kwargs):
    """Compares the id string to either the beginning or the end
    of the path, whichever returns the lowest distance. The comparison
    consists of comparing each character and taking the average of their
    distances.

    :param id_str: An id string sourced from some sort of metainfo
    :type is_str: str
    :param path: The path we want to compare to the id
    :type path: Path
    :param sep: The filesystem separator (default: :obj:`os.sep`)
    :type sep: str
    :param char_dist_func: An optional function which compares two characters and yields a distance (By default it uses a function which returns 0 if the two characters are the same, 0.25 if they have the same uppercase, 0.5 if they are the same when casefolded and 1 otherwise.)
    :type char_dist_func: Callable[[str,str],float]|None
    :param kwargs: Other keyword arguments (Ignored)
    :returns: A float from 0 (complete match) to 1
    :rtype: float
    """
    return _wrap_dist_func(id_str, path, sep, _simple_distance, **kwargs)


def group_distance(id_str: str, path: Path, sep = os.sep, **kwargs):
    """Compares the id string to either the beginning or the end
    of the path, whichever returns the lowest distance. The comparison
    uses groups made up of characters which are "close enough" to each
    other based on some distance function. The result favors string pairs
    which have many consequtive similar characters.

    :param id_str: An id string sourced from some sort of metainfo
    :type is_str: str
    :param path: The path we want to compare to the id
    :type path: Path
    :param sep: The filesystem separator (default: :obj:`os.sep`)
    :type sep: str
    :param char_dist_func: An optional function which compares two characters and yields a distance (By default it uses a function which returns 0 if the two characters are the same, 0.25 if they have the same uppercase, 0.5 if they are the same when casefolded and 1 otherwise.)
    :type char_dist_func: Callable[[str,str],float]|None
    :param tolerance: The distance below which two characters are considered the same
    :type tolerance: float
    :param kwargs: Other keyword arguments (Ignored)
    :returns: A float >=0 (usually under 10, often under 1)
    :rtype: float
    """
    return _wrap_dist_func(id_str, path, sep, _group_distance, **kwargs)
