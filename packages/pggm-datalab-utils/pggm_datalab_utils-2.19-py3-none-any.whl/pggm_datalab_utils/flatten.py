from typing import Iterable, Any, List
from itertools import accumulate
import operator as op


def flatten(it: Iterable[Iterable[Any]]) -> List[Any]:
    """
    Flatten a list of lists, or any kind of nested iterable, into a single list.
    """
    return [x for item in it for x in item]


def flatten_with_mapping(it: Iterable[List[Any]]) -> (List[Any], List[int]):
    """
    Flatten a list of lists, or any kind of nested iterable, into a single list, additionally returning the lengths
    of each of the items, allowing you to restore the original list of lists using `unflatten`.
    We test that `unflatten(*flatten_with_mapping(x)) == x` and vice versa.
    """
    return [x for item in it for x in item], [len(item) for item in it]


def unflatten(flattened: List[Any], mapping: List[int]) -> List[List[Any]]:
    """
    Unflatten a list, breaking it into sublists of length indicated by `mapping`.
    We test that `unflatten(*flatten_with_mapping(x)) == x` and vice versa.
    """
    indices = list(accumulate(mapping, op.add))
    return [flattened[start:end] for start, end in zip([0] + indices[:-1], indices)]
