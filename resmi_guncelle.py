import requests

# Canlı sunucu adresiniz:
BASE_URL = "https://bitirme-g5gn.onrender.com"
# Eğer lokalde denemek isterseniz:
# BASE_URL = "http://127.0.0.1:8000"

def get_all_recipes():
    print("Mevcut Tarifler Getiriliyor...")
    try:
        response = requests.get(f"{BASE_URL}/recipes/")
        if response.status_code == 200:
            recipes = response.json()
            for r in recipes:
                print(f"ID: {r['id']} | İsim: {r['name']} | Mevcut Resim: {r.get('image_url') or 'Yok (Yerel resim kullanılıyor)'}")
        else:
            print("Tarifler getirilirken hata oluştu!")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")

def update_recipe_image():
    recipe_id = input("\nResmini değiştirmek istediğiniz tarifin ID'sini girin: ")
    if not recipe_id.isdigit():
        print("Geçersiz ID.")
        return
    
    new_url = input("Yeni resmin URL'sini yapıştırın (Örn: https://yemek.com/...jpg)\n(Yerel resme dönmek için boş bırakıp Enter'a basın): ")
    
    payload = {"image_url": new_url.strip() if new_url.strip() else ""}
    
    try:
        response = requests.put(f"{BASE_URL}/recipes/{recipe_id}/image", json=payload)
        if response.status_code == 200:
            print("\n[BAŞARILI] " + response.json()["message"])
        else:
            print("\n[HATA] Bir sorun oluştu:", response.text)
    except Exception as e:
        print(f"\n[HATA] Bağlantı kurulamadı: {e}")

if __name__ == "__main__":
    print("--- TARİF RESMİ GÜNCELLEME ARACI ---")
    print("Not: Bu araç sayesinde herhangi bir tarifin resmini istediğiniz bir internet adresiyle değiştirebilirsiniz.")
    print("Eğer URL'yi boş gönderirseniz, uygulama içindeki otomatik resimler devreye girer.\n")
    
    get_all_recipes()
    update_recipe_image()
