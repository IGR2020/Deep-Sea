import pygame as pg
from GUI import Text
from assets import *

def kill(death_message):
    global run

    heading = Text("You Died.", window_width/2, window_height/2, (255, 255, 255), 80, "arialblack", True)
    subText = Text("From what?", window_width/2, window_height/2+65, (255, 255, 255), 30, "arialbalck", True)
    deathText = Text(death_message, window_width/2, window_height/2+110, (255, 255, 255), 50, "arialbalck", True)
    returnMessage = Text("Press any key to quit (restart not yet available)", window_width/2, window_height*0.8, (255, 255, 255), 50, "arialbalck", True)
    float_count = 1

    while run:
        clock.tick(10)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYUP:
                run = False
        
        returnMessage.rect.y += float_count
        if returnMessage.rect.y < window_height*0.8 - 2:
            float_count = 1
        if returnMessage.rect.y > window_height*0.8 + 2:
            float_count = -1


        window.fill((0, 0, 0))
        heading.display(window)
        subText.display(window)
        deathText.display(window)
        returnMessage.display(window)
        pg.display.update()

    pg.quit()
