import json
import warnings
import sys
from main_graph import app

# Suppress some pydantic V2 warnings for cleaner output
warnings.filterwarnings("ignore")

def main():
    print("====================================")
    print("🍽️ Yemek Analizi Ajanı Başlatılıyor")
    print("====================================")
    
    if len(sys.argv) > 1:
        sample_image_url = sys.argv[1]
    else:
        print("Lutfen bir resim yolu girin. Ornek kullanim: python test_run.py yemek.jpg")
        sys.exit(1)
    
    print(f"\nİncelenen Görsel (URL veya Path): {sample_image_url}\n")
    
    initial_state = {
        "image_source": sample_image_url
    }
    
    # Graph'ı çağır
    result_state = app.invoke(initial_state)
    
    print("\n====================================")
    print("🎯 NİHAİ ANALİZ SONUÇLARI")
    print("====================================")
    
    # Diyetisyenin hesapladığı nihai değerleri al
    analysis = result_state.get("food_analysis")
    
    if analysis:
        # Pydantic objesini sözlüğe çevirip ekrana yazdırıyoruz
        if hasattr(analysis, "model_dump"):
            output_dict = analysis.model_dump()
        else:
            output_dict = analysis.dict()
            
        print(json.dumps(output_dict, indent=4, ensure_ascii=False))
    else:
        print("Hata: Analiz verisi alınamadı.")

if __name__ == "__main__":
    main()
