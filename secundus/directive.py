import dectate

from .registry import Registry, System


class App(dectate.App):
    @property
    def registry(self):
        return self.config.registry


@App.directive('component')
class ComponentAction(dectate.Action):
    config = {
        'registry': Registry
    }

    def __init__(self, name):
        self.name = name

    def identifier(self, registry):
        return self.name

    def perform(self, obj, registry):
        registry.register_component(self.name, obj())


@App.directive('system')
class SystemAction(dectate.Action):
    depends = [ComponentAction]

    config = {
        'registry': Registry
    }

    def __init__(self, component_names):
        self.component_names = component_names
        # XXX needs an ordering principle where systems can depend on another
        # to control registration order (and thus execution order)

    def identifier(self, registry):
        # XXX this is actually wrong; we could have multiple systems
        # that affect the same set of components
        return tuple(sorted(self.component_names))

    def perform(self, obj, registry):
        registry.register_system(System(obj, self.component_names))
