# science fiction code to see what secundus should look like
import pandas as pd
import numpy as np
import pyglet
from pyglet.gl import *
import secundus


class App(secundus.App):
    def __init__(self, amount, image):
        self.amount = amount
        self.image = image


@App.component('position')
def get_position(app):
    return pd.DataFrame({
        'x': np.random.rand(app.amount),
        'y': np.random.rand(app.amount)
    }, index=range(app.amount))


@App.component('velocity')
def get_velocity(app):
    return pd.DataFrame({
        'x_speed': np.random.randn(app.amount) / 10,
        'y_speed': np.random.randn(app.amount) / 10
    }, index=range(app.amount))


@App.component('color')
def get_color(app):
    # XXX the range is incorrect with this structure.
    return pd.DataFrame(
        [255, 255, 255, 255] * app.amount * 4,
        index=range(app.amount))


@App.component('texture')
def get_texture(app):
    # XXX the range is incorrect with this structure
    return pd.DataFrame(
        app.image.texture.tex_coords * app.amount,
        index=range(app.amount))


@App.system(['position', 'velocity'])
def update_position_by_velocity(app, update, entity_ids, position, velocity):
    position.loc[entity_ids, 'x'] += velocity.loc[
        entity_ids, 'x_speed'] * update.dt
    position.loc[entity_ids, 'y'] += velocity[
        entity_ids, 'y_speed'] * update.dt


@App.system(['position', 'color', 'texture'])
def render(app, update, entity_ids, position, color, texture):
    scaled = position.loc[entity_ids] * 600
    x1 = scaled['x'] - app.image.anchor_x
    y1 = scaled['y'] - app.image.anchor_y
    x2 = x1 + app.image.width
    y2 = y1 + app.image.height
    # what should the entity ids be here?
    df = pd.DataFrame({'a_x': x1, 'a_y': y1,
                       'b_x': x2, 'b_y': y1,
                       'c_x': x2, 'c_y': y2,
                       'd_x': x1, 'd_y': y2},
                      columns=['a_x', 'a_y', 'b_x', 'b_y',
                               'c_x', 'c_y', 'd_x', 'd_y'])

    batch = pyglet.graphics.Batch()
    group = pyglet.sprite.SpriteGroup(
        app.image.get_texture(),
        GL_SRC_ALPHA,
        GL_ONE_MINUS_SRC_ALPHA)
    batch.add(len(scaled.values) * 4, GL_QUADS, group,
              ('v2f/dynamic', df.values.flatten()),
              ('c4B', color.values.flatten()),
              ('t3f', texture.values.flatten()))
    batch.draw()


def main():
    App.commit()

    gold_image = pyglet.image.load('gold.png')
    gold_image.anchor_x = gold_image.width // 2
    gold_image.anchor_y = gold_image.height // 2

    app = App(1000, gold_image)
    app.run()


if __name__ == '__main__':
    main()
