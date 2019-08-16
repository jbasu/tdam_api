import os
from datetime import datetime, timedelta

import pytest
import responses
from unittest import mock

from tdam_api import TDClient
from tdam_api.entities import (
    SymbolNotFound,
    Quote,
    Instrument,
    Fundamental,
    InvalidArgument,
)
from tdam_api.urls import Urls

apikey = os.environ["TDAM_APP_ID"]


def quote_resp(symbol: str, exchange: str = "NASDAQ") -> dict:
    out = {f"{symbol}": {"symbol": f"{symbol}", "exchange": f"{exchange}"}}
    return out


def fundamental_resp(symbol: str):
    out = {
        f"{symbol}": {
            "fundamental": {
                "symbol": f"{symbol}",
                "marketCap": 234343,
                "peRatio": 18.15,
            }
        }
    }
    return out


def validate_quote_response(res: Quote, symbol: str):
    assert isinstance(res, Quote)
    assert res.bidPrice is not None
    assert res.symbol == symbol
    assert res.exchangeName == "NASD"


@responses.activate
def test_quote():
    c = TDClient(authenticated=False)
    sym = "FB"

    responses.add(
        responses.GET,
        Urls.quote + f"?apikey={apikey}&symbol={sym}",
        json=quote_resp(sym),
        status=200,
    )
    res = c.quote(sym)
    assert res.symbol == sym

    responses.add(
        responses.GET,
        Urls.quote + f"?apikey={apikey}&symbol=No Dice",
        json={},
        status=200,
    )
    with pytest.raises(SymbolNotFound):
        c.quote("No Dice")


@responses.activate
def test_find_instrument():
    c = TDClient(authenticated=False)
    sym = "LYF.*"

    responses.add(
        responses.GET,
        Urls.search + f"?apikey={apikey}&symbol={sym}&projection=symbol-regex",
        json=quote_resp("LYFT"),
        status=200,
    )
    res = c.find_instrument(sym)
    assert len(res) == 1
    assert isinstance(res["LYFT"], Instrument)


@responses.activate
def test_get_fundamentals():
    c = TDClient(authenticated=False)
    sym = "AAPL"

    responses.add(
        responses.GET,
        Urls.search + f"?apikey={apikey}&symbol={sym}&projection=fundamental",
        json=fundamental_resp(sym),
        status=200,
    )
    res = c.get_fundamentals(sym)
    assert isinstance(res, Fundamental)
    assert res.symbol == sym
    assert res.peRatio == 18.15


def test_stock():
    c = TDClient(authenticated=False)
    with mock.patch.object(TDClient, "quote") as m:
        c.stock("FB")
        m.assert_called_once()
        m.assert_called_with("FB")


def test_get_history():
    c = TDClient(authenticated=False)
    with pytest.raises(InvalidArgument):
        c.get_history(
            "AAPL", start_dt=datetime(2019, 1, 31), end_dt=datetime(2019, 1, 1)
        )

    with pytest.raises(InvalidArgument):
        c.get_history("AAPL")

    with pytest.raises(InvalidArgument):
        c.get_history(
            "AAPL",
            start_dt=datetime(2019, 1, 1),
            end_dt=datetime(2019, 1, 31),
            freq="5d",
        )


@pytest.mark.apitest
def test_quote_unauth():
    c = TDClient(authenticated=False)

    # Test Symbol not found
    with pytest.raises(SymbolNotFound):
        c.quote("No Dice")

    # Test valid case
    res = c.quote("FB")
    validate_quote_response(res, "FB")


@pytest.mark.apitest
def test_quotes_unauth():
    c = TDClient(authenticated=False)

    # Test Symbol not found
    with pytest.raises(SymbolNotFound):
        c.quotes(["No Dice", "None Here Too"])

    # Test valid case
    res = c.quotes(["FB", "MSFT"])
    assert len(res.keys()) == 2
    assert "FB" in res.keys()
    assert "MSFT" in res.keys()
    validate_quote_response(res["FB"], "FB")
    validate_quote_response(res["MSFT"], "MSFT")


@pytest.mark.apitest
def test_find_instrument_unauth():
    c = TDClient(authenticated=False)
    res = c.find_instrument("LYF.*")
    # Expecting LYFE and LYFT
    assert len(res.keys()) == 2
    assert "LYFE" in res.keys()
    assert "LYFT" in res.keys()
    assert isinstance(res["LYFT"], Instrument)
    assert res["LYFT"].symbol == "LYFT"
    assert res["LYFT"].exchange == "NASDAQ"


@pytest.mark.apitest
def test_get_fundamentals_unauth():
    c = TDClient(authenticated=False)
    res = c.get_fundamentals("AAPL")
    assert isinstance(res, Fundamental)
    assert res.symbol == "AAPL"
    assert res.peRatio is not None
    assert res.marketCap is not None


@pytest.mark.apitest
def test_get_history_unauth():
    c = TDClient(authenticated=False)
    res = c.get_history(
        "AAPL", start_dt=datetime(2019, 1, 1), end_dt=datetime(2019, 1, 31)
    )
    assert len(res) == 21
    assert len(res[0].keys()) == 6
    keys = ["open", "high", "low", "close", "volume", "datetime"]
    for k in keys:
        assert k in res[0].keys()

    res = c.get_history(
        "No Dice", start_dt=datetime(2019, 1, 1), end_dt=datetime(2019, 1, 31)
    )
    assert res is None


@pytest.mark.apitest
def test_get_history_df_unauth():
    import pandas as pd

    c = TDClient(authenticated=False)
    res = c.get_history_df(
        "AAPL", start_dt=datetime(2019, 1, 1), end_dt=datetime(2019, 1, 31)
    )
    assert isinstance(res, pd.DataFrame)
    assert res.shape == (21, 5)
    assert res.index.name == "datetime"
    keys = ["open", "high", "low", "close", "volume"]
    for k in res.columns:
        assert k in keys

    res = c.get_history_df(
        "No Dice", start_dt=datetime(2019, 1, 1), end_dt=datetime(2019, 1, 31)
    )
    assert res is None


@pytest.mark.apitest
def test_get_intraday_history_df_unauth():
    import pandas as pd

    c = TDClient(authenticated=False)
    res = c.get_history_df(
        "AAPL",
        start_dt=datetime.today() - timedelta(4),
        end_dt=datetime.today(),
        freq="30min",
    )
    assert isinstance(res, pd.DataFrame)
    assert res.shape[1] == 5
    assert res.index.name == "datetime"
    keys = ["open", "high", "low", "close", "volume"]
    for k in res.columns:
        assert k in keys

    with pytest.raises(InvalidArgument):
        res = c.get_history_df(
            "AAPL",
            start_dt=datetime.today() - timedelta(60),
            end_dt=datetime.today() - timedelta(55),
            freq="30min",
        )
