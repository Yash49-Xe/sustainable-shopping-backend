def calculate_score(product: dict) -> dict:
    score = 0
    reasons = []

    # --- Packaging (up to 40 pts) ---
    packaging = product.get("packaging", "").lower()
    packaging_tags = product.get("packaging_tags", [])  # more reliable field
    packaging_all = packaging + " ".join(packaging_tags)

    if any(p in packaging_all for p in ["plastic", "pet", "hdpe", "polystyrene"]):
        score += 40
        reasons.append("Plastic packaging")
    elif any(p in packaging_all for p in ["glass", "verre"]):
        score += 10
        reasons.append("Glass packaging")
    elif any(p in packaging_all for p in ["paper", "cardboard", "carton", "papier"]):
        score += 5
        reasons.append("Paper/cardboard packaging")
    elif any(p in packaging_all for p in ["aluminium", "aluminum", "can", "tin"]):
        score += 20
        reasons.append("Aluminium/can packaging")
    else:
        score += 15
        reasons.append("Packaging type unknown")

    # --- Palm oil (up to 20 pts) ---
    ingredients = product.get("ingredients_text", "").lower()
    if "palm oil" in ingredients or "palm fat" in ingredients:
        score += 20
        reasons.append("Contains palm oil")

    # --- Electronics / general products ---
    categories = product.get("categories", "").lower()
    if any(w in categories for w in ["electronic", "battery", "cable", "charger"]):
        score += 30
        reasons.append("Electronics have high manufacturing carbon footprint")

    # --- Clothing / textile ---
    if any(w in categories for w in ["cloth", "textile", "fabric", "wear", "shirt"]):
        if "synthetic" in ingredients or "polyester" in ingredients:
            score += 25
            reasons.append("Synthetic fabric sheds microplastics when washed")
        elif "cotton" in ingredients or "organic" in ingredients:
            score += 5
            reasons.append("Natural fabric — better than synthetic")

    # --- Cleaning products ---
    if any(w in categories for w in ["clean", "detergent", "bleach", "disinfect"]):
        if "bleach" in ingredients or "chlorine" in ingredients:
            score += 20
            reasons.append("Contains bleach — harmful to aquatic life")
        if "phosphate" in ingredients:
            score += 15
            reasons.append("Contains phosphates — causes water pollution")

    # --- Microplastics / harmful ingredients (beauty products) ---
    if "polyethylene" in ingredients or "microbeads" in ingredients:
        score += 25
        reasons.append("Contains microplastics")
    if "paraben" in ingredients:
        score += 10
        reasons.append("Contains parabens")
    if "triclosan" in ingredients:
        score += 15
        reasons.append("Contains triclosan (harmful to aquatic life)")

    # --- Nutriscore as environmental proxy (optional penalty) ---
    nutriscore = product.get("nutriscore_grade", "").lower()
    if nutriscore in ["d", "e"]:
        score += 10
        reasons.append("Poor nutritional quality (Nutri-score D/E)")

    # --- Eco labels / certifications (reduce score) ---
    labels = product.get("labels", "").lower()
    if "fair trade" in labels or "fairtrade" in labels:
        score -= 10
        reasons.append("Fair Trade certified")
    if "organic" in labels or "bio" in labels:
        score -= 5
        reasons.append("Organic certified")
    if "rainforest alliance" in labels:
        score -= 5
        reasons.append("Rainforest Alliance certified")

    # Clamp score between 0 and 100
    score = max(0, min(score, 100))

    # Map to A–E grade
    if score <= 15:   grade = "A"
    elif score <= 30: grade = "B"
    elif score <= 45: grade = "C"
    elif score <= 60: grade = "D"
    else:             grade = "E"

    return {
        "grade": grade,
        "score": score,
        "reasons": reasons
    }