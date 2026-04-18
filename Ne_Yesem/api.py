from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging

from agent import process_fridge_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ne Yesem AI - Diyetisyen ve Şef Ajanı",
    description="Fotoğraf tabanlı malzeme algılama ve tarif önerme sistemi.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Ne Yesem AI API'sine hoş geldiniz! /docs adresinden API dökümantasyonunu inceleyebilirsiniz."}

@app.post("/analyze")
async def analyze_food(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Sadece resim formatında dosya yükleyebilirsiniz.")
    
    try:
        contents = await file.read()
        logger.info(f"Received image: {file.filename}")
        
        # Süreci LangGraph ajanına gönderiyoruz
        result_state = process_fridge_image(contents)
        
        return JSONResponse(content={
            "status": "success",
            "detected_ingredients": result_state.get("ingredients", []),
            "recommendations": result_state.get("recipes", {})
        })
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
