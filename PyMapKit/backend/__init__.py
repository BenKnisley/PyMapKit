"""
Project: PyMapKit
Title: Backend submodule __init__ file
Function: Provide 'backend' namespace and get_backend function.
Author: Ben Knisley [benknisley@gmail.com]
Created: 17 July, 2020
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
        ## If backend is not found, assume user is using there own
        return backend