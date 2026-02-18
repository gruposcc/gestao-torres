from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.schema import ModelSchema
from core.service import AbstractModelService
from models.base import ObjectStatus
from models.torre import Torre, DocumentoTorre, DespesaTorre
from schemas.torre import TorreIn
import shutil
from typing import List
import os
from pathlib import Path
from fastapi import UploadFile
from core.settings import UPLOADS_DIR

# from core.utils.files import truncate_filename
from pathlib import Path
import uuid
from core.settings import UPLOADS_DIR


class TorreService(AbstractModelService[Torre]):
    model = Torre

    """ async def get_list(
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
     """

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
        self,
        torre: Torre,
        arquivos: list[UploadFile],
        nicknames: list[str] | None = None,
    ):
        documentos_criados = []

        uploads_dir = Path(UPLOADS_DIR / "torres" / str(torre.id))
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # for arquivo, nickname in zip(arquivos, nicknames):

        for arquivo in arquivos:
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

                first_nickname = arquivo.filename.split(".")[0]
                file_ext = arquivo.filename.split(".")[1]

                # CRIA O OBJETO NO BANCO
                novo_doc = DocumentoTorre(
                    id=file_id,
                    filename=arquivo.filename[:255],
                    # nickname=nickname[:100]
                    nickname=first_nickname,
                    path=str(f"torres/{torre.id}"),
                    content_type=arquivo.content_type or None,
                    torre_id=torre.id,
                    # size
                    # extension
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
            await self.dbSession.flush()
            await self.dbSession.refresh(torre, ["documentos"])

        return torre

    async def soft_delete(self, obj: Torre) -> bool:
        # Carrega os documentos se ainda não estiverem na memória
        # para garantir que o status deles também mude
        for doc in obj.documentos:
            doc.status = ObjectStatus.DELETED

        # Chama o comportamento padrão do pai (commit e logs)
        return await super().soft_delete(obj)


class DocumentoTorreService(AbstractModelService[DocumentoTorre]):
    model = DocumentoTorre

    async def hard_delete(self, doc: DocumentoTorre):
        # remover arquivo

        folder_path = Path(UPLOADS_DIR / doc.path)
        self.logger.debug(folder_path)
        if folder_path.exists() and folder_path.is_dir():
            for file in folder_path.iterdir():
                if file.is_file():
                    prefix = file.name.split(".")[0]
                    self.logger.error(f"{file} || {prefix}")
                    if prefix == str(doc.id):
                        os.remove(file)

        await super().hard_delete(doc)

    async def update_nickname(self, doc_id: uuid.UUID, nickname: str):
        # Usando o get_one_by do seu AbstractModelService
        doc = await self.get_one_by(id=doc_id)
        if not doc:
            return None

        doc.nickname = nickname
        return await self.save(doc)

    async def get_all_from_torre(self, torre_id, only_enabled: bool = True):
        stmt = select(self.model).where(self.model.torre_id == torre_id)

        if only_enabled:
            stmt = stmt.where(self.model.status == ObjectStatus.ENABLE)

        # Ordenada pelo mais recente
        # stmt = stmt.order_by(self.model.created_at.desc())

        result = await self.dbSession.execute(stmt)
        return list[DocumentoTorre](result.scalars().all())


class DespesaTorreSerivce(AbstractModelService[DespesaTorre]):
    model = DespesaTorre

    async def get_all_from_torre(self, torre_id):
        stmt = select(self.model).where(self.model.torre_id == torre_id)

        """ if only_enabled:
            stmt = stmt.where(self.model.status == ObjectStatus.ENABLE) """

        # Ordenada pelo mais recente
        # stmt = stmt.order_by(self.model.created_at.desc())

        result = await self.dbSession.execute(stmt)
        return list[DespesaTorre](result.scalars().all())
