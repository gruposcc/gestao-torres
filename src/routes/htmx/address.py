import logging

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from geopy.geocoders import Nominatim

from core.templates import TResponse
from deps.geocoder import get_geocoder

logger = logging.getLogger("app.hmtx.address")

router = APIRouter(prefix="/address")


@router.get("/search")
async def search(
    request: Request,
    address_query: str = Query(..., min_length=3),
    geocoder: Nominatim = Depends(get_geocoder),
):
    template = "pages/terreno/search_results.html"
    # param str featuretype: If present, restrict results to certain type of features.
    # Allowed values: country, state, city, settlement.

    try:
        locations = await geocoder.geocode(  # pyright: ignore[reportGeneralTypeIssues]
            address_query,
            limit=5,
            addressdetails=True,
            timeout=10,  # pyright: ignore[reportArgumentType]
            country_codes="br",
            language="pt-BR",  # pyright: ignore[reportArgumentType]
            exactly_one=False,
            # geometry="geojson",
        )

        logger.debug(f"Search Location results: {locations}")

        if not locations:
            return HTMLResponse('<li class="p-2 text-gray-500">Nenhum resultado.</li>')

        if not isinstance(locations, list):
            locations = [locations]

        context = {"request": request, "results": locations}

        logger.debug(f"returning locations {locations}")
        return TResponse(template, context)

        ##TODO Formatar resposta estadoUF/ cidade /endereço

    except Exception as e:
        return HTMLResponse(f'<li class="p-2 text-red-500">Erro: {str(e)}</li>')
