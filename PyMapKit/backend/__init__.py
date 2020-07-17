#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: July 17, 2020
"""

def get_backend(backend):
    """
    Imports and returns the backend renderer from the given backend name.

    It a backend does not exist, backend passes through; assuming user is using a custom backend.  
    """
    if backend in ('cairo', 'pycairo'):
        from .CairoBackend import CairoBackend
        return CairoBackend()

    elif backend in ('tk', 'tkcanvas', 'tkinter'):
        from .TkBackend import TkBackend
        return TkBackend()

    else:
        return backend