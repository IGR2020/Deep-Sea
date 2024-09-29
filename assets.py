import pygame as pg
from functions import load_assets, loadJson


class Slot:
    def __init__(self, x, y, width, height, name, count) -> None:
        self.rect = pg.Rect(x, y, width, height)
        self.name = name
        self.count = count

    def reloadRect(self):
        if self.name is None:
            return
        self.rect = assets[self.name].get_rect(topleft=(x, y))


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
assets.update(load_assets("assets/items", scale=3, scaleifsize=(16, 16)))
assets["Bubble"] = pg.transform.scale_by(assets["Bubble"], 2)
assets.update(load_assets("assets/Events"))
mob_image_names = load_assets("assets/Mobs", scale=5, getSubDirsAsList=True)
assets.update(mob_image_names)
mob_image_names = list(mob_image_names.keys())
for key in mob_image_names:
    if "Attackbox" in  key:
        mob_image_names.remove(key)
assets["Selected Slot"] = pg.Surface((15, 15)).convert_alpha()
assets["Selected Slot"].fill((200, 200, 200, 100))

# music
backgroundMusic = pg.mixer.Sound("assets\Sounds\Background.mp3")
backgroundMusic.set_volume(0.3)
breakSound = pg.mixer.Sound("assets/Sounds/Break.ogg")
breakSound.set_volume(3)
correctSound = pg.mixer.Sound("assets/Sounds/Correct.mp3")
craftSound = pg.mixer.Sound("assets/Sounds/Craft.mp3")
deathSound = pg.mixer.Sound("assets/Sounds/Death.mp3")
biteSound = pg.mixer.Sound("assets/Sounds/Bite.mp3")
biteSound.set_volume(0.3)


# defines location of font for Text object
fontLocation = "assets/GUI/"

# loading all json data
coordinates = loadJson("data/coordinates.json")
itemsData = loadJson("data/items.json")
upgrades = loadJson("data/upgrades.json")
events = loadJson("data/events.json")
eventsCopy = loadJson("data/events.json") # a copy of the events to reset it after an event is over
smelts = loadJson("data/smelts.json")
mobsData = loadJson("data/mobs.json")
crafts = loadJson("data/crafts.json")
craftTrigger = "glue"
toolData = loadJson("data/tools.json")
toolNames = list(toolData.keys())
defaultItemAngleCorrectionPos = 90
defaultItemAngleCorrection = 45

# creation of inventory slots
inventoryImageName = "Brown Slots"
guiScale = 3
assets["Selected Slot"] = pg.transform.scale_by(assets["Selected Slot"], guiScale)
assets[inventoryImageName] = pg.transform.scale_by(assets[inventoryImageName], guiScale)

inventoryWidth = assets[inventoryImageName].get_width()
inventoryX = window_width - inventoryWidth
inventoryY = 0
slotRelX, slotRelY = coordinates[inventoryImageName]["Initial"]
slotRelX *= guiScale
slotRelY *= guiScale
slots = []
slotWidth, slotHeight = coordinates[inventoryImageName]["Size"]
slotWidth *= guiScale
slotHeight *= guiScale
for x in range(coordinates[inventoryImageName]["X range"]):
    for y in range(coordinates[inventoryImageName]["Y range"]):
        slots.append(
            Slot(
                inventoryX + slotRelX,
                inventoryY + slotRelY,
                slotWidth,
                slotHeight,
                None,
                0,
            )
        )
        slotRelY += (
            slotHeight + coordinates[inventoryImageName]["Continuous"][1] * guiScale
        )
    slotRelX += slotWidth + coordinates[inventoryImageName]["Continuous"][0] * guiScale
    slotRelY = coordinates[inventoryImageName]["Initial"][1] * guiScale

hotbarImageName = "Brown Hotbar"
assets[hotbarImageName] = pg.transform.scale_by(assets[hotbarImageName], guiScale)

hotbarWidth = assets[hotbarImageName].get_width()
hotbarHeight = assets[hotbarImageName].get_height()
hotbarX = (window_width - hotbarWidth) // 2
hotbarY = window_height - hotbarHeight * 1.1
slotRelX, slotRelY = coordinates[hotbarImageName]["Initial"]
slotRelX *= guiScale
slotRelY *= guiScale
hotbarSlots = []
slotWidth, slotHeight = coordinates[hotbarImageName]["Size"]
slotWidth *= guiScale
slotHeight *= guiScale
for x in range(coordinates[hotbarImageName]["X range"]):
    for y in range(coordinates[hotbarImageName]["Y range"]):
        hotbarSlots.append(
            Slot(hotbarX + slotRelX, hotbarY + slotRelY, slotWidth, slotHeight, None, 0)
        )
        slotRelY += (
            slotHeight + coordinates[hotbarImageName]["Continuous"][1] * guiScale
        )
    slotRelX += slotWidth + coordinates[hotbarImageName]["Continuous"][0] * guiScale
    slotRelY = coordinates[hotbarImageName]["Initial"][1] * guiScale

heldItem = Slot(0, 0, 15, 15, None, 0)

upgradeRect = assets["Upgrade"].get_rect(topleft=(20, window_height - 68))

# creating custom mouse
pg.mouse.set_cursor((9, 9), assets["Mouse"])
