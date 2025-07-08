from flask import Flask, render_template, jsonify, request
import character_generation_rules as chargen

app = Flask(__name__)

# In-memory character record for demo (should use session or DB in production)
character_record = None

# Home route serves the main UI
@app.route("/")
def index():
    return render_template("index.html")

# Example API endpoint (stub)
@app.route("/api/create_character", methods=["POST"])
def create_character():
    global character_record
    rng = chargen.set_seed(42)
    character_record = chargen.create_character_record()
    character_record["name"] = chargen.generate_character_name(rng)
    # UPP conversion logic
    def characteristics_to_upp(characteristics):
        # Map to correct order and convert to hex, use '_' for missing or zero
        order = ["strength", "dexterity", "endurance", "intelligence", "education", "social"]
        def to_hex(val):
            if val is None or val == 0:
                return '_'
            return hex(val)[2:].upper() if 10 <= val <= 15 else str(val)
        return ''.join(to_hex(characteristics.get(attr)) for attr in order)
    upp = characteristics_to_upp(character_record.get("characteristics", {}))
    character_record["upp"] = upp
    return jsonify(character_record)

@app.route("/api/generate_characteristic", methods=["POST"])
def generate_characteristic():
    global character_record
    data = request.get_json()
    char_name = data.get("characteristic")
    rng = chargen.set_seed(42)  # Use the same seed or manage per-session
    value = chargen.generate_characteristic(rng, char_name)
    # Update the character record
    if character_record is not None:
        if "characteristics" not in character_record:
            character_record["characteristics"] = {}
        character_record["characteristics"][char_name] = value
        # Check if all six characteristics are present
        all_chars = ["strength", "dexterity", "endurance", "intelligence", "education", "social"]
        if all(all_chars[i] in character_record["characteristics"] for i in range(6)):
            # All characteristics rolled, return full UPP string
            def to_hex(val):
                if val is None or val == 0:
                    return '_'
                return hex(val)[2:].upper() if 10 <= val <= 15 else str(val)
            upp = ''.join(to_hex(character_record["characteristics"].get(attr)) for attr in all_chars)
            character_record["upp"] = upp
            return jsonify({"characteristic": char_name, "value": value, "upp": upp})
    return jsonify({"characteristic": char_name, "value": value})

@app.route("/api/enlist", methods=["POST"])
def enlist():
    global character_record
    data = request.get_json()
    service = data.get("service")
    rng = chargen.set_seed(42)
    if character_record is not None and "characteristics" in character_record:
        character_record = chargen.attempt_enlistment(rng, character_record, service)
        enlistment_result = character_record["career_history"][-1] if character_record.get("career_history") else {}
        return jsonify({
            "success": True,
            "career": character_record.get("career"),
            "enlistment_result": enlistment_result
        })
    return jsonify({"success": False, "error": "No character or characteristics"}), 400

@app.route("/api/survival", methods=["POST"])
def survival():
    global character_record
    rng = chargen.set_seed(42)
    if character_record is not None and "career" in character_record:
        character_record = chargen.check_survival(rng, character_record)
        survival_result = character_record["career_history"][-1] if character_record.get("career_history") else {}
        # Get skill-related data for frontend
        available_tables = chargen.get_available_skill_tables(character_record)
        skill_eligibility = character_record.get("skill_eligibility", 0)
        ready_for_skills = chargen.is_ready_for_skills(character_record)
        return jsonify({
            "success": True,
            "survival_result": survival_result,
            "terms_served": character_record.get("terms_served", 0),
            "available_tables": available_tables,
            "skill_eligibility": skill_eligibility,
            "ready_for_skills": ready_for_skills
        })
    return jsonify({"success": False, "error": "No character or career"}), 400

@app.route("/api/commission", methods=["POST"])
def commission():
    global character_record
    rng = chargen.set_seed(42)
    if character_record is not None and "career" in character_record:
        character_record = chargen.check_commission(rng, character_record)
        commission_result = character_record["career_history"][-1] if character_record.get("career_history") else {}
        # Add rank and career to the response for frontend use
        commission_result["rank"] = character_record.get("rank", 0)
        commission_result["career"] = character_record.get("career", "")
        
        # Get skill-related data for frontend
        available_tables = chargen.get_available_skill_tables(character_record)
        skill_eligibility = character_record.get("skill_eligibility", 0)
        ready_for_skills = chargen.is_ready_for_skills(character_record)
        
        return jsonify({
            "success": True,
            "commission_result": commission_result,
            "available_tables": available_tables,
            "skill_eligibility": skill_eligibility,
            "ready_for_skills": ready_for_skills
        })
    return jsonify({"success": False, "error": "No character or career"}), 400

@app.route("/api/promotion", methods=["POST"])
def promotion():
    global character_record
    rng = chargen.set_seed(42)
    if character_record is not None and "career" in character_record:
        character_record = chargen.check_promotion(rng, character_record)
        promotion_result = character_record["career_history"][-1] if character_record.get("career_history") else {}
        # Add rank and career to the response for frontend use
        promotion_result["rank"] = character_record.get("rank", 0)
        promotion_result["career"] = character_record.get("career", "")
        
        # Get skill-related data for frontend
        available_tables = chargen.get_available_skill_tables(character_record)
        skill_eligibility = character_record.get("skill_eligibility", 0)
        ready_for_skills = chargen.is_ready_for_skills(character_record)
        
        return jsonify({
            "success": True,
            "promotion_result": promotion_result,
            "available_tables": available_tables,
            "skill_eligibility": skill_eligibility,
            "ready_for_skills": ready_for_skills
        })
    return jsonify({"success": False, "error": "No character or career"}), 400

@app.route("/api/resolve_skill", methods=["POST"])
def resolve_skill():
    global character_record
    data = request.get_json()
    table = data.get("table")
    rng = chargen.set_seed(42)
    if character_record is None or "career" not in character_record:
        return jsonify({"success": False, "error": "No character or career"}), 400
    # Check eligibility
    skill_eligibility = character_record.get("skill_eligibility", 0)
    if skill_eligibility <= 0:
        return jsonify({"success": False, "error": "No skill eligibilities remaining"}), 400
    # Get available tables
    available_tables = chargen.get_available_skill_tables(character_record)
    if table not in available_tables or not available_tables[table]:
        return jsonify({"success": False, "error": f"Table '{table}' not available"}), 400
    # Resolve the skill
    try:
        result = chargen.resolve_skill(rng, character_record, table_choice=table)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
    # Prepare response
    skills = character_record.get("skills", {})
    skill_eligibility = character_record.get("skill_eligibility", 0)
    available_tables = chargen.get_available_skill_tables(character_record)
    next_phase = chargen.get_next_phase(character_record)
    return jsonify({
        "success": True,
        "skill_result": result,
        "skill_eligibility": skill_eligibility,
        "available_tables": available_tables,
        "skills": skills,
        "next_phase": next_phase
    })

@app.route("/api/ageing", methods=["POST"])
def ageing():
    global character_record
    rng = chargen.set_seed(42)
    if character_record is not None:
        character_record = chargen.check_ageing(rng, character_record)
        ageing_result = character_record["career_history"][-1] if character_record.get("career_history") else {}
        return jsonify({
            "success": True,
            "ageing_result": ageing_result,
            "character": character_record
        })
    return jsonify({"success": False, "error": "No character"}), 400

@app.route("/api/reenlist", methods=["POST"])
def reenlist():
    global character_record
    data = request.get_json()
    preference = data.get("preference", "reenlist")  # Default to reenlist
    rng = chargen.set_seed(42)
    if character_record is not None:
        character_record = chargen.attempt_reenlistment(rng, character_record, preference)
        reenlistment_result = character_record["career_history"][-1] if character_record.get("career_history") else {}
        
        # Get skill-related data for frontend
        available_tables = chargen.get_available_skill_tables(character_record)
        skill_eligibility = character_record.get("skill_eligibility", 0)
        ready_for_skills = chargen.is_ready_for_skills(character_record)
        
        return jsonify({
            "success": True,
            "reenlistment_result": reenlistment_result,
            "character": character_record,
            "available_tables": available_tables,
            "skill_eligibility": skill_eligibility,
            "ready_for_skills": ready_for_skills
        })
    return jsonify({"success": False, "error": "No character"}), 400

if __name__ == "__main__":
    app.run(debug=True) 