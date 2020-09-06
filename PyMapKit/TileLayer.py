"""
Project: PyMapKit
Title: Tile Layer
Function: Provides a class that can display map tiles from a server.
Author: Ben Knisley [benknisley@gmail.com]
Date: 1 July, 2020
"""
import os
import math
import requests
import tempfile
import pyproj ## Only needed to check projection
from io import BytesIO
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


def zoom2scale(zoom):
    return 156543.03392 / math.pow(2, zoom)

def scale2zoom(scale):
    return math.log(156543.03392 / scale, 2)

def tile2geo(zoom_lvl, tile_x, tile_y):
    n = 2.0 ** zoom_lvl
    lon_deg = tile_x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

def geo2tile(lat, lon, scale):
    zoom_lvl = int(round(math.log(156543.03392 / scale, 2),0))

    lat_rad = math.radians(lat)
    n = 2.0 ** zoom_lvl
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)

    return x_tile, y_tile, zoom_lvl

class _tile:
    def __init__(self, parent_map, path, zoom_lvl, tile_x, tile_y):
        self.parent_map = parent_map
        self.path = path
        self.image = None

        self.zoom_lvl = zoom_lvl
        self.tile_x = tile_x
        self.tile_y = tile_y

        self.lat, self.lon = tile2geo(zoom_lvl, self.tile_x, self.tile_y)
        self.proj_x, self.proj_y = parent_map.geo2proj(self.lon, self.lat)

    def draw(self, renderer, cr):
        if self.image == None:
            self.image = renderer.get_image_obj(self.path)

        ## Get pixel coord of tile
        pix_x, pix_y = self.parent_map.proj2pix(self.proj_x, self.proj_y)

        scaling_factor = zoom2scale(self.zoom_lvl) / self.parent_map.get_scale()
        scaling_factor += (0.005 * (1/scaling_factor))
        
        renderer.draw_image(cr, self.image, pix_x, pix_y, scaling_factor, scaling_factor)

class TileLayer:
    """ """
    def __init__(self, url, blocking=True):
        """ 
        url format: "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
        """
        ## Create placeholder for parent Map Object
        self.parent = None
        #self.tile_cache = TileCache(self) #! <---------------

        ## Create Name property
        self.name = "TileLayer"

        self.url = url
        self.tile_store = {}
        self.requested_tiles = []
        self.executor = ThreadPoolExecutor(max_workers=8)
        ## Flag if layer should block while downloading tiles
        self.blocking = blocking

        ## Create temp directory to store tiles
        self.temp_dir = tempfile.mkdtemp()

    def fetch_tile(self, zoom_lvl, tile_x, tile_y, blocking=True):

        if (zoom_lvl, tile_x, tile_y) in self.tile_store:
            return self.tile_store[(zoom_lvl, tile_x, tile_y)]
        
        elif blocking:
            tile_data = (zoom_lvl, tile_x, tile_y)
            self.start_download(tile_data)
            return self.tile_store[(zoom_lvl, tile_x, tile_y)]
        
        elif (zoom_lvl, tile_x, tile_y) in self.requested_tiles:
            return None
        
        else: 
            self.requested_tiles.append((zoom_lvl, tile_x, tile_y))
            self.executor.submit(self.start_download, (zoom_lvl, tile_x, tile_y))
            return None

    def start_download(self, tile_data):
        zoom_lvl, tile_x, tile_y = tile_data
        path = self.download_tile(tile_data)
        new_tile = _tile(self.parent, path, zoom_lvl, tile_x, tile_y)
        self.tile_store[(zoom_lvl, tile_x, tile_y)] = new_tile

    def download_tile(self, tile_data):
        zoom_lvl, tile_x, tile_y = tile_data
        
        url = self.url
        url = url.replace('{z}', str(zoom_lvl))
        url = url.replace('{x}', str(tile_x))
        url = url.replace('{y}', str(tile_y))
 
        path = f"{self.temp_dir}/{zoom_lvl}.{tile_x}.{tile_y}.png" 

        if os.path.isfile(path):
            return path
        
        response  = requests.get(url, headers={'User-agent': 'PyMapKit/0.1'})

        img = Image.open(BytesIO(response.content))
        img.save(path)

        return path

    def need_redrawn(self):
        return len(self.requested_tiles) != len(self.tile_store)

    def _activate(self, new_parent_map):
        assert new_parent_map._projection == pyproj.Proj("EPSG:3785"), "Projection must be EPSG:3785 to display tiles."
        self.parent = new_parent_map

    def _deactivate(self):
        self.parent = None
    
    def draw(self, renderer, cr):
        """ """
        ## Get number of tiles to cover width and height of canvas
        tile_x_size = int(self.parent.width / 256) + 6
        tile_y_size = int(self.parent.height / 256) + 6

        ## Get tile at map location
        init_tile_x, init_tile_y, zoom_lvl = geo2tile(*self.parent.get_location(), self.parent.get_scale())

        ## Find top left tile
        start_tile_x = init_tile_x - int(tile_x_size / 6) - 4
        start_tile_y = init_tile_y - int(tile_y_size / 6) - 4

        ## Find bottom right tile
        end_tile_x = int(start_tile_x + tile_x_size)
        end_tile_y = int(start_tile_y + tile_y_size)
        
        ## Loop through x range and y range of tiles
        for tile_x in range(start_tile_x, end_tile_x):
            for tile_y in range(start_tile_y, end_tile_y):

                #tile = self.get_tile(zoom_lvl, tile_x, tile_y)
                #tile.draw(cr)

                tile = self.fetch_tile(zoom_lvl, tile_x, tile_y, blocking=self.blocking)

                if isinstance(tile, _tile):
                    tile.draw(renderer, cr)
                else:
                    pass