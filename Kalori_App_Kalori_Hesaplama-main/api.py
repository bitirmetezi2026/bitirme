from fastapi import FastAPI, UploadFile, File, HTTPException
import base64
from main_graph import app as agent_app
import warnings

# Pydantic uyarilarini gizle
warnings.filterwarnings("ignore")

app = FastAPI(title="Yemek Analizi AI Servisi")

@app.get("/")
def home():
    return {"message": "Yemek Analizi API Calisiyor. POST /analyze adresine resim gonderebilirsiniz."}

@app.post("/analyze")
async def analyze_food(file: UploadFile = File(...)):
    """
    Android'den veya baska bir servisten multipart/form-data yontemiyle gelen 'file' yuklemesini isler.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Lutfen sadece resim (image) dosyasi yukleyin.")
        
    try:
        # Resmi byte olarak oku
        contents = await file.read()
        
        # Base64 formata cevir
        base64_string = base64.b64encode(contents).decode('utf-8')
        
        # main_graph icindeki format beklentisini saglamak adina formati birlestir
        image_data = f"data:{file.content_type};base64,{base64_string}"
        
        initial_state = {
            "image_source": image_data
        }
        
        # Yapay Zeka graph'ini baslat
        result_state = agent_app.invoke(initial_state)
        analysis = result_state.get("food_analysis")
        
        if analysis:
            # Pydantic model formatini json'a uyarla
            if hasattr(analysis, "model_dump"):
                return analysis.model_dump()
            else:
                return analysis.dict()
                
        return {"error": "Analiz tamamlanamadi. Lutfen tekrar deneyin."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatasi: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)