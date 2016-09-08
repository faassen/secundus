import pytest
from secundus.registry import (
    Registry, System, entity_ids_system, item_system,
    DataFrameContainer)


def test_registry_system_dict_container():
    r = Registry()
    r.register_component('position')
    r.register_component('velocity')

    def update_position(update, r, entity_ids, positions, velocities):
        assert update == 'update'
        assert sorted(entity_ids) == [1, 2]
        assert list(positions.keys()) == [1, 2, 3]
        assert list(velocities.keys()) == [1, 2, 4]
        for entity_id in entity_ids:
            positions[entity_id]['x'] += velocities[entity_id]['speed']

    r.register_system(System(update_position, ['position', 'velocity']))

    p1 = {'x': 10}
    p2 = {'x': 20}
    p3 = {'x': 40}

    r.add_component(1, 'position', p1)
    r.add_component(2, 'position', p2)
    r.add_component(3, 'position', p3)

    v1 = {'speed': 1}
    v2 = {'speed': 5}
    v4 = {'speed': 10}

    r.add_component(1, 'velocity', v1)
    r.add_component(2, 'velocity', v2)
    r.add_component(4, 'velocity', v4)

    assert r.get(1, 'position')['x'] == 10
    assert r.get(2, 'position')['x'] == 20

    assert r.get(1, 'velocity')['speed'] == 1
    assert r.get(2, 'velocity')['speed'] == 5

    r.execute('update')

    assert r.get(1, 'position')['x'] == 11
    assert r.get(2, 'position')['x'] == 25
    assert r.get(3, 'position')['x'] == 40


def test_registry_system_dict_entity_ids():
    r = Registry()
    r.register_component('position')
    r.register_component('velocity')

    def update_position(update, r, entity_ids, positions, velocities):
        assert update == 'update'
        assert sorted(entity_ids) == [1, 2]
        for position, velocity in zip(positions, velocities):
            position['x'] += velocity['speed']

    r.register_system(entity_ids_system(
        update_position, ['position', 'velocity']))

    p1 = {'x': 10}
    p2 = {'x': 20}
    p3 = {'x': 40}

    r.add_component(1, 'position', p1)
    r.add_component(2, 'position', p2)
    r.add_component(3, 'position', p3)

    v1 = {'speed': 1}
    v2 = {'speed': 5}
    v4 = {'speed': 10}

    r.add_component(1, 'velocity', v1)
    r.add_component(2, 'velocity', v2)
    r.add_component(4, 'velocity', v4)

    assert r.get(1, 'position')['x'] == 10
    assert r.get(2, 'position')['x'] == 20

    assert r.get(1, 'velocity')['speed'] == 1
    assert r.get(2, 'velocity')['speed'] == 5

    r.execute('update')

    assert r.get(1, 'position')['x'] == 11
    assert r.get(2, 'position')['x'] == 25
    assert r.get(3, 'position')['x'] == 40


def test_registry_system_dict_add_components():
    r = Registry()
    r.register_component('position')
    r.register_component('velocity')

    def update_position(update, r, entity_ids, positions, velocities):
        assert update == 'update'
        assert sorted(entity_ids) == [1, 2]
        for position, velocity in zip(positions, velocities):
            position['x'] += velocity['speed']

    r.register_system(entity_ids_system(
        update_position, ['position', 'velocity']))

    p1 = {'x': 10}
    p2 = {'x': 20}
    p3 = {'x': 40}

    v1 = {'speed': 1}
    v2 = {'speed': 5}
    v4 = {'speed': 10}

    r.add_components(1, position=p1, velocity=v1)
    r.add_components(2, position=p2, velocity=v2)
    r.add_components(3, position=p3)
    r.add_components(4, velocity=v4)

    assert r.get(1, 'position')['x'] == 10
    assert r.get(2, 'position')['x'] == 20

    assert r.get(1, 'velocity')['speed'] == 1
    assert r.get(2, 'velocity')['speed'] == 5

    r.execute('update')

    assert r.get(1, 'position')['x'] == 11
    assert r.get(2, 'position')['x'] == 25
    assert r.get(3, 'position')['x'] == 40


def test_registry_system_dict_add_entity():
    r = Registry()
    r.register_component('position')
    r.register_component('velocity')

    def update_position(update, r, entity_ids, positions, velocities):
        assert update == 'update'
        assert sorted(entity_ids) == [0, 1]
        for position, velocity in zip(positions, velocities):
            position['x'] += velocity['speed']

    r.register_system(entity_ids_system(
        update_position, ['position', 'velocity']))

    p1 = {'x': 10}
    p2 = {'x': 20}
    p3 = {'x': 40}

    v1 = {'speed': 1}
    v2 = {'speed': 5}
    v4 = {'speed': 10}

    r.add_entity(position=p1, velocity=v1)
    r.add_entity(position=p2, velocity=v2)
    r.add_entity(position=p3)
    r.add_entity(velocity=v4)

    assert r.get(0, 'position')['x'] == 10
    assert r.get(1, 'position')['x'] == 20

    assert r.get(0, 'velocity')['speed'] == 1
    assert r.get(1, 'velocity')['speed'] == 5

    r.execute('update')

    assert r.get(0, 'position')['x'] == 11
    assert r.get(1, 'position')['x'] == 25
    assert r.get(2, 'position')['x'] == 40


def test_registry_system_df():
    r = Registry()
    r.register_component('position', DataFrameContainer())
    r.register_component('velocity', DataFrameContainer())

    def update_position(update, r, entity_ids, positions, velocities):
        assert update == 'update'
        assert sorted(entity_ids) == [1, 2]
        positions.loc[entity_ids, 'x'] += velocities.loc[entity_ids, 'speed']

    r.register_system(System(
        update_position,
        ['position', 'velocity']))

    p1 = {'x': 10}
    p2 = {'x': 20}
    p3 = {'x': 40}

    r.add_component(1, 'position', p1)
    r.add_component(2, 'position', p2)
    r.add_component(3, 'position', p3)

    v1 = {'speed': 1}
    v2 = {'speed': 5}
    v4 = {'speed': 10}

    r.add_component(1, 'velocity', v1)
    r.add_component(2, 'velocity', v2)
    r.add_component(4, 'velocity', v4)

    assert r.get(1, 'position')['x'] == 10
    assert r.get(2, 'position')['x'] == 20

    assert r.get(1, 'velocity')['speed'] == 1
    assert r.get(2, 'velocity')['speed'] == 5

    r.execute('update')

    assert r.get(1, 'position')['x'] == 11
    assert r.get(2, 'position')['x'] == 25
    assert r.get(3, 'position')['x'] == 40


def test_registry_system_item():
    r = Registry()
    r.register_component('position')
    r.register_component('velocity')

    seen_entity_ids = set()

    def update_position(update, r, entity_id, position, velocity):
        assert update == 'update'
        seen_entity_ids.add(entity_id)
        position.x += velocity.speed

    r.register_system(item_system(update_position, ['position', 'velocity']))

    class Position:
        def __init__(self, x):
            self.x = x

    class Velocity:
        def __init__(self, speed):
            self.speed = speed

    p1 = Position(10)
    p2 = Position(20)
    p3 = Position(40)

    r.add_component(1, 'position', p1)
    r.add_component(2, 'position', p2)
    r.add_component(3, 'position', p3)

    v1 = Velocity(1)
    v2 = Velocity(5)
    v4 = Velocity(10)

    r.add_component(1, 'velocity', v1)
    r.add_component(2, 'velocity', v2)
    r.add_component(4, 'velocity', v4)

    assert r.get(1, 'position').x == 10
    assert r.get(2, 'position').x == 20

    assert r.get(1, 'velocity').speed == 1
    assert r.get(2, 'velocity').speed == 5

    r.execute('update')

    assert r.get(1, 'position').x == 11
    assert r.get(2, 'position').x == 25
    assert seen_entity_ids == set([1, 2])


def test_registry_system_add_remove():
    r = Registry()
    r.register_component('position')
    r.register_component('velocity')

    def update(update, positions, velocities):
        pass

    s = System(update, ['position', 'velocity'])

    r.register_system(s)

    class Position:
        def __init__(self, x):
            self.x = x

    class Velocity:
        def __init__(self, speed):
            self.speed = speed

    p1 = Position(10)
    p2 = Position(20)
    p3 = Position(40)

    r.add_component(1, 'position', p1)
    r.add_component(2, 'position', p2)
    r.add_component(3, 'position', p3)
    assert s.entity_ids == set()

    v1 = Velocity(1)
    v2 = Velocity(5)
    v4 = Velocity(10)

    r.add_component(1, 'velocity', v1)
    assert s.entity_ids == set([1])
    r.add_component(2, 'velocity', v2)
    assert s.entity_ids == set([1, 2])
    r.add_component(4, 'velocity', v4)
    assert s.entity_ids == set([1, 2])

    r.remove_component(1, 'velocity')
    assert s.entity_ids == set([2])


def test_registry_collision_dict():
    r = Registry()
    r.register_component('position')
    r.register_component('size')
    r.register_component('collision')

    def update_collision(update, r, entity_ids, position, size):
        # stupidly inefficient
        for e1, p1, s1 in zip(entity_ids, position, size):
            for e2, p2, s2 in zip(entity_ids, position, size):
                if e1 == e2:
                    continue
                if (p2['x'] + s2['s']) > (p1['x'] - s1['s']) and\
                   (p2['x'] - s2['s']) < (p1['x'] + s1['s']):
                    r.add_component(e1, 'collision', {'other': e2})

    r.register_system(entity_ids_system(update_collision,
                                        ['position', 'size']))

    e0 = r.add_entity(position={'x': 10}, size={'s': 5})
    e1 = r.add_entity(position={'x': 20}, size={'s': 5})
    e2 = r.add_entity(position={'x': 23}, size={'s': 5})

    r.execute(r)

    with pytest.raises(KeyError):
        r.get(e0, 'collision')

    assert r.get(e1, 'collision')['other'] == e2
    assert r.get(e2, 'collision')['other'] == e1


def test_registry_collision_df():
    r = Registry()
    r.register_component('position', DataFrameContainer())
    r.register_component('size', DataFrameContainer())
    r.register_component('collision', DataFrameContainer())

    def update_collision(update, r, entity_ids, position, size):
        # even more stupidly inefficient
        for e1 in entity_ids:
            p1 = position.loc[e1]
            s1 = size.loc[e1]
            for e2 in entity_ids:
                if e1 == e2:
                    continue
                p2 = position.loc[e2]
                s2 = size.loc[e2]
                if (p2['x'] + s2['s']) > (p1['x'] - s1['s']) and\
                   (p2['x'] - s2['s']) < (p1['x'] + s1['s']):
                    r.add_component(e1, 'collision', {'other': e2})

    r.register_system(System(
        update_collision,
        ['position', 'size']))

    e0 = r.add_entity(position={'x': 10}, size={'s': 5})
    e1 = r.add_entity(position={'x': 20}, size={'s': 5})
    e2 = r.add_entity(position={'x': 23}, size={'s': 5})

    r.execute(r)

    with pytest.raises(KeyError):
        r.get(e0, 'collision')

    assert r.get(e1, 'collision')['other'] == e2
    assert r.get(e2, 'collision')['other'] == e1

                     # def test_registry_explosion():
#     r = Registry()
#     r.register_component('position')
#     r.register_component('collision')
#     r.register_component('velocity')
#     r.register_component('debris')

#     def update_position(update, positions, velocities):
#         for position, velocity in zip(positions, velocities):
#             position.x += velocity.x_velocity
#             position.y += velocity.y_velocity

#     r.register_system(System(update_position, ['position', 'velocity']))

#     def update_collision(update, positions, collisions):
#         for position, collision in zip(positions, collisions):
#             # remove collision as we're handling it
#             update.remove(collision.entity_id, 'collision')
#             # debris flies in 4 directions
#             for x_velocity, y_velocity in [(0, -10), (10, 0),
#                                            (0, 10), (-10, 0)]:
#                 new_entity_id = update.create_entity_id()
#                 update.add_component(new_entity_id, 'debris',
#                            Debris())
#                 update.add_component(new_entity_id, 'position',
#                            Position(position.x, position.y))
#                 update.add_component(new_entity_id, 'velocity',
#                            Velocity(x_velocity, y_velocity))

#     class Position:
#         def __init__(self, x, y):
#             self.x = x
#             self.y = y

#     class Velocity:
#         def __init__(self, x_velocity, y_velocity):
#             self.x_velocity = x_velocity
#             self.y_velocity = y_velocity

#     class Collision:
#         def __init__(self, entity_id):
#             self.entity_id = entity_id

#     class Debris:
#         pass

#     p1 = Position(10)
#     p2 = Position(20)
#     p3 = Position(40)

#     r.add_component(1, 'position', p1)
#     r.add_component(2, 'position', p2)
#     r.add_component(3, 'position', p3)

#     v1 = Velocity(1)
#     v2 = Velocity(5)
#     v4 = Velocity(10)

#     r.add_component(1, 'velocity', v1)
#     r.add_component(2, 'velocity', v2)
#     r.add_component(4, 'velocity', v4)

#     assert r.get(1, 'position').x == 10
#     assert r.get(2, 'position').x == 20

#     assert r.get(1, 'velocity').speed == 1
#     assert r.get(2, 'velocity').speed == 5

#     r.execute('update')

#     assert r.get(1, 'position').x == 11
#     assert r.get(2, 'position').x == 25
