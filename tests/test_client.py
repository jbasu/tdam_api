import pytest

from tdam_api import TDClient
from tdam_api.entities import SymbolNotFound


def test_quote():
    c = TDClient(authenticated=False)
    with pytest.raises(SymbolNotFound):
        c.quote("No Dice")
