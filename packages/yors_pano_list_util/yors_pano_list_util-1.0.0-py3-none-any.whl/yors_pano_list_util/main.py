import random
from typing import List, Any, Tuple

def ListDelExclude(start: int, oldlist: List[Any], exclist: List[Any], newlist: List[Any]) -> List[Any]:
    """
    Recursively remove elements from oldlist that are present in the corresponding position of exclist.

    Args:
        start (int): The starting index for the recursive operation.
        oldlist (List[Any]): The original list from which elements may be removed.
        exclist (List[Any]): The list containing elements to be excluded.
        newlist (List[Any]): The list to store the result.

    Returns:
        List[Any]: A new list with excluded elements removed.
    """
    if start == len(oldlist):
        return newlist  # base condition

    if not (exclist[start] in oldlist):  # checking if
        newlist.append(oldlist[start])
    return ListDelExclude(start + 1, oldlist, exclist, newlist)

def ListFillOne(value: Any, count: int = 20) -> List[Any]:
    """
    Create a list filled with a specified value repeated a given number of times.

    Args:
        value (Any): The value to fill the list with.
        count (int, optional): The number of times to repeat the value. Defaults to 20.

    Returns:
        List[Any]: A list filled with the specified value.

    Example:
        ListFillOne('STRING', TEXT_BASE_COLORS_COUNT)
    """
    return [value] * count

def ListToTupe(list: List[Any]) -> Tuple[Any, ...]:
    """
    Convert a list to a tuple.

    Args:
        list (List[Any]): The list to be converted.

    Returns:
        Tuple[Any, ...]: A tuple containing the same elements as the input list.

    Example:
        ListToTupe(ListFillOne('STRING', TEXT_BASE_COLORS_COUNT))
    """
    return tuple(list)

def ListShuffle(l: List[Any], keep_n: int = 0) -> List[Any]:
    """
    Shuffle a list while keeping the first n elements in their original positions.

    Args:
        l (List[Any]): The list to be shuffled.
        keep_n (int, optional): The number of elements to keep at the beginning. Defaults to 0.

    Returns:
        List[Any]: A new shuffled list with the first n elements unchanged.

    Example:
        ListShuffle(textl, int(keep_n_token))
    """
    el = l.copy()
    index = keep_n
    if index >= 1:
        el = l[index:]
    random.shuffle(el)
    if index >= 1:
        el = l[0:index] + el
    return el
