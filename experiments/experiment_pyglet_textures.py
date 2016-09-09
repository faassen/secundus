import pandas as pd
import numpy as np
import pyglet
import time
from pyglet.gl import *


class World:
    def __init__(self, position, velocity, color, texture):
        self.position = position
        self.velocity = velocity
        self.color = color
        self.texture = texture


def make_world():
    amount = 1000
    position = pd.DataFrame({
        'x': np.random.rand(amount),
        'y': np.random.rand(amount)
    })
    velocity = pd.DataFrame({
        'x_speed': np.random.randn(amount) / 10,
        'y_speed': np.random.randn(amount) / 10
    })
    # magical 4 times multiplication to satisfy opengl quads..
    color = [255, 255, 255, 255] * amount * 4
    texture = gold_image.texture.tex_coords * amount
    return World(position, velocity, color, texture)


def update(w, dt):
    w.position['x'] += w.velocity['x_speed'] * dt
    w.position['y'] += w.velocity['y_speed'] * dt


gold_image = pyglet.image.load('gold.png')
gold_image.anchor_x = gold_image.width // 2
gold_image.anchor_y = gold_image.height // 2


def render(w):
    scaled = w.position * 600
    x1 = scaled['x'] - gold_image.anchor_x
    y1 = scaled['y'] - gold_image.anchor_y
    x2 = x1 + gold_image.width
    y2 = y1 + gold_image.height
    df = pd.DataFrame({'a_x': x1, 'a_y': y1,
                       'b_x': x2, 'b_y': y1,
                       'c_x': x2, 'c_y': y2,
                       'd_x': x1, 'd_y': y2},
                      columns=['a_x', 'a_y', 'b_x', 'b_y',
                               'c_x', 'c_y', 'd_x', 'd_y'])
    r = df.values.flatten()

    batch = pyglet.graphics.Batch()
    texture = gold_image.get_texture()
    group = pyglet.sprite.SpriteGroup(texture, GL_SRC_ALPHA,
                                      GL_ONE_MINUS_SRC_ALPHA)
    batch.add(len(scaled.values) * 4, GL_QUADS, group,
              ('v2f/dynamic', r),
              ('c4B', w.color),
              ('t3f', w.texture))
    batch.draw()


class Window(pyglet.window.Window):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.w = make_world()
        self.fps_display = pyglet.clock.ClockDisplay()

    def on_draw(self):
        self.clear()
        render(self.w)
        self.fps_display.draw()

    def animate(self, delta_time):
        update(self.w, delta_time)


def main():
    window = Window()
    pyglet.clock.schedule_interval(window.animate, 1 / 60.)
    pyglet.app.run()


if __name__ == '__main__':
    main()
