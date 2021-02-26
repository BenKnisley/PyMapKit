"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 25 February, 2020
"""
import pytest
import pymapkit as pmk
import skia


def test_init():
    """ Test SkiaRenderer.__init__ """
    r = pmk.SkiaRenderer()
    assert isinstance(r, pmk.SkiaRenderer)


def test_new_canvas():
    """ Test SkiaRenderer.new_canvas """
    r = pmk.SkiaRenderer()
    canvas = r.new_canvas(800, 600)

    assert isinstance(r.surface, skia.Surface)
    assert isinstance(canvas, skia.Canvas)
    assert r.surface.width() == 800
    assert r.surface.height() == 600


def test_is_canvas():
    """ Test SkiaRenderer.is_canvas """
    r = pmk.SkiaRenderer()

    canvas = r.new_canvas(800, 600)
    s = skia.Surface(50,50)
    canvas2 = s.getCanvas()

    assert r.is_canvas(canvas) == True
    assert r.is_canvas(canvas2) == True
    assert r.is_canvas(object()) == False
    assert r.is_canvas("Hello") == False
    assert r.is_canvas(None) == False
