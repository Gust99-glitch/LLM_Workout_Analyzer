 
##import openai 
from openai import OpenAI
import os
import json
import pdfplumber
from datetime import datetime
from supabase import create_client
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# -------------------------
# 1. Extractor (PDF ➜ Blob)
# -------------------------
pdf_path = "/Users/gustave/Downloads/LLM PRACTICE/military_pdf.pdf"
raw_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            raw_text += text + "\n"

os.makedirs("data", exist_ok=True)
with open("data/raw_blob.txt", "w") as f:
    f.write(raw_text)

print("✅ PDF extracted and saved to data/raw_blob.txt")

# -------------------------
# 2. Structurer (Blob ➜ JSON)
# -------------------------
prompt = f"""
You are a data structurer.
Parse the following workout program into valid JSON with this schema:

[
  {{
    "id": int,
    "day": str,
    "title": str,
    "workout": str,
    "extracted_at": str
  }}
]

Text:
{raw_text}
"""
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that outputs ONLY JSON — no text, no explanations."},
        {"role": "user", "content": prompt}
    ],
    temperature=0
)

raw_output = response.choices[0].message.content.strip()

# Debug: Save LLM output to check what it actually returns
with open("data/llm_output.txt", "w") as f:
    f.write(raw_output)

try:
    workouts = json.loads(raw_output)
except json.JSONDecodeError:
    print("❌ Invalid JSON from LLM — check data/llm_output.txt")
    workouts = []

print(f"📋 Collected {len(workouts)} workouts")

# -------------------------
# 3. Loader (JSON ➜ Supabase)
# --------------------------
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

if len(workouts) == 0:
    print("⚠️ No workouts to insert — check JSON output above.")
else:
    if not workouts:
        workouts = [{
            "id": 1,
            "day": "N/A",
            "title": "No Data",
            "workout": "Could not extract workouts",
            "extracted_at": datetime.utcnow().isoformat()
        }]
    
    df = pd.DataFrame(workouts)

    # Ensure extracted_at column exists
    if "extracted_at" not in df.columns:
        df["extracted_at"] = datetime.utcnow().isoformat()

    
# Removed misplaced except block
# -------------------------
# 4. Verify Insert (Read Back)
# -------------------------
try:
    # Drop the 'id' column so Supabase auto-generates it
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    data = df.to_dict(orient="records")
    print(f"\n📦 Preparing to insert {len(data)} rows...")

    result = supabase.table("workouts").upsert(data).execute()
    print("✅ Inserted workouts into Supabase")
except Exception as e:
    print(f"❌ Supabase insert error: {e}")
try:
    result = supabase.table("workouts").select("*").order("id", desc=True).limit(5).execute()
    rows = result.data
    print("\n📌 Last 5 workouts in Supabase:")
    for r in rows:
        print(f"ID: {r['id']}, Day: {r['day']}, Title: {r['title']}, Extracted At: {r['extracted_at']}")
except Exception as e:
    print(f"❌ Error fetching workouts from Supabase: {e}")
finally:
    print("🔑 OpenAI Key Loaded:", os.getenv("OPENAI_API_KEY")[:8] + "...")

# -------------------------------
# 5. Manual JSON Upload to Supabase
# -------------------------------
json_path = "workouts.json"

try:
    with open(json_path, "r") as f:
        workouts = json.load(f)

    # Convert to DataFrame and drop ID column
    df = pd.DataFrame(workouts)
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    data = df.to_dict(orient="records")
    print(f"\n📦 Preparing to insert {len(data)} rows...")

    # Insert into Supabase
    result = supabase.table("workouts").upsert(data).execute()
    print("✅ Uploaded workouts to Supabase successfully!")

    # Verify: read back from Supabase
    result = supabase.table("workouts").select("*").order("id", desc=True).limit(5).execute()
    rows = result.data
    print("\n📌 Last 5 workouts in Supabase:")
    for r in rows:
        print(f"🏋️‍♂️ Day: {r['day']}, Title: {r['title']}, Workout: {r['workout']}")
except Exception as e:
    print(f"❌ Error uploading JSON to Supabase: {e}")