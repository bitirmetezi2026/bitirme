import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# 150+ Popular Turkish Foods and Drinks
foods_data = [
    # Kahvaltılıklar (Breakfast)
    {"food_name": "Menemen", "calories_per_serving": 240.0, "protein": 12.0, "fat": 18.0, "carbs": 8.0, "serving_description": "1 Porsiyon (200g)", "category": "Kahvaltı"},
    {"food_name": "Sahanda Yumurta", "calories_per_serving": 150.0, "protein": 11.0, "fat": 12.0, "carbs": 0.6, "serving_description": "2 adet yumurta", "category": "Kahvaltı"},
    {"food_name": "Simit", "calories_per_serving": 320.0, "protein": 10.0, "fat": 8.0, "carbs": 58.0, "serving_description": "1 adet (100g)", "category": "Kahvaltı"},
    {"food_name": "Ezine Peyniri", "calories_per_serving": 93.0, "protein": 6.0, "fat": 7.5, "carbs": 0.5, "serving_description": "1 dilim (30g)", "category": "Kahvaltı"},
    {"food_name": "Siyah Zeytin", "calories_per_serving": 35.0, "protein": 0.3, "fat": 3.5, "carbs": 1.0, "serving_description": "5 adet (15g)", "category": "Kahvaltı"},
    {"food_name": "Yeşil Zeytin", "calories_per_serving": 25.0, "protein": 0.2, "fat": 2.5, "carbs": 0.8, "serving_description": "5 adet (15g)", "category": "Kahvaltı"},
    {"food_name": "Tereyağı", "calories_per_serving": 72.0, "protein": 0.1, "fat": 8.1, "carbs": 0.1, "serving_description": "1 tatlı kaşığı (10g)", "category": "Kahvaltı"},
    {"food_name": "Süzme Bal", "calories_per_serving": 64.0, "protein": 0.1, "fat": 0.0, "carbs": 17.0, "serving_description": "1 yemek kaşığı (20g)", "category": "Kahvaltı"},
    {"food_name": "Kaymak", "calories_per_serving": 120.0, "protein": 0.5, "fat": 13.0, "carbs": 0.8, "serving_description": "1 yemek kaşığı (20g)", "category": "Kahvaltı"},
    {"food_name": "Poğaça (Sade)", "calories_per_serving": 260.0, "protein": 5.0, "fat": 14.0, "carbs": 28.0, "serving_description": "1 adet (80g)", "category": "Kahvaltı"},
    {"food_name": "Sigara Böreği", "calories_per_serving": 85.0, "protein": 2.5, "fat": 5.0, "carbs": 8.0, "serving_description": "1 adet (30g)", "category": "Kahvaltı"},
    {"food_name": "Pancake", "calories_per_serving": 90.0, "protein": 2.5, "fat": 3.0, "carbs": 14.0, "serving_description": "1 adet orta boy", "category": "Kahvaltı"},
    {"food_name": "Haşlanmış Yumurta", "calories_per_serving": 75.0, "protein": 6.3, "fat": 5.3, "carbs": 0.6, "serving_description": "1 adet (50g)", "category": "Kahvaltı"},
    {"food_name": "Kaşar Peyniri", "calories_per_serving": 105.0, "protein": 8.0, "fat": 8.3, "carbs": 0.5, "serving_description": "1 dilim (30g)", "category": "Kahvaltı"},
    {"food_name": "Reçel (Vişne)", "calories_per_serving": 55.0, "protein": 0.1, "fat": 0.0, "carbs": 14.0, "serving_description": "1 tatlı kaşığı (20g)", "category": "Kahvaltı"},

    # Çorbalar (Soups)
    {"food_name": "Mercimek Çorbası", "calories_per_serving": 140.0, "protein": 8.0, "fat": 4.0, "carbs": 20.0, "serving_description": "1 kepçe (200ml)", "category": "Çorba"},
    {"food_name": "Ezogelin Çorbası", "calories_per_serving": 150.0, "protein": 7.0, "fat": 5.0, "carbs": 21.0, "serving_description": "1 kepçe (200ml)", "category": "Çorba"},
    {"food_name": "Tarhana Çorbası", "calories_per_serving": 120.0, "protein": 4.5, "fat": 3.5, "carbs": 18.0, "serving_description": "1 kepçe (200ml)", "category": "Çorba"},
    {"food_name": "Yayla Çorbası", "calories_per_serving": 135.0, "protein": 5.0, "fat": 6.0, "carbs": 16.0, "serving_description": "1 kepçe (200ml)", "category": "Çorba"},
    {"food_name": "Domates Çorbası", "calories_per_serving": 90.0, "protein": 2.0, "fat": 3.5, "carbs": 13.0, "serving_description": "1 kepçe (200ml)", "category": "Çorba"},
    {"food_name": "Kelle Paça Çorbası", "calories_per_serving": 220.0, "protein": 22.0, "fat": 14.0, "carbs": 1.0, "serving_description": "1 porsiyon (250ml)", "category": "Çorba"},
    {"food_name": "İşkembe Çorbası", "calories_per_serving": 180.0, "protein": 18.0, "fat": 11.0, "carbs": 2.0, "serving_description": "1 porsiyon (250ml)", "category": "Çorba"},
    {"food_name": "Tavuk Suyu Çorbası", "calories_per_serving": 110.0, "protein": 9.0, "fat": 5.0, "carbs": 8.0, "serving_description": "1 kepçe (200ml)", "category": "Çorba"},
    {"food_name": "Şehriye Çorbası", "calories_per_serving": 100.0, "protein": 3.0, "fat": 2.5, "carbs": 17.0, "serving_description": "1 kepçe (200ml)", "category": "Çorba"},

    # Kebaplar, Et ve Tavuk Yemekleri (Meats & Kebabs)
    {"food_name": "Adana Kebap", "calories_per_serving": 480.0, "protein": 32.0, "fat": 38.0, "carbs": 2.0, "serving_description": "1 porsiyon (150g)", "category": "Ana Yemek"},
    {"food_name": "Urfa Kebap", "calories_per_serving": 460.0, "protein": 32.0, "fat": 36.0, "carbs": 2.0, "serving_description": "1 porsiyon (150g)", "category": "Ana Yemek"},
    {"food_name": "İskender Kebap", "calories_per_serving": 750.0, "protein": 38.0, "fat": 48.0, "carbs": 42.0, "serving_description": "1 porsiyon (300g)", "category": "Ana Yemek"},
    {"food_name": "Lahmacun", "calories_per_serving": 220.0, "protein": 10.0, "fat": 8.0, "carbs": 27.0, "serving_description": "1 adet (80g)", "category": "Ana Yemek"},
    {"food_name": "Et Döner", "calories_per_serving": 320.0, "protein": 28.0, "fat": 22.0, "carbs": 1.5, "serving_description": "1 porsiyon (100g pilavsız/ekmeksiz)", "category": "Ana Yemek"},
    {"food_name": "Tavuk Döner", "calories_per_serving": 240.0, "protein": 24.0, "fat": 15.0, "carbs": 1.0, "serving_description": "1 porsiyon (100g pilavsız/ekmeksiz)", "category": "Ana Yemek"},
    {"food_name": "Izgara Köfte", "calories_per_serving": 280.0, "protein": 22.0, "fat": 20.0, "carbs": 4.0, "serving_description": "4 adet/1 porsiyon (120g)", "category": "Ana Yemek"},
    {"food_name": "Tavuk Şiş", "calories_per_serving": 210.0, "protein": 28.0, "fat": 12.0, "carbs": 1.0, "serving_description": "1 porsiyon (150g)", "category": "Ana Yemek"},
    {"food_name": "Kuzu Şiş", "calories_per_serving": 380.0, "protein": 30.0, "fat": 28.0, "carbs": 0.5, "serving_description": "1 porsiyon (150g)", "category": "Ana Yemek"},
    {"food_name": "Tavuk Göğsü (Izgara)", "calories_per_serving": 165.0, "protein": 31.0, "fat": 3.6, "carbs": 0.0, "serving_description": "1 porsiyon (150g)", "category": "Ana Yemek"},
    {"food_name": "Ali Nazik Kebap", "calories_per_serving": 420.0, "protein": 24.0, "fat": 32.0, "carbs": 8.0, "serving_description": "1 porsiyon (250g)", "category": "Ana Yemek"},
    {"food_name": "Hünkar Beğendi", "calories_per_serving": 450.0, "protein": 26.0, "fat": 34.0, "carbs": 11.0, "serving_description": "1 porsiyon (250g)", "category": "Ana Yemek"},
    {"food_name": "Karnıyarık", "calories_per_serving": 270.0, "protein": 12.0, "fat": 22.0, "carbs": 9.0, "serving_description": "1 adet/porsiyon (170g)", "category": "Ana Yemek"},
    {"food_name": "Fırında Somon", "calories_per_serving": 310.0, "protein": 32.0, "fat": 19.0, "carbs": 0.0, "serving_description": "1 porsiyon (150g)", "category": "Ana Yemek"},
    {"food_name": "Etli Ekmek", "calories_per_serving": 450.0, "protein": 22.0, "fat": 24.0, "carbs": 40.0, "serving_description": "1 porsiyon (180g)", "category": "Ana Yemek"},
    {"food_name": "Kuzu Pirzola", "calories_per_serving": 350.0, "protein": 26.0, "fat": 27.0, "carbs": 0.0, "serving_description": "3 adet (150g)", "category": "Ana Yemek"},
    {"food_name": "Tavuk Kanat (Izgara)", "calories_per_serving": 290.0, "protein": 22.0, "fat": 22.0, "carbs": 0.0, "serving_description": "5 adet (150g)", "category": "Ana Yemek"},
    {"food_name": "Kıymalı Pide", "calories_per_serving": 520.0, "protein": 24.0, "fat": 26.0, "carbs": 48.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Karışık Izgara", "calories_per_serving": 680.0, "protein": 48.0, "fat": 52.0, "carbs": 4.0, "serving_description": "1 porsiyon (300g)", "category": "Ana Yemek"},

    # Sebze ve Ev Yemekleri (Vegetable & Traditional Dishes)
    {"food_name": "Kuru Fasulye (Sade)", "calories_per_serving": 220.0, "protein": 11.0, "fat": 6.0, "carbs": 32.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Etli Kuru Fasulye", "calories_per_serving": 290.0, "protein": 18.0, "fat": 12.0, "carbs": 30.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Nohut Yemeği", "calories_per_serving": 210.0, "protein": 10.0, "fat": 5.0, "carbs": 33.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Taze Fasulye (Zeytinyağlı)", "calories_per_serving": 90.0, "protein": 2.0, "fat": 5.0, "carbs": 10.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Ispanak Yemeği", "calories_per_serving": 110.0, "protein": 4.0, "fat": 6.0, "carbs": 12.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Pırasa Yemeği", "calories_per_serving": 120.0, "protein": 2.5, "fat": 5.5, "carbs": 16.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Bamya Yemeği", "calories_per_serving": 85.0, "protein": 3.0, "fat": 4.5, "carbs": 11.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Kabak Mücver", "calories_per_serving": 145.0, "protein": 5.0, "fat": 8.0, "carbs": 14.0, "serving_description": "2 adet (100g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Yaprak Sarma (Zeytinyağlı)", "calories_per_serving": 180.0, "protein": 3.0, "fat": 7.0, "carbs": 27.0, "serving_description": "5 adet (100g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Biber Dolması (Kıymalı)", "calories_per_serving": 210.0, "protein": 10.0, "fat": 12.0, "carbs": 17.0, "serving_description": "1 adet (150g)", "category": "Ana Yemek"},
    {"food_name": "Biber Dolması (Zeytinyağlı)", "calories_per_serving": 170.0, "protein": 2.5, "fat": 6.0, "carbs": 28.0, "serving_description": "1 adet (150g)", "category": "Ana Yemek"},
    {"food_name": "İmambayıldı", "calories_per_serving": 190.0, "protein": 2.5, "fat": 14.0, "carbs": 15.0, "serving_description": "1 porsiyon (150g)", "category": "Ana Yemek"},
    {"food_name": "Türlü Yemeği", "calories_per_serving": 140.0, "protein": 4.0, "fat": 7.0, "carbs": 18.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Bezelye Yemeği (Etli)", "calories_per_serving": 220.0, "protein": 14.0, "fat": 9.0, "carbs": 22.0, "serving_description": "1 porsiyon (200g)", "category": "Ana Yemek"},
    {"food_name": "Mercimek Köftesi", "calories_per_serving": 70.0, "protein": 2.0, "fat": 2.5, "carbs": 10.5, "serving_description": "1 adet (35g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Kısır", "calories_per_serving": 180.0, "protein": 4.0, "fat": 7.0, "carbs": 26.0, "serving_description": "1 porsiyon (100g)", "category": "Meze/Ara Sıcak"},

    # Yan Ürünler, Pilavlar, Makarnalar (Sides, Rice, Pasta)
    {"food_name": "Pirinç Pilavı", "calories_per_serving": 280.0, "protein": 4.5, "fat": 7.5, "carbs": 50.0, "serving_description": "1 porsiyon (150g)", "category": "Yan Ürün"},
    {"food_name": "Bulgur Pilavı", "calories_per_serving": 210.0, "protein": 5.5, "fat": 4.0, "carbs": 38.0, "serving_description": "1 porsiyon (150g)", "category": "Yan Ürün"},
    {"food_name": "Makarna (Domates Soslu)", "calories_per_serving": 290.0, "protein": 8.5, "fat": 5.0, "carbs": 54.0, "serving_description": "1 porsiyon (180g)", "category": "Yan Ürün"},
    {"food_name": "Patates Kızartması", "calories_per_serving": 312.0, "protein": 3.4, "fat": 15.0, "carbs": 41.0, "serving_description": "1 porsiyon orta boy (100g)", "category": "Yan Ürün"},
    {"food_name": "Erişte", "calories_per_serving": 330.0, "protein": 10.0, "fat": 8.0, "carbs": 56.0, "serving_description": "1 porsiyon (150g)", "category": "Yan Ürün"},
    {"food_name": "Patates Püresi", "calories_per_serving": 160.0, "protein": 2.5, "fat": 6.0, "carbs": 25.0, "serving_description": "1 porsiyon (150g)", "category": "Yan Ürün"},

    # Mezeler ve Yoğurtlar (Appetizers & Dairy)
    {"food_name": "Yoğurt (Tam Yağlı)", "calories_per_serving": 130.0, "protein": 7.0, "fat": 7.5, "carbs": 9.0, "serving_description": "1 kase (200g)", "category": "Yan Ürün"},
    {"food_name": "Cacık", "calories_per_serving": 80.0, "protein": 4.0, "fat": 4.5, "carbs": 6.0, "serving_description": "1 kase (200g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Humus", "calories_per_serving": 170.0, "protein": 5.0, "fat": 10.0, "carbs": 16.0, "serving_description": "1 porsiyon (100g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Haydari", "calories_per_serving": 115.0, "protein": 4.5, "fat": 9.0, "carbs": 4.0, "serving_description": "1 porsiyon (100g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Şakşuka", "calories_per_serving": 140.0, "protein": 2.0, "fat": 10.0, "carbs": 11.0, "serving_description": "1 porsiyon (100g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Deniz Börülcesi", "calories_per_serving": 75.0, "protein": 1.5, "fat": 6.0, "carbs": 4.0, "serving_description": "1 porsiyon (100g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Muhammara", "calories_per_serving": 240.0, "protein": 4.0, "fat": 18.0, "carbs": 16.0, "serving_description": "1 porsiyon (100g)", "category": "Meze/Ara Sıcak"},
    {"food_name": "Rus Salatası", "calories_per_serving": 210.0, "protein": 3.0, "fat": 15.0, "carbs": 16.0, "serving_description": "1 porsiyon (100g)", "category": "Meze/Ara Sıcak"},

    # İçecekler (Beverages)
    {"food_name": "Siyah Çay (Şekersiz)", "calories_per_serving": 1.0, "protein": 0.0, "fat": 0.0, "carbs": 0.2, "serving_description": "1 ince belli bardak (100ml)", "category": "İçecek"},
    {"food_name": "Siyah Çay (1 Şekerli)", "calories_per_serving": 20.0, "protein": 0.0, "fat": 0.0, "carbs": 5.0, "serving_description": "1 ince belli bardak (100ml)", "category": "İçecek"},
    {"food_name": "Türk Kahvesi (Şekersiz)", "calories_per_serving": 2.0, "protein": 0.1, "fat": 0.1, "carbs": 0.2, "serving_description": "1 fincan (70ml)", "category": "İçecek"},
    {"food_name": "Türk Kahvesi (Orta)", "calories_per_serving": 22.0, "protein": 0.1, "fat": 0.1, "carbs": 5.2, "serving_description": "1 fincan (70ml)", "category": "İçecek"},
    {"food_name": "Ayran", "calories_per_serving": 76.0, "protein": 3.8, "fat": 4.0, "carbs": 6.0, "serving_description": "1 su bardağı (200ml)", "category": "İçecek"},
    {"food_name": "Limonata", "calories_per_serving": 90.0, "protein": 0.2, "fat": 0.1, "carbs": 22.0, "serving_description": "1 su bardağı (200ml)", "category": "İçecek"},
    {"food_name": "Şalgam Suyu", "calories_per_serving": 10.0, "protein": 0.5, "fat": 0.1, "carbs": 2.0, "serving_description": "1 su bardağı (200ml)", "category": "İçecek"},
    {"food_name": "Kola", "calories_per_serving": 90.0, "protein": 0.0, "fat": 0.0, "carbs": 22.5, "serving_description": "1 kutu (250ml)", "category": "İçecek"},
    {"food_name": "Kola Zero / Light", "calories_per_serving": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "serving_description": "1 kutu (250ml)", "category": "İçecek"},
    {"food_name": "Soda / Maden Suyu", "calories_per_serving": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "serving_description": "1 şişe (200ml)", "category": "İçecek"},
    {"food_name": "Meyve Suyu (Portakal)", "calories_per_serving": 90.0, "protein": 1.4, "fat": 0.2, "carbs": 21.0, "serving_description": "1 su bardağı (200ml)", "category": "İçecek"},
    {"food_name": "Süt (Yarım Yağlı)", "calories_per_serving": 94.0, "protein": 6.0, "fat": 3.0, "carbs": 9.4, "serving_description": "1 su bardağı (200ml)", "category": "İçecek"},

    # Tatlılar (Desserts)
    {"food_name": "Baklava (Fıstıklı)", "calories_per_serving": 330.0, "protein": 4.0, "fat": 18.0, "carbs": 38.0, "serving_description": "2 dilim (80g)", "category": "Tatlı"},
    {"food_name": "Sütlaç", "calories_per_serving": 270.0, "protein": 6.5, "fat": 5.0, "carbs": 50.0, "serving_description": "1 kase (200g)", "category": "Tatlı"},
    {"food_name": "Künefe", "calories_per_serving": 420.0, "protein": 8.0, "fat": 20.0, "carbs": 52.0, "serving_description": "1 porsiyon (120g)", "category": "Tatlı"},
    {"food_name": "Revani", "calories_per_serving": 350.0, "protein": 5.0, "fat": 10.0, "carbs": 60.0, "serving_description": "1 dilim (100g)", "category": "Tatlı"},
    {"food_name": "Şekerpare", "calories_per_serving": 280.0, "protein": 3.5, "fat": 9.0, "carbs": 46.0, "serving_description": "2 adet (80g)", "category": "Tatlı"},
    {"food_name": "Kazandibi", "calories_per_serving": 200.0, "protein": 4.5, "fat": 3.5, "carbs": 38.0, "serving_description": "1 porsiyon (150g)", "category": "Tatlı"},
    {"food_name": "Tavuk Göğsü (Tatlı)", "calories_per_serving": 180.0, "protein": 5.0, "fat": 3.0, "carbs": 34.0, "serving_description": "1 porsiyon (150g)", "category": "Tatlı"},
    {"food_name": "Güllaç", "calories_per_serving": 250.0, "protein": 5.5, "fat": 6.0, "carbs": 44.0, "serving_description": "1 porsiyon (150g)", "category": "Tatlı"},
    {"food_name": "Kemalpaşa Tatlısı", "calories_per_serving": 220.0, "protein": 3.0, "fat": 4.5, "carbs": 42.0, "serving_description": "3 adet (80g)", "category": "Tatlı"},
    {"food_name": "İrmik Helvası", "calories_per_serving": 310.0, "protein": 4.0, "fat": 11.0, "carbs": 49.0, "serving_description": "1 porsiyon (100g)", "category": "Tatlı"},

    # Meyveler (Fruits)
    {"food_name": "Elma", "calories_per_serving": 52.0, "protein": 0.3, "fat": 0.2, "carbs": 14.0, "serving_description": "1 adet orta boy (100g)", "category": "Meyve"},
    {"food_name": "Muz", "calories_per_serving": 89.0, "protein": 1.1, "fat": 0.3, "carbs": 23.0, "serving_description": "1 adet orta boy (100g)", "category": "Meyve"},
    {"food_name": "Mandalina", "calories_per_serving": 46.0, "protein": 0.6, "fat": 0.1, "carbs": 11.0, "serving_description": "1 adet orta boy (85g)", "category": "Meyve"},
    {"food_name": "Portakal", "calories_per_serving": 62.0, "protein": 1.2, "fat": 0.2, "carbs": 15.0, "serving_description": "1 adet orta boy (130g)", "category": "Meyve"},
    {"food_name": "Çilek", "calories_per_serving": 32.0, "protein": 0.7, "fat": 0.3, "carbs": 7.7, "serving_description": "1 porsiyon (100g)", "category": "Meyve"},
    {"food_name": "Karpuz", "calories_per_serving": 30.0, "protein": 0.6, "fat": 0.2, "carbs": 7.6, "serving_description": "1 porsiyon (100g)", "category": "Meyve"},
    {"food_name": "Kavun", "calories_per_serving": 36.0, "protein": 0.8, "fat": 0.2, "carbs": 8.0, "serving_description": "1 porsiyon (100g)", "category": "Meyve"},
    {"food_name": "Üzüm", "calories_per_serving": 69.0, "protein": 0.7, "fat": 0.2, "carbs": 18.0, "serving_description": "1 salkım ufak (100g)", "category": "Meyve"},
    {"food_name": "Şeftali", "calories_per_serving": 39.0, "protein": 0.9, "fat": 0.3, "carbs": 10.0, "serving_description": "1 adet orta boy (100g)", "category": "Meyve"},
    {"food_name": "Armut", "calories_per_serving": 57.0, "protein": 0.4, "fat": 0.1, "carbs": 15.0, "serving_description": "1 adet orta boy (100g)", "category": "Meyve"},

    # Kuruyemişler & Atıştırmalıklar (Nuts & Snacks)
    {"food_name": "Çiğ Badem", "calories_per_serving": 150.0, "protein": 5.5, "fat": 13.0, "carbs": 5.0, "serving_description": "1 avuç (25g)", "category": "Kuruyemiş"},
    {"food_name": "Ceviz İçi", "calories_per_serving": 165.0, "protein": 3.8, "fat": 16.0, "carbs": 3.5, "serving_description": "1 avuç (25g)", "category": "Kuruyemiş"},
    {"food_name": "Kavrulmuş Fındık", "calories_per_serving": 160.0, "protein": 3.7, "fat": 15.0, "carbs": 4.0, "serving_description": "1 avuç (25g)", "category": "Kuruyemiş"},
    {"food_name": "Antep Fıstığı", "calories_per_serving": 140.0, "protein": 5.0, "fat": 11.5, "carbs": 7.0, "serving_description": "1 avuç (25g)", "category": "Kuruyemiş"},
    {"food_name": "Sarı Leblebi", "calories_per_serving": 90.0, "protein": 5.0, "fat": 1.2, "carbs": 14.5, "serving_description": "1 avuç (25g)", "category": "Kuruyemiş"},
    {"food_name": "Patlamış Mısır", "calories_per_serving": 120.0, "protein": 3.0, "fat": 4.5, "carbs": 19.0, "serving_description": "1 porsiyon (30g/1 kase)", "category": "Atıştırmalık"},
    {"food_name": "Cips (Patates)", "calories_per_serving": 270.0, "protein": 3.0, "fat": 17.5, "carbs": 26.0, "serving_description": "1 ufak paket (50g)", "category": "Atıştırmalık"},
    {"food_name": "Bitter Çikolata", "calories_per_serving": 145.0, "protein": 2.0, "fat": 9.5, "carbs": 13.0, "serving_description": "3 kare (25g)", "category": "Atıştırmalık"},
    {"food_name": "Sütlü Çikolata", "calories_per_serving": 135.0, "protein": 1.8, "fat": 7.5, "carbs": 15.0, "serving_description": "3 kare (25g)", "category": "Atıştırmalık"}
]

def populate_db():
    print("Connecting to database...")
    db = SessionLocal()
    try:
        # Create table if it doesn't exist
        models.Base.metadata.create_all(bind=engine)
        
        count_added = 0
        count_updated = 0
        for item in foods_data:
            existing = db.query(models.FoodCalorie).filter(models.FoodCalorie.food_name == item["food_name"]).first()
            if existing:
                # Update existing values to keep it fresh
                existing.calories_per_serving = item["calories_per_serving"]
                existing.protein = item["protein"]
                existing.fat = item["fat"]
                existing.carbs = item["carbs"]
                existing.serving_description = item["serving_description"]
                existing.category = item["category"]
                count_updated += 1
            else:
                new_food = models.FoodCalorie(**item)
                db.add(new_food)
                count_added += 1
        db.commit()
        print(f"Success! Added {count_added} new foods, updated {count_updated} existing foods.")
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_db()
