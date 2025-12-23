from fastapi import Request
from geopy.geocoders import Nominatim


async def get_geocoder(request: Request) -> Nominatim:
    return request.app.state.geocoder
