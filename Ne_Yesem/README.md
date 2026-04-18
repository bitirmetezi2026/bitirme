# Ne Yesem - Yemek Malzemesi Tanıma ve Tarif Önerme Servisi (Backend)

Bu proje, gönderilen yemek/buzdolabı/tezgah fotoğraflarını OpenAI'ın GPT-4o Vision modeli ve LangGraph tabanlı çoklu-ajan mimarisi kullanarak analiz eden ve Android/Client tarafına standart yapılandırılmış JSON dönen bir FastAPI projesidir.

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

Ajanlar her zaman tutarlı bir şekilde fotoğraftaki malzemeleri tespit edip, sağlıklı ve dengeli yemek tariflerini JSON formatında döner.

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
    ): Response<RecipeResponse>
}

// Resim gönderimi
val requestFile = imageFile.asRequestBody("image/*".toMediaTypeOrNull())
val body = MultipartBody.Part.createFormData("file", imageFile.name, requestFile)
```

### Yanıt (Response) Gövdesi (JSON):
Ajan başarılı olursa HTTP 200 döner ve format şöyledir:

```json
{
    "status": "success",
    "detected_ingredients": [
        "Domates",
        "Yeşil Biber",
        "Yumurta",
        "Peynir"
    ],
    "recommendations": {
        "recipes": [
            {
                "name": "Sağlıklı Menemen",
                "description": "Güne zinde başlamanızı sağlayacak yüksek proteinli, az yağlı klasik bir Türk kahvaltısı.",
                "ingredients": [
                    "2 adet Domates",
                    "1 adet Yeşil Biber",
                    "2 adet Yumurta",
                    "1 tatlı kaşığı zeytinyağı"
                ],
                "steps": [
                    "Biberleri ince ince doğrayın ve az zeytinyağında soteleyin.",
                    "Domatesleri rendeleyip tavaya ekleyin, suyunu çekene kadar pişirin.",
                    "Yumurtaları kırıp hafifçe karıştırın.",
                    "Üzerine çok az tuz veya baharat ekleyip sıcak servis edin."
                ],
                "calories": "Yaklaşık 180 kcal"
            }
        ]
    }
}
```

### Kotlin Data Class (Moshi/Gson vb. İçin):
```kotlin
data class RecipeResponse(
    val status: String,
    val detected_ingredients: List<String>,
    val recommendations: Recommendations
)

data class Recommendations(
    val recipes: List<Recipe>
)

data class Recipe(
    val name: String,
    val description: String,
    val ingredients: List<String>,
    val steps: List<String>,
    val calories: String
)
```

> **Not:** Emülatör kullanıyorsanız geliştirme yaparken bilgisayarın localhost'una Android cihazından erişebilmek için IP adresini `10.0.2.2:8000` olarak ayarlamayı unutmayın!
