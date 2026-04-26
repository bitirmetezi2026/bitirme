import requests
import time

# Kullanıcının Render sunucu adresi
BASE_URL = "https://bitirme-g5gn.onrender.com"

# Profesyonel ve geniş kapsamlı Türk mutfağı sağlıklı diyet tarifleri
RECIPES = [
    {
        "name": "Fırınlanmış Zeytinyağlı Enginar",
        "calories": "180 kcal | Protein: 4g | Yağ: 10g | Karb: 15g",
        "description": "Karaciğer dostu, hafif ve besleyici bir bahar lezzeti.",
        "ingredients": "Enginar, Zeytinyağı, Dereotu, Limon, Havuç",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2014/12/zeytinyagli-enginar-yemekcom.jpg"
    },
    {
        "name": "Mercimek Köftesi",
        "calories": "220 kcal | Protein: 12g | Yağ: 5g | Karb: 30g",
        "description": "Bitkisel protein kaynağı, doyurucu ve klasik bir lezzet.",
        "ingredients": "Kırmızı Mercimek, İnce Bulgur, Salça, Taze Soğan",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2014/05/mercimek-koftesi-yemekcom.jpg"
    },
    {
        "name": "Izgara Levrek ve Kuşkonmaz",
        "calories": "320 kcal | Protein: 35g | Yağ: 15g | Karb: 8g",
        "description": "Yüksek omega-3 ve düşük kalorili lüks bir akşam yemeği.",
        "ingredients": "Levrek, Kuşkonmaz, Limon, Karabiber, Zeytinyağı",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2016/09/firin-levrek-tarifi.jpg"
    },
    {
        "name": "Avokadolu Poşe Yumurta",
        "calories": "250 kcal | Protein: 14g | Yağ: 18g | Karb: 10g",
        "description": "Sağlıklı yağlarla dolu, şampiyonların kahvaltısı.",
        "ingredients": "Avokado, Yumurta, Tam Buğday Ekmeği, Pul Biber",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2020/09/avokadolu-yumurta-yemekcom.jpg"
    },
    {
        "name": "Fırında Sebzeli Tavuk Göğsü",
        "calories": "290 kcal | Protein: 35g | Yağ: 8g | Karb: 15g",
        "description": "Spor sonrası kas onarımı için mükemmel ana öğün.",
        "ingredients": "Tavuk Göğsü, Kabak, Biber, Domates, Kekik",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2021/04/sebzeli-tavuk-sote-yemekcom.jpg"
    },
    {
        "name": "Glutensiz Karabuğday Salatası",
        "calories": "210 kcal | Protein: 8g | Yağ: 6g | Karb: 30g",
        "description": "Lif zengini ve tok tutan ferahlatıcı bir salata.",
        "ingredients": "Karabuğday (Greçka), Nar, Maydanoz, Ceviz",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2017/02/karabugday-salatasi-tarifi.jpg"
    },
    {
        "name": "Yoğurtlu Semizotu",
        "calories": "110 kcal | Protein: 6g | Yağ: 5g | Karb: 8g",
        "description": "Demir ve kalsiyum deposu serinletici bir meze.",
        "ingredients": "Semizotu, Süzme Yoğurt, Sarımsak, Zeytinyağı",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2015/06/yogurtlu-semizotu-salatasi-yemekcom.jpg"
    },
    {
        "name": "Chia Tohumlu Puding",
        "calories": "190 kcal | Protein: 7g | Yağ: 9g | Karb: 18g",
        "description": "Şeker ilavesiz tatlı krizlerini kesen pratik tatlı.",
        "ingredients": "Chia Tohumu, Badem Sütü, Yaban Mersini, Bal",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2018/11/kakaolu-chia-puding-yemekcom.jpg"
    },
    {
        "name": "Fırın Mücver",
        "calories": "160 kcal | Protein: 6g | Yağ: 7g | Karb: 15g",
        "description": "Kızartma sevmeyenlere hafif ve diyet mücver.",
        "ingredients": "Kabak, Yumurta, Yulaf Unu, Dereotu, Beyaz Peynir",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2015/05/firin-mucver-tarifi.jpg"
    },
    {
        "name": "Zeytinyağlı Taze Fasulye",
        "calories": "130 kcal | Protein: 4g | Yağ: 6g | Karb: 12g",
        "description": "Yaz aylarının vazgeçilmezi klasik anne yemeği.",
        "ingredients": "Taze Fasulye, Domates, Soğan, Zeytinyağı",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2014/05/zeytinyagli-taze-fasulye-yemekcom.jpg"
    }
]

def add_recipes_to_db():
    print(f"Toplam {len(RECIPES)} adet profesyonel tarif veritabanına ekleniyor...")
    
    success_count = 0
    for recipe in RECIPES:
        try:
            response = requests.post(f"{BASE_URL}/recipes/add", json=recipe)
            if response.status_code == 200:
                print(f"✅ Eklendi: {recipe['name']}")
                success_count += 1
            else:
                print(f"❌ Hata ({recipe['name']}): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Bağlantı hatası: {e}")
        time.sleep(0.5)  # Sunucuyu yormamak için kısa bir bekleme
        
    print(f"\nİşlem tamamlandı! {success_count}/{len(RECIPES)} tarif başarıyla canlı veritabanına aktarıldı.")

if __name__ == "__main__":
    add_recipes_to_db()
