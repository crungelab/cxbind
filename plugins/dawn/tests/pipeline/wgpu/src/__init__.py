__version__ = "0.1.0"

from crunge import core

core.add_plugin(__file__)

from ._wgpu import *
#from ._wgpu import create_proc_table

#create_proc_table()

from .generated import *

from . import instance
from .context import Context
