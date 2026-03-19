from fastapi import FastAPI
from scoring import calculate_score
import requests
import sqlite3
import os
from datetime import datetime
from groq import Groq
import json
import csv

DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            name TEXT,
            brand TEXT,
            grade TEXT,
            score INTEGER,
            scanned_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_scan(barcode, name, brand, grade, score):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO scan_history (barcode, name, brand, grade, score, scanned_at) VALUES (?,?,?,?,?,?)",
        (barcode, name, brand, grade, score, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT barcode, name, brand, grade, score, scanned_at FROM scan_history ORDER BY id DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [
        {"barcode": r[0], "name": r[1], "brand": r[2],
        "grade": r[3], "score": r[4], "scanned_at": r[5]}
        for r in rows
    ]

init_db()

app = FastAPI()

# Load Indian products CSV into memory at startup
INDIAN_PRODUCTS = {}

def load_indian_products():
    csv_path = os.path.join(os.path.dirname(__file__), "indian_products.csv")
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                INDIAN_PRODUCTS[row['barcode'].strip()] = row
        print(f"Loaded {len(INDIAN_PRODUCTS)} Indian products from CSV")
    except Exception as e:
        print(f"CSV load error: {e}")

load_indian_products()

def fetch_from_indian_csv(barcode: str) -> dict:
    product = INDIAN_PRODUCTS.get(barcode.strip())
    if product:
        return {
            "product_name": product.get("product_name", ""),
            "brands": product.get("brand", ""),
            "packaging": product.get("packaging", ""),
            "categories": product.get("category", ""),
            "ingredients_text": product.get("ingredients_text", ""),
            "labels": product.get("labels", ""),
            "nutriscore_grade": product.get("nutriscore_grade", ""),
            "packaging_tags": [],
            "_source": "indian_csv"
        }
    return {}

def fetch_from_openfoodfacts(barcode: str) -> dict:
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("status") == 1:
            product = data["product"]
            if product.get("product_name"):
                product["_source"] = "food"
                return product
    except Exception:
        pass
    return {}

def fetch_from_openbeautyfacts(barcode: str) -> dict:
    url = f"https://world.openbeautyfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("status") == 1:
            product = data["product"]
            if product.get("product_name"):
                product["_source"] = "beauty"
                return product
    except Exception:
        pass
    return {}

def fetch_from_openproductsfacts(barcode: str) -> dict:
    url = f"https://world.openproductsfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("status") == 1:
            product = data["product"]
            if product.get("product_name"):
                product["_source"] = "products"
                return product
    except Exception:
        pass
    return {}

def fetch_from_openpetfoodfacts(barcode: str) -> dict:
    url = f"https://world.openpetfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("status") == 1:
            product = data["product"]
            if product.get("product_name"):
                product["_source"] = "petfood"
                return product
    except Exception:
        pass
    return {}

def fetch_product(barcode: str) -> dict:
    # Check Indian CSV first (fastest, most relevant)
    product = fetch_from_indian_csv(barcode)
    if not product:
        product = fetch_from_openfoodfacts(barcode)
    if not product:
        product = fetch_from_openbeautyfacts(barcode)
    if not product:
        product = fetch_from_openproductsfacts(barcode)
    if not product:
        product = fetch_from_openpetfoodfacts(barcode)
    return product

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_alternative(product: dict) -> dict:
    product_name = product.get("product_name") or "Unknown Product"
    brand = product.get("brands") or "Unknown Brand"
    packaging = product.get("packaging") or "Unknown packaging"
    categories = product.get("categories") or "Unknown category"
    ingredients = product.get("ingredients_text") or "Unknown ingredients"

    try:
        chat_completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an eco-friendly product advisor for Indian consumers. Always respond with valid JSON only, no markdown, no extra text."
                },
                {
                    "role": "user",
                    "content": f"""A user scanned this product:
- Name: {product_name}
- Brand: {brand}
- Packaging: {packaging}
- Categories: {categories}
- Ingredients (first 200 chars): {ingredients[:200]}

Suggest ONE specific eco-friendly alternative available in India.
Respond ONLY in this exact JSON format with no other text:
{{
    "name": "product name",
    "brand": "brand name",
    "reason": "one sentence why it is more eco-friendly",
    "grade": "A",
    "price": "XX-XX",
    "available_at": "where to buy in India"
}}"""
                }
            ],
            temperature=0.3,
            max_tokens=256,
        )

        response_text = chat_completion.choices[0].message.content.strip()

        # Clean markdown if model adds it
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        alternative = json.loads(response_text)
        print(f"Groq SUCCESS: {alternative['name']}")
        return alternative

    except Exception as e:
        print(f"Groq API error: {e}")
        return {
            "name": "Look for local organic alternatives",
            "brand": "Various Indian brands",
            "reason": "Choose products with paper/glass packaging and organic certification",
            "grade": "A",
            "price": "Varies",
            "available_at": "BigBasket, Amazon, local organic stores"
        }

@app.get("/scan/{barcode}")
def scan_product(barcode: str):
    product = fetch_product(barcode)

    if not product:
        return {
            "barcode": barcode,
            "name": "Unknown Product",
            "brand": "Unknown Brand",
            "grade": "C",
            "score": 50,
            "reasons": [
                "Product not found in our database",
                "Unable to verify environmental impact",
                "Consider choosing products with visible eco certifications"
            ],
            "packaging": "Unknown",
            "labels": "None",
            "source": "unknown",
            "alternative": None
        }
    
    score_result = calculate_score(product)
    grade = score_result["grade"]
    alternative = get_alternative(product) if grade in ["C", "D", "E"] else None

    return {
        "barcode": barcode,
        "name": product.get("product_name") or product.get("product_name_en") or "Unknown Product",
        "brand": product.get("brands", "Unknown Brand"),
        "grade": grade,
        "score": score_result["score"],
        "reasons": score_result["reasons"],
        "packaging": product.get("packaging", "Unknown"),
        "labels": product.get("labels", "None"),
        "source": product.get("_source", "unknown"),
        "alternative": alternative,
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/history")
def get_scan_history():
    return {"history": get_history()}