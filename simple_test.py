from Ne_Yesem.agent import process_fridge_image
import json

def run_test():
    try:
        with open("Ne_Yesem/test_fridge.jpg", "rb") as f:
            image_bytes = f.read()

        print("Fotoğraf agent'a gönderiliyor... Lütfen bekleyin.")
        result = process_fridge_image(image_bytes)
        
        # Ekranda çok yer kaplamasın diye base64 verisini gizle
        if "image_base64" in result:
            result["image_base64"] = "<resim verisi gizlendi>"

        print("\n--- SONUÇ ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    run_test()
