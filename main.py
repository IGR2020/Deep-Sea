import pygame as pg
from functions import *
import math
from random import randint
from time import time

window_width, window_height = 900, 500
window = pg.display.set_mode((window_width, window_height))
pg.display.set_caption("Deep Sea")

run = True
clock = pg.time.Clock()
fps = 60

assets: dict[str: pg.Surface] = {}
assets.update(load_assets("assets", scale=4))


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
        self.rect = self.rotatedImage.get_rect(
            center=self.rect.center
        )
        self.mask = pg.mask.from_surface(self.rotatedImage)

    def script(self):
        # getting inputs
        keys = pg.key.get_pressed()
        if keys[pg.K_d]:
            self.angle -= max(abs(self.vel)/3, 1)
            self.reload()
        if keys[pg.K_a]:
            self.angle += max(abs(self.vel)/3, 1)
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
            if self.disabled: self.vel -= 0.1
            else: self.vel -= 0.5
            self.vel = max(self.vel, 0)
        elif self.vel < 0:
            if self.disabled: self.vel += 0.1
            else: self.vel += 0.5
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
        self.rotation = randint(-100, 100)*0.01
        if self.rotation == 0: self.rotation += 0.1 
        self.rotatedImage = pg.transform.rotate(assets[name], self.angle)
        self.mask = pg.mask.from_surface(self.rotatedImage)

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
        self.rotatedImage = pg.transform.rotate(assets[self.name], self.angle)
        self.rect = self.rotatedImage.get_rect(
            center=self.rect.center
        )
        self.mask = pg.mask.from_surface(self.rotatedImage)
    

ship = Ship(100, 100, "Ship")
objects = [Object(200, 100, "Plank")]

while run:
    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    if randint(0, fps*10) == 0:
        objects.append(Object(randint(0, window_width-100), -100, "Plank"))

    ship.script()
    for obj in objects:
        obj.script()
        if pg.sprite.collide_mask(ship, obj):
            ship.vel = -ship.vel
            ship.disabled = True
            ship.time_since_disabled = time()
            obj.x_vel = -ship.hrt_vel
            obj.y_vel = -ship.vrt_vel
        if obj.rect.y > window_height:
            objects.remove(obj)

    window.fill((0, 0, 139))
    for obj in objects:
        obj.display(window, 0, 0)
    ship.display(window, 0, 0)
    pg.display.update()

pg.quit()
quit()