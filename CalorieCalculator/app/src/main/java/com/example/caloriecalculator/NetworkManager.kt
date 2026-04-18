package com.example.caloriecalculator

import okhttp3.MultipartBody
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

// --- DİLA'NIN GÖNDERDİĞİ ŞEMALAR ---
data class UserCreate(
    val email: String, 
    val password: String, 
    val full_name: String? = null,
    val boy_cm: Float? = null,
    val kilo_kg: Float? = null,
    val yas: Int? = null,
    val cinsiyet: String? = null,
    val activity_level: String? = null,
    val hedef: String? = null,
    val hedef_hiz: String? = null,
    val hedef_kilo: Float? = null
)
data class LoginItem(val email: String, val password: String)
data class UserResponse(val id: Int, val email: String, val full_name: String?)

data class LoginResponse(
    val access_token: String,
    val token_type: String,
    val user_id: Int,
    val full_name: String?
)

data class ChatRequest(
    val user_id: Int,
    val user_message: String,
    val history: String,
    val boy_cm: Float,
    val kilo_kg: Float,
    val yas: Int,
    val cinsiyet: String,
    val bugunku_ogunler: List<MealCreate>
)
data class ChatResponse(val reply: String)

data class MealCreate(
    val food_name: String,
    val calories: Float,
    val protein: Float? = 0f,
    val fat: Float? = 0f,
    val carbs: Float? = 0f
)

// Ayarlar Sayfası İçin Güncelleme Şeması
data class UserUpdate(
    val full_name: String? = null,
    val boy_cm: Float? = null,
    val kilo_kg: Float? = null,
    val yas: Int? = null,
    val cinsiyet: String? = null,
    val language: String? = null,
    val email: String? = null
)

data class WaterCreate(
    val amount_ml: Int
)

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

// --- API ARAYÜZÜ ---
interface DiyetApi {
    @POST("users/")
    suspend fun registerUser(@Body request: UserCreate): UserResponse

    @POST("auth/login")
    suspend fun loginUser(@Body request: LoginItem): LoginResponse

    @POST("users/update/") // Dila'ya bu adresi onaylat
    suspend fun updateUserInfo(
        @retrofit2.http.Header("Authorization") token: String,
        @Body request: UserUpdate
    ): UserResponse

    @Multipart
    @POST("analyze")
    suspend fun analyzeFood(
        @Part file: MultipartBody.Part
    ): FoodAnalysisResponse


    @POST("chat")
    suspend fun chatWithAi(
        @retrofit2.http.Header("Authorization") token: String,
        @Body request: ChatRequest
    ): ChatResponse

    @POST("meals/")
    suspend fun saveMeal(
        @retrofit2.http.Header("Authorization") token: String,
        @Body request: MealCreate
    ): MealCreate

    @POST("water/")
    suspend fun addWater(
        @retrofit2.http.Header("Authorization") token: String,
        @Body request: WaterCreate
    ): okhttp3.ResponseBody

    @Multipart
    @POST("recommend-recipes")
    suspend fun getRecipeRecommendations(
        @Part file: MultipartBody.Part
    ): RecipeResponse
}


// Global olarak token tutmak için (Basit çözüm)
object SessionManager {
    var token: String? = null
    var userName: String = "Kullanıcı"
    var userId: Int = 0
    
    // Kayıt anında ara sayfalarda geçici tutulan veriler
    var tempEmail: String = ""
    var tempPassword: String = ""
    var tempName: String = ""
    var tempBoy: Float = 170.0f
    var tempKilo: Float = 70.0f
    var tempYas: Int = 30
    var tempCinsiyet: String = ""
    var tempActivityLevel: String = ""
}

object PersistenceManager {
    private lateinit var prefs: android.content.SharedPreferences

    fun init(context: android.content.Context) {
        if (!this::prefs.isInitialized) {
            prefs = context.getSharedPreferences("calorie_prefs", android.content.Context.MODE_PRIVATE)
        }
    }

    var lastSavedDate: String
        get() = prefs.getString("last_saved_${SessionManager.userId}", "") ?: ""
        set(value) = prefs.edit().putString("last_saved_${SessionManager.userId}", value).apply()

    var boyCm: Float
        get() = prefs.getFloat("boy_cm_${SessionManager.userId}", 170f)
        set(value) = prefs.edit().putFloat("boy_cm_${SessionManager.userId}", value).apply()

    var kiloKg: Float
        get() = prefs.getFloat("kilo_kg_${SessionManager.userId}", 70f)
        set(value) = prefs.edit().putFloat("kilo_kg_${SessionManager.userId}", value).apply()

    var yas: Int
        get() = prefs.getInt("yas_${SessionManager.userId}", 30)
        set(value) = prefs.edit().putInt("yas_${SessionManager.userId}", value).apply()

    var cinsiyet: String
        get() = prefs.getString("cinsiyet_${SessionManager.userId}", "Kadın") ?: "Kadın"
        set(value) = prefs.edit().putString("cinsiyet_${SessionManager.userId}", value).apply()

    var activityLevel: String
        get() = prefs.getString("activity_level_${SessionManager.userId}", "Hareketsiz") ?: "Hareketsiz"
        set(value) = prefs.edit().putString("activity_level_${SessionManager.userId}", value).apply()

    var hedef: String
        get() = prefs.getString("hedef_${SessionManager.userId}", "Korumak") ?: "Korumak"
        set(value) = prefs.edit().putString("hedef_${SessionManager.userId}", value).apply()

    var hedefHiz: String
        get() = prefs.getString("hedef_hiz_${SessionManager.userId}", "") ?: ""
        set(value) = prefs.edit().putString("hedef_hiz_${SessionManager.userId}", value).apply()

    var hedefKilo: Float
        get() = prefs.getFloat("hedef_kilo_${SessionManager.userId}", 0f)
        set(value) = prefs.edit().putFloat("hedef_kilo_${SessionManager.userId}", value).apply()

    fun getTargetCalories(): Float {
        // 1. BMR Hesapla (Mifflin-St Jeor)
        var bmr = 10f * kiloKg + 6.25f * boyCm - 5f * yas
        if (cinsiyet.equals("Erkek", ignoreCase = true)) {
            bmr += 5f
        } else {
            bmr -= 161f
        }

        // 2. Günlük Yakımı Bul (TDEE)
        val activityMultiplier = when (activityLevel) {
            "Hareketsiz" -> 1.2f
            "Az Aktif" -> 1.375f
            "Orta Aktif" -> 1.55f
            "Çok Aktif" -> 1.725f
            else -> 1.2f
        }
        val tdee = bmr * activityMultiplier

        // 3. Hedefe Göre Kalori
        var targetCal = tdee
        if (hedef == "Kilo Vermek") {
            val deficit = when {
                hedefHiz.contains("0.25") -> 275f
                hedefHiz.contains("0.5") -> 550f
                hedefHiz.contains("1.0") -> 1100f
                else -> 550f
            }
            targetCal -= deficit
        } else if (hedef == "Kilo Almak") {
            val surplus = when {
                hedefHiz.contains("Kas Odaklı") -> 250f
                hedefHiz.contains("Hızlı") -> 700f
                else -> 400f
            }
            targetCal += surplus
        }

        // 4. Güvenlik Sınırı
        val minCal = if (cinsiyet.equals("Erkek", ignoreCase = true)) 1500f else 1200f
        if (targetCal < minCal) {
            targetCal = minCal
        }

        return targetCal
    }

    fun getMealCalorie(mealId: String): Float = prefs.getFloat("meal_${SessionManager.userId}_$mealId", 0f)
    fun saveMealCalorie(mealId: String, calories: Float) = prefs.edit().putFloat("meal_${SessionManager.userId}_$mealId", calories).apply()

    fun getHistory(dayIndex: Int): Float = prefs.getFloat("hist_${SessionManager.userId}_$dayIndex", 0f)
    fun saveHistory(dayIndex: Int, totalCalories: Float) = prefs.edit().putFloat("hist_${SessionManager.userId}_$dayIndex", totalCalories).apply()
    
    fun resetTodayCalories() {
        prefs.edit()
            .remove("meal_${SessionManager.userId}_breakfast")
            .remove("meal_${SessionManager.userId}_lunch")
            .remove("meal_${SessionManager.userId}_dinner")
            .remove("meal_${SessionManager.userId}_snack")
            .apply()
    }

    fun clearUserData() {
        // Artık veriler kullanıcıya (userId) özel tutulduğu için SharedPreferences'ı tamamen sıfırlamayacağız.
        // Böylelikle Ahmet çıkıp Mehmet girse bile, Ahmet'in verileri Mehmet'i veya Ahmet tekrar girdiğinde kendini silmez.
    }
}

object RetrofitClient {
    private const val BASE_URL = "https://bitirme-g5gn.onrender.com/"

    private val client = okhttp3.OkHttpClient.Builder()
        .connectTimeout(90, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(90, java.util.concurrent.TimeUnit.SECONDS)
        .writeTimeout(90, java.util.concurrent.TimeUnit.SECONDS)
        .build()

    val instance: DiyetApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(DiyetApi::class.java)
    }
}
