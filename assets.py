import pygame as pg
from functions import load_assets

pg.font.init()

window_width, window_height = 900, 500
window = pg.display.set_mode((window_width, window_height))
pg.display.set_caption("Deep Sea")

run = True
clock = pg.time.Clock()
fps = 60

assets: dict[str : pg.Surface] = {}
assets.update(load_assets("assets"))
assets.update(load_assets("assets/Ship", scale=4))
object_image_names = load_assets("assets/Objects")
assets.update(object_image_names)
object_image_names = list(object_image_names.keys())