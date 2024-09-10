import pygame as pg
from functions import *
import math
from random import randint

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

    def __init__(self, x, y, name):
        self.rect = pg.Rect(x, y, assets[name].get_width(), assets[name].get_height())
        self.name = name
        self.rotatedImage = pg.transform.rotate(assets[name], self.angle)

    def display(self, window, x_offset, y_offset):
        window.blit(self.rotatedImage, (self.rect.x - x_offset, self.rect.y - y_offset))

    def move(self):
        radians = math.radians(self.angle)
        horizontal_movement = math.sin(radians) * self.vel
        vertical_movement = math.cos(radians) * self.vel
        self.rect.x -= horizontal_movement
        self.rect.y -= vertical_movement

    def reload(self):
        self.rotatedImage = pg.transform.rotate(assets[self.name], self.angle)
        self.rect = self.rotatedImage.get_rect(
            center=self.rect.center
        )

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
            self.vel += 1

        # adding the velocities
        self.move()
        self.y_vel += self.sink_speed
        self.y_vel = min(self.y_vel, 1)
        self.rect.y += self.y_vel
        self.vel -= 0.5
        self.vel = max(min(self.vel, 10), 0)

ship = Ship(100, 100, "Ship")

while run:
    clock.tick(fps)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False


    ship.script()

    window.fill((0, 0, 139))
    ship.display(window, 0, 0)
    pg.display.update()

pg.quit()
quit()