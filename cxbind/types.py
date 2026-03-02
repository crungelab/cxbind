from typing import Callable, Optional

from .render_stream import RenderStream

Handled = Optional[bool]

RenderFn = Callable[[RenderStream], None]
