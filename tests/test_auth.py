from requests import HTTPError
import pytest
from unittest import mock
import responses

from tdam_api import TDClient
from tdam_api.urls import Urls
from tdam_api.entities import AuthenticationRequired, Quote


def test_auth_required():
    c = TDClient(authenticated=False)

    with pytest.raises(AuthenticationRequired):
        c._update_access_token()


def test_missing_credentials():
    with mock.patch.dict("os.environ", clear=True):
        with pytest.raises(Exception) as exc_info:
            c = TDClient()
            assert c is None
        assert "Missing Credentials" in str(exc_info.value)


@responses.activate
def test_quote_auth():
    c = TDClient(access_token="Invalid", refresh_token="Invalid", app_id="Invalid")
    responses.add(
        responses.GET,
        Urls.quote + f"?symbol=FB",
        json={"FB": {"symbol": "FB"}},
        status=200,
    )

    res = c.quote("FB")
    assert isinstance(res, Quote)
    assert res.symbol == "FB"


@responses.activate
def test_access_token_refresh_fail():
    c = TDClient(access_token="Invalid", refresh_token="Invalid", app_id="Invalid")
    responses.add(responses.GET, Urls.quote + f"?symbol=FB", json={}, status=401)

    with mock.patch.object(TDClient, "_update_access_token") as m:
        with pytest.raises(HTTPError):
            c.quote("FB")
        m.assert_called_once()


@responses.activate
def test_access_token_refresh_success():
    c = TDClient(access_token="Invalid", refresh_token="Invalid", app_id="Invalid")
    responses.add(responses.GET, Urls.quote + f"?symbol=FB", json={}, status=401)
    responses.add(
        responses.GET,
        Urls.quote + f"?symbol=FB",
        json={"FB": {"symbol": "FB"}},
        status=200,
    )

    with mock.patch.object(TDClient, "_update_access_token") as m:
        res = c.quote("FB")
        assert isinstance(res, Quote)
        assert res.symbol == "FB"
        m.assert_called_once()


@pytest.mark.local
def test_auth_refresh():
    c = TDClient(access_token="Invalid token")
    with mock.patch.object(
        TDClient, "_update_access_token", side_effect=c._update_access_token
    ) as m:
        res = c.quote("AAPL")
        m.assert_called_once()
        assert isinstance(res, Quote)
        assert res.bidPrice is not None
        assert res.symbol == "AAPL"
        assert res.exchangeName == "NASD"

    with mock.patch.object(
        TDClient, "_update_access_token", side_effect=c._update_access_token
    ) as m:
        res = c.quote("FB")
        m.assert_not_called()
        assert isinstance(res, Quote)
        assert res.bidPrice is not None
        assert res.symbol == "FB"
        assert res.exchangeName == "NASD"
