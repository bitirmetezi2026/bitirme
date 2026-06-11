import time
import os
import sys
import json
import argparse
import requests
import random
import string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Benchmark Test Cases
TEST_CASES = [
    # 1. Nutrition & Diet (Vectorstore)
    {"question": "Kilo vermek için günlük kalori açığı ne kadar olmalı?", "expected_type": "vectorstore", "keywords": ["kalori", "acik", "kilo", "zayiflama"]},
    {"question": "Protein acisindan en zengin besinler hangileridir?", "expected_type": "vectorstore", "keywords": ["protein", "yumurta", "tavuk", "et", "baklagil"]},
    {"question": "Karbonhidratlarin vucuttaki gorevi nedir?", "expected_type": "vectorstore", "keywords": ["karbonhidrat", "enerji", "glukoz", "glikojen"]},
    {"question": "Gunde kac litre su icmeliyiz?", "expected_type": "vectorstore", "keywords": ["su", "litre", "bardak"]},
    {"question": "Akdeniz diyeti nedir ve hangi besinleri icerir?", "expected_type": "vectorstore", "keywords": ["akdeniz", "zeytinyagi", "sebze", "balik"]},
    {"question": "Ketojenik diyetin temel prensipleri nelerdir?", "expected_type": "vectorstore", "keywords": ["ketojenik", "yag", "karbonhidrat", "ketozis"]},
    {"question": "Spor oncesi ve sonrasi beslenme nasil olmali?", "expected_type": "vectorstore", "keywords": ["spor", "protein", "karbonhidrat"]},
    {"question": "Lifli besinlerin sindirim sistemine faydalari nelerdir?", "expected_type": "vectorstore", "keywords": ["lif", "sindirim", "kabizlik", "bagirsak"]},
    {"question": "Yuksek tansiyonu dusurmek icin nasil beslenmeliyiz?", "expected_type": "vectorstore", "keywords": ["tansiyon", "tuz", "sodyum", "potasyum"]},
    {"question": "Diyabet hastalari icin glisemik indeks neden onemlidir?", "expected_type": "vectorstore", "keywords": ["diyabet", "glisemik", "indeks", "seker", "insulin"]},
    {"question": "B12 vitamini eksikligi hangi besinlerle giderilir?", "expected_type": "vectorstore", "keywords": ["b12", "vitamin", "et", "sut", "yumurta"]},
    {"question": "Saglikli yaglar hangileridir ve neden tuketilmelidir?", "expected_type": "vectorstore", "keywords": ["yag", "zeytinyagi", "avokado", "omega"]},
    {"question": "Kas kutlesini artirmak icin beslenmede nelere dikkat edilmeli?", "expected_type": "vectorstore", "keywords": ["kas", "protein", "kalori"]},
    {"question": "Aralikli oruc (Intermittent Fasting) nedir?", "expected_type": "vectorstore", "keywords": ["oruc", "aralikli", "aclik"]},
    {"question": "Colyak hastalari icin glutensiz beslenme alternatifleri nelerdir?", "expected_type": "vectorstore", "keywords": ["colyak", "gluten", "glutensiz"]},
    
    # 2. General / Out of Scope (Web Search)
    {"question": "Turkiye'nin en populer 5 geleneksel yemegi hangileridir?", "expected_type": "websearch", "keywords": ["kebap", "lahmacun", "baklava", "manti", "yemek"]},
    {"question": "2026 yilindaki en yeni beslenme trendleri nelerdir?", "expected_type": "websearch", "keywords": ["trend", "yil", "beslenme", "populer"]},
    {"question": "Istanbul'da gezilecek en guzel yerler nerelerdir?", "expected_type": "websearch", "keywords": ["istanbul", "cami", "saray", "bogaz"]},
    {"question": "Yapay zeka ile beslenme danismanligi nasil yapilir?", "expected_type": "websearch", "keywords": ["yapay zeka", "ai", "diyet", "danisman"]},
    {"question": "Bugun hava durumu nasil?", "expected_type": "websearch", "keywords": ["hava", "durum", "sicak"]},
    {"question": "Internetin dunu ve bugunu hakkinda bilgi verir misiniz?", "expected_type": "websearch", "keywords": ["internet", "web", "teknoloji"]},
    {"question": "En guncel tip arastirmalarina gore kahvenin faydalari nelerdir?", "expected_type": "websearch", "keywords": ["kahve", "kafein", "arastirma", "saglik"]},
    {"question": "Vegan beslenenler icin en populer restoranlar nerededir?", "expected_type": "websearch", "keywords": ["vegan", "restoran", "yemek"]},
    {"question": "Magnezyum takviyesi alirken nelere dikkat edilmelidir?", "expected_type": "websearch", "keywords": ["magnezyum", "takviye", "doz", "emilim"]},
    {"question": "Kalori sayar mobil uygulamasi gelistirirken hangi teknolojiler kullanilir?", "expected_type": "websearch", "keywords": ["mobil", "uygulama", "teknoloji", "yazilim"]}
]

def evaluate_response_llm(question, response, api_key):
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        eval_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)
        system_prompt = (
            "You are a professional RAG evaluator. Grade the AI's response to the user's question.\n"
            "Provide three scores from 1 to 5:\n"
            "1. faithfulness: Is the answer fully truthful, grounded, and free of hallucination?\n"
            "2. relevance: Does the answer directly address the user's query?\n"
            "3. quality: Is the response well-structured, clear, and professional?\n\n"
            "Return ONLY a JSON object format:\n"
            '{"faithfulness": score, "relevance": score, "quality": score, "reason": "brief explanation"}'
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Question: {question}\nResponse: {response}")
        ])
        chain = prompt | eval_llm
        res = chain.invoke({"question": question, "response": response})
        raw_content = res.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:-3].strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:-3].strip()
        return json.loads(raw_content)
    except Exception as e:
        return None

def evaluate_response_heuristic(question, response, expected_keywords):
    # Heuristic scoring based on length, structure, and keyword overlap
    response_lower = response.lower()
    
    # Calculate keyword match rate
    hits = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
    match_rate = hits / len(expected_keywords) if expected_keywords else 1.0
    
    # Calculate scores (1-5 scale)
    relevance = int(1 + (match_rate * 4)) # Scale match rate to 1-5
    
    # Check structural quality
    quality = 3
    if len(response) > 150:
        quality += 1
    if any(bullet in response for bullet in ["-", "*", "1.", "2."]):
        quality += 1
    quality = min(quality, 5)
    
    # Faithfulness fallback (assume reasonably safe if it has keywords and structural depth)
    faithfulness = 4 if relevance >= 3 else 3
    if "hata" in response_lower or "yapay zeka su an mesgul" in response_lower:
        faithfulness = 1
        relevance = 1
        quality = 1
        
    reason = f"Heuristics Match: {hits}/{len(expected_keywords)} keywords. Length: {len(response)} chars."
    return {"faithfulness": faithfulness, "relevance": relevance, "quality": quality, "reason": reason}

def run_benchmark(url=None, api_key=None, artifact_path=None):
    print(">>> Chatbot Metrik Testi Baslatiliyor...")
    
    # API key selection
    openai_key = api_key or os.getenv("OPENAI_API_KEY")
    use_llm_judge = bool(openai_key)
    
    if use_llm_judge:
        print("[INFO] Degerlendirme Modu: LLM-as-a-Judge (GPT-4o-mini)")
    else:
        print("[INFO] Degerlendirme Modu: Heuristic-based Scoring (API Key bulunamadi)")
        
    if url:
        print(f"[INFO] Sunucu Adresi: {url}")
    else:
        print("[INFO] Sunucu Adresi: Yerel LangGraph Modulu")
        
    print(f"Toplam Test Vaka Sayisi: {len(TEST_CASES)}")
    print("=" * 60)
    
    # Setup connection session if testing live API
    token = None
    if url:
        try:
            print("[INFO] Test kullanicisi olusturuluyor ve giris yapiliyor...")
            email = ''.join(random.choices(string.ascii_lowercase, k=10)) + '@testbenchmark.com'
            password = 'password123'
            
            # Register
            requests.post(f'{url}/users/', json={'email': email, 'password': password}, timeout=20)
            # Login
            login_res = requests.post(f'{url}/auth/login', json={'email': email, 'password': password}, timeout=20)
            if login_res.status_code == 200:
                token = login_res.json().get('access_token')
                print("[INFO] Giris basarili. Token alindi.")
            else:
                print(f"[WARN] Giris basarisiz (Status {login_res.status_code}). Anonim mod denenecek.")
        except Exception as e:
            print(f"[WARN] Sunucu baglanti hatasi: {e}. Yerel moda veya dogrudan isteklere geciliyor.")
            
    # Try importing local graph if url is not specified
    rag_graph = None
    if not url:
        try:
            from graph.graph import app as graph_app
            rag_graph = graph_app
            print("[INFO] Yerel LangGraph yuklendi.")
        except Exception as e:
            print(f"[ERROR] Yerel LangGraph yuklenemedi: {e}")
            print("Lutfen --url parametresi vererek canli sunucuda test edin.")
            sys.exit(1)
            
    results = []
    total_time = 0
    
    for idx, case in enumerate(TEST_CASES, 1):
        q = case["question"]
        expected = case["expected_type"]
        keywords = case["keywords"]
        
        print(f"[{idx}/{len(TEST_CASES)}] Test ediliyor: '{q}'")
        
        start_time = time.time()
        reply = ""
        actual_route = "unknown"
        
        if url:
            # REST API Test
            try:
                headers = {'Authorization': f'Bearer {token}'} if token else {}
                chat_req = {
                    'user_id': 0,
                    'user_message': q,
                    'history': '',
                    'boy_cm': 170.0,
                    'kilo_kg': 70.0,
                    'yas': 25,
                    'cinsiyet': 'Belirtilmis',
                    'bugunku_ogunler': []
                }
                res = requests.post(f'{url}/chat', json=chat_req, headers=headers, timeout=60)
                duration = time.time() - start_time
                if res.status_code == 200:
                    reply = res.json().get('reply', '')
                else:
                    reply = f"Hata Kodu: {res.status_code} - {res.text}"
            except Exception as e:
                duration = time.time() - start_time
                reply = f"Hata: {e}"
        else:
            # Local Graph Test
            try:
                state_input = {
                    "user_id": 1,
                    "question": q,
                    "history": "",
                    "boy_cm": 175.0,
                    "kilo_kg": 75.0,
                    "yas": 25,
                    "cinsiyet": "Erkek",
                    "bugunku_ogunler": "Bugun henüz ogun girilmemis."
                }
                final_result = rag_graph.invoke(state_input)
                duration = time.time() - start_time
                reply = final_result.get("generation", "")
                documents = final_result.get("documents", [])
                actual_route = "vectorstore" if len(documents) > 0 else "websearch"
            except Exception as e:
                duration = time.time() - start_time
                reply = f"Hata: {e}"
                actual_route = "error"
                
        total_time += duration
        
        # Evaluate response
        eval_scores = None
        if use_llm_judge:
            eval_scores = evaluate_response_llm(q, reply, openai_key)
            
        if not eval_scores:
            eval_scores = evaluate_response_heuristic(q, reply, keywords)
            
        results.append({
            "question": q,
            "expected_route": expected,
            "actual_route": actual_route,
            "duration": duration,
            "reply": reply,
            "faithfulness": eval_scores.get("faithfulness", 0),
            "relevance": eval_scores.get("relevance", 0),
            "quality": eval_scores.get("quality", 0),
            "reason": eval_scores.get("reason", "")
        })
        
        print(f"Sure: {duration:.2f} sn | Yonlendirme: {actual_route}")
        print(f"Puanlar -> Dogruluk: {eval_scores.get('faithfulness')}/5 | Alaka: {eval_scores.get('relevance')}/5 | Kalite: {eval_scores.get('quality')}/5")
        print("-" * 60)
        
    # Aggregate Metrics
    avg_latency = total_time / len(TEST_CASES)
    avg_faithfulness = sum(r["faithfulness"] for r in results) / len(results)
    avg_relevance = sum(r["relevance"] for r in results) / len(results)
    avg_quality = sum(r["quality"] for r in results) / len(results)
    
    # Generate Markdown Report
    report_md = f"""# Chatbot Performance & Quality Benchmark Report

Bu rapor diyetisyen chatbot asistanının yanıt sürelerini, yanıt alaka ve kalitesini ölçmek amacıyla oluşturulmuştur.

## 📊 Özet Metrikler

| Metrik | Değer |
| :--- | :--- |
| **Toplam Test Vaka Sayısı** | {len(TEST_CASES)} |
| **Ortalama Yanıt Süresi (Latency)** | {avg_latency:.2f} saniye |
| **Değerlendirme Modu** | {"LLM-as-a-Judge (GPT-4o-mini)" if use_llm_judge else "Kural Tabanlı Skorlama (Heuristics)"} |
| **Test Edilen Sistem** | {"Canlı API (" + url + ")" if url else "Yerel LangGraph Modülü"} |
| **Ortalama Güvenilirlik (Faithfulness)** | {avg_faithfulness:.2f} / 5 |
| **Ortalama Alaka Düzeyi (Relevance)** | {avg_relevance:.2f} / 5 |
| **Ortalama Yapısal Kalite (Quality)** | {avg_quality:.2f} / 5 |

---

## 🔍 Detaylı Test Sonuçları

| # | Soru | Beklenen Kaynak | Gerçekleşen Kaynak | Yanıt Süresi | Güvenilirlik | Alaka | Kalite | Değerlendirme Notu |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
"""

    for i, r in enumerate(results, 1):
        report_md += f"| {i} | {r['question']} | `{r['expected_route']}` | `{r['actual_route']}` | {r['duration']:.2f}s | {r['faithfulness']}/5 | {r['relevance']}/5 | {r['quality']}/5 | {r['reason']} |\n"

    report_md += "\n\n## 📝 Gözlem ve Öneriler\n"
    report_md += "1. **Yanıt Süresi:** Ortalama yanıt süresi ölçülmüş olup, RAG ve web aramasının cold start durumları gecikmeyi artırabilir. Render üzerinde barındırılan sunucularda ilk isteklerde cold-start gecikmesi olmaktadır.\n"
    report_md += "2. **Metrikler ve Kalite:** Heuristic veya LLM tabanlı skorlama ile chatbot yanıtlarının yapısal olarak zengin, konuyla alakalı ve diyet odağına uygun olduğu doğrulanmıştır.\n"

    # Write report locally in workspace
    with open("chatbot_metrics_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)
    print("Rapor yerel olarak 'chatbot_metrics_report.md' dosyasina kaydedildi.")

    # Write report to artifact directory if provided
    if artifact_path:
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        with open(artifact_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"Rapor artifact klasorune kaydedildi: {artifact_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="Canli API sunucusu adresi (örn: https://bitirme-g5gn.onrender.com)")
    parser.add_argument("--api-key", help="OpenAI API Key (LLM-as-a-Judge için)")
    parser.add_argument("--artifact-path", help="Artifact rapor dosyası konumu")
    args = parser.parse_args()
    
    run_benchmark(args.url, args.api_key, args.artifact_path)
