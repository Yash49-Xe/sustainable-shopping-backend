def calculate_score(product: dict) -> dict:
    score = 0
    reasons = []

    # --- Packaging (PRIMARY factor - up to 60 pts) ---
    packaging = product.get("packaging", "").lower()
    packaging_tags = product.get("packaging_tags", [])
    packaging_all = packaging + " " + " ".join(packaging_tags)

    if any(p in packaging_all for p in
           ["plastic", "pet", "hdpe", "polystyrene", "polypropylene"]):
        score += 60
        reasons.append("Single-use plastic packaging — worst for environment")
    elif any(p in packaging_all for p in ["aluminium", "aluminum", "can", "tin"]):
        score += 30
        reasons.append("Aluminium packaging — recyclable but energy intensive")
    elif any(p in packaging_all for p in ["tetra", "tetra pak", "carton"]):
        score += 20
        reasons.append("Tetra Pak — partially recyclable composite material")
    elif any(p in packaging_all for p in ["glass", "verre"]):
        score += 10
        reasons.append("Glass packaging — recyclable and reusable")
    elif any(p in packaging_all for p in
             ["paper", "cardboard", "carton", "papier", "kraft"]):
        score += 5
        reasons.append("Paper/cardboard packaging — biodegradable")
    elif any(p in packaging_all for p in ["compost", "biodegradable"]):
        score += 0
        reasons.append("Compostable packaging — best for environment")
    else:
        score += 25
        reasons.append("Packaging type unknown — cannot verify recyclability")

    # --- Palm oil (up to 20 pts) ---
    ingredients = product.get("ingredients_text", "").lower()
    if "palm oil" in ingredients or "palm fat" in ingredients:
        score += 20
        reasons.append("Contains palm oil — linked to deforestation")

    # --- Harmful chemicals (personal care / cleaning) ---
    if "microbeads" in ingredients or "polyethylene" in ingredients:
        score += 15
        reasons.append("Contains microplastics — pollutes waterways")
    if "paraben" in ingredients:
        score += 10
        reasons.append("Contains parabens — harmful to aquatic life")
    if "triclosan" in ingredients:
        score += 10
        reasons.append("Contains triclosan — harmful to aquatic ecosystems")
    if "phosphate" in ingredients:
        score += 10
        reasons.append("Contains phosphates — causes water pollution")
    if "bleach" in ingredients or "chlorine" in ingredients:
        score += 10
        reasons.append("Contains bleach — harmful to aquatic life")

    # --- Eco certifications (reduce score) ---
    labels = product.get("labels", "").lower()
    if "fair trade" in labels or "fairtrade" in labels:
        score -= 5
        reasons.append("Fair Trade certified")
    if "organic" in labels or "bio" in labels:
        score -= 10
        reasons.append("Organic certified — no harmful pesticides")
    if "rainforest alliance" in labels:
        score -= 5
        reasons.append("Rainforest Alliance certified")
    if "recyclable" in labels:
        score -= 5
        reasons.append("Recyclable packaging certified")
    if "biodegradable" in labels:
        score -= 10
        reasons.append("Biodegradable packaging certified")

    # --- Refill / concentrate bonus ---
    name = product.get("product_name", "").lower()
    if "refill" in name or "concentrate" in name:
        score -= 10
        reasons.append("Refill/concentrate — less packaging waste")

    # Clamp score
    score = max(0, min(score, 100))

    # Grade mapping
    if score <= 15:   grade = "A"
    elif score <= 30: grade = "B"
    elif score <= 50: grade = "C"
    elif score <= 70: grade = "D"
    else:             grade = "E"

    return {
        "grade": grade,
        "score": score,
        "reasons": reasons
    }