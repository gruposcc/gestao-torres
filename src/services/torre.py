from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.schema import ModelSchema
from core.service import AbstractModelService
from models.base import ObjectStatus
from models.torre import Torre, DocumentoTorre
from schemas.torre import TorreIn
import shutil
from typing import List
import os
from pathlib import Path
from fastapi import UploadFile
from core.settings import UPLOADS_DIR
from datetime import datetime
from core.utils.files import truncate_filename
from pathlib import Path
import uuid


class TorreService(AbstractModelService[Torre]):
    model = Torre

    async def get_list(
        self,
        out_schema: ModelSchema | None = None,
        only_enable=True,
        load_relations: list | None = None,
    ):
        stmt = select(self.model)

        if load_relations:
            for rel in load_relations:
                # VERIFICAR SE EXISTE A REFERENCIA
                # ex: Torre.terreno
                if hasattr(self.model, rel):
                    attr = getattr(self.model, rel)
                    stmt = stmt.options(selectinload(attr))

                else:
                    pass

        if only_enable:
            stmt = stmt.where(self.model.status == ObjectStatus.ENABLE)

        result = await self.dbSession.execute(stmt)

        items = result.scalars().all()

        # .unique() é recomendado ao usar joins ou selectinload para evitar duplicatas nos resultados
        # items = result.scalars().unique().all()

        if not out_schema:
            return items

        #
        # cogitar uso de type adapter
        else:
            parsed = [out_schema.model_validate(item) for item in items]
            return parsed

    async def search_by_name(self, name: str, limit: int = 3):
        # Se o nome estiver vazio, podemos retornar os mais recentes
        if not name or len(name.strip()) == 0:
            stmt = select(self.model).order_by(self.model.created_at.desc())
        else:
            # O .contains() gera automaticamente o '%termo%'
            stmt = select(self.model).filter(self.model.name.ilike(f"%{name}%"))

        stmt = stmt.filter(self.model.status == ObjectStatus.ENABLE).limit(limit)

        self.logger.debug(f"SEARCH BY: {stmt}")
        result = await self.dbSession.execute(stmt)
        return result.scalars().all()

    async def append_docs(
        self, torre: Torre, arquivos: list[UploadFile], nicknames: list[str]
    ) -> List[DocumentoTorre]:
        documentos_criados = []

        uploads_dir = Path(UPLOADS_DIR / "torres" / str(torre.id))
        uploads_dir.mkdir(parents=True, exist_ok=True)

        for arquivo, nickname in zip(arquivos, nicknames):
            if not arquivo.filename:
                continue

            file_id = uuid.uuid4()

            # Gerar um nome único para o arquivo no disco para evitar sobrescrita
            ext = os.path.splitext(arquivo.filename)[1]
            fs_name = f"{file_id}{ext}"
            file_path = Path(uploads_dir / fs_name)

            try:
                # SALVAR O ARQUIVO
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(arquivo.file, buffer)

                # CRIA O OBJETO NO BANCO
                novo_doc = DocumentoTorre(
                    id=file_id,
                    filename=arquivo.filename[:255],
                    nickname=nickname[:100],
                    path=str(f"torres/{torre.id})"),
                    content_type=arquivo.content_type or None,
                    torre_id=torre.id,
                )
                self.dbSession.add(novo_doc)

                documentos_criados.append(novo_doc)

            except Exception as e:
                if file_path.exists():
                    os.remove(file_path)

                self.logger.error(f"Erro salvando arquivo: {arquivo.filename}")
                self.logger.error(e)

                continue

        if documentos_criados:
            await self.dbSession.commit()

        return documentos_criados

    async def soft_delete(self, obj: Torre) -> bool:
        # Carrega os documentos se ainda não estiverem na memória
        # para garantir que o status deles também mude
        """for doc in obj.documentos:
        doc.status = ObjectStatus.DELETED"""

        # Chama o comportamento padrão do pai (commit e logs)
        return await super().soft_delete(obj)


class DocumentoTorreService(AbstractModelService[DocumentoTorre]):
    model = DocumentoTorre
