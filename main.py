import pygame as pg
from functions import *
import math
from random import randint, choice
from time import time
from assets import *
from menu import kill
from GUI import Text

sky_start = -150


pg.display.set_icon(assets["Ship"])


class Ship:
    vel = 0
    angle = 0
    sink_speed = 0.1
    y_vel = 0
    hrt_vel, vrt_vel = 0, 0
    disabled = False
    disabled_time = 0.5
    time_since_disabled = 0
    pressure_limit = 2_000
    health = 200
    max_health = health
    slots = []
    hotBarSlots = []
    heldItem = []

    def __init__(self, x, y, name, slots, hotBarSlots, heldItem):
        self.rect = pg.Rect(x, y, assets[name].get_width(), assets[name].get_height())
        self.name = name
        self.rotatedImage = pg.transform.rotate(assets[name], self.angle)
        self.mask = pg.mask.from_surface(self.rotatedImage)

        self.slots = slots
        self.hotBarSlots = hotBarSlots
        self.heldItem = heldItem

    def display(self, window, x_offset, y_offset):
        window.blit(self.rotatedImage, (self.rect.x - x_offset, self.rect.y - y_offset))

    def move(self):
        radians = math.radians(self.angle)
        self.hrt_vel = math.sin(radians) * self.vel
        self.vrt_vel = math.cos(radians) * self.vel
        self.rect.x -= self.hrt_vel
        self.rect.y -= self.vrt_vel

    def reload(self):
        self.rotatedImage = pg.transform.rotate(assets[self.name], self.angle)
        self.rect = self.rotatedImage.get_rect(center=self.rect.center)
        self.mask = pg.mask.from_surface(self.rotatedImage)

    def script(self):
        # checking if ship is in valid area
        if self.rect.y < sky_start:
            self.vel -= 2

        # getting inputs
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            self.angle -= max(abs(self.vel) / 3, 1)
            self.reload()
        if keys[pg.K_a]:
            self.angle += max(abs(self.vel) / 3, 1)
            self.reload()
        if keys[pg.K_w]:
            if self.disabled:
                self.vel += 0.3
            else:
                self.vel += 1

        # auto removing disabled tag
        if time() - self.time_since_disabled > self.disabled_time:
            self.disabled = False

        # adding the velocities
        self.move()
        self.y_vel += self.sink_speed
        self.y_vel = min(self.y_vel, 1)
        self.rect.y += self.y_vel
        if self.vel > 0:
            if self.disabled:
                self.vel -= 0.1
            else:
                self.vel -= 0.5
            self.vel = max(self.vel, 0)
        elif self.vel < 0:
            if self.disabled:
                self.vel += 0.1
            else:
                self.vel += 0.5
            self.vel = min(self.vel, 0)
        self.vel = max(min(self.vel, 10), -10)


class Object(pg.sprite.Sprite):
    x_vel, y_vel = 0, 0
    angle = 0
    sink_speed = 0.1
    sink_vel = 0
    max_sink_speed = 1

    def __init__(self, x, y, name, type="Object") -> None:
        self.rect = pg.Rect(x, y, assets[name].get_width(), assets[name].get_height())
        self.name = name
        self.scale = randint(10, 40) * 0.1
        self.rotation = randint(-100, 100) * 0.01
        if self.rotation == 0:
            self.rotation += 0.1
        self.scaledImage = pg.transform.scale_by(assets[self.name], self.scale)
        self.rotatedImage = pg.transform.rotate(self.scaledImage, self.angle)
        self.mask = pg.mask.from_surface(self.rotatedImage)
        if type == "Object":
            self.health = itemsData[self.name]["Health"]
        self.type = type

    def display(self, window, x_offset, y_offset):
        window.blit(self.rotatedImage, (self.rect.x - x_offset, self.rect.y - y_offset))

    def script(self):

        self.sink_vel += self.sink_speed
        self.sink_vel = min(self.sink_vel, self.max_sink_speed)

        self.rect.y += self.y_vel
        self.rect.y += self.sink_vel
        self.rect.x += self.x_vel
        self.x_vel *= 0.9
        self.y_vel *= 0.9

        self.angle += self.rotation
        self.reload()

        if self.rect.y < sky_start:
            self.rect.y += 8

    def reload(self):
        self.rotatedImage = pg.transform.rotate(self.scaledImage, self.angle)
        self.rect = self.rotatedImage.get_rect(center=self.rect.center)
        self.mask = pg.mask.from_surface(self.rotatedImage)

    def totalReload(self):
        self.scaledImage = pg.transform.scale_by(assets[self.name], self.scale)
        self.rotatedImage = pg.transform.rotate(self.scaledImage, self.angle)
        self.rect = self.rotatedImage.get_rect(center=self.rect.center)
        self.mask = pg.mask.from_surface(self.rotatedImage)

    @classmethod
    def loadFromRain(self, rain):
        self = self(rain.rect.x, rain.rect.y, rain.name)
        self.x_vel, self.y_vel = rain.x_vel, rain.y_vel
        self.scale, self.angle, self.rotation = rain.scale, rain.angle, rain.rotation
        self.scaledImage = pg.transform.scale_by(assets[self.name], self.scale)
        self.reload()
        self.rect.topleft = rain.rect.x, rain.rect.y
        return self


class Particle:
    outOfView = False

    def __init__(self, name, x, y, y_vel, x_vel):
        self.x, self.y = x, y
        self.name = name
        self.y_vel = y_vel
        self.x_vel = x_vel

    def display(self, window, x_offset, y_offset):
        if self.outOfView:
            return
        self.x += self.x_vel
        self.y += self.y_vel
        window.blit(assets[self.name], (self.x - x_offset, self.y - y_offset))
        if (
            self.x - x_offset < -window_width
            or self.x - x_offset > window_width * 2
            or self.y - y_offset < -window_height
            or self.y - y_offset > window_height * 2
            or (self.name == "Bubble" and self.y < sky_start)
        ):
            self.outOfView = True


class Rain(Object):
    isInWater = False

    def __init__(self, x, y, name, x_vel, y_vel, drop) -> None:
        """Drop tells the game to drop something if the rain moves into the water"""
        super().__init__(x, y, name, "Rain")
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.drop = drop

    def script(self):
        if self.isInWater:
            return
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        if self.rect.y > sky_start:
            self.isInWater = True

        self.angle += self.rotation
        self.reload()


class Item(Object):
    def __init__(self, x, y, name, count) -> None:
        super().__init__(x, y, name, "Item")
        self.count = count
        self.scale = 1
        self.totalReload()

    def script(self):
        if eventType is not None and self.rect.y < sky_start:
            if eventType["Type"] == "Rain":
                if eventType["Rain"] == "Effect":
                    if eventType["Effect"] == "Smelt":
                        for smelt in smelts:
                            if smelt["Name"] == self.name:
                                self.name = smelt["Smelt"]
                                self.totalReload()
                                break

        super().script()


class Mob:
    animation_count = 0
    animation_speed = 3
    vel = 0
    angle = 0
    rotateDir = True  # true is for rotation to the left
    type = "Mob"
    x_vel, y_vel = 0, 0

    def __init__(self, x, y, name: str, sheet: bool, correctionAngle=0) -> None:
        if sheet:
            self.image = assets[name][0]
        else:
            self.image = assets[name]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pg.mask.from_surface(self.image)
        self.name = name
        self.is_sheet = sheet
        self.correctionAngle = correctionAngle
        self.health = mobsData[name]["Health"]
        self.damage = mobsData[name]["Damage"]
        self.rotatedImage = pg.transform.rotate(self.image, self.angle)

    def reload(self):
        self.rotatedImage = pg.transform.rotate(self.image, self.angle)

    def display(self, window, x_offset, y_offset):
        if self.is_sheet:
            self.animation_count += 1
            index = (self.animation_count // self.animation_speed) % len(
                assets[self.name]
            )
            self.image = assets[self.name][index]
            self.reload()
            window.blit(
                self.rotatedImage, (self.rect.x - x_offset, self.rect.y - y_offset)
            )
        else:
            window.blit(
                self.rotatedImage, (self.rect.x - x_offset, self.rect.y - y_offset)
            )
            self.reload()

    def script(self):
        self.move()
        for ship in ships:
            distanceToPlayer = abs(self.rect.x - ships[ship].rect.x) + abs(
                self.rect.y - ships[ship].rect.y
            )
            if distanceToPlayer < mobAttackDistance:
                target = ships[ship]
                break
        else:
            target = None
        if target is not None:
            dx, dy = (
                target.rect.centerx - self.rect.centerx,
                self.rect.centery - target.rect.centery,
            )
            self.angle = math.degrees(math.atan2(dy, dx)) - self.correctionAngle
            self.vel = 5
        else:
            if randint(0, fps // 12) == 0:
                if self.rotateDir:
                    self.angle -= 1
                else:
                    self.angle += 1
            if randint(0, fps) == 0:
                self.rotateDir = not self.rotateDir
            self.vel = 2

    def move(self):
        radians = math.radians(self.angle + 90)
        self.hrt_vel = math.sin(radians) * self.vel
        self.vrt_vel = math.cos(radians) * self.vel
        self.rect.x -= self.hrt_vel
        self.rect.y -= self.vrt_vel


ships = {"IGR2020": Ship(100, 100, "Ship", slots, hotbarSlots, heldItem)}
name = "IGR2020"
objects = [Object(300, 200, "Plank"), Mob(400, 200, "Shark", True, 180)]

bubbles = []

scroll_area = 200
x_offset, y_offset = 0, 0

pressure = 0
pressureText = Text("Pressure", 0, 0, (255, 255, 255), 30, "Retro Font")
pressure_rect = pg.Rect(0, pressureText.rect.bottom, 100, 25)
current_pressure_rect = pg.Rect(4, 4 + pressureText.rect.bottom, 92, 17)

healthText = Text(
    "Health", 0, pressure_rect.bottom + 10, (255, 255, 255), 30, "Retro Font"
)
healthRect = pg.Rect(0, healthText.rect.bottom, 100, 25)
current_health_rect = pg.Rect(4, 4 + healthText.rect.bottom, 92, 17)

inventoryView = True
inventoryShift = 0

upgradeFound = False
upgradeID = None
nextItem = False
upgradeImageFloat = -1

eventOccurring = False
timeSinceLastEvent = 0
eventGap = 60  # minimum time between events (time in seconds)
eventChance = 60  # chance of event occurring (time in seconds)
eventType = None  # assign the json event object in event.json durring event

freeCam = False

slotFound = False

mobAttackDistance = 500
mobSummonChance = 60
debrisSummonChance = 10

backgroundMusic.play(-1)

while run:

    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

        if event.type == pg.KEYDOWN:

            if event.key == pg.K_e:
                inventoryView = not inventoryView

            if event.key == pg.K_f:
                if freeCam:
                    x_offset, y_offset = (
                        ship.rect.x - window_width / 2,
                        ship.rect.y - window_height / 2,
                    )
                freeCam = not freeCam

        if event.type == pg.MOUSEBUTTONUP:
            if inventoryView:
                # inventory management
                slotFound = False
                for slot in ships[name].slots:
                    if slot.rect.collidepoint(mouseX, mouseY):
                        if (
                            slot.name == ships[name].heldItem.name
                            and ships[name].heldItem.name is not None
                        ):
                            slot.count += ships[name].heldItem.count
                            ships[name].heldItem.name = None
                            ships[name].heldItem.count = None
                        else:
                            ships[name].heldItem.name, slot.name = (
                                slot.name,
                                ships[name].heldItem.name,
                            )
                            ships[name].heldItem.count, slot.count = (
                                slot.count,
                                ships[name].heldItem.count,
                            )
                        slotFound = True
                for slot in ships[name].hotBarSlots:
                    if slot.rect.collidepoint(mouseX, mouseY):
                        if (
                            slot.name == ships[name].heldItem.name
                            and ships[name].heldItem.name is not None
                        ):
                            slot.count += ships[name].heldItem.count
                            ships[name].heldItem.name = None
                            ships[name].heldItem.count = None
                        else:
                            ships[name].heldItem.name, slot.name = (
                                slot.name,
                                ships[name].heldItem.name,
                            )
                            ships[name].heldItem.count, slot.count = (
                                slot.count,
                                ships[name].heldItem.count,
                            )
                        slotFound = True
                ships[name].heldItem.reloadRect()

                if not slotFound and ships[name].heldItem.name is not None:
                    objects.append(
                        Item(
                            mouseX + x_offset,
                            mouseY + y_offset,
                            ships[name].heldItem.name,
                            ships[name].heldItem.count,
                        )
                    )
                    ships[name].heldItem.name = None
                    ships[name].heldItem.count = 0
                slotFound = False

            # checking for upgrading
            if upgradeRect.collidepoint(mouseX, mouseY) and upgradeFound:
                CorrectSound.play()

                upgrade = upgrades[upgradeID]
                for cost in upgrade["Cost"]:
                    for slot in (*ships[name].slots, *ships[name].hotBarSlots):
                        if cost["Name"] == slot.name and cost["Count"] <= slot.count:
                            slot.count -= cost["Count"]
                            if slot.count < 1:
                                slot.name = None
                                slot.count = 0
                            break

                # upgrading the ship on basis of type
                if upgrade["Type"] == "Depth":
                    ships[name].pressure_limit += upgrade["Change"]
                elif upgrade["Type"] == "Health":
                    ships[name].max_health += upgrade["Change"]
                    ships[name].health += upgrade["Change"]

                upgrades.remove(upgrade)
                upgradeFound = False
                upgradeID = None

    # extracting mouse position
    mouseX, mouseY = pg.mouse.get_pos()

    # summoning debris
    if randint(0, fps * debrisSummonChance) == 0:
        objects.append(
            Object(
                randint(
                    ships[name].rect.centerx - window_width // 2,
                    ships[name].rect.centerx + window_width // 2,
                ),
                sky_start - 200,
                choice(object_image_names),
            )
        )

    ships[name].script()
    for ship in ships:
        for obj in objects:
            obj.script()
            if obj.type == "Rain":
                if obj.isInWater:
                    if obj.drop:
                        objects.append(Object.loadFromRain(obj))
                    objects.remove(obj)
                continue
            if pg.sprite.collide_mask(ships[ship], obj):
                if obj.type == "Item":
                    for slot in ships[ship].slots:
                        if slot.name == obj.name:
                            slot.count += obj.count
                            break
                        if slot.name is None:
                            slot.name = obj.name
                            slot.count = obj.count
                            break
                    objects.remove(obj)
                    continue
                breakSound.play()
                if obj.health < 1 and obj.type == "Object":
                    for drop in itemsData[obj.name]["Drops"]:
                        for slot in ships[ship].slots:
                            if slot.name == drop:
                                slot.count += randint(*itemsData[obj.name]["Count"])
                                break
                            if slot.name is None:
                                slot.name = drop
                                slot.count += randint(*itemsData[obj.name]["Count"])
                                break
                    objects.remove(obj)

                elif obj.health < 1 and obj.type == "Mob":
                    for drop in mobsData[obj.name]["Drops"]:
                        for slot in ships[ship].slots:
                            if slot.name == drop:
                                slot.count += randint(*mobsData[obj.name]["Count"])
                                break
                            if slot.name is None:
                                slot.name = drop
                                slot.count += randint(*mobsData[obj.name]["Count"])
                                break
                    objects.remove(obj)

                # elastic knockback
                obj.health -= abs(ships[ship].vel)
                if obj.type == "Mob":
                    ships[ship].health -= mobsData[obj.name]["Damage"]
                else:
                    ships[ship].health -= itemsData[obj.name]["Damage"]
                if ships[ship].vel > 0:
                    ships[ship].vel += 1
                else:
                    ships[ship].vel -= 1
                ships[ship].vel = -ships[ship].vel
                ships[ship].disabled = True
                ships[ship].time_since_disabled = time()
                obj.x_vel = -ships[ship].hrt_vel
                obj.y_vel = -ships[ship].vrt_vel

    # scrolling of the game window
    mouseRelX, mouseRelY = pg.mouse.get_rel()
    mouseDown = pg.mouse.get_pressed()
    if freeCam:
        if True in mouseDown:
            x_offset -= mouseRelX
            y_offset -= mouseRelY
    else:
        x_offset = ships[name].rect.centerx - window_width / 2
        y_offset = ships[name].rect.centery - window_height / 2

    # checking for available upgrades
    for i, upgrade in enumerate(upgrades):
        for cost in upgrade["Cost"]:
            nextItem = False
            for slot in (*ships[name].slots, *ships[name].hotBarSlots):
                if cost["Name"] == slot.name and cost["Count"] <= slot.count:
                    nextItem = True
                    break
            if nextItem:
                continue
            break
        else:
            upgradeFound = True
            upgradeID = i
            break
    else:
        upgradeFound = False
        upgradeID = None

    # checking for kill events
    if ships[name].rect.y > ships[name].pressure_limit:
        kill("High pressure.")

    if ships[name].health < 1:
        kill("Ship damaged too much.")

    # setting inventory shift
    if inventoryView and inventoryX > window_width - inventoryWidth:
        inventoryShift = -3
    elif not inventoryView and inventoryX < window_width:
        inventoryShift = 3
    else:
        inventoryShift = 0

    # creating bubbles & removing bubbles
    if (ships[name].disabled and randint(0, 10) == 0) or (
        abs(ships[name].vel) < 1 and randint(0, 30) == 0
    ):
        bubbles.append(
            Particle(
                "Bubble",
                ships[name].rect.x + randint(-30, 30),
                ships[name].rect.y,
                -1.5,
                0,
            )
        )
    for bubble in bubbles:
        if bubble.outOfView:
            bubbles.remove(bubble)

    # setting events
    if (
        randint(0, round(fps * eventChance)) == 0
        and time() - timeSinceLastEvent > eventGap
        and not eventOccurring
    ):
        events = eventsCopy
        eventOccurring = True
        timeSinceLastEvent = time()
        eventType = choice(events)
        if eventType["Type"] == "Rain":
            try:
                eventType["Direction"]
            except:
                eventType["Direction"] = randint(-5, 5)
            try:
                eventType["Fall Speed"]
            except:
                eventType["Fall Speed"] = randint(5, 15)

            # note summon range start is added to ship x and summon range end is subtracted to ship x
            if eventType["Direction"] > 0:
                eventType["Summon Range Start"] = window_width // 2
                eventType["Summon Range End"] = 0
            elif eventType["Direction"] < 0:
                eventType["Summon Range Start"] = 0
                eventType["Summon Range End"] = window_width // 2
            else:
                eventType["Summon Range Start"] = window_width // 2
                eventType["Summon Range End"] = window_width // 2

    # event script
    if eventOccurring and eventType is not None:
        if eventType["Type"] == "Rain":
            if randint(0, round(fps * eventType["Summon Speed"])) == 0:
                objects.append(
                    Rain(
                        randint(
                            ships[name].rect.centerx - eventType["Summon Range Start"],
                            ships[name].rect.centerx + eventType["Summon Range End"],
                        ),
                        sky_start - window_height,
                        eventType["Summon"],
                        eventType["Direction"],
                        eventType["Fall Speed"],
                        eventType["Rain"] == "Drop",
                    )
                )

    # stopping event
    if eventOccurring and eventType is not None:
        if time() - timeSinceLastEvent > eventType["Duration"]:
            eventOccurring = False
            eventType = None

    # summoning mobs
    if randint(0, fps * mobSummonChance) == 0:
        objects.append(
            Mob(
                randint(
                    ships[name].rect.centerx - window_width // 2,
                    ships[name].rect.centerx + window_width // 2,
                ),
                ships[name].rect.y + window_height / 2 * 1.1,
                choice(mob_image_names),
                True,
                180,
            )
        )

    window.fill((0, 0, 139))
    window.blit(assets["Sky"], (0, sky_start - 500 - y_offset))
    for obj in objects:
        obj.display(window, x_offset, y_offset)

    # rendering bubbles
    for bubble in bubbles:
        bubble.display(window, x_offset, y_offset)

    for ship in ships:
        ships[ship].display(window, x_offset, y_offset)

    # displaying pressure
    pg.draw.rect(window, (0, 0, 0), pressure_rect)
    current_pressure = min(max(ships[name].rect.y / ships[name].pressure_limit, 0), 1)
    current_pressure_rect.width = 92 * current_pressure
    pg.draw.rect(
        window,
        (255 * current_pressure, 255 * (1 - current_pressure), 0),
        current_pressure_rect,
    )
    pressureText.display(window)

    # displaying health
    current_health = max(ships[name].health / ships[name].max_health, 0)
    current_health_rect.width = 92 * current_health
    healthText.display(window)
    pg.draw.rect(window, (0, 0, 0), healthRect)
    pg.draw.rect(
        window,
        (255 * (1 - current_health), 255 * current_health, 0),
        current_health_rect,
    )

    # displaying inventory & shifting inventory
    inventoryX += inventoryShift
    window.blit(assets[inventoryImageName], (inventoryX, inventoryY))
    for slot in ships[name].slots:
        slot.rect.x += inventoryShift
        if slot.name is not None:
            window.blit(assets[slot.name], slot.rect)
            blit_text(window, slot.count, slot.rect.topleft, (255, 255, 255), 20)

    # displaying hotbar
    window.blit(assets[hotbarImageName], (hotbarX, hotbarY))
    for slot in ships[name].hotBarSlots:
        if slot.name is not None:
            window.blit(assets[slot.name], slot.rect)
            blit_text(window, slot.count, slot.rect.topleft, (255, 255, 255), 20)

    # displaying ship.heldItem
    if ships[name].heldItem.name is not None:
        ships[name].heldItem.rect.center = mouseX, mouseY
        window.blit(assets[ships[name].heldItem.name], ships[name].heldItem.rect)
        blit_text(
            window,
            ships[name].heldItem.count,
            ships[name].heldItem.rect.topleft,
            (255, 255, 255),
            20,
        )

    # upgrade displaying
    if upgradeFound:
        window.blit(assets["Upgrade"], upgradeRect)
        upgradeRect.y += upgradeImageFloat

        if upgradeRect.y > window_height - 58:
            upgradeImageFloat = -1
        if upgradeRect.y < window_height - 78:
            upgradeImageFloat = 1

    pg.display.update()

pg.quit()
quit()
