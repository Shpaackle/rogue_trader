from components.entity_component import EntityComponent


class Item(EntityComponent):
    def __init__(self, use_function=None, **kwargs):
        self.use_function = use_function
        self.function_kwargs = kwargs
