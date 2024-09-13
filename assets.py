import pygame as pg
from functions import load_assets, loadJson

class Slot:
    def __init__(self, x, y, width, height, name, count) -> None:
        self.rect = pg.Rect(x, y, width, height)
        self.name = name
        self.count = count

pg.font.init()
pg.mixer.init()

window_width, window_height = 900, 500
window = pg.display.set_mode((window_width, window_height))
pg.display.set_caption("Deep Sea")

run = True
clock = pg.time.Clock()
fps = 60

# image assets
assets: dict[str : pg.Surface] = {}
assets.update(load_assets("assets"))
assets.update(load_assets("assets/Ship", scale=4))
assets["Sky"] = pg.Surface((window_width, window_height))
assets["Sky"].fill((51, 153, 255))
object_image_names = load_assets("assets/Objects")
assets.update(object_image_names)
object_image_names = list(object_image_names.keys())
assets.update(load_assets("assets/items", scale=3))

# music
backgroundMusic = pg.mixer.Sound("assets/Sounds/Background.mp3")
backgroundMusic.set_volume(0.5)
breakSound = pg.mixer.Sound("assets/Sounds/Break.ogg")
breakSound.set_volume(3)
metalBang = pg.mixer.Sound("assets/Sounds/Metal Bang.mp3")
metalBang.set_volume(0.5)

# defines location of font for Text object
fontLocation = "assets/GUI/"

# loading all json data
coordinates = loadJson("coordinates.json")
itemsData = loadJson("items.json")
upgrades = loadJson("upgrades.json")

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
            Slot(inventoryX + slotRelX, inventoryY + slotRelY, slotWidth, slotHeight, None, 0)
        )
        slotRelY += slotHeight + coordinates[inventoryImageName]["Continuous"][1] * inventoryScale
    slotRelX += slotWidth + coordinates[inventoryImageName]["Continuous"][0] * inventoryScale
    slotRelY = coordinates[inventoryImageName]["Initial"][1] * inventoryScale
