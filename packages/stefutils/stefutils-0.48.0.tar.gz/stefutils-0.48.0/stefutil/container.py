"""
container operations, including functional, deep dictionary syntactic sugar
"""


import operator
import itertools
from typing import Tuple, List, Dict, Iterable, Callable, TypeVar, Any, Union
from functools import reduce
from collections import OrderedDict

from stefutil.primitive import is_int
from stefutil.prettier import style
from stefutil.packaging import _use_dl


__all__ = [
    'get', 'set_', 'it_keys',
    'list_is_same_elms', 'chain_its', 'join_it',
    'group_n', 'length_hint', 'split_n', 'list_split', 'lst2uniq_ids', 'compress',
    'np_index', 'describe', 'df_col2cat_col'
]


if _use_dl():
    __all__ += ['pt_sample']


T = TypeVar('T')
K = TypeVar('K')


Key = Union[int, str]


def _num_key2int(key: str = None, container: Union[dict, list, Any] = None) -> Key:
    """
    optionally converts a number key into int if
    1> the key indices into a list or
    2> the int version of the key exists in dict but not the str version
    """
    if is_int(key, allow_str=True):
        if isinstance(container, list):
            return int(key)
        elif isinstance(container, dict) and key not in container and int(key) in container:
            return int(key)

    return key


def _log_key_error(key: Key = None, container: Union[dict, list, Any] = None, past_keys: List[Key] = None):
    _past_keys = style.nc('=>', fg='m').join([style.nc(k) for k in past_keys])
    if isinstance(container, dict):
        available_ks = list(container.keys())
    else:
        assert isinstance(container, list)
        available_ks = f'[0,{len(container)-1}]'
    d_log = {'past keys': _past_keys, 'available keys': available_ks}
    raise ValueError(f'{style.nc(key)} not found at level {style.nc(len(past_keys)+1)} with {style.nc(d_log)}')


def get(container: Union[dict, list], ks: str = None):
    """
    :param container: Potentially multi-level dictionary/list
    :param ks: Potentially `.`-separated keys
    """
    if ks is None or ks in ['', '.']:
        return container
    else:
        ks = ks.split('.')
        _past_keys = []
        acc = container
        for lvl, k in enumerate(ks):
            k = _num_key2int(key=k, container=acc)

            if (isinstance(acc, list) and not (is_int(k) and 0 <= k < len(acc))) or \
                    (isinstance(acc, dict) and k not in acc):
                _log_key_error(key=k, container=acc, past_keys=_past_keys)
            acc = acc[k]
            _past_keys.append(k)
        return acc


def set_(container: Union[dict, list], ks: str = None, val: Any = None):
    def fn(acc, k):
        k = _num_key2int(key=k, container=acc)
        return acc[k]

    ks = ks.split('.')
    # node = reduce(lambda acc, elm: acc[elm], ks[:-1], dic)
    node = reduce(fn, ks[:-1], container)

    k_ = _num_key2int(key=ks[-1], container=node)
    node[k_] = val


def it_keys(dic, prefix=''):
    """
    :return: Generator for all potentially-nested keys
    """
    def _full(k_):
        return k_ if prefix == '' else f'{prefix}.{k_}'
    for k, v in dic.items():
        if isinstance(v, dict):
            for k__ in it_keys(v, prefix=_full(k)):
                yield k__
        else:
            yield _full(k)


def list_is_same_elms(lst: List[T]) -> bool:
    return all(l == lst[0] for l in lst)


def chain_its(its: Union[
    Iterable[Iterable[T]],
    Iterable[List[T]]
]) -> Iterable[T]:
    """
    Chain multiple iterables
    """
    out = itertools.chain()
    for it in its:
        out = itertools.chain(out, it)
    return out


def join_it(it: Iterable[T], sep: T) -> Iterable[T]:
    """
    Generic join elements with separator element, like `str.join`
    """
    it = iter(it)

    curr = next(it, None)
    if curr is not None:
        yield curr
        curr = next(it, None)
    while curr is not None:
        yield sep
        yield curr
        curr = next(it, None)


def length_hint(it: Iterable[T]) -> int:
    try:
        return len(it)  # Try to get the exact length
    except TypeError:
        # If obj doesn't support len(), try to get an estimated length
        return operator.length_hint(it, 0)


def group_n(it: Iterable[T], n: int) -> Iterable[Tuple[T]]:
    """
    Slice iterable into groups of size n (last group included) by iteration order
    """
    # Credit: https://stackoverflow.com/a/8991553/10732321
    it = iter(it)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def split_n(it: Iterable[T], n: int) -> Iterable[Tuple[T]]:
    """
    Split iterable into exactly `n` groups of as even sizes as possible
    """
    n_sample_per_group = len(list(it)) / n
    group_ordinal = 0
    curr_group = []
    for i, elm in enumerate(it):
        edge = (group_ordinal + 1) * n_sample_per_group
        if i + 0.5 < edge:
            curr_group.append(elm)
        else:
            yield tuple(curr_group)
            curr_group = [elm]
            group_ordinal += 1
    yield tuple(curr_group)


def list_split(lst: List[T], call: Callable[[T], bool]) -> List[List[T]]:
    """
    :return: Split a list by locations of elements satisfying a condition
    """
    return [list(g) for k, g in itertools.groupby(lst, call) if k]


def lst2uniq_ids(lst: List[T]) -> List[int]:
    """
    Each unique element in list assigned a unique id, in increasing order of iteration
    """
    elm2id = {v: k for k, v in enumerate(OrderedDict.fromkeys(lst))}
    return [elm2id[e] for e in lst]


def compress(lst: List[T]) -> List[Tuple[T, int]]:
    """
    :return: A compressed version of `lst`, as 2-tuple containing the occurrence counts
    """
    if not lst:
        return []
    return ([(lst[0], len(list(itertools.takewhile(lambda elm: elm == lst[0], lst))))]
            + compress(list(itertools.dropwhile(lambda elm: elm == lst[0], lst))))


def np_index(arr, idx):
    import numpy as np  # lazy import to save time
    return np.where(arr == idx)[0][0]


def describe(vals: Iterable, round_dec: int = None) -> Dict[str, Any]:
    import numpy as np  # lazy import to save time
    import pandas as pd
    vals: Union[List, np.ndarray]

    if round_dec is None:
        if any(isinstance(v, float) for v in vals):
            round_dec = 2

    df = pd.DataFrame(vals, columns=['value'])
    ret = df.describe().to_dict()['value']
    if round_dec:
        ret = {k: round(v, round_dec) for k, v in ret.items()}
    ret['count'] = int(ret['count'])
    return ret


def df_col2cat_col(df, col_name: str, categories: List[str]):
    """
    Enforced ordered categories to a column, the dataframe is modified in-place
    """
    import pandas as pd  # lazy import to save time
    from pandas.api.types import CategoricalDtype
    df: pd.DataFrame
    cat = CategoricalDtype(categories=categories, ordered=True)  # Enforce order by definition
    df[col_name] = df[col_name].astype(cat, copy=False)
    return df


if _use_dl():
    def pt_sample(d: Dict[K, Union[float, Any]]) -> K:
        """
        Sample a key from a dict based on confidence score as value
            Keys with confidence evaluated to false are ignored

        Internally uses `torch.multinomial`
        """
        import torch  # lazy import to save time
        d_keys = {k: v for k, v in d.items() if v}  # filter out `None`s
        keys, weights = zip(*d_keys.items())
        return keys[torch.multinomial(torch.tensor(weights), 1, replacement=True).item()]


if __name__ == '__main__':
    from icecream import ic

    def check_get():
        d = {'a': {'b': {'c': 1, 'd': 2}, 'e': 3}, 'f': 4}
        ic(d)
        ic(get(d, 'a.b.c'))

        ic(get(d, ''))
        ic(get(d, '.'))
        ic(get(d, None))
        ic(get(d))

        ic(get(d, 'a.b.e'))  # will raise error
    # check_get()

    def check_get_int():
        d = {'a': {1: 2}, 1: 3}
        ic(d)
        ic(get(d, 'a.1'))

        d = {'a': ['b', 'c', {'d': 'e'}]}
        ic(d)
        ic(get(d, 'a.2.d'))
    # check_get_int()

    def check_set_int():
        d = {'a': {1: 2}, 'b': {1: 3}}
        ic(d)
        set_(d, 'b.1', 4)
        ic(d)

        d = {'a': ['b', 'c', {'d': 'e'}]}
        ic(d)
        set_(d, 'a.2.d', 'f')
        ic(d)
    # check_set_int()

    def check_split_n():
        def _test(n_it: int = None, n: int = None):
            ret = list(split_n(range(n_it), n))
            ic(len(ret))
            assert len(ret) == n
            ic([len(elms) for elms in ret])
            assert sum(len(elms) for elms in ret) == n_it
        _test(n_it=16, n=3)
        _test(n_it=156602, n=100)
        _test(n_it=156602, n=1000)
    # check_split_n()

    def check_desc():
        lst = [1, 2, 3]
        ic(describe(lst))

        lst = [1, 2.2, 3.3, 4.4, 5.5]
        ic(describe(lst))
    check_desc()

    def check_chain():
        import time
        import random

        from stefutil.prettier import tqdc

        lsts = [
            [1, 2, 3],
            [3, 4, 5],
            [5, 6, 7]
        ]
        ic(list(chain_its(lsts)))
        for item in tqdc(chain_its(lsts)):
            time.sleep(random.random())
            ic(item)
    # check_chain()
