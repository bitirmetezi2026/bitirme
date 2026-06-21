import time
import csv
from dotenv import load_dotenv

load_dotenv()

from graph.graph import app as rag_graph
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.answer_grader import answer_grader

test_questions = [
    # Kategori 1: RAG & Diyet
    "Günde kaç litre su içmeliyim?",
    "Ketojenik diyet nedir, zararları var mıdır?",
    "Kilo vermek için karbonhidratı tamamen kesmeli miyim?",
    "Aralıklı oruç (Intermittent Fasting) nasıl yapılır?",
    "Tip 2 diyabet hastaları ara öğünde ne yiyebilir?",
    
    # Kategori 2: Halüsinasyon Kontrolü (Uydurma)
    "Zayıflamak için günde 5 bardak elma sirkesi içsem işe yarar mı?",
    "Sadece lahana çorbası içerek 1 haftada 10 kilo verebilir miyim?",
    
    # Kategori 3: Kapsam Dışı (Web Search / Reddetme)
    "Türkiye'nin başkenti neresidir?",
    "2024 Avrupa Şampiyonasını kim kazandı?",
    "Bana Python'da bir 'for' döngüsü yazar mısın?",
    
    # Kategori 4: Matematik ve Context
    "170 cm boyunda ve 80 kilo bir kadınım. Hedefim kilo vermek. Bana günlük kalori hedefimi hesapla.",
    "Bugün kahvaltıda 500 kalori aldım. Günlük hedefim 1500 kalori. Geriye kaç kalorim kaldı?",
    "1 gram protein kaç kaloridir?",
    
    # Kategori 5: Muhabbet
    "Selam, nasılsın?",
    "Bana biraz kendinden bahset, sen kimsin?"
]

results = []

print("Bot Testi (Evaluation) Basliyor...\n")

for i, q in enumerate(test_questions):
    print(f"[{i+1}/{len(test_questions)}] Soru: {q}")
    
    start_time = time.time()
    
    user_input = {
        "user_id": 1,
        "question": q,
        "history": "",
        "boy_cm": 170.0,
        "kilo_kg": 70.0,
        "yas": 30,
        "cinsiyet": "Kadın",
        "bugunku_ogunler": "Bugün henüz öğün girilmemiş.",
    }
    
    try:
        final_state = rag_graph.invoke(user_input)
        generation = final_state.get("generation", "Cevap üretilemedi.")
        documents = final_state.get("documents", [])
        
        end_time = time.time()
        latency = round(end_time - start_time, 2)
        
        # Selamlama/Muhabbet kontrolü (Graph.py'deki mantıkla aynı)
        q_lower = q.lower().strip()
        greetings = ["selam", "merhaba", "naber", "nasılsın", "günaydın", "iyi akşamlar", "hey", "hi"]
        is_greeting = any(q_lower.startswith(word) for word in greetings) or len(q_lower) < 15
        
        hallucination_score = "N/A (Greeting)"
        answer_score = "N/A (Greeting)"
        
        if not is_greeting and documents:
            # Halüsinasyon Kontrolü
            h_res = hallucination_grader.invoke({"documents": documents, "generation": generation})
            hallucination_score = "Pass" if h_res.binary_score else "Fail"
            
            # Soruya Cevap Verme Kontrolü
            a_res = answer_grader.invoke({"question": q, "generation": generation})
            answer_score = "Pass" if a_res.binary_score else "Fail"
        
        print(f"   Sure: {latency} sn | Halusinasyon: {hallucination_score} | Cevap Kalitesi: {answer_score}")
        
        results.append({
            "Question": q,
            "Latency_sec": latency,
            "Has_Documents": "Yes" if documents else "No",
            "Hallucination": hallucination_score,
            "Relevance": answer_score,
            "Generation": generation.replace("\n", " ")
        })
        
    except Exception as e:
        print(f"   HATA: {e}")
        results.append({
            "Question": q,
            "Latency_sec": -1,
            "Has_Documents": "Error",
            "Hallucination": "Error",
            "Relevance": "Error",
            "Generation": str(e)
        })

# CSV'ye yaz
csv_file = "evaluation_results.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Question", "Latency_sec", "Has_Documents", "Hallucination", "Relevance", "Generation"])
    writer.writeheader()
    writer.writerows(results)

print(f"\nTest tamamlandi! Sonuclar '{csv_file}' dosyasina kaydedildi.")
