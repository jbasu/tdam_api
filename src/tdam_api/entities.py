from typing import List, Dict, Any

import attr


@attr.s(frozen=True)
class Entity:
    _data: Dict[str, Any] = attr.ib()

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
    @classmethod
    def float_to_strike(cls, strike: float = None) -> str:
        return str(round(strike + 0.0, 4))


@attr.s(frozen=True)
class VerticalSpread:
    long_option: Option = attr.ib(validator=attr.validators.instance_of(Option))
    short_option: Option = attr.ib(validator=attr.validators.instance_of(Option))


@attr.s(frozen=True)
class Straddle:
    call_option: Option = attr.ib(validator=attr.validators.instance_of(Option))
    put_option: Option = attr.ib(validator=attr.validators.instance_of(Option))


class Strangle(Straddle):
    pass


@attr.s(frozen=True)
class OptionChain:
    _calls: Dict[str, Option] = attr.ib(validator=attr.validators.instance_of(dict))
    _puts: Dict[str, Option] = attr.ib(validator=attr.validators.instance_of(dict))

    def get(self, strike: float, right: str) -> Option:
        key = Option.float_to_strike(strike)
        if right.lower() == "c" or right.lower() == "call":
            return self._calls.get(key, None)
        if right.lower() == "p" or right.lower() == "put":
            return self._puts.get(key, None)
        raise InvalidArgument("right should be one of (c)all or (p)ut")

    def get_vertical(
        self, right: str = "C", long_strike: float = None, short_strike: float = None
    ) -> VerticalSpread:
        long_opt = self.get(long_strike, right)
        short_opt = self.get(short_strike, right)
        return VerticalSpread(long_opt, short_opt)

    def get_straddle(self, strike: float = None) -> Straddle:
        call_opt = self.get(strike, "C")
        put_opt = self.get(strike, "P")
        return Straddle(call_opt, put_opt)

    def get_strangle(
        self, call_strike: float = None, put_strike: float = None
    ) -> Strangle:
        call_opt = self.get(call_strike, "C")
        put_opt = self.get(put_strike, "P")
        return Strangle(call_opt, put_opt)


class Order(Entity):
    pass


# Custom Exceptions
class SymbolNotFound(ValueError):
    pass


class InvalidArgument(ValueError):
    pass


class AuthenticationRequired(Exception):
    pass
