import functools
import math
import operator
from typing import *

from tqdm import tqdm


def do_flatten_list(list_of_list: List[List[Any]]) -> List[Any]:
    """Flatten a list of list to a list

    :param list_of_list: list to flatten
    :type list_of_list: List[List[Any]]
    :return: flatten list
    :rtype: List[Any]
    """
    return functools.reduce(operator.iconcat, list_of_list, [])


def map_many(functions: List, iterable: List[Any]) -> List[Any]:
    return list(functools.reduce(lambda x, y: map(y, x), functions, iterable))


def get(items: List[Any], idx: int, default: Any = "") -> Any:
    if idx < 0:
        return default
    try:
        return items[idx]
    except IndexError:
        return default


def divide_into_chunks(
    lst: Union[List[Any], Dict], num_chunks: int
) -> Union[List[Any], Dict]:
    num_of_items_in_chunk = math.ceil(len(lst) / num_chunks)
    if isinstance(lst, dict):
        # Convert dict items to a list of key-value tuples, split them, and then convert back to a list of dictionaries
        items = list(lst.items())
        divided_chunks = [
            dict(items[i : i + num_of_items_in_chunk])
            for i in range(0, len(items), num_of_items_in_chunk)
        ]
    elif isinstance(lst, list):
        divided_chunks = [
            lst[i : i + num_of_items_in_chunk]
            for i in range(0, len(lst), num_of_items_in_chunk)
        ]
    return divided_chunks


def chunks(
    iterator: Union[Iterable[Any], List[Any]],
    chunk_size: int,
    show_progress: bool = False,
) -> Iterable[List[Any]]:
    """Yield successive n-sized chunks from iterator."""
    if show_progress:
        iterator = tqdm(iterator)
    chunk = []
    for x in iterator:
        chunk.append(x)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if len(chunk) > 0:
        yield chunk


def safe_zip(*args: List[Iterable]) -> Iterable[tuple]:
    item_len = 0
    for idx, arg in enumerate(args):
        if idx == 0:
            # Save the length of first item
            item_len = len(arg)
        else:
            # Check if all items have the same length
            if len(arg) != item_len:
                raise ValueError("All arguments must have the same length")
    return zip(*args)
