# Yemek Analizi Yapay Zeka Servisi (Backend)

Bu proje, gönderilen yemek fotoğraflarını OpenAI'ın GPT-4o Vision modeli ve LangGraph tabanlı çoklu-ajan mimarisi kullanarak analiz eden ve Android/Client tarafına standart yapılandırılmış JSON dönen bir FastAPI projesidir.

## 1. Projeyi Çalıştırma (Backend Geliştiricisi / Sunucu İçin)

Projenin içinde bulunduğu klasöre gidin ve aşağıdaki adımları sırasıyla terminal (CMD/Powershell) üzerinden çalıştırın:

1. Gerekli kütüphaneleri kurun:
   ```bash
   pip install -r requirements.txt
   ```
2. `.env` dosyasının içerisinde geçerli bir `OPENAI_API_KEY` ve `LANGCHAIN_API_KEY` olduğundan emin olun.
3. FastAPI sunucusunu ayağa kaldırın:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   ```

Sunucu çalıştığında `http://0.0.0.0:8000` üzerinden veya bilgisayarınızın yerel IP adresi üzerinden yayın yapmaya başlayacaktır.

---

## 2. API Kullanım Rehberi (Android Geliştiricisi İçin)

Ajanlar her zaman tutarlı bir şekilde yemeğin porsiyon, kalori ve makro (Protein, Karbonhidrat, Yağ) değerlerini JSON formatında döner.

### Endpoint:
**URL:** `POST /analyze` (Örn: `http://192.168.1.x:8000/analyze`)
**Header:** `Content-Type: multipart/form-data`

### İstek (Request) Gövdesi:
Sadece `file` adında, `image/jpeg` veya `image/png` türünde Multipart dosya gönderilmelidir. Retrofit ile Kotlin örneği aşağıdadır:

```kotlin
interface FoodApi {
    @Multipart
    @POST("/analyze")
    suspend fun analyzeFood(
        @Part file: MultipartBody.Part
    ): Response<FoodAnalysisResponse>
}

// Resim gönderimi
val requestFile = imageFile.asRequestBody("image/*".toMediaTypeOrNull())
val body = MultipartBody.Part.createFormData("file", imageFile.name, requestFile)
```

### Yanıt (Response) Gövdesi (JSON):
Ajan başarılı olursa HTTP 200 döner ve format şöyledir:

```json
{
    "food_name": "Cheeseburger",
    "portion": "1 büyük hamburger",
    "calories": 850.0,
    "macros": {
        "protein": 45.0,
        "carbs": 60.0,
        "fat": 50.0
    }
}
```

### Kotlin Data Class (Moshi/Gson vb. İçin):
```kotlin
data class FoodAnalysisResponse(
    val food_name: String,
    val portion: String,
    val calories: Double,
    val macros: Macros
)

data class Macros(
    val protein: Double,
    val carbs: Double,
    val fat: Double
)
```

> **Not:** Emülatör kullanıyorsanız geliştirme yaparken bilgisayarın localhost'una Android cihazından erişebilmek için IP adresini `10.0.2.2:8000` olarak ayarlamayı unutmayın!
