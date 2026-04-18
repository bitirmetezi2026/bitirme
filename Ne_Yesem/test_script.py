import urllib.request
import os

from agent import process_fridge_image

def download_image(url, save_path):
    # Spoof user agent to avoid basic 403 blocks
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )
    with urllib.request.urlopen(req) as response:
        with open(save_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    print(f"Downloaded image to {save_path}")

def run_test():
    image_url = "https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?q=80&w=600&auto=format&fit=crop"
    image_path = "test_fridge.jpg"
    
    if not os.path.exists(image_path):
        download_image(image_url, image_path)
    
    print("Reading image and running the agent...")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        
    result = process_fridge_image(image_bytes)
    
    print("\n--- TESPİT EDİLEN MALZEMELER ---")
    for ing in result.get("ingredients", []):
        print(f"- {ing}")
        
    print("\n--- ÖNERİLEN TARİFLER ---")
    import json
    print(json.dumps(result.get("recipes", {}), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_test()
