'''
# hintwith
Hints your function with an existing one.

## Usage

Use `hintwith()` to hint a function with another function:

```py
>>> from hintwith import hintwith
>>> def a(x: int, y: int, z: int = 0) -> int:
...     """Sums x, y and z."""
...     return x + y + z
...
>>> @hintwith(a)
... def b(*args, **kwargs) -> float:
...     return float(a(*args, **kwargs))
...
```

Also, there is `hintwithmethod()` to hint the function with a method rather than a
direct callable.

## See Also
### Github repository
* https://github.com/Chitaoji/hintwith/

### PyPI project
* https://pypi.org/project/hintwith/

## License
This project falls under the BSD 3-Clause License.

'''

from .__version__ import __version__
from .core import *
from .core import __all__
