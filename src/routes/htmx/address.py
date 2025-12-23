import logging

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from geopy.geocoders import Nominatim

from deps.geocoder import get_geocoder

logger = logging.getLogger("app.hmtx.address")
logger.level = logging.DEBUG


router = APIRouter(prefix="/address")


@router.get("/search")
async def search(
    request: Request,
    q: str = Query(..., min_length=3),
    geocoder: Nominatim = Depends(get_geocoder),
):
    # param str featuretype: If present, restrict results to certain type of features.
    # Allowed values: country, state, city, settlement.
    try:
        locations = await geocoder.geocode(
            q,
            limit=5,
            addressdetails=True,
            timeout=10,
            country_codes="br",
            language="pt-BR",
            # geometry="geojson",
        )

        if not locations:
            return HTMLResponse('<li class="p-2 text-gray-500">Nenhum resultado.</li>')

        if not isinstance(locations, list):
            locations = [locations]

        html_output = ""
        for loc in locations:
            logger.debug(loc.raw)

            lat = loc.latitude
            lng = loc.longitude

            f_name = loc
            html_output += f"""
            <li class="p-2 hover:bg-indigo-100 cursor-pointer border-b border-gray-100 text-sm"
                @click="selectAddress({{lat: {lat}, lng: {lng}, address: '{f_name}'}})">
                <div class="font-medium text-gray-800">{f_name}</div>
            </li>
            """
        return HTMLResponse(content=html_output)
    except Exception as e:
        return HTMLResponse(f'<li class="p-2 text-red-500">Erro: {str(e)}</li>')
