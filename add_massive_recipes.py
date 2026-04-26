import requests
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Ortam değişkenlerini yükle (OPENAI_API_KEY için)
load_dotenv()

# Render API Adresin
BASE_URL = "https://bitirme-g5gn.onrender.com"

# OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_recipes(count=5):
    print(f"🧠 Yapay Zeka (ChatGPT) {count} adet YEPYENİ diyet tarifi üretiyor... Lütfen bekleyin.")
    
    prompt = f"""
    Sen uzman bir diyetisyen ve şefsin. Bana daha önce vermediğin, birbirinden farklı ve yaratıcı tam {count} adet sağlıklı, yüksek proteinli veya düşük kalorili diyet yemeği tarifi üret.
    
    Cevabını sadece aşağıdaki JSON formatında ver, başka hiçbir metin ekleme:
    [
        {{
            "name": "Yemeğin Adı",
            "calories": "300 kcal | Protein: 30g | Yağ: 10g | Karb: 20g",
            "description": "Yemek hakkında 1-2 cümlelik çekici açıklama.",
            "ingredients": "Malzeme 1, Malzeme 2, Malzeme 3",
            "steps": "1. Adım... 2. Adım... 3. Adım...",
            "image_keyword": "salmon,food" (İngilizce 2 kelime)
        }}
    ]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            response_format={ "type": "json_object" }
        )
        
        # Eğer json_object formatı direk liste dönmüyorsa diye ufak bir düzeltme:
        # GPT-4o-mini json_object modunda genellikle {"recipes": [...]} döner.
    except Exception as e:
        print(f"OpenAI Hatası: {e}")
        return []

    # Parse response
    content = response.choices[0].message.content
    try:
        # Eğer liste değilse dict olabilir
        data = json.loads(content)
        if isinstance(data, dict):
            # Sözlük içindeki ilk listeyi bul
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return [data] # fallback
        return data
    except Exception as e:
        print(f"JSON Parse Hatası: {e}")
        return []

def add_recipes_to_db():
    # OpenAI'den yepyeni tarifleri al!
    new_recipes = generate_ai_recipes(count=5)
    
    if not new_recipes:
        print("❌ Tarif üretilemedi!")
        return

    print(f"✅ ChatGPT başarıyla {len(new_recipes)} yeni tarif üretti! Şimdi veritabanına ekleniyor...")
    
    success_count = 0
    for r in new_recipes:
        # Resim linki oluştur (LoremFlickr üzerinden rastgele ama konuya uygun resim)
        keyword = r.pop("image_keyword", "healthy,food")
        r["image_url"] = f"https://loremflickr.com/400/300/{keyword.replace(' ', ',')}"
        
        try:
            response = requests.post(f"{BASE_URL}/recipes/add", json=r)
            if response.status_code == 200:
                print(f"✅ Veritabanına Eklendi: {r.get('name')}")
                success_count += 1
            else:
                print(f"❌ Veritabanı Hatası ({r.get('name')}): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
        time.sleep(1)  # Sunucuyu yormamak için bekleme
        
    print(f"\nİşlem tamamlandı! {success_count}/{len(new_recipes)} yepyeni tarif canlı sistemde yayında!")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Lütfen .env dosyasına OPENAI_API_KEY ekleyin.")
    else:
        add_recipes_to_db()
