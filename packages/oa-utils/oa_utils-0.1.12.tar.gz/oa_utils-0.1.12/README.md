# oa-utils

Statically typed Python utilities for functional programming.

## Pipeline

This class is useful for programming in the [collection pipeline](https://martinfowler.com/articles/collection-pipeline/) style. It wraps a homogenous variadic tuple and exposes a fluent interface with common functional programming operations. Why a tuple and not a "lazy" iterator? Because a tuple is relatively immutable and because, in my opinion, reified collections are much easier to reason about than stateful iterators.

```python
from oa_utils.pipeline import Pipeline

result = (Pipeline(range(10))
            .filter(lambda x: x % 2 == 0)
            .map(lambda x: x * x)
            .sum()) # 120
```

See [pipeline.py](https://github.com/OlegAlexander/oa-utils/blob/main/oa_utils/pipeline.py) for docstrings and doctests of every method.