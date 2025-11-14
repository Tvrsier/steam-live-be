# Steam Live Dashboard – Backend

Backend del progetto **Steam Live Dashboard**, sviluppato in **Python + FastAPI**.
Il backend gestisce l’aggregazione e l’aggiornamento dei dati Steam, esportandoli in un JSON statico
che il frontend può leggere localmente o tramite Amazon S3.

## 🚀 Features

- Backend veloce basato su **FastAPI**
- Full type-hints + **mypy** con configurazione strict
- Storage astratto:
  - `LocalStorage` → salva su disco
  - `S3Storage` → salva su Amazon S3 tramite `mypy-boto3-s3`
- Modelli dati basati su Pydantic
- Job di aggiornamento che genera un file JSON statico
- Frontend che legge sempre e solo un file (locale o S3)

---

## 🛠️ Setup

### Creazione ambiente virtuale

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Installazione dipendenze

```bash
pip install -r requirements.txt
```

---

## ▶️ Avvio FastAPI

```bash
uvicorn app.main:app --reload
```

Endpoint utile (solo in dev):

- `GET /steam-data` → ritorna il JSON generato

---

## 🔧 Configurazione (`.env`)

```
STORAGE_BACKEND=local
LOCAL_JSON_PATH=data/steam_dashboard.json

S3_BUCKET=nome-bucket
S3_KEY=steam-live/steam_dashboard.json
AWS_REGION=eu-central-1
```

---

## 📦 Job: aggiornamento dati Steam

```bash
python update_steam_data.py
```

Il job:

1. integra i dati da Steam API  
2. li aggrega  
3. salva il JSON localmente o su S3  

---

## 🧪 Controllo tipi

```bash
mypy .
```

---

## 📌 Roadmap

- Implementazione completa Steam Web API
- Aggregazione reale (Top, Trending, On Sale)
- Supporto regioni per i prezzi
- Upload S3 ottimizzato
- Pipeline CI/CD per job periodico
- Test automatizzati (pytest)
