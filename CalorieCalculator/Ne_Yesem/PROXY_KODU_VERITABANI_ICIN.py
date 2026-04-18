from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import httpx # Terminalde `pip install httpx` komutu ile kurulmalıdır.

# ---------------------------------------------------------
# AŞAĞIDAKİ BLOK VERİTABANI MAIN.PY DOSYASINA EKLENMELİDİR
# ---------------------------------------------------------

# MEHMET'IN BİLGİSAYARININ IP ADRESİ VE DOĞRU ENDPOINT BURADA OLMALI
MEHMET_AI_SERVER_URL = "http://192.168.1.11:8000/analyze" 

@app.post("/recommend-recipes")
async def forward_to_ai_agent(file: UploadFile = File(...)):
    """
    Mehmet'in AI sunucusuna fotoğrafı ileten Proxy/Köprü fonksiyonu.
    """
    print(f"DEBUG: {file.filename} için tarif isteği alındı. Mehmet'e iletiliyor...")
    
    try:
        # Gelen fotoğrafın içeriğini RAM'e oku
        file_bytes = await file.read()
        
        # Dosya boşsa hata ver
        if not file_bytes:
            print("ERROR: Alınan dosya içeriği boş!")
            raise HTTPException(status_code=400, detail="Dosya içeriği boş.")

        # Mehmet'in yapay zeka sunucusuna asenkron istek atıyoruz
        async with httpx.AsyncClient(timeout=90.0) as client:
            # Multipart form datayı paketliyoruz
            # Content-type yoksa image/jpeg varsayıyoruz
            content_type = file.content_type or "image/jpeg"
            files = {"file": (file.filename, file_bytes, content_type)}
            
            print(f"DEBUG: Mehmet'e ({MEHMET_AI_SERVER_URL}) istek atılıyor...")
            response = await client.post(MEHMET_AI_SERVER_URL, files=files)
            
            print(f"DEBUG: Mehmet'ten cevap geldi. Status: {response.status_code}")
            
            if response.status_code == 200:
                json_data = response.json()
                print(f"DEBUG: Başarılı! Tespit edilen malzeme sayısı: {len(json_data.get('detected_ingredients', []))}")
                return JSONResponse(content=json_data)
            else:
                error_detail = response.text
                print(f"ERROR: Mehmet AI Hatası. Detay: {error_detail}")
                raise HTTPException(status_code=response.status_code, detail=f"Mehmet AI Hatası: {error_detail}")
                
    except httpx.ConnectError:
        print("ERROR: Mehmet'in sunucusuna (192.168.1.11) bağlanılamadı!")
        raise HTTPException(status_code=503, detail="Mehmet'in sunucusuna bağlanılamadı. IP yanlış veya sunucu kapalı.")
    except Exception as e:
        print(f"ERROR: Beklenmedik hata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
