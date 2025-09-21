from typing import Callable, Optional

from .emission import Emission

Handled = Optional[bool]

EmitFn = Callable[[Emission], None]
