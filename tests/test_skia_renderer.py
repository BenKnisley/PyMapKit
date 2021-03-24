"""
Author: Ben Knisley [benknisley@gmail.com]
Date: 25 February, 2020
"""
import pytest
from unittest.mock import MagicMock
import pymapkit as pmk
import skia

class mock_skia_image:
    def __init__(self):
        self.save = MagicMock()

class mock_surface:
    def __init__(self):
        self.image_mock = mock_skia_image()
        self.makeImageSnapshot = MagicMock()
        self.makeImageSnapshot.return_value = self.image_mock

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


def test_save():
    """ Test SkiaRenderer.save """
    ## Setup
    r = pmk.SkiaRenderer()
    canvas = r.new_canvas(800, 600)
    output = "./test.png"

    ## Replace real surface with mock surface
    r.surface = mock_surface()
    
    ## Tests that a none output, does not call mocked fns
    r.save(canvas, None)
    r.surface.makeImageSnapshot.assert_not_called()
    r.surface.image_mock.save.assert_not_called()

    ## Reset Mocks after first test
    r.surface.makeImageSnapshot.reset_mock()
    r.surface.image_mock.save.reset_mock()

    ## Tests that a str output, calls functions correctly
    r.save(canvas, output)
    r.surface.makeImageSnapshot.assert_called_once()
    r.surface.image_mock.save.assert_called_once_with(output, skia.kPNG)

 
def test_cache_color():
    """ Test SkiaRenderer.cache_color """
    r = pmk.SkiaRenderer()

    ## Test caching color names
    result = r.cache_color("red")
    expected = 4294901760
    assert result == expected

    result = r.cache_color("teal")
    expected = 4278222976
    assert result == expected

    ## Test with opacity 
    result = r.cache_color("teal", 0.5)
    expected = 2130739328
    assert result == expected

    ## Test with Hex string color
    result = r.cache_color("#8B5EA0")
    expected = 4287323808
    assert result == expected

    ## Test with Hex string color and opacity
    result = r.cache_color("#8B5EA0", 0.4)
    expected = 1720409760
    assert result == expected

    ## Test with tuple input color
    result = r.cache_color((139, 94, 160))
    expected = 4287323808
    assert result == expected

    ## Test with tuple input color and opacity
    result = r.cache_color((139, 94, 160), 0.4)
    expected = 1720409760
    assert result == expected

    ## Test with float tuple input color
    result = r.cache_color((0.55, 0.36, 0.62))
    expected = 4287388574
    assert result == expected


    ## Test with float tuple input color
    result = r.cache_color((0.55, 0.36, 0.62), 0.33)
    expected = 1418484638
    assert result == expected




