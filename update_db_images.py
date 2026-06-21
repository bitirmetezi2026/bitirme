import urllib.parse
from database import SessionLocal
from models import RecipeDB

def update_images():
    db = SessionLocal()
    recipes = db.query(RecipeDB).all()
    count = 0
    for r in recipes:
        if r.image_url and "loremflickr.com" in r.image_url:
            safe_name = urllib.parse.quote(f"{r.name} healthy food")
            new_url = f"https://image.pollinations.ai/prompt/{safe_name}?width=800&height=600&nologo=true"
            r.image_url = new_url
            count += 1
    
    db.commit()
    print(f"Toplam {count} adet tarifin resmi başarıyla pollinations.ai ile güncellendi!")
    db.close()

if __name__ == "__main__":
    update_images()
