from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from evaluation.inference_xgb_api import run_inference

app = FastAPI(
    title="Protein Quality Predictor API",
    description="Predicción de PTM e IPTM usando ESM-2 + ProteinMPNN",
    version="1.0.0"
)

# Definimos el esquema de entrada
class PredictionRequest(BaseModel):
    secuencia: str
    score_energetico: float

@app.get("/")
def read_root():
    return {"message": "API de Predicción de Proteínas Operativa"}

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        # Ejecutamos la lógica que acabas de probar en consola
        result = run_inference(request.secuencia, request.score_energetico)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Comando para ejecutar:
# uvicorn api_service:app --host 0.0.0.0 --port 8000