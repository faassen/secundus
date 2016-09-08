import secundus


def test_directive():
    class App(secundus.App):
        pass

    @App.component('position')
    def position_component():
        return secundus.DictContainer()

    @App.component('velocity')
    def velocity_component():
        return secundus.DictContainer()

    @App.system(['position', 'velocity'])
    def update_position(update, r, entity_ids, positions, velocities):
        assert update == 'update'
        assert sorted(entity_ids) == [1, 2]
        assert list(positions.keys()) == [1, 2, 3]
        assert list(velocities.keys()) == [1, 2, 4]
        for entity_id in entity_ids:
            positions[entity_id]['x'] += velocities[entity_id]['speed']

    app = App()
    app.commit()

    r = app.registry

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

    r.execute('update')

    assert r.get(1, 'position')['x'] == 11
    assert r.get(2, 'position')['x'] == 25
    assert r.get(3, 'position')['x'] == 40
