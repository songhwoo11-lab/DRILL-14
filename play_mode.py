from pico2d import *
import game_world
import game_framework
from boy import Boy
from eagle import create_flock
from grass import Grass

boy = None
eagles = []


def handle_events():


    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)


def init():
    global boy, eagles

    eagles = create_flock(get_canvas_width(), get_canvas_height())
    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)

    for eagle in eagles:
        game_world.add_oject(eagle)


def pause():
    boy.pause()


def resume():
    pass


def finish():
    global boy, eagles
    game_world.clear()
    boy = None
    eagles = []


def update():
    game_world.update()

def render():
    clear_canvas()
    game_world.render()
    update_canvas()








