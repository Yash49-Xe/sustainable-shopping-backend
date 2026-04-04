import csv
import json
import time
from groq import Groq
import os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CATEGORIES = [
    {"name": "chips_snacks", "label": "Chips & Snacks", "count": 40},
    {"name": "biscuits_cookies", "label": "Biscuits & Cookies", "count": 40},
    {"name": "noodles_pasta", "label": "Noodles & Pasta", "count": 30},
    {"name": "beverages_juices", "label": "Beverages & Juices", "count": 35},
    {"name": "chocolates_sweets", "label": "Chocolates & Sweets", "count": 35},
    {"name": "dairy", "label": "Dairy Products", "count": 30},
    {"name": "personal_care", "label": "Personal Care & Soaps", "count": 35},
    {"name": "household_cleaning", "label": "Household & Cleaning", "count": 30},
    {"name": "staples", "label": "Staples Rice Dal Oil", "count": 35},
    {"name": "baby_products", "label": "Baby Products", "count": 25},
    {"name": "stationery", "label": "Stationery", "count": 20},
]

# Common size variants per category
SIZE_VARIANTS = {
    "chips_snacks": [
        {"size": "26g", "price": "₹10"},
        {"size": "52g", "price": "₹20"},
        {"size": "104g", "price": "₹40"},
        {"size": "200g", "price": "₹70"},
    ],
    "biscuits_cookies": [
        {"size": "100g", "price": "₹20"},
        {"size": "200g", "price": "₹35"},
        {"size": "400g", "price": "₹65"},
        {"size": "800g", "price": "₹120"},
    ],
    "noodles_pasta": [
        {"size": "70g", "price": "₹14"},
        {"size": "140g", "price": "₹25"},
        {"size": "280g", "price": "₹45"},
        {"size": "560g", "price": "₹85"},
    ],
    "beverages_juices": [
        {"size": "200ml", "price": "₹20"},
        {"size": "500ml", "price": "₹40"},
        {"size": "1L", "price": "₹70"},
        {"size": "2L", "price": "₹120"},
    ],
    "chocolates_sweets": [
        {"size": "15g", "price": "₹10"},
        {"size": "40g", "price": "₹25"},
        {"size": "100g", "price": "₹60"},
        {"size": "200g", "price": "₹110"},
    ],
    "dairy": [
        {"size": "200ml", "price": "₹22"},
        {"size": "500ml", "price": "₹52"},
        {"size": "1L", "price": "₹98"},
        {"size": "5L", "price": "₹460"},
    ],
    "personal_care": [
        {"size": "50g", "price": "₹30"},
        {"size": "100g", "price": "₹55"},
        {"size": "200g", "price": "₹99"},
        {"size": "500g", "price": "₹220"},
    ],
    "household_cleaning": [
        {"size": "500ml", "price": "₹65"},
        {"size": "1L", "price": "₹120"},
        {"size": "2L", "price": "₹220"},
        {"size": "5L", "price": "₹499"},
    ],
    "staples": [
        {"size": "500g", "price": "₹55"},
        {"size": "1kg", "price": "₹105"},
        {"size": "5kg", "price": "₹499"},
        {"size": "10kg", "price": "₹950"},
    ],
    "baby_products": [
        {"size": "100g", "price": "₹120"},
        {"size": "200g", "price": "₹220"},
        {"size": "400g", "price": "₹420"},
        {"size": "900g", "price": "₹899"},
    ],
    "stationery": [
        {"size": "1 piece", "price": "₹10"},
        {"size": "5 pack", "price": "₹45"},
        {"size": "10 pack", "price": "₹85"},
        {"size": "20 pack", "price": "₹160"},
    ],
}

def generate_base_products(category: dict, start_barcode: int) -> list:
    print(f"\nGenerating products for {category['label']}...")
    all_products = []
    
    # Split into batches of 10 to stay under token limit
    batch_size = 10
    total = category['count']
    batches = total // batch_size
    
    for batch in range(batches):
        current_barcode = start_barcode + (batch * batch_size * 4)
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product database expert. Respond with valid JSON array only."
                    },
                    {
                        "role": "user",
                        "content": f"""Generate {batch_size} Indian {category['label']} products.
Brands: Amul,Nestle,ITC,HUL,Dabur,Patanjali,Haldirams,Britannia,PepsiCo,Parle,Tata,Marico,Godrej,Himalaya,Colgate,Reckitt.
Start barcode: {current_barcode}

JSON array only:
[{{"barcode_base":"{current_barcode}","product_name":"name only no size","brand":"brand","category":"{category['name']}","packaging":"plastic/paper/glass/cardboard/tetra pak/aluminium/compostable","ingredients_text":"ingredients","labels":"Vegetarian/Vegan/Organic or empty","recyclable":"yes/no/partial"}}]"""
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            response_text = chat_completion.choices[0].message.content.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            products = json.loads(response_text)
            all_products.extend(products)
            print(f"  Batch {batch+1}/{batches}: got {len(products)} products")
            time.sleep(2)

        except Exception as e:
            print(f"  Batch {batch+1} error: {e}")
            time.sleep(3)
            continue

    print(f"  Total for {category['label']}: {len(all_products)}")
    return all_products


def expand_with_variants(base_products: list, category_name: str) -> list:
    """Expand each base product into multiple size variants"""
    variants = SIZE_VARIANTS.get(category_name, [
        {"size": "small", "price": "₹30"},
        {"size": "medium", "price": "₹60"},
        {"size": "large", "price": "₹120"},
    ])

    all_rows = []
    for product in base_products:
        base_barcode = int(product.get("barcode_base", 8901000000001))
        for i, variant in enumerate(variants):
            barcode = str(base_barcode + i)
            all_rows.append({
                "barcode": barcode,
                "product_name": f"{product.get('product_name', '')} {variant['size']}",
                "brand": product.get("brand", ""),
                "category": product.get("category", ""),
                "packaging": product.get("packaging", "plastic"),
                "ingredients_text": product.get("ingredients_text", ""),
                "labels": product.get("labels", ""),
                "nutriscore_grade": "",
                "price": variant["price"],
                "size": variant["size"],
                "recyclable": product.get("recyclable", "no"),
            })
    return all_rows


def main():
    all_products = []
    existing_barcodes = set()

    # Load existing CSV
    try:
        with open("indian_products.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_barcodes.add(row['barcode'])
                all_products.append(row)
        print(f"Loaded {len(all_products)} existing products")
    except FileNotFoundError:
        print("Starting fresh dataset")

    start_barcode = 8901000010001

    for category in CATEGORIES:
        base_products = generate_base_products(category, start_barcode)

        if base_products:
            variants = expand_with_variants(base_products, category["name"])

            added = 0
            for product in variants:
                if product["barcode"] not in existing_barcodes:
                    existing_barcodes.add(product["barcode"])
                    all_products.append(product)
                    added += 1

            print(f"  Added {added} variants "
                  f"({len(base_products)} products × "
                  f"{len(SIZE_VARIANTS.get(category['name'], []))} sizes)")

        save_csv(all_products)
        print(f"  Total so far: {len(all_products)}")
        time.sleep(3)

    print(f"\nDataset complete! Total: {len(all_products)} products")


def save_csv(products: list):
    fieldnames = ["barcode", "product_name", "brand", "category",
                  "packaging", "ingredients_text", "labels",
                  "nutriscore_grade", "price", "size", "recyclable"]

    with open("indian_products.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()
        writer.writerows(products)
    print(f"  Saved {len(products)} to indian_products.csv")


if __name__ == "__main__":
    main()