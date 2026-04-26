from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# 1. KULLANICI TABLOSU
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String, nullable=True)
    
    # Kişisel Bilgiler
    boy_cm = Column(Float, nullable=True, default=170.0)
    kilo_kg = Column(Float, nullable=True, default=70.0)
    yas = Column(Integer, nullable=True, default=30)
    cinsiyet = Column(String, nullable=True)  # "Erkek", "Kadın" veya "Belirtilmemiş"
    language = Column(String, nullable=True, default="English")
    activity_level = Column(String, nullable=True, default="Hareketsiz")
    hedef = Column(String, nullable=True, default="Korumak")
    hedef_hiz = Column(String, nullable=True)
    hedef_kilo = Column(Float, nullable=True)
    dietary_restrictions = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    meals = relationship("Meal", back_populates="owner")
    chats = relationship("ChatLog", back_populates="owner")
    water_logs = relationship("WaterLog", back_populates="owner")

# 2. YEMEK TABLOSU
class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    food_name = Column(String)
    calories = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbs = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="meals")

# 3. SOHBET GEÇMİŞİ TABLOSU
class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user_message = Column(String)
    bot_response = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="chats")

# 4. SU TÜKETİMİ TABLOSU
class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    amount_ml = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="water_logs")

# 5. TARİFLER TABLOSU
class RecipeDB(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    calories = Column(String)  # "280 kcal | Protein: 20g | Yağ: 10g | Karb: 15g"
    description = Column(String)
    ingredients = Column(String)  # Virgülle ayrılmış liste
    steps = Column(String, nullable=True) # Tarifin hazırlanış adımları
    image_url = Column(String, nullable=True) # Resim linki
    created_at = Column(DateTime(timezone=True), server_default=func.now())
