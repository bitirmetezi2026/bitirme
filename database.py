from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Bağlantı adresi (.env yoksa Render panelindeki Environment Variables'dan alır)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345@localhost/yemek_db")

# Motoru çalıştır
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Oturum açma sınıfı
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablo iskeleti
Base = declarative_base()
