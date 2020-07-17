#!/usr/bin/env python3
"""
Author: Ben Knisley [benknisley@gmail.com]
Date: July 17, 2020

"""

def get_backend(backend):
    if backend in ('cairo', 'pycairo'):
        from .CairoPainter import CairoBackend
        return CairoBackend()

    elif backend in ('tk', 'tkcanvas', 'tkinter'):
        from .TkPainter import TkBackend
        return TkBackend()

    else:
        return backend