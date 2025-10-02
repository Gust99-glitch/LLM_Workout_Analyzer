# 🧠 Military Fitness Workout Analyzer  

### 🧩 Overview  
This project uses **Large Language Models (LLMs)** to extract, clean, and structure text data from a military fitness PDF into a JSON format — then stores it in **Supabase** and displays it in a **Streamlit dashboard** deployed on **Modal**.  

It demonstrates a full modern data pipeline:
- PDF → Text extraction (`pdfplumber`)
- Text → Structured JSON (OpenAI GPT-4o-mini)
- JSON → Database (Supabase)
- Database → Web Dashboard (Streamlit on Modal)

---

### ⚙️ Tech Stack  
| Component | Tool |
|------------|------|
| **Language Model** | OpenAI GPT-4o-mini |
| **Data Extraction** | pdfplumber |
| **Database** | Supabase |
| **Frontend** | Streamlit |
| **Deployment** | Modal |
| **Environment Management** | dotenv + .gitignore |

---

### 🧾 Workflow Summary  

#### 1️⃣ **Extractor (PDF → Text)**  
Extracted text from a 48-page *Military Fitness PDF* using `pdfplumber` and saved the raw data to `data/raw_blob.txt`.

#### 2️⃣ **Structurer (Text → JSON)**  
Prompted OpenAI GPT-4o-mini to transform the unstructured text into structured JSON with fields:
```json
{
  "day": "Day 1",
  "title": "Beginner Workout",
  "workout": "Walk/run/bike - 15:00, Pushups - 5 reps, Crunches - 5 reps",
  "extracted_at": "2023-10-01T00:00:00Z"
}
