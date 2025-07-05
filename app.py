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
from character_generation_endpoints import (
    set_seed,
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
    get_skill_eligibility_count
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue.js frontend

# In-memory storage for characters (replace with database in production)
characters_db: Dict[str, Dict[str, Any]] = {}

def generate_character_id() -> str:
    """Generate a unique character ID"""
    return f"char_{random.randint(100000, 999999)}"

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
        
        # Create random generator with character's seed
        random_generator = set_seed(character["seed"])
        
        # Call the stateless endpoint
        character = attempt_enlistment(random_generator, character, service)
        
        # Parse the enlistment result from career_history (last event)
        enlistment_result = character["career_history"][-1]
        
        # Update character in storage
        update_character(character_id, character)
        
        # Return UI-friendly data parsed from the character record
        return jsonify({
            "success": True,
            "service_attempted": service,
            "assigned_service": enlistment_result["assigned_service"],
            "enlisted": enlistment_result["success"],
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
        
        # Create random generator with character's seed
        random_generator = set_seed(character["seed"])
        
        # Call the stateless endpoint
        character = check_commission(random_generator, character)
        
        # Parse the commission result from career_history (last event)
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
        
        # Create random generator with character's seed
        random_generator = set_seed(character["seed"])
        
        # Call the stateless endpoint
        character = check_promotion(random_generator, character)
        
        # Parse the promotion result from career_history (last event)
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
    
    Request body:
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
        table_choice = data.get('table')
        
        if not table_choice:
            return jsonify({
                "success": False,
                "error": "Table choice is required"
            }), 400
        
        character = get_character(character_id)
        
        # Create random generator with character's seed
        random_generator = set_seed(character["seed"])
        
        # Call the stateless endpoint
        character = resolve_skill(random_generator, character, table_choice)
        
        # Parse the skill result from career_history (last event)
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
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000) 