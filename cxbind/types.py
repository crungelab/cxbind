from typing import Callable

from .emission import Emission

EmitFn = Callable[[Emission], None]