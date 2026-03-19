from scoring import calculate_score

# Test product 1 — bad product
bad_product = {
    "packaging": "plastic",
    "ingredients_text": "water, sugar, palm oil, salt",
    "labels": ""
}

# Test product 2 — good product
good_product = {
    "packaging": "cardboard",
    "ingredients_text": "organic oats, honey",
    "labels": "organic, fair trade"
}

print("Bad product:", calculate_score(bad_product))
print("Good product:", calculate_score(good_product))