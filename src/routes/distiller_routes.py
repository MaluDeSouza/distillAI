from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.distiller_service import KnowledgeDistillerService
from src.schemas.distiller import DistillerResponse

router = APIRouter(prefix="/v1/distill", tags=["Engine Destiladora"])

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