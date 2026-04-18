import asyncio
from fastapi.testclient import TestClient
from main import app
import json
import os

client = TestClient(app)

def test_recommend_recipes():
    print("Testing /recommend-recipes endpoint...")
    
    # Try using test_fridge.jpg
    image_path = "Ne_Yesem/test_fridge.jpg"
    
    if not os.path.exists(image_path):
        print(f"Error: Could not find image at {image_path}")
        return
        
    with open(image_path, "rb") as img_file:
        response = client.post(
            "/recommend-recipes",
            files={"file": ("test_fridge.jpg", img_file, "image/jpeg")}
        )
    
    print(f"Status Code: {response.status_code}")
    
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    test_recommend_recipes()
