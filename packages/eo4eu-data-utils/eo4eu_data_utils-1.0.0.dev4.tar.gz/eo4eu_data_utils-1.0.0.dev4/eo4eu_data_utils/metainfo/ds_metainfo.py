import json
import functools
from eo4eu_base_utils.typing import Self, Any, Callable, List, Dict

from ..settings import Settings


def _get_default_ds_info():
    return {"extraInfo": {
        "datasetId": 0,
        "persistentId": "unknown",
        "datasetName": "unknown",
        "description": "",
        "variables": "variables",
        "fileformats": "fileformats",
        "geometry": [],
    }}


def _make_into_func(func: Any) -> Callable[[dict,dict],Any]:
    if callable(func):
        return func
    return functools.partial(
        lambda product, info, val: val,
        val = func
    )


class DSMetainfo:
    """An EO4EU datasource metainfo object. It consists of a list
    of products (generally, those will be data files; it is possible
    that a product may correspond to several files) described by
    (almost) arbitrary Python dictionaries, and some general info
    about the dataset.

    :param products: The products of the dataset
    :type products: List[Dict]
    :param info: The extra info of the dataset
    :type info: Dict
    """

    def __init__(self, products: List[Dict], info: Dict):
        self.products = products
        """The products of the dataset"""
        self.info = info
        """The extra info of the dataset"""

    @classmethod
    def only_info(cls, info: Dict) -> Self:
        """Construct a partial dataset, consisting only of extra
        info and no products. This is definitely the result of
        some error somewhere, but components like the pre-processor
        will try to amend it by automatically generating the products

        :param info: The dataset's extra info
        :type info: Dict
        :rtype: DSMetainfo
        """
        return DSMetainfo([], info)

    @classmethod
    def only_products(cls, products: List[Dict]) -> Self:
        """Construct a partial dataset, consisting only of products
        and no extra info. This is definitely the result of
        some error somewhere, but components like the pre-processor
        will try to amend it by automatically assigning dataset names

        :param products: The dataset's products
        :type products: List[Dict]
        :rtype: DSMetainfo
        """
        return DSMetainfo(products, _get_default_ds_info())

    @classmethod
    def default(cls) -> Self:
        """Construct a default, empty dataset metainfo object.

        :rtype: DSMetainfo
        """
        return DSMetainfo([], _get_default_ds_info())

    @classmethod
    def parse(cls, json_object: Any) -> Self:
        """Read metainfo from deserialized JSON. This function tries its
        best to account for different errors in the format

        :param json_object: The loaded JSON object
        :type json_object: Any
        :rtype: DSMetainfo
        """
        logger = Settings.LOGGER

        if not isinstance(json_object, list):
            msg = f"JSON object is \"{json_object.__class__.__name__}\", expected \"list\": upcasting to {{}}"
            if isinstance(json_object, dict):
                if "extraInfo" in json_object:
                    logger.warning(msg.format("DSMetainfo.only_info"))
                    return DSMetainfo.only_info(json_object)
                elif "id" in json_object:
                    logger.warning(msg.format("DSMetainfo.only_products"))
                    return DSMetainfo.only_products([json_object])

            logger.warning(msg.format("DSMetainfo.default"))
            return DSMetainfo.default()

        extra_infos = [
            (idx, item) for idx, item in enumerate(json_object)
            if "extraInfo" in item
        ]
        if len(extra_infos) == 0:
            logger.warning("JSON object has no extra info, returning DSMetainfo.only_products")
            return DSMetainfo.only_products(json_object)
        elif len(extra_infos) > 1:
            logger.warning("JSON object has multiple instances of extra info, keeping the last one")

        _, extra_info = extra_infos[-1]  # use the last object with "extraInfo"
        extra_info_indices = {idx for idx, _ in extra_infos}
        return DSMetainfo(
            products = [
                product for i, product in enumerate(json_object)
                if i not in extra_info_indices
            ],
            info = extra_info,
        )

    def to_obj(self) -> List[Dict]:
        """Converts the DSMetainfo object back to a JSON object

        :rtype: List[Dict]
        """
        return [*self.products, self.info]

    def to_json(self) -> str:
        """Converts the DSMetainfo object back to a JSON object and
        serializes it into a string

        :rtype: str
        """
        return json.dumps(self.to_obj())

    def name(self, default: str = "unknown") -> str:
        """Get the dataset name from the dataset's exta info

        :param default: The default name to return, if the name can't be found
        :type defautlt: str (default: "unknown")
        :rtype: str
        """
        try:
            return self.info["extraInfo"]["datasetName"]
        except KeyError:
            return default

    def with_products(self, products: List[Dict]) -> Self:
        """Create a DSMetainfo object with the same extra info
        but different products.

        :param products: The new products
        :type products: List[Dict]
        :returns: A new metainfo object (the current one is not modified!)
        :rtype: DSMetainfo
        """
        return DSMetainfo(
            products = products,
            info = self.info,
        )

    def with_info(self, info: dict) -> Self:
        """Create a DSMetainfo object with the same products
        but different extra info.

        :param info: The new extra info
        :type info: Dict
        :returns: A new metainfo object (the current one is not modified!)
        :rtype: DSMetainfo
        """
        return DSMetainfo(
            products = self.products,
            info = info,
        )

    def unpack(self) -> tuple[List[Dict],Dict]:
        """Unpacks the metainfo object to products and extra info

        :rtype: tuple[List[Dict], Dict]
        """
        return (self.products(), self.info())

    def map(self, func: Callable[[Dict,Dict],Dict]) -> Self:
        """Runs the given function through all the products. The function
        must take a second argument, in which the extra info is inserted

        :param func: The function to modify each product
        :type func: Callable[[Dict,Dict],Dict]
        :returns: A new metainfo object (the current one is not modified!)
        :rtype: DSMetainfo
        """
        return self.with_products([
            func(product, self.info) for product in self.products
        ])

    def attach(self, **kwargs: Any|Callable[[Dict,Dict],Any]) -> Self:
        """Attaches the given keyword arguments to each product metainfo.
        If the keyword is a callable, it tries calling it with the following
        arguments: ``(product metainfo, extra info)`` and adds the result to the
        metainfo. If it is not, it simply adds the keyword value to the dict.

        :param kwargs: Some named values/function
        :type func: Callable[[Dict,Dict],Any]|Any
        :returns: A new metainfo object (the current one is not modified!)
        :rtype: DSMetainfo
        """
        return self.map(lambda product, info: product | {
            field: _make_into_func(func)(product, info)
            for field, func in kwargs.items()
        })
