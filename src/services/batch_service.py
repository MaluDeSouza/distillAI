import asyncio
from typing import List
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.distiller_service import KnowledgeDistillerService

# Importe o seu modelo de banco de dados (ajuste o caminho de acordo com o seu projeto)
from src.models.agents import KnowledgeBaseModel 

class BatchIngestionService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.distiller = KnowledgeDistillerService()

    async def process_batch(self, agent_id: int, files: List[UploadFile]) -> dict:
        """
        Lê arquivos simultaneamente, extrai regras usando Gemini e salva no PostgreSQL.
        """
        # 1. Leitura assíncrona do conteúdo dos arquivos
        contents = []
        for file in files:
            content = await file.read()
            contents.append(content.decode("utf-8"))

        # 2. Enfileiramento das tarefas no Gemini (Processamento Concorrente)
        # O asyncio.gather vai rodar todas as extrações ao mesmo tempo
        tasks = [self.distiller.distill_logs(text) for text in contents]
        
        # return_exceptions=True evita que um arquivo com erro quebre todo o lote
        results = await asyncio.gather(*tasks, return_exceptions=True)

        sucessos = 0
        falhas = 0

        # 3. Persistência no Banco de Dados
        for result in results:
            if isinstance(result, Exception):
                falhas += 1
                continue
            
            # Supondo que 'result' seja o seu DistillerResponse (que contém uma lista de knowledge_bases)
            # Iteramos pelas regras extraídas para salvar atreladas ao agente
            for kb in result.knowledge_bases:
                nova_regra = KnowledgeBaseModel(
                    agent_id=agent_id,
                    categoria=kb.categoria,
                    regras_payload=kb.model_dump()["procedimentos"] # <--- AQUI ESTÁ A CORREÇÃO!
                )
                self.db.add(nova_regra)
                sucessos += 1

        # Comita a transação no banco de dados
        await self.db.commit()

        return {
            "arquivos_processados": len(files),
            "regras_salvas_com_sucesso": sucessos,
            "falhas_de_extracao": falhas
        }