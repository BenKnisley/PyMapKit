"""
Project: PyMapKit
Title: Backend submodule __init__ file
Function: Provide 'backend' namespace and get_backend function.
Author: Ben Knisley [benknisley@gmail.com]
Created: 17 July, 2020
"""
from .base_backend import BaseBackend


def get_backend(backend):
    """
    Imports and returns the backend renderer from the given backend name.

    It a backend does not exist, backend passes through; assuming user is using a custom backend.  
    """
    if backend in ('cairo', 'pycairo'):
        from .cairo_backend import CairoBackend
        return CairoBackend()

    elif backend in ('tk', 'tkcanvas', 'tkinter'):
        from .tk_backend import TkBackend
        return TkBackend()
    
    elif backend in ('skia', 'pyskia'):
        from .skia_backend import SkiaBackend
        return SkiaBackend()


    else:
        ## If backend is not found, assume user is using there own
        return backend