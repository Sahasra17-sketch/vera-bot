from flask import Flask, request, jsonify
import random
import time
import os

app = Flask(__name__)

# -------- MEMORY (anti-spam) --------
last_sent = {}

# -------- MESSAGE TEMPLATES --------
repeat_templates = [
    "We missed you! Enjoy {discount}% off on {item} today!",
    "It's been a while! Get {discount}% off your favorites today.",
    "Come back today and enjoy {discount}% off on {item}!"
]

new_templates = [
    "Welcome! Get {discount}% off on {item}.",
    "First time here? Enjoy {discount}% off today!",
    "Start with {discount}% off on your first order!"
]

# -------- ROOT (optional, avoids Not Found) --------
@app.route('/')
def home():
    return "Vera Bot is running!"

# -------- HEALTH --------
@app.route('/v1/healthz', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# -------- METADATA --------
@app.route('/v1/metadata', methods=['GET'])
def metadata():
    return jsonify({
        "name": "Vera AI Bot",
        "version": "1.0",
        "description": "Smart messaging decision engine"
    })

# -------- CONTEXT --------
@app.route('/v1/context', methods=['POST'])
def context():
    return jsonify({"status": "context received"})

# -------- REPLY --------
@app.route('/v1/reply', methods=['POST'])
def reply():
    return jsonify({"status": "reply received"})

# -------- MAIN LOGIC --------
@app.route('/v1/tick', methods=['POST'])
def tick():
    data = request.json or {}

    sales = data.get("salesTrend", "normal")
    customer = data.get("customerType", "new")
    festival = data.get("festival", False)
    category = data.get("category", "general")
    user_id = data.get("userId", "default_user")

    # --- Anti-spam ---
    now = time.time()
    if user_id in last_sent and now - last_sent[user_id] < 60:
        return jsonify({
            "decision": "suppress",
            "reason": "Recently messaged user, avoiding spam",
            "score": 0
        })

    # --- Simulated sales drop ---
    sales_drop = random.randint(10, 40) if sales == "down" else 0

    # --- Scoring ---
    score = 0
    reasons = []

    if sales == "down":
        score += 5
        reasons.append(f"Sales dropped {sales_drop}%")

    if customer == "repeat":
        score += 3
        reasons.append("Repeat customer")

    if festival:
        score += 2
        reasons.append("Festival opportunity")

    # --- Decision ---
    if score >= 6:

        # Discount logic
        if sales_drop >= 30:
            discount = 30
        elif sales_drop >= 20:
            discount = 25
        else:
            discount = 20

        # Category mapping
        category_map = {
            "restaurant": ("your favorite meals", "Order Now"),
            "salon": ("your next makeover", "Book Now"),
            "gym": ("your fitness plan", "Join Now")
        }

        item, cta = category_map.get(category, ("our services", "Explore Now"))

        # Message selection
        if customer == "repeat":
            template = random.choice(repeat_templates)
            persona = "friendly_owner"
        else:
            template = random.choice(new_templates)
            persona = "brand"

        message = template.format(discount=discount, item=item)

        last_sent[user_id] = now

        return jsonify({
            "decision": "send",
            "message": message,
            "cta": cta,
            "persona": persona,
            "score": score,
            "reason": f"{'; '.join(reasons)} | Category={category} | Action=Send"
        })

    else:
        return jsonify({
            "decision": "suppress",
            "score": score,
            "reason": "Low relevance, message suppressed"
        })

# -------- RUN SERVER --------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
