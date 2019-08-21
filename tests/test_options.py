import os
import json

import pytest
import responses

from tdam_api import TDClient
from tdam_api.entities import (
    InvalidArgument,
    SymbolNotFound,
    Option,
    OptionChain,
    VerticalSpread,
    Straddle,
    Strangle,
)
from tdam_api.urls import Urls

apikey = os.environ["TDAM_APP_ID"]


@responses.activate
def test_get_expirations():
    c = TDClient(authenticated=False)
    sym = "AAPL"

    with open("tests/data/aapl_all_exp_calls.json", "r") as json_file:
        chain_resp = json.load(json_file)

    responses.add(
        responses.GET,
        Urls.option_chain
        + (
            f"?apikey={apikey}&symbol={sym}"
            f"&contractType=CALL&strategy=SINGLE&range=NTM"
        ),
        json=chain_resp,
        status=200,
    )

    expiries = c.get_expirations(sym)
    expected = [
        "2019-08-23",
        "2019-08-30",
        "2019-09-06",
        "2019-09-13",
        "2019-09-20",
        "2019-09-27",
        "2019-10-18",
        "2019-11-15",
        "2019-12-20",
        "2020-01-17",
        "2020-03-20",
        "2020-04-17",
        "2020-06-19",
        "2020-09-18",
        "2021-01-15",
        "2021-06-18",
    ]

    assert sorted(expiries) == sorted(expected)


@responses.activate
def test_get_option_chain():
    c = TDClient(authenticated=False)
    sym = "AAPL"
    expiry = "2019-08-23"

    with pytest.raises(InvalidArgument):
        c.get_option_chain()
    with pytest.raises(InvalidArgument):
        c.get_option_chain(sym)
    with pytest.raises(InvalidArgument):
        c.get_option_chain(expiry=expiry)

    with open("tests/data/aapl_one_expiry.json", "r") as json_file:
        chain_resp = json.load(json_file)

    responses.add(
        responses.GET,
        Urls.option_chain
        + (
            f"?apikey={apikey}&symbol={sym}"
            f"&strategy=SINGLE&fromDate={expiry}&toDate={expiry}"
        ),
        json=chain_resp,
        status=200,
    )
    chain = c.get_option_chain(sym, expiry)
    expected_strikes = list(range(130, 150, 5))
    expected_strikes.extend([x / 10 for x in range(1500, 2501, 25)])

    assert isinstance(chain, OptionChain)
    assert len(chain._calls) == len(expected_strikes)
    assert len(chain._puts) == len(expected_strikes)
    for strike in expected_strikes:
        assert isinstance(chain.get(strike, "C"), Option)
        assert isinstance(chain.get(strike, "P"), Option)

    with pytest.raises(InvalidArgument):
        chain.get(200, "")
    with pytest.raises(InvalidArgument):
        chain.get(200, "call_option")

    vs = chain.get_vertical("C", 145, 150)
    assert isinstance(vs, VerticalSpread)
    assert isinstance(vs.long_option, Option)
    assert isinstance(vs.short_option, Option)
    assert vs.long_option.strikePrice == 145.0
    assert vs.short_option.strikePrice == 150.0

    s = chain.get_straddle(200)
    assert isinstance(s, Straddle)
    assert isinstance(s.call_option, Option)
    assert isinstance(s.put_option, Option)
    assert s.call_option.strikePrice == 200.0
    assert s.put_option.strikePrice == 200.0

    s = chain.get_strangle(200, 202.5)
    assert isinstance(s, Strangle)
    assert isinstance(s.call_option, Option)
    assert isinstance(s.put_option, Option)
    assert s.call_option.strikePrice == 200.0
    assert s.put_option.strikePrice == 202.5


@responses.activate
def test_get_option():
    c = TDClient(authenticated=False)
    sym = "AAPL"
    expiry = "2019-08-23"
    strike = 200

    with open("tests/data/aapl_200.json", "r") as json_file:
        chain_resp = json.load(json_file)

    responses.add(
        responses.GET,
        Urls.option_chain
        + (
            f"?apikey={apikey}&symbol={sym}"
            f"&contractType=CALL&strategy=SINGLE&strike=200"
            f"&fromDate={expiry}&toDate={expiry}"
        ),
        json=chain_resp,
        status=200,
    )

    opt = c.get_option(symbol=sym, expiry=expiry, right="C", strike=strike)

    assert isinstance(opt, Option)
    assert opt.strikePrice == 200.0
    assert opt.putCall == "CALL"
    assert opt.lastTradingDay == 1566532800000
    assert sym in opt.symbol

    responses.add(
        responses.GET,
        Urls.option_chain
        + (
            f"?apikey={apikey}&symbol={sym}"
            f"&contractType=PUT&strategy=SINGLE&strike=200"
            f"&fromDate={expiry}&toDate={expiry}"
        ),
        json=chain_resp,
        status=200,
    )

    opt = c.get_option(symbol=sym, expiry=expiry, right="P", strike=strike)

    assert isinstance(opt, Option)
    assert opt.strikePrice == 200.0
    assert opt.putCall == "PUT"
    assert opt.lastTradingDay == 1566532800000
    assert sym in opt.symbol

    with open("tests/data/no_dice.json", "r") as json_file:
        chain_resp = json.load(json_file)

    sym = "NO DICE"
    responses.add(
        responses.GET,
        Urls.option_chain
        + (
            f"?apikey={apikey}&symbol={sym}"
            f"&contractType=CALL&strategy=SINGLE&strike=200"
            f"&fromDate={expiry}&toDate={expiry}"
        ),
        json=chain_resp,
        status=200,
    )

    with pytest.raises(SymbolNotFound):
        c.get_option(symbol="NO DICE", expiry=expiry, right="C", strike=strike)
