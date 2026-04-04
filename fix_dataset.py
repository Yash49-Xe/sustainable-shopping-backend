import csv

# Correct size variants per category
SIZE_VARIANTS = {
    "chips": [
        {"suffix": "26g", "price": "₹10"},
        {"suffix": "52g", "price": "₹20"},
        {"suffix": "104g", "price": "₹40"},
        {"suffix": "200g", "price": "₹70"},
    ],
    "snack": [
        {"suffix": "30g", "price": "₹10"},
        {"suffix": "80g", "price": "₹20"},
        {"suffix": "150g", "price": "₹40"},
        {"suffix": "400g", "price": "₹99"},
    ],
    "biscuit": [
        {"suffix": "100g", "price": "₹10"},
        {"suffix": "200g", "price": "₹20"},
        {"suffix": "400g", "price": "₹38"},
        {"suffix": "800g", "price": "₹70"},
    ],
    "noodles": [
        {"suffix": "70g", "price": "₹14"},
        {"suffix": "140g", "price": "₹25"},
        {"suffix": "280g", "price": "₹45"},
        {"suffix": "560g", "price": "₹85"},
    ],
    "chocolate": [
        {"suffix": "15g", "price": "₹10"},
        {"suffix": "40g", "price": "₹25"},
        {"suffix": "100g", "price": "₹60"},
        {"suffix": "200g", "price": "₹110"},
    ],
    "sweet": [
        {"suffix": "200g", "price": "₹50"},
        {"suffix": "400g", "price": "₹99"},
        {"suffix": "750g", "price": "₹180"},
        {"suffix": "1kg", "price": "₹230"},
    ],
    "juice": [
        {"suffix": "200ml", "price": "₹20"},
        {"suffix": "500ml", "price": "₹45"},
        {"suffix": "1L", "price": "₹80"},
        {"suffix": "2L", "price": "₹140"},
    ],
    "beverage": [
        {"suffix": "200ml", "price": "₹20"},
        {"suffix": "500ml", "price": "₹40"},
        {"suffix": "1L", "price": "₹70"},
        {"suffix": "2L", "price": "₹120"},
    ],
    "milk": [
        {"suffix": "200ml", "price": "₹22"},
        {"suffix": "500ml", "price": "₹52"},
        {"suffix": "1L", "price": "₹98"},
        {"suffix": "5L", "price": "₹460"},
    ],
    "dairy": [
        {"suffix": "100g", "price": "₹35"},
        {"suffix": "200g", "price": "₹65"},
        {"suffix": "500g", "price": "₹150"},
        {"suffix": "1kg", "price": "₹280"},
    ],
    "soap": [
        {"suffix": "50g", "price": "₹20"},
        {"suffix": "100g", "price": "₹38"},
        {"suffix": "150g", "price": "₹55"},
        {"suffix": "3x100g", "price": "₹105"},
    ],
    "shampoo": [
        {"suffix": "80ml", "price": "₹60"},
        {"suffix": "180ml", "price": "₹120"},
        {"suffix": "340ml", "price": "₹210"},
        {"suffix": "650ml", "price": "₹380"},
    ],
    "toothpaste": [
        {"suffix": "50g", "price": "₹40"},
        {"suffix": "100g", "price": "₹70"},
        {"suffix": "200g", "price": "₹130"},
        {"suffix": "300g", "price": "₹180"},
    ],
    "sauce": [
        {"suffix": "200g", "price": "₹40"},
        {"suffix": "500g", "price": "₹85"},
        {"suffix": "1kg", "price": "₹155"},
        {"suffix": "2kg", "price": "₹290"},
    ],
    "tea": [
        {"suffix": "100g", "price": "₹55"},
        {"suffix": "250g", "price": "₹120"},
        {"suffix": "500g", "price": "₹220"},
        {"suffix": "1kg", "price": "₹420"},
    ],
    "coffee": [
        {"suffix": "50g", "price": "₹120"},
        {"suffix": "100g", "price": "₹220"},
        {"suffix": "200g", "price": "₹420"},
        {"suffix": "500g", "price": "₹999"},
    ],
    "oil": [
        {"suffix": "500ml", "price": "₹80"},
        {"suffix": "1L", "price": "₹150"},
        {"suffix": "2L", "price": "₹280"},
        {"suffix": "5L", "price": "₹650"},
    ],
    "rice": [
        {"suffix": "1kg", "price": "₹80"},
        {"suffix": "5kg", "price": "₹380"},
        {"suffix": "10kg", "price": "₹740"},
        {"suffix": "25kg", "price": "₹1800"},
    ],
    "dal": [
        {"suffix": "500g", "price": "₹60"},
        {"suffix": "1kg", "price": "₹115"},
        {"suffix": "5kg", "price": "₹540"},
        {"suffix": "10kg", "price": "₹1050"},
    ],
    "salt": [
        {"suffix": "200g", "price": "₹10"},
        {"suffix": "500g", "price": "₹22"},
        {"suffix": "1kg", "price": "₹40"},
        {"suffix": "5kg", "price": "₹185"},
    ],
    "oats": [
        {"suffix": "200g", "price": "₹60"},
        {"suffix": "500g", "price": "₹140"},
        {"suffix": "1kg", "price": "₹260"},
        {"suffix": "2kg", "price": "₹499"},
    ],
    "default": [
        {"suffix": "small", "price": "₹30"},
        {"suffix": "medium", "price": "₹60"},
        {"suffix": "large", "price": "₹110"},
        {"suffix": "family", "price": "₹200"},
    ],
}

PACKAGING_RECYCLABLE = {
    "plastic": "no",
    "paper": "yes",
    "cardboard": "yes",
    "glass": "yes",
    "tetra pak": "partial",
    "aluminium": "yes",
    "compostable": "yes",
    "can": "yes",
    "tin": "yes",
}

def get_variants(category: str) -> list:
    # Try exact match first
    if category in SIZE_VARIANTS:
        return SIZE_VARIANTS[category]
    # Try partial match
    for key in SIZE_VARIANTS:
        if key in category or category in key:
            return SIZE_VARIANTS[key]
    return SIZE_VARIANTS["default"]

def get_recyclable(packaging: str) -> str:
    packaging_lower = packaging.lower()
    for key, value in PACKAGING_RECYCLABLE.items():
        if key in packaging_lower:
            return value
    return "no"

def main():
    # Read existing products
    products = []
    with open("indian_products.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)

    print(f"Loaded {len(products)} existing products")

    # Keep only products that already have size variants
    # (price column is filled) OR are from original manual list
    base_products = []
    seen_names = set()

    for p in products:
        # Skip if already a size variant from new generator
        if p.get("price") and p.get("size"):
            continue
        # Skip duplicates
        key = f"{p['product_name'].lower()}_{p['brand'].lower()}"
        if key not in seen_names:
            seen_names.add(key)
            base_products.append(p)

    print(f"Found {len(base_products)} unique base products to expand")

    # Generate variants
    all_variants = []
    barcode_counter = 8902000000001

    for product in base_products:
        category = product.get("category", "").lower()
        variants = get_variants(category)
        recyclable = get_recyclable(product.get("packaging", ""))

        for variant in variants:
            all_variants.append({
                "barcode": str(barcode_counter),
                "product_name": f"{product['product_name']} {variant['suffix']}",
                "brand": product.get("brand", ""),
                "category": product.get("category", ""),
                "packaging": product.get("packaging", ""),
                "ingredients_text": product.get("ingredients_text", ""),
                "labels": product.get("labels", ""),
                "nutriscore_grade": product.get("nutriscore_grade", ""),
                "price": variant["price"],
                "size": variant["suffix"],
                "recyclable": recyclable,
            })
            barcode_counter += 1

    print(f"Generated {len(all_variants)} size variants")

    # Save final CSV with original products + all variants
    final_products = []

    # Add originals with recyclable filled in
    for p in base_products:
        p["recyclable"] = get_recyclable(p.get("packaging", ""))
        p["price"] = p.get("price", "")
        p["size"] = p.get("size", "")
        final_products.append(p)

    # Add variants
    final_products.extend(all_variants)

    fieldnames = ["barcode", "product_name", "brand", "category",
                  "packaging", "ingredients_text", "labels",
                  "nutriscore_grade", "price", "size", "recyclable"]

    with open("indian_products.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()
        writer.writerows(final_products)

    print(f"Saved {len(final_products)} total products to indian_products.csv")
    print(f"  - {len(base_products)} base products")
    print(f"  - {len(all_variants)} size variants")

if __name__ == "__main__":
    main()