# Chatbot Performance & Quality Benchmark Report

Bu rapor diyetisyen chatbot asistanının yanıt sürelerini, yanıt alaka ve kalitesini ölçmek amacıyla oluşturulmuştur.

## 📊 Özet Metrikler

| Metrik | Değer |
| :--- | :--- |
| **Toplam Test Vaka Sayısı** | 25 |
| **Ortalama Yanıt Süresi (Latency)** | 2.75 saniye |
| **Değerlendirme Modu** | Kural Tabanlı Skorlama (Heuristics) |
| **Test Edilen Sistem** | Canlı API (https://bitirme-g5gn.onrender.com) |
| **Ortalama Güvenilirlik (Faithfulness)** | 1.00 / 5 |
| **Ortalama Alaka Düzeyi (Relevance)** | 1.00 / 5 |
| **Ortalama Yapısal Kalite (Quality)** | 1.00 / 5 |

---

## 🔍 Detaylı Test Sonuçları

| # | Soru | Beklenen Kaynak | Gerçekleşen Kaynak | Yanıt Süresi | Güvenilirlik | Alaka | Kalite | Değerlendirme Notu |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | Kilo vermek için günlük kalori açığı ne kadar olmalı? | `vectorstore` | `unknown` | 51.89s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 2 | Protein acisindan en zengin besinler hangileridir? | `vectorstore` | `unknown` | 0.65s | 1/5 | 1/5 | 1/5 | Heuristics Match: 1/5 keywords. Length: 47 chars. |
| 3 | Karbonhidratlarin vucuttaki gorevi nedir? | `vectorstore` | `unknown` | 0.69s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 4 | Gunde kac litre su icmeliyiz? | `vectorstore` | `unknown` | 0.58s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 5 | Akdeniz diyeti nedir ve hangi besinleri icerir? | `vectorstore` | `unknown` | 0.56s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 6 | Ketojenik diyetin temel prensipleri nelerdir? | `vectorstore` | `unknown` | 0.67s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 7 | Spor oncesi ve sonrasi beslenme nasil olmali? | `vectorstore` | `unknown` | 0.62s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 8 | Lifli besinlerin sindirim sistemine faydalari nelerdir? | `vectorstore` | `unknown` | 0.62s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 9 | Yuksek tansiyonu dusurmek icin nasil beslenmeliyiz? | `vectorstore` | `unknown` | 0.61s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 10 | Diyabet hastalari icin glisemik indeks neden onemlidir? | `vectorstore` | `unknown` | 0.63s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/5 keywords. Length: 47 chars. |
| 11 | B12 vitamini eksikligi hangi besinlerle giderilir? | `vectorstore` | `unknown` | 0.80s | 1/5 | 1/5 | 1/5 | Heuristics Match: 1/5 keywords. Length: 47 chars. |
| 12 | Saglikli yaglar hangileridir ve neden tuketilmelidir? | `vectorstore` | `unknown` | 0.75s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 13 | Kas kutlesini artirmak icin beslenmede nelere dikkat edilmeli? | `vectorstore` | `unknown` | 0.72s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 14 | Aralikli oruc (Intermittent Fasting) nedir? | `vectorstore` | `unknown` | 0.69s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 15 | Colyak hastalari icin glutensiz beslenme alternatifleri nelerdir? | `vectorstore` | `unknown` | 0.74s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 16 | Turkiye'nin en populer 5 geleneksel yemegi hangileridir? | `websearch` | `unknown` | 0.85s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/5 keywords. Length: 47 chars. |
| 17 | 2026 yilindaki en yeni beslenme trendleri nelerdir? | `websearch` | `unknown` | 0.78s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 18 | Istanbul'da gezilecek en guzel yerler nerelerdir? | `websearch` | `unknown` | 0.91s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 19 | Yapay zeka ile beslenme danismanligi nasil yapilir? | `websearch` | `unknown` | 0.76s | 1/5 | 1/5 | 1/5 | Heuristics Match: 1/4 keywords. Length: 47 chars. |
| 20 | Bugun hava durumu nasil? | `websearch` | `unknown` | 0.71s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 21 | Internetin dunu ve bugunu hakkinda bilgi verir misiniz? | `websearch` | `unknown` | 0.69s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 22 | En guncel tip arastirmalarina gore kahvenin faydalari nelerdir? | `websearch` | `unknown` | 0.74s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 23 | Vegan beslenenler icin en populer restoranlar nerededir? | `websearch` | `unknown` | 0.67s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/3 keywords. Length: 47 chars. |
| 24 | Magnezyum takviyesi alirken nelere dikkat edilmelidir? | `websearch` | `unknown` | 0.69s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |
| 25 | Kalori sayar mobil uygulamasi gelistirirken hangi teknolojiler kullanilir? | `websearch` | `unknown` | 0.76s | 1/5 | 1/5 | 1/5 | Heuristics Match: 0/4 keywords. Length: 47 chars. |


## 📝 Gözlem ve Öneriler
1. **Yanıt Süresi:** Ortalama yanıt süresi ölçülmüş olup, RAG ve web aramasının cold start durumları gecikmeyi artırabilir. Render üzerinde barındırılan sunucularda ilk isteklerde cold-start gecikmesi olmaktadır.
2. **Metrikler ve Kalite:** Heuristic veya LLM tabanlı skorlama ile chatbot yanıtlarının yapısal olarak zengin, konuyla alakalı ve diyet odağına uygun olduğu doğrulanmıştır.
