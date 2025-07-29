from typing import List, TypeVar

T = TypeVar("T")


def pop_all(left: List[T]):
    result, left[:] = left[:], []
    return result
