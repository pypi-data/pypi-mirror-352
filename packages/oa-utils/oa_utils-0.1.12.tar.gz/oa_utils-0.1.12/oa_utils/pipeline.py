from __future__ import annotations
import functools
import itertools
import more_itertools
import json
from pprint import pprint, pformat
from tabulate import tabulate
from collections import defaultdict
from typing import IO, Callable, Iterable, Sequence, Literal, TypeVar, Any
from dataclasses import dataclass

@dataclass
class Vector2:
    """Used for testing."""
    x: float
    y: float

def default_json_encoder(obj: Any) -> Any:
    return vars(obj) if hasattr(obj, '__dict__') else str(obj)

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
K = TypeVar("K")

class Pipeline(tuple[T_co, ...]):
    """This class is useful for programming in the *collection pipeline* style.
    It wraps a homogenous variadic tuple and exposes a fluent interface with 
    common functional programming operations. Why a tuple and not a "lazy" iterator? 
    Because a tuple is relatively immutable and because, in my opinion, 
    reified collections are much easier to reason about than stateful iterators.
        
    >>> (Pipeline(range(10))
    ... .filter(lambda x: x % 2 == 0)
    ... .map(lambda x: x * x)
    ... .sum())                      
    120
    """

    def map(self, fn: Callable[[T_co], U]) -> Pipeline[U]:
        """Apply *fn* to every element.
        
        >>> Pipeline([1, 2, 3]).map(lambda x: x * 2)
        (2, 4, 6)
        """
        return Pipeline(map(fn, self))

    def filter(self, pred: Callable[[T_co], bool]) -> Pipeline[T_co]:
        """Keep only elements for which *pred* returns True.
        
        >>> Pipeline([1, 2, 3, 4]).filter(lambda x: x % 2 == 0)
        (2, 4)
        """
        return Pipeline(filter(pred, self))

    def zip(self, other: Iterable[U], strict: bool = False) -> Pipeline[tuple[T_co, U]]:
        """Pair each element with the corresponding element from *other* (like :func:`zip`).
        
        >>> Pipeline([1, 2]).zip([10, 20])
        ((1, 10), (2, 20))
        """
        return Pipeline(zip(self, other, strict=strict))

    def zip_longest(self, other: Iterable[U], fillvalue: V) -> Pipeline[tuple[T_co | V, U | V]]:
        """Zip two iterables, filling missing positions with *fillvalue* (like :func:`itertools.zip_longest`).
        
        >>> Pipeline([1, 2]).zip_longest([10, 20, 30], fillvalue=None)
        ((1, 10), (2, 20), (None, 30))
        
        >>> Pipeline([1, 2, 3]).zip_longest([10, 20], fillvalue=0)
        ((1, 10), (2, 20), (3, 0))
        """
        return Pipeline(itertools.zip_longest(self, other, fillvalue=fillvalue))

    def zip_with(self, fn: Callable[[T_co, U], V], other: Iterable[U], strict: bool = False) -> Pipeline[V]:
        """Zip with *other* and immediately combine pairs using *fn*.
        
        >>> Pipeline([1, 2]).zip_with(lambda a, b: a + b, [10, 20])
        (11, 22)
        """
        return Pipeline(fn(a, b) for a, b in zip(self, other, strict=strict))

    def join_with(self: Pipeline[T], separator: T) -> Pipeline[T]:
        """Join elements with a *separator*.
        
        >>> Pipeline([1, 2, 3]).join_with(0)
        (1, 0, 2, 0, 3)
        """
        if not self:
            return Pipeline([])
        return Pipeline(itertools.chain.from_iterable(
            (item, separator) for item in self[:-1])).append(self[-1])

    def starmap(self: Pipeline[tuple[T, U]], fn: Callable[[T, U], V]) -> Pipeline[V]:
        """Apply *fn* to tuples, unpacking each element (2-tuple version of :func:`itertools.starmap`).
        
        >>> Pipeline([(1, 2), (3, 4)]).starmap(lambda a, b: a + b)
        (3, 7)
        """
        if not all(isinstance(item, tuple) and len(item) == 2 for item in self):
            raise ValueError("starmap requires a Pipeline of tuples with 2 elements")
        return Pipeline(fn(a, b) for a, b in self) 

    def cartesian_product(self, other: Iterable[U]) -> Pipeline[tuple[T_co, U]]:
        """Return the Cartesian product of *self* x *other*.
        
        >>> Pipeline([1, 2]).cartesian_product([10, 20])
        ((1, 10), (1, 20), (2, 10), (2, 20))
        """
        return Pipeline(itertools.product(self, other))

    def sort(self, key: Callable[[T_co], Any] | None = None, reverse: bool = False) -> Pipeline[T_co]:
        """Sort the elements.
        
        >>> Pipeline([3, 1, 2]).sort()
        (1, 2, 3)
        
        >>> Pipeline([3, 1, 2]).sort(reverse=True)
        (3, 2, 1)
        """
        return Pipeline(sorted(self, key=key, reverse=reverse)) # type: ignore

    def unique(self) -> Pipeline[T_co]:
        """Remove duplicates while preserving order.
        
        >>> Pipeline([1, 2, 2, 3]).unique()
        (1, 2, 3)
        """
        return Pipeline(dict.fromkeys(self))
    
    def slice(self, start: int = 0, end: int | None = None, step: int = 1) -> Pipeline[T_co]:
        """Return a slice of the pipeline like *self[start:end:step]*.
        
        >>> Pipeline([1, 2, 3, 4, 5]).slice(1, 4)
        (2, 3, 4)
        """
        if end is None:
            end = len(self)
        return Pipeline(self[start:end:step])

    def take(self, n: int) -> Pipeline[T_co]:
        """Return the first *n* items.
        
        >>> Pipeline([1, 2, 3, 4]).take(2)
        (1, 2)

        >>> Pipeline([1, 2, 3, 4]).take(-1)
        (1, 2, 3)
        """
        return Pipeline(self[:n])
    
    def drop(self, n: int) -> Pipeline[T_co]:
        """Drop the first *n* items.

        >>> Pipeline([1, 2, 3, 4]).drop(2)
        (3, 4)

        >>> Pipeline([1, 2, 3, 4]).drop(-3)
        (2, 3, 4)
        """
        return Pipeline(self[n:])

    def enumerate(self, start: int = 0) -> Pipeline[tuple[int, T_co]]:
        """Enumerate the pipeline, yielding (index, item) pairs.
        
        >>> Pipeline(['a', 'b']).enumerate()
        ((0, 'a'), (1, 'b'))
        """
        return Pipeline(enumerate(self, start))

    def batch(self, n: int, strict: bool = False) -> Pipeline[Pipeline[T_co]]:
        """Group the data into fixed-size chunks. Like :func:`more_itertools.chunked`.
        
        >>> Pipeline(range(1, 6)).batch(2)
        ((1, 2), (3, 4), (5,))
        """
        return Pipeline([Pipeline(batch) for batch 
                         in more_itertools.chunked(self, n, strict=strict)])
    
    def batch_fill(self, n: int, 
                   fillvalue: U,
                   incomplete: Literal['fill', 'ignore', 'strict'] = 'fill') -> Pipeline[Pipeline[T_co | U]]:
        """Batch with padding via *fillvalue* (delegate to :func:`more_itertools.grouper`).
        
        >>> Pipeline(range(1, 6)).batch_fill(2, fillvalue=0)
        ((1, 2), (3, 4), (5, 0))
        """
        return Pipeline([Pipeline(row) for row in more_itertools.grouper(
                        self, n, incomplete=incomplete, fillvalue=fillvalue)])

    def flatten(self: Pipeline[Iterable[T]]) -> Pipeline[T]:
        """Flatten one level of nesting.
        
        >>> Pipeline([[1, 2], [3, 4]]).flatten()
        (1, 2, 3, 4)
        """
        if not all(isinstance(item, Iterable) for item in self):
            raise ValueError("flatten requires a Pipeline of Iterables")
        return Pipeline(itertools.chain.from_iterable(self))

    def for_each(self, fn: Callable[[T_co], None]) -> Pipeline[T_co]:
        """Call a side-effecting function for every element and return self.
        
        >>> Pipeline([1, 2, 3]).for_each(print)
        1
        2
        3
        (1, 2, 3)
        """
        for item in self:
            fn(item)
        return self

    def for_self(self, fn: Callable[[Pipeline[T_co]], None]) -> Pipeline[T_co]:
        """Call *fn(self)* for its side-effects and return self.
        
        >>> Pipeline([1, 2, 3]).for_self(lambda p: print(p.len()))
        3
        (1, 2, 3)
        """
        fn(self)
        return self

    def apply(self, fn: Callable[[Iterable[T_co]], Iterable[U]]) -> Pipeline[U]:
        """Apply an external iterable-to-iterable function (e.g. from *itertools* or *more_itertools*).
        To preserve type safety, it is recommended to use a type hint for *fn*.
        
        >>> transpose: Callable[[Iterable[Iterable[int]]], Iterable[tuple[int, ...]]] = more_itertools.transpose
        >>> Pipeline([[1, 2, 3], [4, 5, 6]]).apply(transpose)
        ((1, 4), (2, 5), (3, 6))
        
        >>> pairwise: Callable[[Iterable[int]], Iterable[tuple[int, int]]] = itertools.pairwise
        >>> Pipeline([1, 2, 3]).apply(pairwise)
        ((1, 2), (2, 3))
        """
        return Pipeline(fn(self))

    def print(self, label: str = "", 
              label_only: bool = False,
              end: str | None = "\n",
              file: IO[str] | None = None,
              flush: bool = False) -> Pipeline[T_co]:
        """Print the pipeline (optionally with a *label*) and return *self*.
        
        >>> Pipeline([1, 2, 3]).print("Numbers: ", end="\\n\\n")
        Numbers: (1, 2, 3)
        <BLANKLINE>
        (1, 2, 3)
        
        >>> Pipeline([1, 2, 3]).print("Numbers:", label_only=True)
        Numbers:
        (1, 2, 3)
        """
        if label_only:
            print(label, end=end, file=file, flush=flush)
        else:
            print(f"{label}{self}", end=end, file=file, flush=flush)
        return self

    def pprint(self, label: str = "", end: str = "",
               stream: IO[str] | None = None, 
               indent: int = 1, width: int = 80, 
               depth: int | None = None, 
               compact: bool = False, 
               sort_dicts: bool = True, 
               underscore_numbers: bool = False) -> Pipeline[T_co]:
        """Pretty-print the pipeline with :pymeth:`pprint.pprint`.
        
        >>> Pipeline([1, 2, 3]).pprint("Numbers:" , end="---------")
        Numbers:
        (1, 2, 3)
        ---------
        (1, 2, 3)
        """
        if label:
            print(label, file=stream)
        pprint(self, stream=stream, indent=indent, width=width,
               depth=depth, compact=compact, sort_dicts=sort_dicts,
               underscore_numbers=underscore_numbers)
        if end:
            print(end, file=stream)
        return self

    def print_json(self, label: str = "", end: str = "", 
                   stream: IO[str] | None = None, 
                   indent: int | str | None = 2,
                   default: Callable[[Any], Any] = default_json_encoder) -> Pipeline[T_co]:
        """Print the pipeline as JSON (with an optional *label*).
        
        >>> Pipeline([1, 2, 3]).print_json()
        [
          1,
          2,
          3
        ]
        (1, 2, 3)
        
        >>> Pipeline([Vector2(1.0, 2.0)]).print_json()
        [
          {
            "x": 1.0,
            "y": 2.0
          }
        ]
        (Vector2(x=1.0, y=2.0),)
        """
        if label:
            print(label, file=stream)
        print(json.dumps(self, indent=indent, default=default), file=stream)
        if end:
            print(end, file=stream)
        return self

    def print_table(self: Pipeline[T_co], label: str = "", end: str = "",
                    stream: IO[str] | None = None,
                    headers: str | dict[Any, str] | Sequence[str] = "keys",
                    tablefmt: str = "github",
                    floatfmt: str | Iterable[str] = "g",
                    intfmt: str | Iterable[str] = "",
                    numalign: str | None = "default",
                    stralign: str | None = "default",
                    missingval: str | Iterable[str] = "",
                    showindex: str | bool | Iterable[Any] = "default",
                    disable_numparse: bool | Iterable[int] = False,
                    colalign: Iterable[str | None] | None = None,
                    maxcolwidths: int | Iterable[int | None] | None = None,
                    rowalign: str | Iterable[str] | None = None,
                    maxheadercolwidths: int | Iterable[int] | None = None) -> Pipeline[T_co]:
        """Print a pipeline of "rows" as a table (with an optional *label*).
        
        >>> Pipeline([{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]).print_table()
        | name   |   age |
        |--------|-------|
        | Alice  |    30 |
        | Bob    |    25 |
        ({'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25})
        
        
        >>> Pipeline([Vector2(1.0, 2.0), Vector2(3.0, 4.0)]).print_table(showindex=True)
        |    |   x |   y |
        |----|-----|-----|
        |  0 |   1 |   2 |
        |  1 |   3 |   4 |
        (Vector2(x=1.0, y=2.0), Vector2(x=3.0, y=4.0))
        """
        if label:
            print(label, file=stream)
        print(tabulate(self, # type: ignore
                       headers=headers, 
                       tablefmt=tablefmt, 
                       floatfmt=floatfmt, 
                       intfmt=intfmt, 
                       numalign=numalign, 
                       stralign=stralign, 
                       missingval=missingval, 
                       showindex=showindex, 
                       disable_numparse=disable_numparse,
                       colalign=colalign,
                       maxcolwidths=maxcolwidths,
                       rowalign=rowalign,
                       maxheadercolwidths=maxheadercolwidths), file=stream)
        if end:
            print(end, file=stream)
        return self

    def append(self, item: T) -> Pipeline[T_co | T]:
        """Return a new pipeline with *item* appended.
        
        >>> Pipeline([1, 2]).append(3)
        (1, 2, 3)
        """
        return Pipeline(self + (item,))

    def prepend(self, item: T) -> Pipeline[T_co | T]:
        """Return a new pipeline with *item* prepended.
        
        >>> Pipeline([2, 3]).prepend(1)
        (1, 2, 3)
        """
        return Pipeline((item,) + self)

    def extend(self, items: Iterable[T_co]) -> Pipeline[T_co]:
        """Concatenate *items* onto the end of a pipeline.
        
        >>> Pipeline([1, 2]).extend([3, 4])
        (1, 2, 3, 4)
        """
        return Pipeline(self + tuple(items))
    
    def insert(self, index: int, item: T) -> Pipeline[T_co | T]:
        """Insert an *item* at *index*.
        
        >>> Pipeline([1, 2, 4]).insert(2, 3)
        (1, 2, 3, 4)
        """
        return Pipeline(self[:index] + (item,) + self[index:])
    
    def reverse(self) -> Pipeline[T_co]:
        """Reverse the order of the elements.
        
        >>> Pipeline([1, 2, 3]).reverse()
        (3, 2, 1)
        """
        return Pipeline(reversed(self))

    def group_by(self, key: Callable[[T_co], K]) -> Pipeline[tuple[K, Pipeline[T_co]]]:
        """Group elements by *key* and return (key, subgroup) pairs.
        Use to_dict() to convert the pairs to a dictionary.
        
        >>> names = ['Roger', 'Alice', 'Adam', 'Bob']
        >>> Pipeline(names).group_by(lambda name: name[0])
        (('R', ('Roger',)), ('A', ('Alice', 'Adam')), ('B', ('Bob',)))
        
        >>> people = [{'name': 'Roger', 'age': 25},
        ...           {'name': 'Alice', 'age': 25},
        ...           {'name': 'Bob', 'age': 11}]
        >>> Pipeline(people).group_by(lambda person: person['age'])
        ((25, ({'name': 'Roger', 'age': 25}, {'name': 'Alice', 'age': 25})), (11, ({'name': 'Bob', 'age': 11},)))
        
        >>> Pipeline(range(10)).group_by(lambda x: x % 2 == 0)
        ((True, (0, 2, 4, 6, 8)), (False, (1, 3, 5, 7, 9)))
        """
        grouped: defaultdict[K, list[T_co]] = defaultdict(list)
        for item in self:
            grouped[key(item)].append(item)
        return Pipeline((k, Pipeline(v)) for k, v in grouped.items())

    # === Terminal methods ===

    def to_list(self) -> list[T_co]:
        """Convert to a list`.
        
        >>> Pipeline([1, 2, 3]).to_list()
        [1, 2, 3]
        """
        return list(self)

    def to_set(self) -> set[T_co]:
        """Convert to a set, removing duplicates.
        
        >>> Pipeline([1, 2, 3, 3]).to_set()
        {1, 2, 3}
        """
        return set(self)

    def to_dict(self: Pipeline[tuple[K, V]]) -> dict[K, V]:
        """Convert a pipeline of (key, value) tuples to a dict.
        
        >>> Pipeline([("a", 1), ("b", 2)]).to_dict()
        {'a': 1, 'b': 2}
        """
        return dict(self)

    def to_json(self, indent: int | str | None = 2, 
                default: Callable[[Any], Any] = default_json_encoder) -> str:
        """Serialize the pipeline to a JSON string.
        
        >>> Pipeline([1, 2, 3]).to_json()
        '[\\n  1,\\n  2,\\n  3\\n]'
        
        >>> Pipeline([Vector2(1.0, 2.0)]).to_json()
        '[\\n  {\\n    "x": 1.0,\\n    "y": 2.0\\n  }\\n]'
        """
        return json.dumps(self, indent=indent, default=default)

    def to_pformat(self, indent: int = 1, 
                   width: int = 80, 
                   depth: int | None = None, 
                   compact: bool = False, 
                   sort_dicts: bool = True, 
                   underscore_numbers: bool = False) -> str:
        """Return the pretty-formatted string representation of the pipeline.
                
        >>> Pipeline([Vector2(1.0, 2.0), Vector2(3.0, 4.0)]).to_pformat()
        '(Vector2(x=1.0, y=2.0), Vector2(x=3.0, y=4.0))'
        """
        return pformat(self, indent=indent, width=width, depth=depth, compact=compact, 
                       sort_dicts=sort_dicts, underscore_numbers=underscore_numbers)

    def first(self) -> T_co:
        """Return the first element.
        >>> Pipeline([1, 2, 3]).first()
        1
        """
        if not self:
            raise IndexError("Pipeline is empty")
        return self[0]
    
    def last(self) -> T_co:
        """Return the last element.
        
        >>> Pipeline([1, 2, 3]).last()
        3
        """
        if not self:
            raise IndexError("Pipeline is empty")
        return self[-1]

    def reduce(self, fn: Callable[[V, T_co], V], initial: V) -> V:
        """Reduce the pipeline to a single value using *fn*.
        
        >>> Pipeline([104, 101, 108, 108, 111]).reduce(lambda acc, x: acc + chr(x), "")     
        'hello'
        """
        return functools.reduce(fn, self, initial)

    def reduce_non_empty(self, fn: Callable[[T_co, T_co], T_co]) -> T_co:
        """Reduce a non-empty pipeline to a single value using *fn*.
        
        >>> Pipeline([1, 2, 3]).reduce_non_empty(lambda acc, x: acc + x)
        6
        """
        if not self:
            raise ValueError("Pipeline is empty")
        return functools.reduce(fn, self)

    def len(self) -> int:
        """Return the length of the pipeline.
        
        >>> Pipeline([1, 2, 3]).len()
        3
        """
        return len(self)
    
    def min(self) -> T_co:
        """Return the minimum element.
        
        >>> Pipeline([3, 1, 2]).min()
        1
        """
        return min(self) # type: ignore 
    
    def max(self) -> T_co:
        """Return the maximum element.
        
        >>> Pipeline([3, 1, 2]).max()
        3
        """
        return max(self) # type: ignore
    
    def sum(self) -> T_co:
        """Return the sum of the elements.
        
        >>> Pipeline([1, 2, 3]).sum()
        6
        """
        return sum(self) # type: ignore
    
    def avg(self) -> float:
        """Return the average of the elements.
        
        >>> Pipeline([1, 2, 3]).avg()
        2.0
        """
        if not self:
            raise ValueError("Pipeline is empty")
        return sum(self) / len(self) # type: ignore
    
    def any(self) -> bool:
        """Return True if any element is True.
        
        >>> Pipeline([False, False, True]).any()
        True
        
        >>> Pipeline([False, False, False]).any()
        False
        """
        return any(self)
    
    def all(self) -> bool:
        """Return True if all elements are True.
        
        >>> Pipeline([True, True, True]).all()
        True
        
        >>> Pipeline([True, False, True]).all()
        False
        """
        return all(self)
    
    def contains(self, item: T) -> bool:
        """Return True if *item* is in the pipeline.
        
        >>> Pipeline([1, 2, 3]).contains(2)
        True
        
        >>> Pipeline([1, 2, 3]).contains(4)
        False
        """
        return item in self

if __name__ == "__main__":
    # Interpreter usage: 
    # from importlib import reload; import oa_utils.pipeline; reload(oa_utils.pipeline); from oa_utils.pipeline import Pipeline
    import doctest
    doctest.testmod()
    