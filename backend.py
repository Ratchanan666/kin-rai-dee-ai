import pandas as pd
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"

def load_data():
    try:
        file_path = "menu.csv"
        df = pd.read_csv(
            file_path,
            encoding="utf-8-sig",
            on_bad_lines="skip"
        )
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

def recommend_menu(user_input, df):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        menu_json = df.to_dict(orient="records")

        prompt = f"""
You are a Thai food recommendation AI.

User request:
"{user_input}"

Menu data:
{json.dumps(menu_json, ensure_ascii=False)}

Rules:
- Only recommend food from the menu data
- Choose the BEST 3 items
- Must match user intent
- Return exact name from dataset
- DO NOT answer anything outside food domain

IMPORTANT:
- If the request is NOT about food, return:
{{
  "recommendations": []
}}

Return ONLY JSON:
{{
  "recommendations": [
    {{
      "name": "..."
    }}
  ]
}}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "")
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}