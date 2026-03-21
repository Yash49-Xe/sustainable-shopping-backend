import csv
import json
import time
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CATEGORIES = [
    {"name": "chips_snacks", "label": "Chips and Snacks", "count": 250},
    {"name": "biscuits_cookies", "label": "Biscuits and Cookies", "count": 250},
    {"name": "noodles_pasta", "label": "Noodles and Pasta", "count": 150},
    {"name": "beverages_juices", "label": "Beverages and Juices", "count": 200},
    {"name": "chocolates_sweets", "label": "Chocolates and Sweets", "count": 200},
    {"name": "dairy", "label": "Dairy Products", "count": 150},
    {"name": "personal_care", "label": "Personal Care and Soaps", "count": 200},
    {"name": "household_cleaning", "label": "Household and Cleaning", "count": 150},
    {"name": "staples", "label": "Staples Rice Dal Oil", "count": 200},
    {"name": "baby_products", "label": "Baby Products", "count": 150},
    {"name": "stationery", "label": "Stationery", "count": 100},
]

BATCH_SIZE = 50

def generate_batch(category: dict, start_barcode: int, batch_num: int) -> list:
    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a product database expert for Indian consumer goods. Always respond with a valid JSON array only. No markdown, no explanation, no extra text whatsoever."
                },
                {
                    "role": "user",
                    "content": f"""Generate exactly {BATCH_SIZE} realistic Indian {category['label']} products.

Use Indian brands: Amul, Nestle, ITC, HUL, Dabur, Patanjali, Haldirams, Britannia, PepsiCo, Parle, Tata, Marico, Godrej, Himalaya, Colgate, Reckitt.

Barcodes start from {start_barcode}, increment by 1 each product.

Return ONLY a JSON array of exactly {BATCH_SIZE} objects like this:
[{{"barcode":"{start_barcode}","product_name":"name","brand":"brand","category":"{category['name']}","packaging":"plastic","ingredients_text":"ingredients","labels":"Vegetarian","nutriscore_grade":"d"}}]

Rules:
- packaging: only use plastic/paper/glass/cardboard/tetra pak/aluminium
- nutriscore_grade: only use a/b/c/d/e or empty string
- No special characters in any field
- Keep ingredients_text short under 50 chars
- Barcodes must start with 890"""
                }
            ],
            temperature=0.7,
            max_tokens=4000,
        )

        response_text = chat_completion.choices[0].message.content.strip()

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Fix truncated JSON by finding last complete object
        if not response_text.endswith("]"):
            last_complete = response_text.rfind("},")
            if last_complete != -1:
                response_text = response_text[:last_complete + 1] + "]"
            else:
                response_text = response_text + "]"

        products = json.loads(response_text)
        print(f"  Batch {batch_num}: generated {len(products)} products")
        return products

    except Exception as e:
        print(f"  Batch {batch_num} error: {e}")
        return []

def save_csv(products: list):
    with open("indian_products.csv", "w", newline='', encoding='utf-8') as f:
        fieldnames = ["barcode", "product_name", "brand", "category",
                     "packaging", "ingredients_text", "labels", "nutriscore_grade"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products)

def main():
    all_products = []
    existing_barcodes = set()
    start_barcode = 8901000000001

    # Load existing products
    try:
        with open("indian_products.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_barcodes.add(row['barcode'])
                all_products.append(row)
        print(f"Loaded {len(all_products)} existing products")
    except FileNotFoundError:
        print("Starting fresh")

    for category in CATEGORIES:
        print(f"\nGenerating {category['count']} products for {category['label']}...")
        total_generated = 0
        batch_num = 1
        batches_needed = category['count'] // BATCH_SIZE

        while total_generated < category['count']:
            products = generate_batch(category, start_barcode, batch_num)

            for product in products:
                barcode = str(product.get("barcode", start_barcode))
                if barcode not in existing_barcodes:
                    existing_barcodes.add(barcode)
                    all_products.append({
                        "barcode": barcode,
                        "product_name": str(product.get("product_name", ""))[:100],
                        "brand": str(product.get("brand", ""))[:50],
                        "category": str(product.get("category", category['name']))[:50],
                        "packaging": str(product.get("packaging", "plastic"))[:30],
                        "ingredients_text": str(product.get("ingredients_text", ""))[:200],
                        "labels": str(product.get("labels", ""))[:100],
                        "nutriscore_grade": str(product.get("nutriscore_grade", ""))[:1]
                    })
                    total_generated += 1
                start_barcode += 1

            # Save after every batch
            save_csv(all_products)
            print(f"  Total products: {len(all_products)}")

            batch_num += 1
            # Stop if we have enough for this category
            if total_generated >= category['count']:
                break

            # Respect rate limits
            time.sleep(2)

        print(f"Finished {category['label']}: {total_generated} products added")

    print(f"\nDone! Final total: {len(all_products)} products")

if __name__ == "__main__":
    main()