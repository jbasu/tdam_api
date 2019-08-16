import os
import functools
from typing import List, Dict
from datetime import datetime

import requests

from .urls import Urls
from .entities import (
    Quote,
    Instrument,
    Fundamental,
    Stock,
    SymbolNotFound,
    InvalidArgument,
)


def auth_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if args[0]._authenticated:
            return f(*args, **kwargs)
        else:
            raise Exception("Method requires authentication")

    return wrapper


class TDClient:
    def __init__(
        self, access_token=None, refresh_token=None, app_id=None, authenticated=True
    ):
        if authenticated:
            self.access_token = self._get_auth_var(access_token, "TDAM_ACCESS_TOKEN")
            self.refresh_token = self._get_auth_var(refresh_token, "TDAM_REFRESH_TOKEN")

        self.app_id = self._get_auth_var(app_id, "TDAM_APP_ID")
        self._authenticated = authenticated

    def _get_auth_var(self, param: str, env_var: str) -> str:
        if param is None:
            if env_var in os.environ:
                return os.environ[env_var]
            else:
                raise Exception("Missing Credentials.")
        else:
            return param

    @auth_required
    def _update_access_token(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.app_id,
        }
        resp: requests.Response = requests.post(Urls.auth, data=data)
        if resp.status_code == 200:
            self.access_token = resp.json()["access_token"]
        else:
            resp.raise_for_status()

    def _auth_header(self):
        return {"Authorization": "Bearer " + self.access_token}

    def _get_with_retry(self, url: str, params: dict) -> requests.Response:
        if not self._authenticated:
            params["apikey"] = self.app_id
            resp: requests.Response = requests.get(url, params=params)
            if resp.status_code == 200:
                return resp
            else:
                resp.raise_for_status()

        resp: requests.Response = requests.get(
            url, params=params, headers=self._auth_header()
        )

        if resp.status_code == 200:
            return resp
        elif resp.status_code == 401:
            self._update_access_token()
            resp = requests.get(url, params=params, headers=self._auth_header())
            if resp.status_code == 200:
                return resp

        resp.raise_for_status()

    @auth_required
    def _post_with_retry(self, url, data) -> requests.Response:
        resp: requests.Response = requests.post(
            url, json=data, headers=self._auth_header()
        )

        if resp.status_code == 200:
            return resp
        elif resp.status_code == 401:
            self._update_access_token()
            resp = requests.post(url, json=data, headers=self._auth_header())
            if resp.status_code == 200:
                return resp

        # resp will contain the latest http call response
        resp.raise_for_status()

    def quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        params = {"symbol": ",".join(symbols)}
        resp: requests.Response = self._get_with_retry(Urls.quote, params=params)
        output = resp.json()
        output = {k: Quote(v) for k, v in output.items()}
        if output:
            return output
        else:
            raise SymbolNotFound(f"{','.join(symbols)} not found")

    def quote(self, symbol: str) -> Quote:
        output = self.quotes([symbol])
        return output[symbol]

    def stock(self, symbol: str) -> Stock:
        output = self.quote(symbol)
        return Stock(output._get_data)

    def find_instrument(self, symbol_pattern: str) -> Dict[str, Instrument]:
        params = {"symbol": symbol_pattern, "projection": "symbol-regex"}
        resp: requests.Response = self._get_with_retry(Urls.search, params=params)
        output = resp.json()
        output = {k: Instrument(v) for k, v in output.items()}
        return output

    def get_fundamentals(self, symbol: str) -> Fundamental:
        params = {"symbol": symbol, "projection": "fundamental"}
        resp: requests.Response = self._get_with_retry(Urls.search, params=params)
        output = resp.json()
        return Fundamental(output[symbol]["fundamental"])

    def get_history(
        self,
        symbol: str,
        start_dt: datetime = None,
        end_dt: datetime = None,
        outside_rth: bool = False,
    ) -> List[Dict[str, float]]:
        if end_dt < start_dt:
            raise InvalidArgument("Start Date should be before End Date")

        params = {
            "periodType": "year",
            "frequencyType": "daily",
            "frequency": 1,
            "needExtendedHoursData": outside_rth,
            "startDate": int(start_dt.timestamp()) * 1000,
            "endDate": int(end_dt.timestamp()) * 1000,
        }
        resp: requests.Response = self._get_with_retry(
            Urls.history % symbol, params=params
        )
        output = resp.json()
        # TODO Check for the empty case. Wasn't able to simulate it
        return output["candles"]

    def get_history_df(
        self,
        symbol: str,
        start_dt: datetime = None,
        end_dt: datetime = None,
        outside_rth: bool = False,
    ):
        import pandas as pd

        output = self.get_history(
            symbol, start_dt=start_dt, end_dt=end_dt, outside_rth=outside_rth
        )
        df = pd.DataFrame(output)
        df["datetime"] = pd.to_datetime(df["datetime"], unit="ms").dt.date
        df.set_index("datetime", inplace=True)
        return df

    def get_intraday_history(
        self,
        symbol: str,
        start_dt: datetime = None,
        end_dt: datetime = None,
        frequency: int = 1,
        outside_rth: bool = False,
    ):
        if end_dt < start_dt:
            raise InvalidArgument("Start Date should be before End Date")
        if frequency not in [1, 5, 10, 15, 30]:
            raise InvalidArgument("Frequency not supported. [1, 5, 10, 15, 30]")

        params = {
            "periodType": "day",
            "frequencyType": "minute",
            "frequency": frequency,
            "needExtendedHoursData": outside_rth,
            "startDate": int(start_dt.timestamp()) * 1000,
            "endDate": int(end_dt.timestamp()) * 1000,
        }
        resp: requests.Response = self._get_with_retry(
            Urls.history % symbol, params=params
        )
        output = resp.json()
        # TODO Check for the empty case. Wasn't able to simulate it
        return output["candles"]

    def get_intraday_history_df(
        self,
        symbol: str,
        start_dt: datetime = None,
        end_dt: datetime = None,
        frequency: int = 1,
        outside_rth: bool = False,
    ):
        import pandas as pd

        output = self.get_intraday_history(
            symbol,
            start_dt=start_dt,
            end_dt=end_dt,
            frequency=frequency,
            outside_rth=outside_rth,
        )
        df = pd.DataFrame(output)
        df["datetime"] = pd.to_datetime(df["datetime"], unit="ms")
        df.set_index("datetime", inplace=True)
        return df
