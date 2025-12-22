import logging

from fastapi import APIRouter, Depends, Query, Request
from geopy.geocoders import Nominatim

from core.geocode import get_geocoder
from core.settings import TEMPLATES
from deps.db import get_db
from schemas.auth import UserAuthForm
from services.auth import AuthService

logger = logging.getLogger("app.hmtx.address")
logger.level = logging.DEBUG


router = APIRouter(prefix="/address")


from fastapi.responses import HTMLResponse


@router.get("/search")
async def search(
    request: Request,
    q: str = Query(..., min_length=3),
    geocoder: Nominatim = Depends(get_geocoder),
):
    try:
        locations = await geocoder.geocode(q, limit=5, addressdetails=True, timeout=10)

        if not locations:
            return HTMLResponse('<li class="p-2 text-gray-500">Nenhum resultado.</li>')

        if not isinstance(locations, list):
            locations = [locations]

        html_output = ""
        for loc in locations:
            # Escapamos o endereço para não quebrar o JS

            logger.debug(loc.raw)

            if hasattr(loc, "address"):
                display_name = loc.address.replace("'", "\\'")
                lat = loc.latitude
                lng = loc.longitude

                html_output += f"""
                <li class="p-2 hover:bg-indigo-100 cursor-pointer border-b border-gray-100 text-sm"
                    @click="selectAddress({{lat: {lat}, lng: {lng}, address: '{display_name}'}})">
                    <div class="font-medium text-gray-800">{display_name}</div>
                </li>
                """
        return HTMLResponse(content=html_output)
    except Exception as e:
        return HTMLResponse(f'<li class="p-2 text-red-500">Erro: {str(e)}</li>')
