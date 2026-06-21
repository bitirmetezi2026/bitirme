from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import httpx
import base64
from ai_graph import app as vision_app
from Ne_Yesem.agent import process_fridge_image

import utils
import models
import schemas
from database import engine, SessionLocal
import difflib
import re

# =============================================
# KAAN'IN RAG YAPAY ZEKA GRAFİĞİNİ İMPORT ET
# =============================================
from graph.graph import app as rag_graph

# =============================================
# YARDIMCI FONKSİYONLAR (Gıda Kalori Lookup & Ölçekleme)
# =============================================

def find_closest_food(food_name: str, db: Session, threshold: float = 0.6):
    """
    food_calories tablosunda en yakın eşleşen yemeği bulur.
    SequenceMatcher kullanarak fuzzy arama yapar.
    """
    food_name_clean = food_name.strip().lower()
    exact_match = db.query(models.FoodCalorie).filter(
        models.FoodCalorie.food_name.ilike(food_name_clean)
    ).first()
    if exact_match:
        return exact_match

    all_foods = db.query(models.FoodCalorie).all()
    best_match = None
    best_score = 0.0
    
    for f in all_foods:
        score = difflib.SequenceMatcher(None, food_name_clean, f.food_name.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = f
            
    if best_score >= threshold:
        print(f"Fuzzy matched '{food_name}' to '{best_match.food_name}' (score: {best_score:.2f})")
        return best_match
        
    return None

def extract_grams(text: str) -> float | None:
    if not text:
        return None
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|gr|gram|grams)\b', text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

def scale_nutrition(db_food: models.FoodCalorie, predicted_portion: str) -> dict:
    """
    Veritabanındaki yemek değerlerini AI'ın tahmin ettiği porsiyon büyüklüğüne göre ölçekler.
    """
    calories = db_food.calories_per_serving
    protein = db_food.protein or 0.0
    fat = db_food.fat or 0.0
    carbs = db_food.carbs or 0.0
    
    db_grams = extract_grams(db_food.serving_description)
    pred_grams = extract_grams(predicted_portion)
    
    ratio = 1.0
    if db_grams and pred_grams:
        ratio = pred_grams / db_grams
        ratio = max(0.1, min(10.0, ratio))
    else:
        # Porsiyon çarpanı kontrolü: "2 adet", "3 dilim" vb.
        match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:adet|porsiyon|tabak|dilim|fincan|bardak|kase)\b', predicted_portion, re.IGNORECASE)
        if match:
            ratio = float(match.group(1))
            
    return {
        "food_name": db_food.food_name,
        "calories": round(calories * ratio, 1),
        "protein": round(protein * ratio, 1),
        "fat": round(fat * ratio, 1),
        "carbs": round(carbs * ratio, 1),
        "portion": predicted_portion,
        "note": f"Veritabanından çekildi ({db_food.food_name} - {db_food.serving_description} x {ratio:.2f})"
    }

# =============================================
# UYGULAMA KURULUMU
# =============================================

# Tabloları Supabase'de otomatik oluştur (ilk çalıştırmada)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Diyet Asistanı AI Servisi (Kaan + Dila)")

# CORS - Eylül'ün Android uygulamasının bağlanabilmesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Diyet Asistanı API başarıyla çalışıyor! (Render Health Check OK)"}

@app.head("/")
def home_head():
    return {"message": "Diyet Asistanı API başarıyla çalışıyor! (Render Health Check OK)"}

# =============================================
# GÜVENLİK & VERİTABANI BAĞLANTISI
# =============================================

security = HTTPBearer()

def get_db():
    """Her istekte yeni bir veritabanı oturumu açar, bitince kapatır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """JWT token'ını kontrol eder ve giriş yapmış kullanıcıyı döner."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Giriş yapmanız gerekiyor (Token geçersiz)",
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# =============================================
# 1. KAYIT OL (REGISTER)
# =============================================

@app.post("/users/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kayıtlı!")

    hashed_pwd = utils.hash_password(user.password)
    new_user = models.User(
        email=user.email,
        password_hash=hashed_pwd,
        full_name=user.full_name,
        boy_cm=user.boy_cm,
        kilo_kg=user.kilo_kg,
        yas=user.yas,
        cinsiyet=user.cinsiyet,
        language=user.language,
        activity_level=user.activity_level,
        hedef=user.hedef,
        hedef_hiz=user.hedef_hiz,
        hedef_kilo=user.hedef_kilo,
        dietary_restrictions=user.dietary_restrictions
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# =============================================
# 2. GİRİŞ YAP (LOGIN)
# =============================================

@app.post("/auth/login")
def login(user_credentials: schemas.LoginItem, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(status_code=403, detail="Kullanıcı bulunamadı veya şifre hatalı!")

    if not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(status_code=403, detail="Kullanıcı bulunamadı veya şifre hatalı!")

    access_token = utils.create_access_token(
        data={"sub": user.email, "id": user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
    }

# =============================================
# 3. KULLANICI BİLGİ GÜNCELLEME (SETTINGS)
# =============================================

@app.post("/users/update/", response_model=schemas.UserResponse)
def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Android Gson null olanları gönderdiği için None olmayanları filtreliyoruz
    update_data = {k: v for k, v in user_update.dict(exclude_unset=True).items() if v is not None}
    
    if "email" in update_data and update_data["email"] != current_user.email:
        existing_user = db.query(models.User).filter(models.User.email == update_data["email"]).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Bu e-posta adresi zaten kullanımda.")
            
    if "password" in update_data:
        pwd = update_data.pop("password")
        if pwd and str(pwd).strip():
            update_data["password_hash"] = utils.hash_password(pwd)

    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/users/me/", response_model=schemas.UserResponse)
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    """Giriş yapmış kullanıcının profil detaylarını döner."""
    return current_user

# =============================================
# 4. KULLANICI LİSTELE
# =============================================

@app.get("/users/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# =============================================
# 5. YEMEK KAYDETME & LİSTELEME
# =============================================

@app.post("/meals/", response_model=schemas.MealResponse)
def create_meal(
    meal: schemas.MealCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_meal = models.Meal(**meal.dict(), user_id=current_user.id)
    db.add(new_meal)
    db.commit()
    db.refresh(new_meal)
    return new_meal

@app.get("/meals/", response_model=List[schemas.MealResponse])
def read_meals(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    meals = db.query(models.Meal).filter(models.Meal.user_id == current_user.id).all()
    return meals

@app.get("/meals/by-date/", response_model=List[schemas.MealResponse])
def read_meals_by_date(
    date: str = Query(..., description="Tarih formatı: YYYY-MM-DD"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Belirli bir tarihe ait yemekleri döner. date parametresi YYYY-MM-DD formatında olmalıdır."""
    from datetime import datetime, timedelta
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        next_day = target_date + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tarih formatı hatalı. YYYY-MM-DD kullanın.")
    
    meals = db.query(models.Meal).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.created_at >= target_date,
        models.Meal.created_at < next_day
    ).order_by(models.Meal.created_at.asc()).all()
    return meals

@app.delete("/meals/{meal_id}", status_code=status.HTTP_200_OK)
def delete_meal(
    meal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının girdiği bir yemeği siler."""
    meal = db.query(models.Meal).filter(
        models.Meal.id == meal_id,
        models.Meal.user_id == current_user.id
    ).first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Yemek bulunamadı.")
        
    db.delete(meal)
    db.commit()
    return {"message": "Yemek başarıyla silindi."}

# =============================================
# 6. SU TAKİBİ
# =============================================

@app.post("/water/", response_model=schemas.WaterResponse)
def create_water_log(
    water: schemas.WaterCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_water = models.WaterLog(amount_ml=water.amount_ml, user_id=current_user.id)
    db.add(new_water)
    db.commit()
    db.refresh(new_water)
    return new_water

@app.get("/water/", response_model=List[schemas.WaterResponse])
def read_water_logs(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    water_logs = db.query(models.WaterLog).filter(models.WaterLog.user_id == current_user.id).all()
    return water_logs

# =============================================
# 7. EGZERSİZ TAKİBİ
# =============================================

class ExerciseCreate(schemas.BaseModel):
    exercise_type: str
    minutes: int
    calories_burned: float

class ExerciseResponse(schemas.BaseModel):
    id: int
    exercise_type: str
    minutes: int
    calories_burned: float
    created_at: datetime

    class Config:
        from_attributes = True

@app.post("/exercises/", response_model=ExerciseResponse)
def save_exercise(
    exercise: ExerciseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_ex = models.ExerciseLog(
        user_id=current_user.id,
        exercise_type=exercise.exercise_type,
        minutes=exercise.minutes,
        calories_burned=exercise.calories_burned
    )
    db.add(new_ex)
    db.commit()
    db.refresh(new_ex)
    return new_ex

@app.get("/exercises/by-date/", response_model=List[ExerciseResponse])
def get_exercises_by_date(
    date: str = Query(..., description="Tarih: YYYY-MM-DD"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        next_day = target_date + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tarih formatı hatalı. YYYY-MM-DD kullanın.")

    logs = db.query(models.ExerciseLog).filter(
        models.ExerciseLog.user_id == current_user.id,
        models.ExerciseLog.created_at >= target_date,
        models.ExerciseLog.created_at < next_day
    ).order_by(models.ExerciseLog.created_at.asc()).all()
    return logs

@app.get("/recipes/", response_model=List[schemas.RecipeOut])
def get_all_recipes(db: Session = Depends(get_db)):
    """Android'in açılışta tüm tarifleri çekmesi için endpoint"""
    recipes = db.query(models.RecipeDB).all()
    return recipes

@app.post("/recipes/add", response_model=schemas.RecipeOut)
def add_recipe(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    """Profesyonel/Bot arayüzlerinden yeni tarif eklemek için endpoint"""
    new_recipe = models.RecipeDB(**recipe.model_dump() if hasattr(recipe, 'model_dump') else recipe.dict())
    db.add(new_recipe)
    db.commit()
    db.refresh(new_recipe)
    return new_recipe

@app.get("/reset-db")
def reset_database(secret: str = Query(None)):
    """⚠️ TEHLİKELİ: Yeni sütunlar eklendiğinde veritabanını sıfırlamak için geçici endpoint.
    Kullanmak için: /reset-db?secret=DILA_RESET_2025 şeklinde çağırın.
    UYARI: Bu endpoint tüm kullanıcı ve yemek verilerini siler!
    """
    if secret != "DILA_RESET_2025":
        raise HTTPException(status_code=403, detail="⛔ Bu endpoint'e erişim yetkiniz yok. Gizli anahtar gerekli.")
    from database import engine
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    return {"message": "⚠️ Veritabanı başarıyla sıfırlandı ve yeni sütunlar ile tekrar oluşturuldu!"}

@app.get("/populate-recipes")
def populate_recipes_endpoint(db: Session = Depends(get_db)):
    """Render Shell paralı olduğu için tarayıcıdan tetiklenecek doldurma linki"""
    recipes_data = [
        {"name": "Fırında Somon", "calories": "350 kcal | Protein: 35g | Yağ: 15g | Karb: 0g", "description": "Omega-3 deposu somon.", "ingredients": "Somon, Limon, Zeytinyağı", "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2020/11/firinda-somon-yemekcom.jpg"},
        {"name": "Izgara Tavuk Salata", "calories": "280 kcal | Protein: 30g | Yağ: 10g | Karb: 10g", "description": "Sporcu salatası.", "ingredients": "Tavuk, Marul, Domates", "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2016/05/izgara-tavuklu-salata-tarifi.jpg"},
        {"name": "Yulaf Lapası", "calories": "250 kcal | Protein: 8g | Yağ: 5g | Karb: 40g", "description": "Güne enerjik başlamak için.", "ingredients": "Yulaf, Süt, Muz", "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2021/01/yulaf-lapasi-tarifi.jpg"},
        {"name": "Kinoa Kısırı", "calories": "200 kcal | Protein: 6g | Yağ: 7g | Karb: 25g", "description": "Glutensiz kısır.", "ingredients": "Kinoa, Salça, Yeşillik", "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2017/02/kinoa-kisiri-tarifi.jpg"}
    ]
    existing = db.query(models.RecipeDB).count()
    if existing == 0:
        for r in recipes_data:
            db.add(models.RecipeDB(**r))
        db.commit()
        return {"status": "success", "message": f"{len(recipes_data)} tarif basariyla eklendi!"}
    return {"status": "info", "message": f"Zaten {existing} tarif var, tekrar eklenmedi."}

from pydantic import BaseModel
class RecipeImageUpdate(BaseModel):
    image_url: str

@app.put("/recipes/{recipe_id}/image")
def update_recipe_image(recipe_id: int, payload: RecipeImageUpdate, db: Session = Depends(get_db)):
    """Kullanıcının manuel olarak resim linki güncelleyebilmesi için endpoint."""
    recipe = db.query(models.RecipeDB).filter(models.RecipeDB.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Tarif bulunamadı.")
    
    recipe.image_url = payload.image_url
    db.commit()
    return {"status": "success", "message": f"Tarif (ID: {recipe_id}) resmi başarıyla güncellendi!"}

# =============================================
# 8. CHATBOT (KAAN'IN RAG SİSTEMİ - DOĞRUDAN)
# =============================================

@app.post("/chat")
def chat_with_ai(
    chat_request: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Android'den gelen soruyu alır, RAG Yapay Zeka sistemine doğrudan sorar,
    cevabı veritabanına kaydeder ve Android'e geri döner.
    """
    # Mesajı al (Android'in user_message veya Dila'nın message formatını destekle)
    message = chat_request.user_message or chat_request.message
    if not message:
        raise HTTPException(status_code=400, detail="Bir mesaj yazmanız gerekiyor.")

    # Öğün bilgisini string formatına çevir (RAG'ın beklediği format)
    ogunler_str = ""
    if chat_request.bugunku_ogunler:
        for ogun in chat_request.bugunku_ogunler:
            ogunler_str += f"- {ogun.food_name} ({ogun.calories} kcal, Protein: {ogun.protein}g, Yağ: {ogun.fat}g, Karb: {ogun.carbs}g)\n"
    else:
        # Eğer Android öğün göndermemişse, veritabanından son 5 öğünü çek
        last_meals = db.query(models.Meal).filter(models.Meal.user_id == current_user.id).order_by(models.Meal.created_at.desc()).limit(5).all()
        for m in last_meals:
            ogunler_str += f"- {m.food_name} ({m.calories} kcal)\n"

    if not ogunler_str:
        ogunler_str = "Bugün henüz öğün girilmemiş."

    # Kullanıcı bilgilerini al (Android'in default Kadın göndermesini ezip veritabanını önceliklendir)
    boy = getattr(current_user, 'boy_cm', None) or chat_request.boy_cm or 170.0
    kilo = getattr(current_user, 'kilo_kg', None) or chat_request.kilo_kg or 70.0
    yas = getattr(current_user, 'yas', None) or chat_request.yas or 30
    
    db_cinsiyet = getattr(current_user, 'cinsiyet', None)
    cinsiyet = db_cinsiyet if db_cinsiyet and db_cinsiyet != "Belirtilmemiş" else (chat_request.cinsiyet or "Belirtilmemiş")

    print(f"🤖 Chat İsteği -> Kullanıcı: {current_user.email} | Boy: {boy} | Kilo: {kilo} | Mesaj: {message[:50]}...")

    # ============================================
    # RAG YAPAY ZEKA GRAFİĞİNİ DOĞRUDAN ÇAĞIR
    # (Artık proxy yok, doğrudan Kaan'ın kodu çalışıyor!)
    # ============================================
    try:
        user_input = {
            "user_id": current_user.id,
            "question": message,
            "history": chat_request.history,
            "boy_cm": boy,
            "kilo_kg": kilo,
            "yas": yas,
            "cinsiyet": cinsiyet,
            "bugunku_ogunler": ogunler_str,
        }
        final_result = rag_graph.invoke(user_input)
        ai_reply = final_result.get("generation", "AI cevap üretemedi.")

    except Exception as e:
        print(f"❌ RAG Hatası: {e}")
        ai_reply = f"Yapay zeka şu an meşgul. Lütfen tekrar deneyin."

    # Sohbeti veritabanına kaydet (Dila'nın ChatLog tablosu)
    try:
        new_chat = models.ChatLog(
            user_id=current_user.id,
            user_message=message,
            bot_response=ai_reply
        )
        db.add(new_chat)
        db.commit()
    except Exception as e:
        print(f"⚠️ Chat log kaydedilemedi: {e}")

    return {"reply": ai_reply}

# =============================================
# 8. YEMEK ANALİZ (FOTOĞRAF -> KALORİ)
# =============================================

@app.post("/analyze")
async def analyze_food(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Fotoğraftan yemek tanıma - Doğrudan LangGraph entegrasyonu ve DB lookup"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Lutfen sadece resim (image) dosyasi yukleyin.")
        
    try:
        contents = await file.read()
        base64_string = base64.b64encode(contents).decode('utf-8')
        image_data = f"data:{file.content_type};base64,{base64_string}"
        
        initial_state = {"image_source": image_data}
        result_state = vision_app.invoke(initial_state)
        analysis = result_state.get("food_analysis")
        
        if analysis:
            data = analysis.model_dump() if hasattr(analysis, "model_dump") else analysis.dict()
            food_name = data.get("food_name")
            portion = data.get("portion")
            
            # Veritabanında ara
            db_food = find_closest_food(food_name, db)
            if db_food:
                scaled = scale_nutrition(db_food, portion)
                return {
                    "food_name": scaled["food_name"],
                    "portion": scaled["portion"],
                    "calories": scaled["calories"],
                    "macros": {
                        "protein": scaled["protein"],
                        "fat": scaled["fat"],
                        "carbs": scaled["carbs"]
                    },
                    "note": scaled["note"]
                }
            else:
                data["note"] = "AI tahmini (Veritabanında bulunamadı)"
                return data
                
        return {"error": "Analiz tamamlanamadi. Lutfen tekrar deneyin."}
    except Exception as e:
        print(f"⚠️ Yemek Analiz Hatası: {e}")
        return {
            "food_name": "Sistem Hatası",
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "note": str(e)
        }


class TextAnalyzeRequest(schemas.BaseModel):
    text: str

@app.post("/analyze/text")
def analyze_food_text(
    req: TextAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Metinden yemek tanıma - Diyetisyen Agent + DB lookup"""
    text = req.text
    from agents.dietitian_agent import run_dietitian_agent
    
    try:
        # Diyetisyen ajanı çalıştırıp yemek adı ve porsiyonu tahmin et
        analysis = run_dietitian_agent(f"Kullanıcı metin olarak girdi: {text}", feedback=None)
        
        if analysis:
            data = analysis.model_dump() if hasattr(analysis, "model_dump") else analysis.dict()
            food_name = data.get("food_name")
            portion = data.get("portion")
            
            # Veritabanında ara
            db_food = find_closest_food(food_name, db)
            if db_food:
                scaled = scale_nutrition(db_food, portion)
                return {
                    "food_name": scaled["food_name"],
                    "portion": scaled["portion"],
                    "calories": scaled["calories"],
                    "macros": {
                        "protein": scaled["protein"],
                        "fat": scaled["fat"],
                        "carbs": scaled["carbs"]
                    },
                    "note": scaled["note"]
                }
            else:
                data["note"] = "AI tahmini (Veritabanında bulunamadı)"
                return data
                
        return {"error": "Analiz tamamlanamadi."}
    except Exception as e:
        print(f"⚠️ Metin Analiz Hatası: {e}")
        return {
            "food_name": text[:40],
            "portion": "1 porsiyon",
            "calories": 150.0,
            "macros": {"protein": 5.0, "fat": 5.0, "carbs": 15.0},
            "note": f"Varsayılan değerler (Hata: {str(e)})"
        }


# =============================================
# 9. TARİF ÖNERİSİ (NE YESEM?)
# =============================================

@app.post("/recommend-recipes")
async def forward_to_ai_agent(
    file: UploadFile = File(None),
    manuel_malzemeler: str = Form(None),
    kalan_kalori: str = Query(None),
    kisitlamalar: str = Query(None)
):
    """Buzdolabı fotoğrafından veya manuel metinden tarif önerisi (Ne Yesem)"""
    if not file and not manuel_malzemeler:
        raise HTTPException(status_code=400, detail="Lütfen bir fotoğraf yükleyin veya malzeme listesi girin.")
        
    contents = None
    if file:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Sadece resim formatında dosya yükleyebilirsiniz.")
        contents = await file.read()
    
    try:
        # Süreci LangGraph ajanına gönderiyoruz
        result_state = process_fridge_image(image_bytes=contents, manual_ingredients=manuel_malzemeler, kalan_kalori=kalan_kalori, kisitlamalar=kisitlamalar)
        
        return {
            "status": "success",
            "detected_ingredients": result_state.get("ingredients", []),
            "recommendations": result_state.get("recipes", {})
        }
    except Exception as e:
        print(f"Error processing recipe request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/daily-summary/", response_model=schemas.DailySummaryResponse)
def get_daily_summary(
    date: str = Query(..., description="Tarih formatı: YYYY-MM-DD"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir gün için kalori, su, egzersiz toplamlarını ve kalori hedefini döner."""
    from datetime import datetime, timedelta
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        next_day = target_date + timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Tarih formatı hatalı. YYYY-MM-DD kullanın.")
        
    # Yemekler
    meals = db.query(models.Meal).filter(
        models.Meal.user_id == current_user.id,
        models.Meal.created_at >= target_date,
        models.Meal.created_at < next_day
    ).all()
    
    total_calories_eaten = sum(m.calories for m in meals)
    total_protein = sum(m.protein or 0.0 for m in meals)
    total_fat = sum(m.fat or 0.0 for m in meals)
    total_carbs = sum(m.carbs or 0.0 for m in meals)
    
    # Su
    water_logs = db.query(models.WaterLog).filter(
        models.WaterLog.user_id == current_user.id,
        models.WaterLog.created_at >= target_date,
        models.WaterLog.created_at < next_day
    ).all()
    total_water_ml = sum(w.amount_ml for w in water_logs)
    
    # Egzersiz
    exercise_logs = db.query(models.ExerciseLog).filter(
        models.ExerciseLog.user_id == current_user.id,
        models.ExerciseLog.created_at >= target_date,
        models.ExerciseLog.created_at < next_day
    ).all()
    total_calories_burned = sum(e.calories_burned for e in exercise_logs)
    
    # Kalori Hedefi
    boy = current_user.boy_cm or 170.0
    kilo = current_user.kilo_kg or 70.0
    yas = current_user.yas or 30
    cinsiyet = current_user.cinsiyet or "Belirtilmemiş"
    activity_level = current_user.activity_level or "Hareketsiz"
    hedef = current_user.hedef or "Korumak"
    hedef_hiz = current_user.hedef_hiz or ""
    
    bmr = 10.0 * kilo + 6.25 * boy - 5.0 * yas
    if cinsiyet.lower() == "erkek":
        bmr += 5.0
    else:
        bmr -= 161.0
        
    activity_multiplier = 1.2
    if activity_level == "Az Aktif":
        activity_multiplier = 1.375
    elif activity_level == "Orta Aktif":
        activity_multiplier = 1.55
    elif activity_level == "Çok Aktif":
        activity_multiplier = 1.725
        
    tdee = bmr * activity_multiplier
    target_cal = tdee
    
    if hedef == "Kilo Vermek":
        deficit = 550.0
        if "0.25" in hedef_hiz:
            deficit = 275.0
        elif "1.0" in hedef_hiz:
            deficit = 1100.0
        target_cal -= deficit
    elif hedef == "Kilo Almak":
        surplus = 400.0
        if "Kas Odaklı" in hedef_hiz:
            surplus = 250.0
        elif "Hızlı" in hedef_hiz:
            surplus = 700.0
        target_cal += surplus
        
    min_cal = 1500.0 if cinsiyet.lower() == "erkek" else 1200.0
    if target_cal < min_cal:
        target_cal = min_cal
        
    return {
        "total_calories_eaten": round(total_calories_eaten, 1),
        "total_protein": round(total_protein, 1),
        "total_fat": round(total_fat, 1),
        "total_carbs": round(total_carbs, 1),
        "total_water_ml": total_water_ml,
        "total_calories_burned": round(total_calories_burned, 1),
        "target_calories": round(target_cal, 1)
    }

@app.get("/food-calories/", response_model=List[schemas.FoodCalorieResponse])
def get_food_calories(
    query: Optional[str] = Query(None, description="Arama sorgusu (yemek adı)"),
    db: Session = Depends(get_db)
):
    """Veritabanındaki yemek ve kalori listesini döner, dilenirse sorgulanabilir."""
    if query:
        return db.query(models.FoodCalorie).filter(
            models.FoodCalorie.food_name.ilike(f"%{query}%")
        ).all()
    return db.query(models.FoodCalorie).all()

@app.post("/food-calories/populate")
def populate_food_calories_table(db: Session = Depends(get_db)):
    """Yemek kalorileri tablosunu başlangıç verisi ile doldurur."""
    from populate_food_calories import foods_data
    count_added = 0
    count_updated = 0
    for item in foods_data:
        existing = db.query(models.FoodCalorie).filter(models.FoodCalorie.food_name == item["food_name"]).first()
        if existing:
            existing.calories_per_serving = item["calories_per_serving"]
            existing.protein = item["protein"]
            existing.fat = item["fat"]
            existing.carbs = item["carbs"]
            existing.serving_description = item["serving_description"]
            existing.category = item["category"]
            count_updated += 1
        else:
            new_food = models.FoodCalorie(**item)
            db.add(new_food)
            count_added += 1
    db.commit()
    return {"status": "success", "message": f"Added {count_added} new foods, updated {count_updated}."}

@app.get("/chat-history/")
def get_chat_history_endpoint(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının geçmiş sohbet kayıtlarını döner."""
    chats = db.query(models.ChatLog).filter(
        models.ChatLog.user_id == current_user.id
    ).order_by(models.ChatLog.created_at.asc()).all()
    return [
        {
            "id": c.id,
            "user_message": c.user_message,
            "bot_response": c.bot_response,
            "created_at": c.created_at.isoformat() if c.created_at else None
        } for c in chats
    ]

# =============================================
# SUNUCU BAŞLATMA
# =============================================

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)