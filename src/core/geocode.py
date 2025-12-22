from typing import Optional

from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim

_geocoder: Optional[Nominatim] = None


def get_geocoder() -> Nominatim:
    global _geocoder
    if _geocoder is None:
        _geocoder = Nominatim(user_agent="scctorres_v1", adapter_factory=AioHTTPAdapter)
    return _geocoder


async def stop_geocoder():
    global _geocoder
    if _geocoder is not None:
        await _geocoder.adapter.close()  # pyright: ignore[reportAttributeAccessIssue]
        _geocoder = None
