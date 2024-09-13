import pygame as pg
from functions import load_assets, loadJson

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
assets["Sky"] = pg.Surface((window_width, window_height))
assets["Sky"].fill((51, 153, 255))
object_image_names = load_assets("assets/Objects")
assets.update(object_image_names)
object_image_names = list(object_image_names.keys())

coordinates = loadJson("coordinates.json")

# creation of inventory slots
inventoryImageName = "Brown Slots"
inventoryScale = 3
assets[inventoryImageName] = pg.transform.scale_by(assets[inventoryImageName], inventoryScale) 

inventoryX = window_width - assets[inventoryImageName].get_width()
inventoryY = 0
slotRelX, slotRelY = coordinates[inventoryImageName]["Initial"]
slotRelX *= inventoryScale
slotRelY *= inventoryScale
slots = []
slotWidth, slotHeight = coordinates[inventoryImageName]["Size"]
slotWidth *= inventoryScale
slotHeight *= inventoryScale
for x in range(coordinates[inventoryImageName]["X range"]):
    for y in range(coordinates[inventoryImageName]["Y range"]):
        slots.append(
            pg.Rect(inventoryX + slotRelX, inventoryY + slotRelY, slotWidth, slotHeight)
        )
        slotRelY += slotHeight + coordinates[inventoryImageName]["Continuous"][1] * inventoryScale
    slotRelX += slotWidth + coordinates[inventoryImageName]["Continuous"][0] * inventoryScale
    slotRelY = coordinates[inventoryImageName]["Initial"][1] * inventoryScale
