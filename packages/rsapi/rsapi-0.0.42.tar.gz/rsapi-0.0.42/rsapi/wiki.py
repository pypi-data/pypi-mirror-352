import re
import time
import typing
import functools

import requests
import typing_extensions

from rsapi import USER_AGENT

API_URL = "https://prices.runescape.wiki"
MAPPING_PATH = "api/v1/osrs/mapping"
LATEST_PATH = "api/v1/osrs/latest"
TIMESERIES_PATH = "api/v1/osrs/timeseries"


class Item(typing.TypedDict, total=False):
    examine: str
    id: int
    members: bool
    value: int
    icon: str
    name: str
    lowalch: typing.Optional[int]
    highalch: typing.Optional[int]
    limit: typing.Optional[int]


class PriceLatest(typing.TypedDict, total=False):
    id: int
    high: int
    highTime: int
    low: int
    lowTime: int


class PriceTimeSeries(typing.TypedDict, total=False):
    timestamp: int
    avgHighPrice: int
    avgLowPrice: int
    highPriceVolume: int
    lowPriceVolume: int


def _get_ttl_hash(seconds=300):
    """Return the same value withing `seconds` time period"""
    return time.time() // seconds


@functools.lru_cache(maxsize=10)
def __request(path: str, ttl_hash=None, **params) -> dict:
    resp = requests.get(
        f"{API_URL}/{path}",
        params=params,
        headers={
            "User-Agent": USER_AGENT,
        }
    )
    resp.raise_for_status()
    return resp.json()


def _request(path: str, **params) -> dict:
    return __request(path, ttl_hash=_get_ttl_hash(), **params)


def items(
    exact: bool = False,
    **filters: typing_extensions.Unpack[Item]
) -> typing.Iterable[Item]:
    for item in _request(MAPPING_PATH):
        if not filters:
            yield item
        for key, value in filters.items():
            if key not in item:
                continue
            if isinstance(value, int):
                if item[key] == value:
                    yield item
            elif isinstance(value, str):
                if str(item[key]).lower() == value.lower():
                    yield item
                elif (
                    not exact
                    and re.search(value, str(item[key]), flags=re.IGNORECASE)
                ):
                    yield item
            else:
                raise TypeError("Bad argument type")


def price_latest(
    exact: bool = False,
    **filters: typing_extensions.Unpack[Item]
) -> typing.Iterable[PriceLatest]:
    _items = list(items(exact=exact, **filters))
    _prices = _request(LATEST_PATH)["data"]

    for item in _items:
        id_ = item["id"]
        price = _prices.get(str(id_))
        if price is None:
            continue

        yield PriceLatest({
            "id": id_,
            **price,
        })


def price_timeseries(
    timestep: str = "24h",
    exact: bool = False,
    **filters: typing_extensions.Unpack[Item]
) -> typing.Iterable[PriceTimeSeries]:
    _items = list(items(exact=exact, **filters))
    if len(_items) > 1:
        raise Exception(f"too many matches ({len(_items)}) on timeseries")

    item = _items[0]
    prices = _request(
        TIMESERIES_PATH, timestep=timestep, id=item["id"])["data"]

    for price in prices:
        yield PriceTimeSeries({
            **price,
        })
