import base64
import os

def get_image_data(image_source: str) -> str:
    """
    Kullanicidan gelen gorsel kaynagini kontrol eder.
    Eger yerel bir dosya yolu ise, onu okur ve base64 string'e cevirir.
    Eger zaten bir base64 string veya url ise onu dondurur.
    Cogu vision modeli base64 url formatinda calistigi icin ona gore hazirlar.
    """
    if os.path.exists(image_source):
        with open(image_source, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # Basit formati dondur
            return f"data:image/jpeg;base64,{encoded_string}"
    
    # Eger data:image ile baslamiyorsa ama base64 ise formatlayabiliriz veya direk dondurebiliriz
    if not image_source.startswith("http") and not image_source.startswith("data:image"):
        # varsayilan olarak base64 string e default data:image/jpeg ekle
        return f"data:image/jpeg;base64,{image_source}"
        
    return image_source
