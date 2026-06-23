"""
	Author: GianC-Dev <gianegekck@gmail.com>
					  _    _
					 | |  | |
					 | |__| | __ ___   ____ _
					 |  __  |/ _` \ \ / / _` |
					 | |  | | (_| |\ V / (_| |
					 |_|  |_|\__,_| \_/ \__,_|
      
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.
"""

import sys

class AST(object):
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        mod = sys.modules[cls.__module__]
        if not hasattr(cls, '__annotations__'):
            return

        hints = list(cls.__annotations__.items())

        def __init__(self, *args, **kwargs):
            if len(hints) != len(args):
                raise TypeError(f'Expected {len(hints)} arguments')
            for arg, (name, val) in zip(args, hints):
                if isinstance(val, str):
                    val = getattr(mod, val)
                if not isinstance(arg, val):
                    raise TypeError(f'{name} argument must be {val}')
                setattr(self, name, arg)

        cls.__init__ = __init__

