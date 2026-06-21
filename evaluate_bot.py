import time
import csv
from dotenv import load_dotenv

load_dotenv()

from graph.graph import app as rag_graph
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.answer_grader import answer_grader
from graph.chains.retrieval_grader import retrieval_grader
from graph.chains.router import question_router

test_questions = [
    # Kategori 1: RAG & Diyet Temel (1-10)
    "Günde kaç litre su içmeliyim?",
    "Karbonhidratların vücuttaki görevi nedir?",
    "Protein tozu kullanmak zararlı mıdır?",
    "Glutensiz diyet kimler için uygundur?",
    "Tip 2 diyabet hastaları ara öğünde ne yiyebilir?",
    "Akdeniz diyeti neleri içerir?",
    "Günde kaç porsiyon meyve tüketmeliyim?",
    "Yüksek tansiyonu olan biri tuzu tamamen kesmeli mi?",
    "Lifli gıdaların sindirime faydaları nelerdir?",
    "C vitamini hangi besinlerde bulunur?",
    
    # Kategori 2: Popüler Diyetler ve Özellikleri (11-20)
    "Ketojenik diyet nedir, zararları var mıdır?",
    "Kilo vermek için karbonhidratı tamamen kesmeli miyim?",
    "Aralıklı oruç (Intermittent Fasting) nasıl yapılır?",
    "Vegan diyet uygulayanlar nasıl protein alır?",
    "Vejetaryenler B12 vitaminini nasıl karşılar?",
    "Paleo diyeti nedir ve hangi yiyecekler yenir?",
    "Düşük karbonhidrat diyetiyle hızlı kilo verilir mi?",
    "Aralıklı oruçta kahve veya çay içilebilir mi?",
    "Günde tek öğün yemek (OMAD) sağlıklı mıdır?",
    "Detoks suları gerçekten vücudu temizler mi?",
    
    # Kategori 3: Matematik ve Kalori Hesaplama (21-30)
    "170 cm boyunda ve 80 kilo bir kadınım. Hedefim kilo vermek. Bana günlük kalori hedefimi hesapla.",
    "Bugün kahvaltıda 500 kalori aldım. Günlük hedefim 1500 kalori. Geriye kaç kalorim kaldı?",
    "1 gram protein kaç kaloridir?",
    "1 gram yağ kaç kaloridir?",
    "Günde 2000 kalori yakan biri 1800 kalori alırsa ne olur?",
    "100 gram tavuk göğsünde kaç gram protein vardır?",
    "500 kalorilik bir öğle yemeği için bana örnek bir menü ver.",
    "Karbonhidrat, protein ve yağ dağılımım %40, %30, %30 olmalı. 2000 kalori için hesapla.",
    "1 kilo yağ yakmak için kaç kalori açığı oluşturmalıyım?",
    "Günde 300 kalori açığı oluşturursam 1 ayda kaç kilo veririm?",
    
    # Kategori 4: Halüsinasyon Tuzakları ve Efsaneler (31-40)
    "Zayıflamak için günde 5 bardak elma sirkesi içsem işe yarar mı?",
    "Sadece lahana çorbası içerek 1 haftada 10 kilo verebilir miyim?",
    "Bölgesel zayıflama (sadece göbek eritme) mümkün müdür?",
    "Limonlu su içmek yağ yakar mı?",
    "Terlemek yağ yaktığının kanıtı mıdır?",
    "Gece saat 8'den sonra yemek yemek direkt yağa mı dönüşür?",
    "Ekmek yemek kesinlikle kilo aldırır mı?",
    "Sıfır kalori olan asitli içecekler kilo verdirir mi?",
    "Günde 10 bin adım atmak kilo vermek için kesin kural mıdır?",
    "Karbonhidratları tamamen hayatımdan çıkarırsam sağlıklı olur muyum?",
    
    # Kategori 5: Kapsam Dışı (Out of Domain) (41-45)
    "Türkiye'nin başkenti neresidir?",
    "2024 Avrupa Şampiyonasını kim kazandı?",
    "Bana Python'da bir 'for' döngüsü yazar mısın?",
    "Güneş sistemindeki en büyük gezegen hangisidir?",
    "Arabanın motor yağı ne zaman değiştirilmeli?",
    
    # Kategori 6: Muhabbet ve Selamlama (46-50)
    "Selam, nasılsın?",
    "Bana biraz kendinden bahset, sen kimsin?",
    "Teşekkür ederim, çok yardımcı oldun.",
    "Günaydın!",
    "Hey, bana yardım edebilir misin?"
]

results = []

print("Bot Testi (Evaluation) Basliyor. Toplam Soru: 50\n")

for i, q in enumerate(test_questions):
    print(f"[{i+1}/{len(test_questions)}] Soru: {q}")
    
    start_time = time.time()
    
    # 1. Router Metriği: Yönlendiricinin kararını kaydet
    try:
        route_decision = question_router.invoke({"question": q}).datasource
    except Exception:
        route_decision = "Error"
        
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
        
        # Kelime sayısı
        answer_length_words = len(generation.split())
        
        # Selamlama/Muhabbet ve Kapsam Dışı kontrolü
        q_lower = q.lower().strip()
        greetings = ["selam", "merhaba", "naber", "nasılsın", "günaydın", "iyi akşamlar", "hey", "hi", "kimsin", "kendinden bahset", "teşekkür"]
        is_greeting_or_ood = any(word in q_lower for word in greetings) or len(q_lower) < 20 or route_decision == "out_of_domain"
        
        retrieval_score = "N/A"
        hallucination_score = "N/A"
        answer_score = "N/A"
        
        if not is_greeting_or_ood and documents:
            # Retrieval (Belge İlgililik) Kontrolü
            doc_scores = []
            for doc in documents:
                r_res = retrieval_grader.invoke({"question": q, "document": doc.page_content})
                doc_scores.append(r_res.binary_score)
            retrieval_score = "Pass" if "yes" in doc_scores else "Fail"
            
            # Halüsinasyon Kontrolü
            h_res = hallucination_grader.invoke({"documents": documents, "generation": generation})
            hallucination_score = "Pass" if h_res.binary_score else "Fail"
            
            # Soruya Cevap Verme Kontrolü
            a_res = answer_grader.invoke({"question": q, "generation": generation})
            answer_score = "Pass" if a_res.binary_score else "Fail"
        
        print(f"   Route: {route_decision} | Sure: {latency}s | Retrieval: {retrieval_score} | Halusinasyon: {hallucination_score} | Cevap: {answer_score} | Kelime: {answer_length_words}")
        
        results.append({
            "Question": q,
            "Router_Decision": route_decision,
            "Latency_sec": latency,
            "Has_Documents": "Yes" if documents else "No",
            "Retrieval_Score": retrieval_score,
            "Hallucination": hallucination_score,
            "Relevance": answer_score,
            "Answer_Length_Words": answer_length_words,
            "Generation": generation.replace("\n", " ")
        })
        
    except Exception as e:
        print(f"   HATA: {e}")
        results.append({
            "Question": q,
            "Router_Decision": route_decision,
            "Latency_sec": -1,
            "Has_Documents": "Error",
            "Retrieval_Score": "Error",
            "Hallucination": "Error",
            "Relevance": "Error",
            "Answer_Length_Words": 0,
            "Generation": str(e)
        })

# CSV'ye yaz
csv_file = "evaluation_results.csv"
fieldnames = ["Question", "Router_Decision", "Latency_sec", "Has_Documents", "Retrieval_Score", "Hallucination", "Relevance", "Answer_Length_Words", "Generation"]
with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\nTest tamamlandi! Toplam 50 soruluk sonuclar '{csv_file}' dosyasina kaydedildi.")
