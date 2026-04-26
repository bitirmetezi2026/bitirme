from database import engine, SessionLocal
from models import RecipeDB, Base

recipes = [
    {
        "name": "Fırında Somon",
        "calories": "350 kcal | Protein: 35g | Yağ: 15g | Karb: 0g",
        "description": "Omega-3 deposu, zeytinyağı ve limonla harmanlanmış nefis somon balığı.",
        "ingredients": "Somon, Zeytinyağı, Limon, Tuz, Karabiber",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2020/11/firinda-somon-yemekcom.jpg"
    },
    {
        "name": "Izgara Tavuk Salata",
        "calories": "280 kcal | Protein: 30g | Yağ: 10g | Karb: 10g",
        "description": "Yüksek proteinli, taze yeşilliklerle hazırlanmış doyurucu sporcu salatası.",
        "ingredients": "Tavuk Göğsü, Marul, Domates, Salatalık, Zeytinyağı",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2016/05/izgara-tavuklu-salata-tarifi.jpg"
    },
    {
        "name": "Yulaf Lapası",
        "calories": "250 kcal | Protein: 8g | Yağ: 5g | Karb: 40g",
        "description": "Güne enerjik başlamak için meyve ve kuruyemişli yulaf lapası.",
        "ingredients": "Yulaf, Süt, Muz, Ceviz, Tarçın",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2021/01/yulaf-lapasi-tarifi.jpg"
    },
    {
        "name": "Zeytinyağlı Enginar",
        "calories": "150 kcal | Protein: 4g | Yağ: 8g | Karb: 15g",
        "description": "Karaciğer dostu, hafif ve besleyici zeytinyağlı enginar yemeği.",
        "ingredients": "Enginar, Havuç, Bezelye, Zeytinyağı, Limon",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2014/06/zeytinyagli-enginar-yemekcom.jpg"
    },
    {
        "name": "Kinoa Kısırı",
        "calories": "200 kcal | Protein: 6g | Yağ: 7g | Karb: 25g",
        "description": "Geleneksel kısırın daha yüksek proteinli, glutensiz ve sağlıklı hali.",
        "ingredients": "Kinoa, Domates Salçası, Maydanoz, Taze Soğan, Nar Ekşisi",
        "image_url": "https://cdn.yemek.com/mnresize/940/940/uploads/2017/02/kinoa-kisiri-tarifi.jpg"
    }
]

def populate():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    existing = db.query(RecipeDB).count()
    if existing == 0:
        for r in recipes:
            new_recipe = RecipeDB(
                name=r["name"],
                calories=r["calories"],
                description=r["description"],
                ingredients=r["ingredients"],
                image_url=r["image_url"]
            )
            db.add(new_recipe)
        db.commit()
        print(f"{len(recipes)} tarif Supabase'e basariyla eklendi!")
    else:
        print(f"Supabase'de zaten {existing} tarif bulunuyor. Istersen bunlari silip tekrar calistirabilirsin.")
    
    db.close()

if __name__ == "__main__":
    populate()
