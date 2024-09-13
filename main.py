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

    def __init__(self, x, y, name):
        self.rect = pg.Rect(x, y, assets[name].get_width(), assets[name].get_height())
        self.name = name
        self.rotatedImage = pg.transform.rotate(assets[name], self.angle)
        self.mask = pg.mask.from_surface(self.rotatedImage)

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

    def __init__(self, x, y, name) -> None:
        self.rect = pg.Rect(x, y, assets[name].get_width(), assets[name].get_height())
        self.name = name
        self.scale = randint(10, 40) * 0.1
        self.rotation = randint(-100, 100) * 0.01
        if self.rotation == 0:
            self.rotation += 0.1
        self.scaledImage = pg.transform.scale_by(assets[self.name], self.scale)
        self.rotatedImage = pg.transform.rotate(
            self.scaledImage, self.angle
        )
        self.mask = pg.mask.from_surface(self.rotatedImage)
        self.health = itemsData[self.name]["Health"]

    def display(self, window, x_offset, y_offset):
        window.blit(self.rotatedImage, (self.rect.x - x_offset, self.rect.y - y_offset))

    def script(self):
        self.sink_vel += self.sink_speed
        self.sink_vel = min(self.sink_vel, 1)
        self.rect.y += self.y_vel
        self.rect.y += self.sink_vel
        self.rect.x += self.x_vel
        self.x_vel *= 0.9
        self.y_vel *= 0.9
        self.angle += self.rotation
        self.reload()

    def reload(self):
        self.rotatedImage = pg.transform.rotate(
            self.scaledImage, self.angle
        )
        self.rect = self.rotatedImage.get_rect(center=self.rect.center)
        self.mask = pg.mask.from_surface(self.rotatedImage)


ship = Ship(100, 100, "Ship")
objects = [Object(200, 100, "Plank")]

scroll_area = 200
x_offset, y_offset = 0, 0

pressure = 0
pressureText = Text("Pressure", 0, 0, (255, 255, 255), 30, "Retro Font")
pressure_rect = pg.Rect(0, pressureText.rect.bottom, 100, 25)
current_pressure_rect = pg.Rect(4, 4+pressureText.rect.bottom, 92, 17)

healthText = Text("Health", 0, pressure_rect.bottom + 10, (255, 255, 255), 30, "Retro Font")
healthRect = pg.Rect(0, healthText.rect.bottom, 100, 25)
current_health_rect = pg.Rect(4, 4+healthText.rect.bottom, 92, 17)


backgroundMusic.play()

while run:
    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    if randint(0, fps * 10) == 0:
        objects.append(
            Object(
                randint(
                    ship.rect.centerx - window_width // 2,
                    ship.rect.centerx + window_width // 2,
                ),
                -100,
                choice(object_image_names),
            )
        )

    ship.script()
    for obj in objects:
        obj.script()
        if pg.sprite.collide_mask(ship, obj):
            breakSound.play()
            if obj.health < 1:
                for drop in itemsData[obj.name]["Drops"]:
                    for slot in slots:
                        if slot.name == drop:
                            slot.count += randint(*itemsData[obj.name]["Count"])
                            break
                        if slot.name is None:
                            slot.name = drop
                            slot.count += randint(*itemsData[obj.name]["Count"])
                            break
                objects.remove(obj)
                break
            obj.health -= abs(ship.vel)
            ship.health -= itemsData[obj.name]["Damage"]
            ship.vel = -ship.vel
            ship.disabled = True
            ship.time_since_disabled = time()
            obj.x_vel = -ship.hrt_vel
            obj.y_vel = -ship.vrt_vel

    # scrolling of the game window
    if ship.rect.x - x_offset < scroll_area:
        x_offset -= round(abs(ship.hrt_vel))

    if ship.rect.x - x_offset > window_width - scroll_area:
        x_offset += round(abs(ship.hrt_vel))

    if ship.rect.y - y_offset < scroll_area:
        y_offset -= round(abs(ship.vrt_vel))

    if ship.rect.y - y_offset > window_height - scroll_area:
        y_offset += round(abs(ship.vrt_vel)) + 1

    if ship.rect.y > ship.pressure_limit:
        kill("High pressure.")

    if ship.health < 1:
        kill("Ship damaged too much")

    window.fill((0, 0, 139))
    window.blit(assets["Sky"], (0, sky_start - 500 - y_offset))
    for obj in objects:
        obj.display(window, x_offset, y_offset)
    ship.display(window, x_offset, y_offset)

    # displaying pressure
    pg.draw.rect(window, (0, 0, 0), pressure_rect)
    current_pressure = min(max(ship.rect.y/ship.pressure_limit, 0), 1)
    current_pressure_rect.width = 92 * current_pressure
    pg.draw.rect(window, (255 * current_pressure, 255 * (1 - current_pressure), 0), current_pressure_rect)
    pressureText.display(window)

    # displaying health
    current_health = ship.health/ship.max_health
    current_health_rect.width = 92 * current_health
    healthText.display(window)
    pg.draw.rect(window, (0, 0, 0), healthRect)
    pg.draw.rect(window, (255 * current_health, 255 * (1 - current_health), 0), current_health_rect)


    # displaying inventory
    window.blit(assets[inventoryImageName], (inventoryX, inventoryY))
    for slot in slots:
        if slot.name is not None:
            window.blit(assets[slot.name], slot.rect)
            blit_text(window, slot.count, slot.rect.topleft, (255, 255, 255), 20)

    pg.display.update()

pg.quit()
quit()
