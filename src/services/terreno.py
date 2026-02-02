from core.service import AbstractModelService
from models.terreno import Terreno
from schemas.terreno import TerrenoIn

class TerrenoService(AbstractModelService[Terreno])
    model = Terreno 
    
    async def create(self, data:TerrenoIn):
        ...