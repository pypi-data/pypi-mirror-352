# 🤖 AI Models Scrapers & Manager

Kompletny zestaw skryptów do pobierania, wyszukiwania i zarządzania modelami AI z Ollama i HuggingFace Hub.

## 📦 Zawartość

- **`OllamaModelsScraper.py`** - Scraper modeli z Ollama Library
- **`HuggingFaceModelsScraper.py`** - Scraper modeli z HuggingFace Hub
- **`UnifiedModelsManager.py`** - Jednolity manager do wyszukiwania i zarządzania

## 🚀 Szybki Start

### 1. Instalacja Zależności

```bash
pip install requests beautifulsoup4 lxml
```

### 2. Pobranie Modeli z Ollama

```bash
# Pobierz wszystkie modele
python OllamaModelsScraper.py --output ollama_models.json

# Pobierz z detalami (wolniej)
python OllamaModelsScraper.py --detailed --output ollama_detailed.json

# Wyszukaj konkretny model
python OllamaModelsScraper.py --search "bielik" --category "chat"
```

### 3. Pobranie Modeli z HuggingFace

```bash
# Pobierz modele kompatybilne z Ollama
python HuggingFaceModelsScraper.py --ollama-only --limit 5000 --output hf_ollama_models.json

# Pobierz wszystkie modele (duży plik!)
python HuggingFaceModelsScraper.py --limit 10000 --output hf_all_models.json

# Wyszukaj modele
python HuggingFaceModelsScraper.py --search "polish" --task "text-generation"

# Użyj tokena HF dla lepszych limitów
python HuggingFaceModelsScraper.py --use-token --ollama-only
```

### 4. Zarządzanie Modelami

```bash
# Załaduj i wyświetl podsumowanie
python UnifiedModelsManager.py

# Wyszukaj modele
python UnifiedModelsManager.py --search "bielik" --local-only

# Rekomendacje dla konkretnego przypadku
python UnifiedModelsManager.py --recommend polish

# Generuj skrypt instalacji
python UnifiedModelsManager.py --recommend coding --install-script install_coding.sh
```

## 📋 Szczegółowe Użycie

### Ollama Scraper

```bash
# Wszystkie opcje
python OllamaModelsScraper.py \
    --output ollama_models.json \
    --detailed \
    --search "text-generation" \
    --category "embedding"

# Przykładowe kategorie: vision, code, embedding, tools, multimodal
```

### HuggingFace Scraper

```bash
# Zaawansowane filtrowanie
python HuggingFaceModelsScraper.py \
    --output hf_models.json \
    --limit 5000 \
    --search "conversational" \
    --task "text-generation" \
    --language "pl" \
    --ollama-only \
    --detailed

# Dostępne taski: text-generation, conversational, feature-extraction, 
# sentence-similarity, image-to-text, visual-question-answering
```

### Unified Manager

```bash
# Wyszukiwanie zaawansowane
python UnifiedModelsManager.py \
    --search "polish" \
    --source "huggingface" \
    --task "text-generation" \
    --local-only \
    --min-downloads 1000 \
    --max-size 5.0 \
    --limit 20

# Rekomendacje
python UnifiedModelsManager.py \
    --recommend coding \
    --export coding_models.json \
    --format json \
    --install-script install_coding.sh

# Dostępne rekomendacje: general, coding, embedding, polish, small, vision
```

## 📊 Formaty Eksportu

### JSON (domyślny)
```json
{
  "source": "ollama.com",
  "scraped_at": "2025-01-29T12:00:00",
  "total_models": 150,
  "models": [
    {
      "name": "llama3.2",
      "url": "https://ollama.com/library/llama3.2",
      "pulls": "5.3M",
      "size": "4.7GB",
      "description": "Meta's latest model...",
      "ollama_command": "ollama pull llama3.2",
      "local_ready": true
    }
  ]
}
```

### CSV
```bash
python UnifiedModelsManager.py --search "bielik" --export models.csv --format csv
```

### Markdown
```bash
python UnifiedModelsManager.py --recommend polish --export polish_models.md --format md
```

## 🔧 Przykłady Użycia

### Znajdź Polskie Modele

```bash
# Wyszukaj wszystkie polskie modele
python UnifiedModelsManager.py \
    --search "polish" \
    --local-only \
    --export polish_models.json

# Rekomendacje dla polskiego
python UnifiedModelsManager.py \
    --recommend polish \
    --install-script install_polish.sh
```

### Modele do Kodowania

```bash
# Znajdź modele do kodowania
python UnifiedModelsManager.py \
    --search "code" \
    --task "text-generation" \
    --max-size 10 \
    --min-downloads 5000

# Lub użyj rekomendacji
python UnifiedModelsManager.py --recommend coding
```

### Małe Modele (Edge Computing)

```bash
# Modele < 3GB dla edge computing
python UnifiedModelsManager.py \
    --max-size 3.0 \
    --local-only \
    --min-downloads 1000 \
    --export small_models.json

# Rekomendacje małych modeli
python UnifiedModelsManager.py --recommend small
```

### Modele Multimodalne

```bash
# Znajdź modele vision/multimodal
python HuggingFaceModelsScraper.py \
    --task "image-to-text" \
    --ollama-only \
    --output vision_models.json

python UnifiedModelsManager.py --recommend vision
```

## 🚀 Generowanie Skryptów Instalacji

Manager automatycznie generuje skrypty bash do instalacji:

```bash
# Generuj skrypt dla polskich modeli
python UnifiedModelsManager.py \
    --recommend polish \
    --install-script install_polish_models.sh

# Uruchom skrypt
chmod +x install_polish_models.sh
./install_polish_models.sh
```

Przykładowy wygenerowany skrypt:
```bash
#!/bin/bash
echo '🚀 Installing selected AI models...'

echo 'Installing SpeakLeash/bielik-11b-v2.3-instruct...'
ollama pull SpeakLeash/bielik-11b-v2.3-instruct:Q4_K_M

echo '✅ Model installation completed!'
```

## 📈 Statystyki i Analiza

### Wyświetl Podsumowanie
```bash
python UnifiedModelsManager.py
```

Przykładowy output:
```
📊 MODELS SUMMARY:
Total models: 2847
Ollama models: 156
HuggingFace models: 2691
Ready for local use: 234

📋 Top tasks:
  text-generation: 1456
  feature-extraction: 445
  conversational: 234
  image-to-text: 123
```

## 🔍 Zaawansowane Wyszukiwanie

### Operatory Wyszukiwania

```bash
# Wyszukaj modele z konkretną nazwą
python UnifiedModelsManager.py --search "llama"

# Kombinuj filtry
python UnifiedModelsManager.py \
    --search "instruct" \
    --source "ollama" \
    --max-size 8.0 \
    --min-downloads 1000

# Tylko modele gotowe do lokalnego użycia
python UnifiedModelsManager.py \
    --local-only \
    --task "text-generation"
```

### Sortowanie i Limity

```bash
# Pokaż top 10 najpopularniejszych modeli
python UnifiedModelsManager.py \
    --min-downloads 10000 \
    --limit 10

# Małe modele posortowane według popularności
python UnifiedModelsManager.py \
    --max-size 2.0 \
    --min-downloads 1000 \
    --limit 20
```

## 🛠️ Integracja z WronAI

### Znajdź Modele Idealne dla Edge Computing

```bash
# Modele < 2GB dla mesh edge computing
python UnifiedModelsManager.py \
    --max-size 2.0 \
    --local-only \
    --task "text-generation" \
    --export wronai_edge_models.json \
    --install-script install_wronai_models.sh

# Rekomendacje dla małych modeli
python UnifiedModelsManager.py \
    --recommend small \
    --max-size 1.5 \
    --export wronai_tiny_models.json
```

### Pipeline dla WronAI

```bash
# 1. Pobierz kompatybilne modele
python HuggingFaceModelsScraper.py --ollama-only --limit 5000

# 2. Znajdź idealne dla edge
python UnifiedModelsManager.py \
    --max-size 3.0 \
    --local-only \
    --min-downloads 500 \
    --export wronai_models.json

# 3. Generuj skrypt instalacji
python UnifiedModelsManager.py \
    --hf-file huggingface_models.json \
    --max-size 3.0 \
    --local-only \
    --install-script wronai_install.sh
```

## 📝 Struktura Danych

### Model Ollama
```json
{
  "name": "llama3.2",
  "url": "https://ollama.com/library/llama3.2",
  "pulls": "5.3M",
  "size": "4.7GB",
  "updated": "1 month ago",
  "description": "Meta's latest model",
  "tags": ["text-generation", "chat"],
  "source": "ollama",
  "ollama_command": "ollama pull llama3.2",
  "availability": ["ollama"],
  "local_ready": true,
  "scraped_at": "2025-01-29 12:00:00"
}
```

### Model HuggingFace
```json
{
  "id": "microsoft/DialoGPT-medium",
  "name": "microsoft/DialoGPT-medium",
  "author": "microsoft",
  "url": "https://huggingface.co/microsoft/DialoGPT-medium",
  "downloads": 234567,
  "likes": 145,
  "pipeline_tag": "conversational",
  "tags": ["pytorch", "gpt2", "conversational"],
  "source": "huggingface",
  "ollama_compatible": true,
  "gguf_available": false,
  "recommended_for_ollama": false,
  "availability": ["huggingface", "convertible_to_ollama"],
  "local_ready": false,
  "ollama_import_command": "# May require conversion to GGUF format first"
}
```

## 🔄 Automatyzacja i Cron Jobs

### Codzienne Aktualizacje

```bash
# Dodaj do crontaba (crontab -e)
# Codziennie o 2:00 AM
0 2 * * * /usr/bin/python3 /path/to/OllamaModelsScraper.py --output /data/ollama_models.json
0 3 * * * /usr/bin/python3 /path/to/HuggingFaceModelsScraper.py --ollama-only --output /data/hf_models.json
```

### Monitoring Nowych Modeli

```bash
#!/bin/bash
# check_new_models.sh

# Sprawdź nowe modele polskie
python3 UnifiedModelsManager.py \
    --search "polish" \
    --min-downloads 100 \
    --local-only \
    --export new_polish_models.json

# Wyślij notyfikację jeśli są nowe
if [ -s new_polish_models.json ]; then
    echo "Nowe polskie modele dostępne!" | mail -s "WronAI: Nowe modele" admin@example.com
fi
```

## 🐛 Rozwiązywanie Problemów

### Błędy Rate Limiting

```bash
# Dla HuggingFace - użyj tokena
python HuggingFaceModelsScraper.py --use-token --limit 1000

# Dodaj opóźnienia między requestami
# Edytuj time.sleep() w skryptach
```

### Błędy Parsowania

```bash
# Sprawdź logi
python OllamaModelsScraper.py --search "test" 2>&1 | tee scraper.log

# Debugowanie konkretnego modelu
python UnifiedModelsManager.py --search "exact_model_name"
```

### Problemy z Pamięcią

```bash
# Ograicz liczbę modeli
python HuggingFaceModelsScraper.py --limit 1000 --ollama-only

# Wyłącz detailed mode
python OllamaModelsScraper.py --output models.json  # bez --detailed
```

## 📊 Przykładowe Wyniki

### Top Polskie Modele
```bash
$ python UnifiedModelsManager.py --recommend polish

🎯 RECOMMENDATIONS FOR 'POLISH':
1. SpeakLeash/bielik-11b-v2.3-instruct ✅ (Score: 25.4)
   Source: ollama, Task: text-generation
   Downloads: 1600, Size: 6.7GB

2. speakleash/Bielik-7B-Instruct-v0.1 ✅ (Score: 22.1)
   Source: huggingface, Task: text-generation
   Downloads: 15670, Size: Unknown
```

### Top Modele do Kodowania
```bash
$ python UnifiedModelsManager.py --recommend coding --limit 5

🎯 RECOMMENDATIONS FOR 'CODING':
1. codellama:13b ✅ (Score: 28.9)
2. codegemma:latest ✅ (Score: 26.5)
3. deepseek-coder:6.7b ✅ (Score: 24.2)
4. starcoder2:15b ✅ (Score: 22.8)
5. granite-code:8b ✅ (Score: 21.4)
```

## 🔗 Integracje

### API Endpoints

Użyj wygenerowanych danych w swoich aplikacjach:

```python
import json
import requests

# Załaduj dane modeli
with open('ollama_models.json') as f:
    models = json.load(f)

# Znajdź model
def find_model(name):
    for model in models['models']:
        if name.lower() in model['name'].lower():
            return model
    return None

# Użyj w aplikacji
bielik = find_model('bielik')
if bielik:
    print(f"Install: {bielik['ollama_command']}")
```

### Docker Integration

```dockerfile
FROM python:3.9-slim

COPY OllamaModelsScraper.py HuggingFaceModelsScraper.py UnifiedModelsManager.py ./
RUN pip install requests beautifulsoup4

# Scrape daily
RUN echo "0 2 * * * python OllamaModelsScraper.py" >> /etc/crontab
```

## 🎯 Roadmap

### Planowane Funkcje

- [ ] **GUI Interface** - Graficzny interface do przeglądania modeli
- [ ] **Model Benchmarks** - Automatyczne benchmarki wydajności
- [ ] **Docker Support** - Bezpośrednia integracja z Docker
- [ ] **Model Conversion** - Automatyczna konwersja formatów
- [ ] **API Server** - REST API do zarządzania modelami
- [ ] **Update Notifications** - Powiadomienia o nowych modelach
- [ ] **Performance Metrics** - Metryki wydajności modeli
- [ ] **Cost Calculator** - Kalkulator kosztów inference

### Przyszłe Integracje

- **Kubernetes** - Deployment modeli w K8s
- **AWS/GCP/Azure** - Cloud deployment
- **Prometheus** - Monitoring i metryki
- **Grafana** - Dashboardy wydajności

## 📖 Więcej Informacji

### Dokumentacja API

- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [HuggingFace Hub API](https://huggingface.co/docs/hub/api)

### Przydatne Linki

- [Ollama Library](https://ollama.com/library)
- [HuggingFace Models](https://huggingface.co/models)
- [GGUF Format](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)


