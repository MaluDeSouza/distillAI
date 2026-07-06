import asyncio
from typing import Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from src.services.distiller_service import KnowledgeDistillerService
from src.services.pdf_service import PdfExportService
from src.schemas.distiller import DistillerResponse

router = APIRouter(prefix="/v1/distill", tags=["Engine Destiladora"])

class SwaggerUploadFile(UploadFile):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any) -> dict[str, Any]:
        return {"type": "string", "format": "binary"}

@router.post("", response_model=DistillerResponse)
async def distill_logs_endpoint(file: UploadFile = File(...)):
    """
    Recebe um arquivo de texto com logs brutos de atendimento e 
    retorna as regras de negócio destiladas em JSON.
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .txt são permitidos no formato bruto.")
    
    # Lendo o arquivo assincronamente direto da memória
    content = await file.read()
    raw_logs = content.decode("utf-8")
    
    service = KnowledgeDistillerService()
    result = await service.distill_logs(raw_logs)
    
    return result

@router.post("/export-pdf", response_class=StreamingResponse)
async def export_distilled_pdf(
    files: List[SwaggerUploadFile] = File(..., description="Envie até 50 arquivos .txt para consolidar em um PDF")
):
    """
    Recebe múltiplos logs brutos, processa a destilação estruturada via LLM 
    de forma assíncrona e devolve um único documento tipografado.
    """
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="O limite máximo é de 50 arquivos por vez.")
    
    contents = []
    for file in files:
        if not file.filename.endswith(".txt"):
            raise HTTPException(status_code=400, detail=f"O arquivo {file.filename} é inválido. Envie apenas .txt")
        
        content = await file.read()
        contents.append(content.decode("utf-8"))
    
    distiller = KnowledgeDistillerService()
    
    # 1. Dispara a extração de todos os arquivos simultaneamente
    tasks = [distiller.distill_logs(text) for text in contents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 2. Consolida todas as extrações em uma única lista
    bases_consolidadas = []
    for result in results:
        if isinstance(result, Exception):
            # Se um arquivo falhar, ignoramos ele para não quebrar o PDF inteiro
            print(f"Aviso: Falha ao destilar um dos arquivos. Erro: {result}")
            continue
        
        # Anexa as regras destiladas deste arquivo na lista mestre
        bases_consolidadas.extend(result.knowledge_bases)
        
    if not bases_consolidadas:
         raise HTTPException(status_code=422, detail="Nenhuma regra válida foi extraída dos arquivos enviados.")
        
    # 3. Monta o objeto raiz consolidado
    dados_finais = DistillerResponse(knowledge_bases=bases_consolidadas)
    
    # 4. Renderiza o documento único
    pdf_renderer = PdfExportService()
    pdf_stream = pdf_renderer.generate_pdf(dados_finais)
    
    headers = {
        "Content-Disposition": f"attachment; filename=distillai_manual_consolidado.pdf"
    }
    
    return StreamingResponse(
        pdf_stream, 
        media_type="application/pdf", 
        headers=headers
    )