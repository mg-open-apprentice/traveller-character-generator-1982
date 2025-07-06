#!/usr/bin/env python3
"""
Classic Traveller Character Generator Flask App

A Flask web application for generating Classic Traveller characters
using the character generation endpoints.
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random
import json
import os
from typing import Dict, Any, List

# Import our character generation functions
from character_generation_rules import (
    set_seed,
    get_random_generator,
    save_random_state,
    create_character_record,
    generate_character_name,
    generate_characteristic,
    get_available_services,
    attempt_enlistment,
    check_survival,
    check_commission,
    check_promotion,
    resolve_skill,
    attempt_reenlistment,
    get_available_skill_tables,
    get_skill_eligibility_count,
    perform_mustering_out,
    calculate_mustering_out_info,
    check_ageing
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue.js frontend

# In-memory storage for characters (replace with database in production)
characters_db: Dict[str, Dict[str, Any]] = {}

def generate_character_id() -> str:
    """Generate a unique character ID with collision detection"""
    max_attempts = 100
    for _ in range(max_attempts):
        char_id = f"char_{random.randint(100000, 999999)}"
        # Check both in-memory database and JSON files for collisions
        if char_id not in characters_db and not os.path.exists(get_character_filename(char_id)):
            return char_id
    raise Exception("Unable to generate unique character ID after maximum attempts")

def get_character_filename(character_id: str) -> str:
    """Get the JSON filename for a character"""
    return f"traveller_character_{character_id.replace('char_', '')}.json"

def save_character_to_json(character: Dict[str, Any], character_id: str) -> None:
    """Save character to JSON file"""
    filename = get_character_filename(character_id)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(character, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving character to {filename}: {e}")
        raise

def load_character_from_json(character_id: str) -> Dict[str, Any]:
    """Load character from JSON file"""
    filename = get_character_filename(character_id)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"Character {character_id} not found")
    except Exception as e:
        print(f"Error loading character from {filename}: {e}")
        raise

def save_character(character: Dict[str, Any]) -> str:
    """Save character to storage and return character ID"""
    character_id = generate_character_id()
    characters_db[character_id] = character
    # Also save to JSON file
    save_character_to_json(character, character_id)
    return character_id

def get_character(character_id: str) -> Dict[str, Any]:
    """Retrieve character from storage"""
    # Try memory first, then JSON file
    if character_id in characters_db:
        return characters_db[character_id]
    
    try:
        character = load_character_from_json(character_id)
        # Cache in memory
        characters_db[character_id] = character
        return character
    except ValueError:
        raise ValueError(f"Character {character_id} not found")

def update_character(character_id: str, character: Dict[str, Any]) -> None:
    """Update character in storage"""
    if character_id not in characters_db:
        # Try to load from JSON first
        try:
            load_character_from_json(character_id)
        except ValueError:
            raise ValueError(f"Character {character_id} not found")
    
    characters_db[character_id] = character
    # Also save to JSON file
    save_character_to_json(character, character_id)

def discover_character_files() -> List[str]:
    """Discover existing character JSON files and return their character IDs"""
    character_ids = []
    for filename in os.listdir('.'):
        if filename.startswith('traveller_character_') and filename.endswith('.json'):
            # Extract character ID from filename
            # traveller_character_138340.json -> char_138340
            number = filename.replace('traveller_character_', '').replace('.json', '')
            character_id = f"char_{number}"
            character_ids.append(character_id)
    return character_ids



# API Routes

@app.route('/api/character/initialize', methods=['POST'])
def initialize_character():
    """
    Initialize a new character with name, age=18, terms=0
    
    Request body (optional):
    {
        "seed": 12345  // Optional seed for reproducible results
    }
    
    Returns:
    {
        "character_id": "char_123456",
        "name": "Generated Name",
        "age": 18,
        "terms_served": 0,
        "seed": 12345
    }
    """
    try:
        # Get seed from request (optional)
        data = request.get_json() or {}
        seed = data.get('seed', random.randint(1, 999999))
        
        # Create random generator
        random_generator = set_seed(seed)
        
        # Create character record
        character = create_character_record()
        
        # Generate name
        character["name"] = generate_character_name(random_generator)
        character["seed"] = seed
        
        # Save character and return with ID
        character_id = save_character(character)
        
        return jsonify({
            "success": True,
            "character_id": character_id,
            "name": character["name"],
            "age": character["age"],  # 18
            "terms_served": character["terms_served"],  # 0
            "seed": seed
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>', methods=['GET'])
def get_character_details(character_id: str):
    """
    Get complete character details
    
    Returns:
    {
        "success": true,
        "character": { ... character data ... }
    }
    """
    try:
        character = get_character(character_id)
        return jsonify({
            "success": True,
            "character": character
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/characteristic/<characteristic_name>', methods=['POST'])
def generate_single_characteristic(character_id: str, characteristic_name: str):
    """
    Generate a single characteristic for a character
    
    Returns:
    {
        "success": true,
        "characteristic": "strength",
        "value": 8
    }
    """
    try:
        # Validate characteristic name
        valid_characteristics = ["strength", "dexterity", "endurance", "intelligence", "education", "social"]
        if characteristic_name not in valid_characteristics:
            return jsonify({
                "success": False,
                "error": f"Invalid characteristic: {characteristic_name}"
            }), 400
        
        character = get_character(character_id)
        
        # Initialize characteristics dict if it doesn't exist
        if "characteristics" not in character:
            character["characteristics"] = {}
        
        # Check if characteristic already exists
        if characteristic_name in character["characteristics"]:
            return jsonify({
                "success": False,
                "error": f"{characteristic_name.capitalize()} already generated"
            }), 400
        
        # Create random generator with character's seed
        random_generator = set_seed(character["seed"])
        
        # Generate the single characteristic
        value = generate_characteristic(random_generator, characteristic_name)
        
        # Update character record
        character["characteristics"][characteristic_name] = value
        update_character(character_id, character)
        
        return jsonify({
            "success": True,
            "characteristic": characteristic_name,
            "value": value
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/enlist', methods=['POST'])
def enlist_character(character_id: str):
    """
    Attempt to enlist a character in a service
    
    Request body:
    {
        "service": "Navy"  // Service to attempt to enlist in
    }
    
    Returns:
    {
        "success": true,
        "service_attempted": "Navy",
        "assigned_service": "Navy", 
        "enlisted": true,
        "roll": 8,
        "target": 8,
        "modifiers": "+2 (Intelligence 9≥8)"
    }
    """
    try:
        # Get service from request
        data = request.get_json() or {}
        service = data.get('service')
        
        if not service:
            return jsonify({
                "success": False,
                "error": "Service is required"
            }), 400
        
        character = get_character(character_id)
        
        # Validate that characteristics are generated
        if "characteristics" not in character or len(character["characteristics"]) < 6:
            return jsonify({
                "success": False,
                "error": "All characteristics must be generated before enlistment"
            }), 400
        
        # Get random generator with restored state
        random_generator = get_random_generator(character)
        
        # Call the stateless endpoint
        character = attempt_enlistment(random_generator, character, service)
        
        # Save the updated random state
        save_random_state(character, random_generator)
        
        # Parse the enlistment result from career_history (last event)
        if not character.get("career_history"):
            raise ValueError("No career history available after enlistment")
        enlistment_result = character["career_history"][-1]
        
        # Update character in storage
        update_character(character_id, character)
        
        # Return UI-friendly data parsed from the character record
        return jsonify({
            "success": True,
            "service_attempted": service,
            "assigned_service": enlistment_result["assigned_service"],
            "outcome": enlistment_result["outcome"],
            "roll": enlistment_result["roll"],
            "target": enlistment_result["target"],
            "modifiers": ", ".join(enlistment_result["modifier_details"]) if enlistment_result["modifier_details"] else "None"
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/commission', methods=['POST'])
def commission_character(character_id: str):
    """
    Attempt to get a commission for a character
    
    Returns:
    {
        "success": true,
        "applicable": true,
        "commissioned": true,
        "roll": 9,
        "target": 10,
        "modifiers": "+1 (Social 9≥9)",
        "rank": 1
    }
    """
    try:
        character = get_character(character_id)
        
        # Validate that character has a career
        if "career" not in character:
            return jsonify({
                "success": False,
                "error": "Character must have a career before attempting commission"
            }), 400
        
        # Get random generator with restored state
        random_generator = get_random_generator(character)
        
        # Call the stateless endpoint
        character = check_commission(random_generator, character)
        
        # Save the updated random state
        save_random_state(character, random_generator)
        
        # Parse the commission result from career_history (last event)
        if not character.get("career_history"):
            raise ValueError("No career history available after commission check")
        commission_result = character["career_history"][-1]
        
        # Update character in storage
        update_character(character_id, character)
        
        # Return UI-friendly data parsed from the character record
        return jsonify({
            "success": True,
            "applicable": commission_result.get("applicable", True),
            "commissioned": commission_result["success"],
            "roll": commission_result.get("roll"),
            "target": commission_result.get("target"),
            "modifiers": ", ".join(commission_result.get("modifier_details", [])) if commission_result.get("modifier_details") else "None",
            "rank": character.get("rank") if commission_result["success"] else None,
            "reason": commission_result.get("reason", "")
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/promotion', methods=['POST'])
def promote_character(character_id: str):
    """
    Attempt to get a promotion for a character
    
    Returns:
    {
        "success": true,
        "applicable": true,
        "promoted": true,
        "roll": 8,
        "target": 8,
        "modifiers": "+1 (Education 8≥7)",
        "current_rank": 1,
        "new_rank": 2
    }
    """
    try:
        character = get_character(character_id)
        
        # Validate that character has a career
        if "career" not in character:
            return jsonify({
                "success": False,
                "error": "Character must have a career before attempting promotion"
            }), 400
        
        # Get random generator with restored state
        random_generator = get_random_generator(character)
        
        # Call the stateless endpoint
        character = check_promotion(random_generator, character)
        
        # Save the updated random state
        save_random_state(character, random_generator)
        
        # Parse the promotion result from career_history (last event)
        if not character.get("career_history"):
            raise ValueError("No career history available after promotion check")
        promotion_result = character["career_history"][-1]
        
        # Update character in storage
        update_character(character_id, character)
        
        # Return UI-friendly data parsed from the character record
        return jsonify({
            "success": True,
            "applicable": promotion_result.get("applicable", True),
            "promoted": promotion_result["success"],
            "roll": promotion_result.get("roll"),
            "target": promotion_result.get("target"),
            "modifiers": ", ".join(promotion_result.get("modifier_details", [])) if promotion_result.get("modifier_details") else "None",
            "current_rank": promotion_result.get("current_rank"),
            "new_rank": character.get("rank") if promotion_result["success"] else None,
            "reason": promotion_result.get("reason", "")
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/survival', methods=['POST'])
def check_character_survival(character_id: str):
    """
    Check survival for a character's current term
    
    Returns:
    {
        "success": true,
        "survived": true,
        "roll": 8,
        "target": 5,
        "modifiers": "+2 (Intelligence 9≥7)",
        "outcome": "survived",
        "new_age": 22,
        "new_terms_served": 1
    }
    """
    try:
        character = get_character(character_id)
        
        # Validate that character has a career
        if "career" not in character:
            return jsonify({
                "success": False,
                "error": "Character must have a career before survival check"
            }), 400
        
        # Get random generator with restored state
        random_generator = get_random_generator(character)
        
        # Call the stateless endpoint
        character = check_survival(random_generator, character)
        
        # Save the updated random state
        save_random_state(character, random_generator)
        
        # Parse the survival result from career_history (last event)
        if not character.get("career_history"):
            raise ValueError("No career history available after survival check")
        survival_result = character["career_history"][-1]
        
        # Update character in storage
        update_character(character_id, character)
        
        # Return UI-friendly data
        return jsonify({
            "success": True,
            "survived": survival_result["success"],
            "roll": survival_result["roll"],
            "target": survival_result["target"],
            "modifiers": ", ".join(survival_result["modifier_details"]) if survival_result["modifier_details"] else "None",
            "outcome": survival_result["outcome"],
            "new_age": character["age"],
            "new_terms_served": character["terms_served"]
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """
    Get list of available services
    
    Returns:
    {
        "success": true,
        "services": ["Navy", "Marines", "Army", "Scouts", "Merchants", "Others"]
    }
    """
    try:
        services = get_available_services()
        return jsonify({
            "success": True,
            "services": services
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/skill-eligibility', methods=['GET'])
def get_character_skill_eligibility(character_id: str):
    """
    Get the skill eligibility count for a character
    
    Returns:
    {
        "success": true,
        "skill_eligibility": 3
    }
    """
    try:
        character = get_character(character_id)
        
        eligibility_count = get_skill_eligibility_count(character)
        
        return jsonify({
            "success": True,
            "skill_eligibility": eligibility_count
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/skill', methods=['POST'])
def resolve_character_skill(character_id: str):
    """
    Resolve a skill for a character
    
    Expected JSON body:
    {
        "table": "personal" | "service" | "advanced" | "education"
    }
    
    Returns:
    {
        "success": true,
        "skill_gained": "Gun Combat",
        "skill_type": "skill_gain" | "characteristic_increase"
    }
    """
    try:
        data = request.get_json() or {}
        table_choice = data.get('table_choice')
        
        if not table_choice:
            return jsonify({
                "success": False,
                "error": "Table choice is required"
            }), 400
        
        character = get_character(character_id)
        
        # Get random generator with restored state
        random_generator = get_random_generator(character)
        
        # Call the stateless endpoint
        character = resolve_skill(random_generator, character, table_choice)
        
        # Save the updated random state
        save_random_state(character, random_generator)
        
        # Parse the skill result from career_history (last event)
        if not character.get("career_history"):
            raise ValueError("No career history available after skill resolution")
        skill_result = character["career_history"][-1]
        
        # Update character in storage
        update_character(character_id, character)
        
        # Return UI-friendly data
        return jsonify({
            "success": True,
            "skill_gained": skill_result["skill_gained"],
            "skill_type": skill_result["result_type"],
            "table_used": table_choice
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/reenlist', methods=['POST'])
def reenlist_character(character_id: str):
    """
    Attempt re-enlistment for a character
    
    Expected JSON body:
    {
        "preference": "reenlist" | "discharge" | "retire"
    }
    
    Returns:
    {
        "success": true,
        "outcome": "reenlisted" | "discharged" | "retired" | "retained",
        "status_text": "reenlisted" | "military discharge" | "retired" | "retained (mandatory)",
        "continue_career": true | false,
        "roll": 7,
        "target": 6,
        "preference": "reenlist",
        "skill_eligibilities_granted": 1
    }
    """
    try:
        data = request.get_json() or {}
        preference = data.get('preference', 'reenlist')
        
        if preference not in ['reenlist', 'discharge', 'retire']:
            return jsonify({
                "success": False,
                "error": "Invalid preference. Must be 'reenlist', 'discharge', or 'retire'"
            }), 400
        
        character = get_character(character_id)
        
        # Get random generator with restored state
        random_generator = get_random_generator(character)
        
        # Call the stateless endpoint
        character = attempt_reenlistment(random_generator, character, preference)
        
        # Save the updated random state
        save_random_state(character, random_generator)
        
        # Parse the reenlistment result from career_history (last event)
        if not character.get("career_history"):
            raise ValueError("No career history available after reenlistment")
        reenlistment_result = character["career_history"][-1]
        
        # Update character in storage
        update_character(character_id, character)
        
        # Prepare response data
        response_data = {
            "success": True,
            "outcome": reenlistment_result["outcome"],
            "status_text": reenlistment_result["status_text"],
            "continue_career": reenlistment_result["continue_career"],
            "roll": reenlistment_result["roll"],
            "target": reenlistment_result["target"],
            "preference": reenlistment_result["preference"],
            "skill_eligibilities_granted": reenlistment_result.get("skill_eligibilities_granted", 0)
        }
        
        # If character failed re-enlistment, include mustering out information
        if not reenlistment_result["continue_career"]:
            try:
                mustering_out_info = calculate_mustering_out_info(character)
                response_data["mustering_out_info"] = mustering_out_info
            except Exception as e:
                # If mustering out calculation fails, log it but don't break the response
                print(f"Warning: Failed to calculate mustering out info: {e}")
        
        # Return UI-friendly data
        return jsonify(response_data)
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/muster-out', methods=['POST'])
def muster_out_character(character_id: str):
    """
    Perform mustering out for a character
    
    Request body (optional):
    {
        "cash_rolls": 2,      // Optional: number of cash rolls to use (max 3)
        "gambling_skill": 1   // Optional: gambling skill level for bonus
    }
    
    Returns:
    {
        "success": true,
        "mustering_out_benefits": {
            "cash": 25000,
            "items": ["Blade", "High Psg"],
            "characteristic_boosts": {"intelligence": 1},
            "cash_roll_details": [...],
            "benefit_roll_details": [...]
        },
        "total_rolls": 4,
        "cash_rolls": 2,
        "benefit_rolls": 2
    }
    """
    try:
        # Get request data
        data = request.get_json() or {}
        cash_rolls = data.get('cash_rolls')
        
        # Validate cash_rolls if provided
        if cash_rolls is not None and (not isinstance(cash_rolls, int) or cash_rolls < 0 or cash_rolls > 3):
            return jsonify({
                "success": False,
                "error": "cash_rolls must be an integer between 0 and 3"
            }), 400
        
        character = get_character(character_id)
        
        # Check if character is eligible for mustering out
        if character.get('terms_served', 0) == 0:
            return jsonify({
                "success": False,
                "error": "Character must have served at least one term to muster out"
            }), 400
        
        # Check if already mustered out
        if character.get('mustering_out_benefits'):
            return jsonify({
                "success": False,
                "error": "Character has already mustered out"
            }), 400
        
        # Get random generator with restored state
        random_generator = get_random_generator(character)
        
        # Call the stateless endpoint
        character = perform_mustering_out(random_generator, character, cash_rolls)
        
        # Save the updated random state
        save_random_state(character, random_generator)
        
        # Update character in storage
        update_character(character_id, character)
        
        # Get mustering out results
        mustering_out_benefits = character.get('mustering_out_benefits', {})
        
        # Calculate rolls for response
        terms_served = character.get('terms_served', 0)
        rank = character.get('rank', 0)
        total_rolls = int(terms_served)
        if 1 <= rank <= 2:
            total_rolls += 1
        elif 3 <= rank <= 4:
            total_rolls += 2
        elif 5 <= rank <= 6:
            total_rolls += 3
        
        actual_cash_rolls = len(mustering_out_benefits.get('cash_roll_details', []))
        actual_benefit_rolls = len(mustering_out_benefits.get('benefit_roll_details', []))
        
        # Return UI-friendly data
        return jsonify({
            "success": True,
            "mustering_out_benefits": mustering_out_benefits,
            "total_rolls": total_rolls,
            "cash_rolls": actual_cash_rolls,
            "benefit_rolls": actual_benefit_rolls,
            "character_updates": {
                "characteristics": character.get('characteristics', {}),
                "cash": mustering_out_benefits.get('cash', 0),
                "items": mustering_out_benefits.get('items', []),
                "characteristic_boosts": mustering_out_benefits.get('characteristic_boosts', {})
            }
        })
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>/check-ageing-after-skills', methods=['POST'])
def check_ageing_after_skills(character_id: str):
    """
    Check for ageing effects after all skills are resolved, if age >= 34.
    Returns:
    {
        "success": true,
        "ageing_applicable": true/false,
        "ageing_effects": [...],
        "checks_performed": [...],
        "total_effects": 0,
        "previous_age": ...,
        "current_age": ...
    }
    """
    try:
        character = get_character(character_id)
        random_generator = get_random_generator(character)
        age = character.get("age", 18)
        if age < 34:
            return jsonify({
                "success": True,
                "ageing_applicable": False
            })
        # Perform ageing check
        character = check_ageing(random_generator, character)
        save_random_state(character, random_generator)
        update_character(character_id, character)
        # Get the last ageing event
        ageing_result = character["career_history"][-1] if character["career_history"] else {}
        return jsonify({
            "success": True,
            "ageing_applicable": True,
            "ageing_effects": ageing_result.get("ageing_effects", []),
            "checks_performed": ageing_result.get("checks_performed", []),
            "total_effects": ageing_result.get("total_effects", 0),
            "previous_age": ageing_result.get("previous_age", 0),
            "current_age": ageing_result.get("current_age", 0)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/characters', methods=['GET'])
def list_characters():
    """
    Get list of all characters from memory and JSON files
    
    Returns:
    {
        "success": true,
        "characters": [
            {
                "character_id": "char_123456",
                "name": "Character Name",
                "age": 18,
                "terms_served": 0
            },
            ...
        ]
    }
    """
    try:
        character_list = []
        
        # Get characters from memory
        for character_id, character in characters_db.items():
            character_list.append({
                "character_id": character_id,
                "name": character.get("name", "Unknown"),
                "age": character.get("age", 18),
                "terms_served": character.get("terms_served", 0),
                "career": character.get("career", "None")
            })
        
        # Get characters from JSON files that aren't already in memory
        json_character_ids = discover_character_files()
        for character_id in json_character_ids:
            if character_id not in characters_db:
                try:
                    character = load_character_from_json(character_id)
                    character_list.append({
                        "character_id": character_id,
                        "name": character.get("name", "Unknown"),
                        "age": character.get("age", 18),
                        "terms_served": character.get("terms_served", 0),
                        "career": character.get("career", "None")
                    })
                except Exception as e:
                    print(f"Error loading character {character_id}: {e}")
                    continue
        
        return jsonify({
            "success": True,
            "characters": character_list
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/character/<character_id>', methods=['DELETE'])
def delete_character(character_id: str):
    """
    Delete a character from memory and JSON file
    
    Returns:
    {
        "success": true,
        "message": "Character deleted"
    }
    """
    try:
        # Check if character exists (in memory or JSON file)
        character_exists = False
        if character_id in characters_db:
            character_exists = True
        else:
            try:
                load_character_from_json(character_id)
                character_exists = True
            except ValueError:
                pass
        
        if not character_exists:
            return jsonify({
                "success": False,
                "error": "Character not found"
            }), 404
        
        # Delete from memory if present
        if character_id in characters_db:
            del characters_db[character_id]
        
        # Delete JSON file if it exists
        filename = get_character_filename(character_id)
        if os.path.exists(filename):
            os.remove(filename)
        
        return jsonify({
            "success": True,
            "message": "Character deleted"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Frontend Routes (for serving Vue.js app)

@app.route('/')
def index():
    """Serve the main Vue.js application"""
    return render_template('index.html')

@app.route('/characters')
def characters_page():
    """Serve the characters list page"""
    return render_template('index.html')

@app.route('/characters/new')
def new_character_page():
    """Serve the new character creation page"""
    return render_template('index.html')

@app.route('/characters/<character_id>')
def character_detail_page(character_id):
    """Serve the character detail page"""
    return render_template('index.html')

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Use environment variables for production safety
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Run the Flask app
    app.run(debug=debug_mode, host='0.0.0.0', port=5000) 