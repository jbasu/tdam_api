from typing import List, Any


class Entity:
    def __init__(self, data: dict) -> None:
        self._data = data

    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        return self.__getattribute__(name)

    def keys(self) -> List[str]:
        return self._data.keys()

    def __getitem__(self, key):
        return self._data[key]

    def _get_data(self):
        return self._data


# For asset based features to be added later
class Quote(Entity):
    pass


class Instrument(Entity):
    pass


class Fundamental(Entity):
    pass


class Stock(Entity):
    pass


class Option(Entity):
    pass


class Order(Entity):
    pass


# Custom Exceptions
class SymbolNotFound(ValueError):
    pass


class InvalidArgument(ValueError):
    pass
