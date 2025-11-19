import os
import base64
import json
import time
import sys # Komut satırı argümanlarını almak için
from google import genai
from google.genai import types
from tqdm import tqdm # İlerleme çubuğu için

# --- YAPILANDIRMA ---
try:
    client = genai.Client()
except Exception as e:
    print(f"HATA: Google GenAI istemcisi başlatılamadı. API anahtarını kontrol edin: {e}") 

ASSET_DIR = "."

def get_base64_image(image_path):
    """Görüntüyü Base64 formatına dönüştürür ve MIME tipini belirler."""
    try:
        with open(image_path, "rb") as f:
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                mime_type = 'image/jpeg'
            elif image_path.lower().endswith('.png'):
                mime_type = 'image/png'
            else:
                return None, None
                
            return base64.b64encode(f.read()).decode("utf-8"), mime_type
            
    except FileNotFoundError:
        print(f"HATA: Dosya bulunamadı - {image_path}")
        return None, None
    except Exception as e:
        print(f"Görüntü okuma hatası: {e}")
        return None, None

def process_asset(image_path):
    """Bir görüntü dosyasını Gemini'a gönderir ve yapılandırılmış etiketler alır."""
    base64_data, mime_type = get_base64_image(image_path)
    if not base64_data:
        return None

    # 1. Sisteme Talimat (System Instruction): Modelin rolünü tanımlar.
    system_prompt = (
        "Sen bir oyun geliştirme stüdyosunun yapay zeka varlık sınıflandırma uzmanısın. "
        "Görevin, girdi olarak verilen oyun varlığını analiz etmek ve çıktıyı verilen JSON şemasına göre oluşturmaktır. "
        "Detaylı, yaratıcı ve oyun geliştirme için uygun etiketler kullan. Dosya adlarını doğru şekilde koru."
    )

    # 2. Kullanıcı Sorgusu (User Query): Modelden beklenen görev.
    user_query = (
        "Lütfen bu oyun varlığını analiz et. Hangi kategoriye ait olduğunu, ana temanın ne olduğunu "
        "ve oyun geliştiriciler için faydalı olabilecek üç ek etiket (metadata) ver."
    )

    # 3. Yapılandırılmış Çıktı Şeması (Schema)
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "filename": types.Schema(type=types.Type.STRING, description="Analiz edilen dosyanın adı."),
            "category": types.Schema(type=types.Type.STRING, description="Varlığın ana kategorisi (örn: 'Character', 'Background', 'UI Icon', 'Environment Object')."),
            "main_theme": types.Schema(type=types.Type.STRING, description="Varlığın temel teması ve stili (örn: 'Gotik Fantazi', 'Pixel Art', 'Sci-Fi Minimalist')."),
            "additional_tags": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="Oyun geliştirme için önemli 3 adet ek etiket (örn: 'Düşük Poligon', 'Animasyon Gerektirir', 'Yüksek Kontrast').")
        },
        required=["filename", "category", "main_theme", "additional_tags"]
    )

    # 4. API İstek Gövdesi (Payload) - Sürüm Uyumlu Çözüm
    contents = [
        {"text": user_query}, # Sürüm uyumluluğu için Part.from_text() yerine dict kullandık
        types.Part.from_bytes(data=base64_data, mime_type=mime_type)
    ]

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=response_schema
            )
        )

        json_output = json.loads(response.text)
        return json_output

    except Exception as e:
        error_message = f"API Çağrısı Başarısız: {e}"
        if 'response' in locals() and hasattr(response, 'text') and response.text:
             error_message += f"\nAPI Ham Yanıtı: {response.text[:200]}..."
        # Hata mesajı, tqdm ilerleme çubuğunun hemen altına yazılır.
        tqdm.write(f"!!! {os.path.basename(image_path)} İşlenemedi. Hata: {error_message}")
        return None

def main():
    """Ana program akışı."""
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("HATA: GEMINI_API_KEY ortam değişkeni tanımlı değil. Lütfen 'export GEMINI_API_KEY=\"AIza...\"' komutunu çalıştırın.")
        return

    # Resim dosyalarını (mevcut klasörde) listeleme
    asset_files = [f for f in os.listdir(ASSET_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not asset_files:
        print(f"\nİşlenecek resim dosyası (.png, .jpg) bulunamadı. Lütfen '{os.path.abspath(ASSET_DIR)}' içine dosya ekleyin.")
        return

    # --- YENİ ÖZELLİK: ETİKET FİLTRELEME ARGÜMANI ---
    filter_tag = None
    if len(sys.argv) > 1:
        # Komut satırındaki ilk argümanı filtre etiketi olarak al
        filter_tag = sys.argv[1].strip()
        print(f"\n[Filtreleme Etiketi Belirlendi: '{filter_tag}']")

    results = []
    print("\n--- Generative AI Varlık Sınıflandırma Başlatılıyor ---")

    MAX_RETRIES = 3
    # YENİ ÖZELLİK: tqdm ile ilerleme çubuğu ekleniyor
    for filename in tqdm(asset_files, desc="Varlıklar İşleniyor"):
        for attempt in range(MAX_RETRIES):
            full_path = os.path.join(ASSET_DIR, filename) 
            result = process_asset(full_path)
            
            if result:
                results.append(result)
                break
            elif attempt == MAX_RETRIES - 1:
                tqdm.write(f"!!! {filename} dosyası maksimum denemeye rağmen işlenemedi. Atlanıyor.")
                
            time.sleep(1) # API çağrıları arasında kısa bir bekleme

    print("\n--- İşleme Tamamlandı ---")
    
    if results:
        # YENİ ÖZELLİK: SONUÇLARI JSON DOSYASINA KAYDETME
        output_filepath = 'asset_classification_results.json'
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                # ensure_ascii=False Türkçe karakterlerin bozulmasını engeller
                json.dump(results, f, indent=4, ensure_ascii=False)
            print(f"\n✅ Tüm {len(results)} sonuç başarıyla '{output_filepath}' dosyasına kaydedildi.")
        except Exception as e:
            print(f"HATA: Sonuçlar dosyaya yazılamadı: {e}")

        # YENİ ÖZELLİK: FİLTRELENMİŞ SONUÇLARI GÖSTERME
        if filter_tag:
            # Etiketi, kategori veya ana temayı içerenleri bul
            filtered_results = [
                r for r in results 
                if (filter_tag in r.get("additional_tags", []) or 
                    filter_tag.lower() in r.get("category", "").lower() or 
                    filter_tag.lower() in r.get("main_theme", "").lower())
            ]
            
            print(f"\n--- FİLTRELENMİŞ SONUÇLAR ({len(filtered_results)} Adet) ---")
            if filtered_results:
                print(json.dumps(filtered_results, indent=4, ensure_ascii=False))
            else:
                print(f"'{filter_tag}' etiketi, kategori veya temasıyla eşleşen hiçbir varlık bulunamadı.")
        else:
            # Filtre yoksa, dosyaya kaydedilen tüm sonuçları yazdır
            print("\n--- TÜM İŞLENEN SONUÇLAR (Filtresiz) ---")
            print(json.dumps(results, indent=4, ensure_ascii=False))


        print("\n--- CV GÜÇLENDİRME MADDESİ ---")
        print("Bu projeyi CV'nizdeki AI/MLOps kısmına şöyle ekleyebilirsiniz:")
        print("\n* **Generative AI Asset Classification:** Developed a Python tool leveraging the Gemini Vision API and **Structured JSON Schema** to automatically categorize and generate production metadata (theme, style, tags) for thousands of game assets, demonstrating proficiency in **GenAI for asset pipeline automation** and **MLOps discipline**.")


if __name__ == '__main__':
    main()