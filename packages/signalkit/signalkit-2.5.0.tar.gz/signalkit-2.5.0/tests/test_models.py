class MyHandlerClass:
    def __init__(self):
        self.handled_value = None

    def method_handler(self, sender, value_to_set=None):
        if value_to_set is not None:
            self.handled_value = value_to_set
            return f"set_{value_to_set}"
        return None

    async def async_method_handler(self, sender, value_to_set=None):
        if value_to_set is not None:
            self.handled_value = value_to_set
            return f"async_set_{value_to_set}"
        return None
