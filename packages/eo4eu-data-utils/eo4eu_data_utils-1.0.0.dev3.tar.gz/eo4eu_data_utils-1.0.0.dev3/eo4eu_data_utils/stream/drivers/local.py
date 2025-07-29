from pathlib import Path
from eo4eu_base_utils.typing import List

from ..model import PathSpec, Lister


class LocalDriver(Lister):
    """An implementation of :class:`eo4eu_data_utils.stream.Lister`
    which lists items in local filesystem directories.

    :param root: The root from which to evaluate paths (default: current directory)
    :type root: Path|str
    """

    def __init__(self, root: Path|str = ""):
        self._root = Path(root).absolute()

    def ls(self, src: Path) -> List[PathSpec]:
        """List `src` recursively, using :func:`pathlib.Path.rglob`

        :param src: The directory to list
        :type src: Path
        :returns: A list of :class:`eo4eu_data_utils.stream.PathSpec` objects which have the same names as paths and no metainfo
        :rtype: List[PathSpec]
        """
        src_dir = src
        if not src_dir.is_absolute():
            src_dir = self._root.joinpath(src)

        return [
            PathSpec(
                name = path.relative_to(src_dir),
                path = path,
                meta = {}
            )
            for path in src_dir.rglob("*")
        ]
