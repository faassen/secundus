from functools import partial
import pandas as pd

# the following functions should be easy:

# a function that just gets all the component collections it requires.
# useful for pandas.

# a function that gets the component collections, filtered by the
# intersection of entity_id. Useful for Python, not useful for pandas.

# a function that gets a single instance of each component it requests.
# useful for Python update functions, not useful for pandas.

# a pure function that gets all component collections it requires, and
# must return new copies of those component collections, including having
# done any add and removal.

# a pure function that gets the component collections, filtered by the
# interaction of entity_ids, and returns collections with updated components,
# plus component_id / entity_ids to remove, plus component / entity_ids to add.
# Useful for Pandas and Python.

# a pure function that *returns* a new single instance of each component it
# requests. This is going to be stored in the collection.


class DictContainer(dict):
    """Component container backed by dict.

    This is in fact a Python dict.
    """
    def value(self):
        """Get the underlying container object.
        """
        return self


class DataFrameContainer:
    """Component container backed by pandas DataFrame.

    This can give a performance boost when you have a large
    amount of components and you use vectorized functionality to query
    and update components.

    adds and removes are buffered for efficiency, only once
    the container is accessed for its value is the buffer flushed;
    typically this happens before the next system runs that requires
    this component container.
    """
    def __init__(self):
        self.df = pd.DataFrame([])
        self.to_add_entity_ids = []
        self.to_add_components = []
        self.to_remove_entity_ids = []

    def __setitem__(self, entity_id, component):
        self.to_add_entity_ids.append(entity_id)
        self.to_add_components.append(component)

    def __delitem__(self, entity_id):
        self.to_remove.append(entity_id)

    def _complete(self):
        self._complete_remove()
        self._complete_add()

    def _complete_add(self):
        if not self.to_add_entity_ids:
            return
        add_df = self._create(self.to_add_components,
                              self.to_add_entity_ids)
        self.df = pd.concat([self.df, add_df])
        self.to_add_entity_ids = []
        self.to_add_components = []

    def _complete_remove(self):
        if not self.to_remove_entity_ids:
            return
        self.df = self.df.drop(self.to_remove_entity_ids)

    def _create(self, components, entity_ids):
        return pd.DataFrame(components, index=entity_ids)

    def __getitem__(self, entity_id):
        self._complete()
        return self.df.loc[entity_id]

    def __contains__(self, entity_id):
        # cannot call self._complete here as we do not want
        # to trigger it during tracking checks
        if entity_id in self.to_remove_entity_ids:
            return False
        return (entity_id in self.df.index or
                entity_id in self.to_add_entity_ids)

    def value(self):
        """Backing value is a pandas DataFrame
        """
        self._complete()
        return self.df


class Registry:
    """Entity component system registry.
    """
    def __init__(self):
        self.components = {}
        self.systems = []
        self.component_to_systems = {}
        self.entity_id_counter = 0

    def register_component(self, component_id, container=None):
        """Register a component container that contains components.
        """
        if container is None:
            container = DictContainer()
        self.components[component_id] = container
        self.component_to_systems[component_id] = []

    def register_system(self, system):
        """Register a system that processes components.
        """
        # XXX add topological sort options so you can design system
        # execution order where this matters
        self.systems.append(system)
        self._update_component_to_systems(system, system.component_ids)

    def _update_component_to_systems(self, system, component_ids):
        """Maintain map of component_ids to systems that are interested.
        """
        for component_id in component_ids:
            self.component_to_systems.setdefault(component_id, []).append(
                system)

    def has_components(self, entity_id, component_ids):
        """Check whether an entity has the listed component_ids.
        """
        for component_id in component_ids:
            if entity_id not in self.components[component_id]:
                return False
        return True

    def get(self, entity_id, component_id):
        """Get a specific component for an entity.

        KeyError if this component doesn't exist for this entity.
        """
        return self.components[component_id][entity_id]

    def create_entity_id(self):
        """Create a new entity id.
        """
        result = self.entity_id_counter
        self.entity_id_counter += 1
        return result

    def add_entity(self, **components):
        """Add a new entity with a bunch of associated components.
        """
        entity_id = self.create_entity_id()
        self.add_components(entity_id, **components)
        return entity_id

    def add_components(self, entity_id, **components):
        """Add a bunch of components for an entity.
        """
        for component_id, component in components.items():
            self.add_component(entity_id, component_id, component)

    def add_component(self, entity_id, component_id, component):
        """Add a component to an entity.

        This makes sure all interested systems track this entity.
        """
        self.components[component_id][entity_id] = component
        for system in self.component_to_systems[component_id]:
            if self.has_components(entity_id, system.component_ids):
                system.track(entity_id)

    def remove_component(self, entity_id, component_id):
        """Remove a component from an entity.

        This makes sure interested systems stop tracking this entity.
        """
        del self.components[component_id][entity_id]
        for system in self.component_to_systems[component_id]:
            system.forget(entity_id)

    def component_containers(self, component_ids):
        """Get component containers.
        """
        return [self.components[component_id]
                for component_id in component_ids]

    def execute(self, update):
        """Execute all systems.

        The update argument is passed through to all systems. It can
        contain information about the current state of the game, including
        an API to add components.
        """
        for system in self.systems:
            containers = self.component_containers(system.component_ids)
            system.execute(update, self, containers)


class System:
    def __init__(self, func, component_ids):
        """
        :param func: a function that takes the update and component
          container arguments and updates the state accordingly.
        :param component_ids: the component ids that this system cares about.
        """
        self.func = func
        self.component_ids = component_ids
        self.entity_ids = set()

    def execute(self, update, registry, component_containers):
        """Execute this system.

        Passed in are the component containers that this system can
        consult and update.
        """
        args = ([self.entity_ids] +
                [container.value() for container in component_containers])
        self.func(update, registry, *args)

    def track(self, entity_id):
        """Track entity_id with this system."""
        self.entity_ids.add(entity_id)

    def forget(self, entity_id):
        """Stop tracking entity_id with this system."""
        self.entity_ids.remove(entity_id)


def _entity_ids_func(func, update, r, entity_ids, *containers):
    entity_ids_containers = [
        [container[entity_id] for entity_id in entity_ids]
        for container in containers]
    func(update, r, entity_ids, *entity_ids_containers)


def entity_ids_system(func, component_ids):
    return System(partial(_entity_ids_func, func), component_ids)


def _item_func(func, update, r, *lists):
    for items in zip(*lists):
        func(update, r, *items)


def item_system(func, component_ids):
    """A system where you update individual items, not collections of them.
    """
    return System(partial(_entity_ids_func, partial(_item_func, func)),
                  component_ids)
