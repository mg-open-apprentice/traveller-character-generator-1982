#!/usr/bin/env python3
"""
Classic Traveller Character Generation API

This module provides a stateless implementation of Classic Traveller character generation rules.
It offers functions for creating and manipulating character records, generating characteristics,
and handling enlistment processes.

Usage:
    import character_generation_endpoints as chargen
    
    # Create a seeded random generator for reproducible results
    rng = chargen.set_seed(42)
    
    # Create a new character record
    character = chargen.create_character_record()
    
    # Generate a name and characteristics
    character["name"] = chargen.generate_character_name(rng)
    character["characteristics"] = {
        "strength": chargen.generate_characteristic(rng, "strength"),
        "dexterity": chargen.generate_characteristic(rng, "dexterity"),
        # ... and so on
    }
"""

__version__ = "0.1.0"
__author__ = "System Two Digital"

import random
from typing import Any, List, Tuple, Optional

def set_seed(seed: int = 77) -> random.Random:
    """
    Create a random generator with the specified seed
    
    Args:
        seed: The seed to use
        
    Returns:
        A random generator initialized with the seed
    """
    return random.Random(seed)

def generate_character_name(random_generator: random.Random) -> str:
    """
    Generate a random sci-fi character name with separate first and last name pools
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        
    Returns:
        A randomly generated character name
    """
    first_names = [
        "Zara", "Orion", "Nova", "Elexis", "Jaxon", "Lyra", "Nyx", "Ryker",
        "Elara", "Caelum", "Vega", "Draco", "Aurora", "Cassius", "Astra", 
        "Kaius", "Seren", "Altair", "Selene", "Maximus"
    ]
    
    last_names = [
        "Xylo", "Pax", "Kin", "Vortex", "Starfire", "Nebulae", "Solaris", 
        "Quantum", "Galaxy", "Void", "Stardust", "Cosmos", "Hyperdrive", 
        "Meteor", "Comet", "Eclipse", "Andromeda", "Nebular", "Astraeus", "Ion"
    ]
    
    return f"{random_generator.choice(first_names)} {random_generator.choice(last_names)}"

def create_character_record() -> dict[str, Any]:
    """
    Create an empty data structure to hold character generation data
    """
    return {
        "name": "",
        "age": 18,
        "terms_served": 0,
        "characteristics": {},
        "skills": {},
        "career_history": [],  # Track career progression and generation events
        "skill_eligibility": 0,  # Track available skill points
        "seed": 77
    }

def roll_2d6(random_generator: random.Random) -> int:
    """
    Roll 2d6 using the provided random generator
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        
    Returns:
        Sum of two six-sided dice
    """
    return random_generator.randint(1, 6) + random_generator.randint(1, 6)

def generate_characteristic(random_generator: random.Random, characteristic: str) -> int:
    """
    Generate a value for a single characteristic
    
    Args:
        random_generator: The base random generator with the user's seed
        characteristic: The characteristic to generate ('strength', 'dexterity', etc.)
        
    Returns:
        Generated value for the characteristic (2-12)
    """
    # Create a characteristic-specific random generator
    original_state = random_generator.getstate()
    char_seed = f"{random_generator.random()}_{characteristic}"
    characteristic_random_generator = random.Random(char_seed)
    
    # Generate the value
    value = roll_2d6(characteristic_random_generator)
    
    # Restore the original state
    random_generator.setstate(original_state)
    
    return value

def get_enlistment_target(service: str) -> int:
    """
    Get the target number needed for enlistment in a specific service
    
    Args:
        service: The service to enlist in ('Navy', 'Marines', 'Army', etc.)
        
    Returns:
        Target number for enlistment roll
    """
    enlistment_targets = {
        'Navy': 8,
        'Marines': 9,
        'Army': 5,
        'Scouts': 7,
        'Merchants': 7,
        'Others': 3
    }
    return enlistment_targets.get(service, 5)  # Default to 5 for unknown services

def get_enlistment_modifiers(characteristics: dict[str, int], service: str) -> Tuple[int, List[str]]:
    """
    Calculate modifiers for enlistment based on characteristics
    
    Args:
        characteristics: Dictionary of character characteristics
        service: The service to enlist in
        
    Returns:
        Tuple of (total modifier, list of modifier descriptions)
    """
    modifiers = []
    total_modifier = 0
    
    # Define characteristic requirements and bonuses for each service
    service_bonuses = {
        'Navy': [('intelligence', 8, 1), ('education', 9, 2)],
        'Marines': [('intelligence', 8, 1), ('strength', 8, 2)],
        'Army': [('dexterity', 6, 1), ('endurance', 5, 2)],
        'Scouts': [('intelligence', 6, 1), ('strength', 8, 2)],
        'Merchants': [('strength', 7, 1), ('intelligence', 6, 2)],
        'Others': []
    }
    
    # Apply modifiers based on characteristics
    for char, req, bonus in service_bonuses.get(service, []):
        if characteristics.get(char, 0) >= req:
            total_modifier += bonus
            modifiers.append(f"{char.capitalize()} {characteristics.get(char, 0)}≥{req} (+{bonus})")
    
    return total_modifier, modifiers

def get_available_services() -> List[str]:
    """
    Get list of available services for enlistment
    
    Returns:
        List of service names
    """
    return ['Navy', 'Marines', 'Army', 'Scouts', 'Merchants', 'Others']

def get_draft_service(random_generator: random.Random) -> str:
    """
    Determine which service a character is drafted into
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        
    Returns:
        Service name
    """
    # Roll 1d6 for draft service (uniform distribution)
    services = get_available_services()
    roll = random_generator.randint(1, 6)
    return services[roll - 1]  # Convert 1-6 to 0-5 index

def attempt_enlistment(random_generator: random.Random, character_record: dict[str, Any], service_choice: str) -> dict[str, Any]:

    """
    Attempt to enlist a character in their chosen service
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        character_record: The character's record
        service_choice: The service the character is attempting to join
        
    Returns:
        Updated character record with enlistment results
    """
    # Get target number for chosen service
    target = get_enlistment_target(service_choice)
    
    # Calculate modifiers
    modifier, modifier_details = get_enlistment_modifiers(character_record["characteristics"], service_choice)
    
    # Roll for enlistment
    roll = roll_2d6(random_generator)
    total = roll + modifier
    success = total >= target
    
    # Record the enlistment attempt
    enlistment_result = {
        "event_type": "enlistment_attempt",
        "service": service_choice,
        "roll": roll,
        "modifier": modifier,
        "modifier_details": modifier_details,
        "target": target,
        "total": total,
        "success": success
    }
    
        # Update character record based on result
    if success:
        # Successfully enlisted in chosen service
        character_record["career"] = service_choice
        enlistment_result["outcome"] = "enlisted"
        enlistment_result["assigned_service"] = service_choice
    else:
        # Failed enlistment, drafted into random service
        drafted_service = get_draft_service(random_generator)
        character_record["career"] = drafted_service
        character_record["drafted"] = True
        enlistment_result["outcome"] = "drafted"
        enlistment_result["assigned_service"] = drafted_service

    # Grant skill eligibilities for the upcoming term
    # First term gets +2 eligibilities, subsequent terms get +1 (+2 for Scouts)
    current_terms = character_record.get("terms_served", 0)
    assigned_service = enlistment_result["assigned_service"]
    
    if current_terms == 0:
        # First term - always +2 eligibilities
        skill_eligibilities_granted = 2
    else:
        # Subsequent terms - +1 for most careers, +2 for Scouts
        skill_eligibilities_granted = 2 if assigned_service == "Scouts" else 1
    
    character_record["skill_eligibility"] = character_record.get("skill_eligibility", 0) + skill_eligibilities_granted
    enlistment_result["skill_eligibilities_granted"] = skill_eligibilities_granted

    # Add the enlistment attempt to the character's history
    character_record["career_history"].append(enlistment_result)
    
    return character_record

def check_survival(random_generator: random.Random, character_record: dict[str, Any], death_rule_enabled: bool = False) -> dict[str, Any]:
    """
    Check if a character survives their current term and update the character record
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        character_record: The character's record
        death_rule_enabled: Whether character can die on failed survival rolls (default: False)
        
    Returns:
        Updated character record with survival results and term structure
    """
    # Get career and characteristics
    career = character_record["career"]
    characteristics = character_record.get("characteristics", {})
    
    # Get survival target number
    survival_targets = {
        'Navy': 5,
        'Marines': 6,
        'Army': 5,
        'Scouts': 7,
        'Merchants': 5,
        'Others': 5
    }
    target = survival_targets.get(career, 5)
    
    # Define characteristic bonuses for each career
    survival_bonuses = {
        'Navy': [('intelligence', 7, 2)],
        'Marines': [('endurance', 8, 2)],
        'Army': [('education', 6, 2)],
        'Scouts': [('endurance', 9, 2)],
        'Merchants': [('intelligence', 7, 2)],
        'Others': [('intelligence', 9, 2)]
    }
    career_bonuses = survival_bonuses.get(career, [])
    
    # Calculate modifiers based on characteristics
    modifier = 0
    modifier_details = []
    
    # Apply modifiers based on characteristics
    for char, req, bonus in career_bonuses:
        if characteristics.get(char, 0) >= req:
            modifier += bonus
            modifier_details.append(f"{char.capitalize()} {characteristics.get(char, 0)}≥{req} (+{bonus})")
    
    # Roll for survival
    roll = roll_2d6(random_generator)
    total = roll + modifier
    survived = total >= target
    
    # Determine outcome
    if survived:
        outcome = "survived"
    else:
        outcome = "died" if death_rule_enabled else "injured"
    
    # Create the survival result
    survival_result = {
        "event_type": "survival_check",
        "career": career,
        "roll": roll,
        "modifier": modifier,
        "modifier_details": modifier_details,
        "target": target,
        "total": total,
        "success": survived,
        "outcome": outcome
    }
    
    # Calculate current term number
    current_term = int(character_record.get("terms_served", 0)) + 1
    
    # Create term record
    term_record = {
        "term_number": current_term,
        "survival": outcome
    }
    
    # Initialize terms structure if it doesn't exist
    if "terms" not in character_record:
        character_record["terms"] = []
    
    # Add the term record to the character's terms
    character_record["terms"].append(term_record)
    
    # Add the survival check to the character's career history
    character_record["career_history"].append(survival_result)
    
    # Update character record based on outcome
    if survived:
        # Complete term (add 4 years)
        character_record["age"] = character_record.get("age", 18) + 4
        character_record["terms_served"] = character_record.get("terms_served", 0) + 1
    else:
        # Partial term (add 2 years)
        character_record["age"] = character_record.get("age", 18) + 2
        character_record["terms_served"] = character_record.get("terms_served", 0) + 0.5
    
    return character_record

def check_commission(random_generator: random.Random, character_record: dict[str, Any]) -> dict[str, Any]:
    """
    Check if a character receives a commission during their current term and update the character record
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        character_record: The character's record
        
    Returns:
        Updated character record with commission results
    """
    # Get career and characteristics
    career = character_record["career"]
    characteristics = character_record.get("characteristics", {})
    
    # Create the commission result structure
    commission_result = {
        "event_type": "commission_check",
        "career": career,
    }
    
    # Check if character is already commissioned (can only happen once in a career)
    if character_record.get("commissioned", False):
        # Already commissioned
        commission_result["applicable"] = False
        commission_result["reason"] = "Already commissioned"
        commission_result["success"] = False
        commission_result["outcome"] = "not applicable"
        
        # Add the commission check to the character's career history
        character_record["career_history"].append(commission_result)
        return character_record
    
    # Check if character is eligible for commission
    if career in ['Scouts', 'Others']:
        # These careers don't have commissions
        commission_result["applicable"] = False
        commission_result["reason"] = f"{career} does not have commissions"
        commission_result["success"] = False
        commission_result["outcome"] = "not applicable"
        
        # Add the commission check to the character's career history
        character_record["career_history"].append(commission_result)
        return character_record
    
    if character_record.get("drafted", False) and character_record.get("terms_served", 0) < 1:
        # Drafted characters cannot be commissioned in their first term
        commission_result["applicable"] = False
        commission_result["reason"] = "Drafted characters cannot be commissioned in first term"
        commission_result["success"] = False
        commission_result["outcome"] = "not applicable"
        
        # Add the commission check to the character's career history
        character_record["career_history"].append(commission_result)
        return character_record
    
    # Character is eligible for commission
    commission_result["applicable"] = True
    
    # Define commission target numbers
    commission_targets = {
        'Navy': 10,
        'Marines': 9,
        'Army': 5,
        'Merchants': 4
    }
    target = commission_targets.get(career, 8)
    commission_result["target"] = target
    
    # Define characteristic bonuses for each career
    commission_bonuses = {
        'Navy': [('social', 9, 1)],
        'Marines': [('education', 7, 1)],
        'Army': [('endurance', 7, 1)],
        'Merchants': [('intelligence', 9, 1)]
    }
    career_bonuses = commission_bonuses.get(career, [])
    
    # Calculate modifiers based on characteristics
    modifier = 0
    modifier_details = []
    
    # Apply modifiers based on characteristics
    for char, req, bonus in career_bonuses:
        if characteristics.get(char, 0) >= req:
            modifier += bonus
            modifier_details.append(f"{char.capitalize()} {characteristics.get(char, 0)}≥{req} (+{bonus})")
    
    commission_result["modifier"] = modifier
    commission_result["modifier_details"] = modifier_details
    
    # Roll for commission
    roll = roll_2d6(random_generator)
    total = roll + modifier
    commissioned = total >= target
    
    commission_result["roll"] = roll
    commission_result["total"] = total
    commission_result["success"] = commissioned
    
    # Update character record based on outcome
    if commissioned:
        # Set commissioned flag in the main character record (permanent status)
        character_record["commissioned"] = True
        character_record["rank"] = 1
        commission_result["outcome"] = "commissioned as officer"
        
        # Grant +1 skill eligibility for successful commission
        character_record["skill_eligibility"] = character_record.get("skill_eligibility", 0) + 1
        commission_result["skill_eligibilities_granted"] = 1
        
        # Add commission information to the current term
        if "terms" in character_record and character_record["terms"]:
            current_term = character_record["terms"][-1]
            current_term["commission"] = True  # Record that commission happened in this term
    else:
        commission_result["outcome"] = "not commissioned"
        commission_result["skill_eligibilities_granted"] = 0
    
    # Add the commission check to the character's career history
    character_record["career_history"].append(commission_result)
    
    return character_record

def check_promotion(random_generator: random.Random, character_record: dict[str, Any]) -> dict[str, Any]:
    """
    Check if a character is promoted during their current term and update the character record
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        character_record: The character's record
        
    Returns:
        Updated character record with promotion results
    """
    # Get career and characteristics
    career = character_record["career"]
    characteristics = character_record.get("characteristics", {})
    current_rank = character_record.get("rank", 0)
    
    # Create the promotion result structure
    promotion_result = {
        "event_type": "promotion_check",
        "career": career,
        "current_rank": current_rank
    }
    
    # Check if character is eligible for promotion
    if not character_record.get("commissioned", False):
        # Character must be commissioned to be promoted
        promotion_result["applicable"] = False
        promotion_result["reason"] = "Character is not commissioned"
        promotion_result["success"] = False
        promotion_result["outcome"] = "not applicable"
        
        # Add the promotion check to the character's career history
        character_record["career_history"].append(promotion_result)
        return character_record
    
    if career in ['Scouts', 'Others']:
        # These careers don't have rank structure
        promotion_result["applicable"] = False
        promotion_result["reason"] = f"{career} does not have promotions"
        promotion_result["success"] = False
        promotion_result["outcome"] = "not applicable"
        
        # Add the promotion check to the character's career history
        character_record["career_history"].append(promotion_result)
        return character_record
    
    # Check for maximum rank limits
    max_ranks = {
        'Navy': 6,
        'Marines': 6,
        'Army': 6,
        'Merchants': 5
    }
    max_rank = max_ranks.get(career, 6)
    
    if current_rank >= max_rank:
        # Character has reached maximum rank for their career
        promotion_result["applicable"] = False
        promotion_result["reason"] = f"Character has reached maximum rank ({max_rank}) for {career}"
        promotion_result["success"] = False
        promotion_result["outcome"] = "not applicable"
        
        # Add the promotion check to the character's career history
        character_record["career_history"].append(promotion_result)
        return character_record
    
    # Character is eligible for promotion
    promotion_result["applicable"] = True
    
    # Define promotion target numbers
    promotion_targets = {
        'Navy': 8,
        'Marines': 9,
        'Army': 6,
        'Merchants': 10
    }
    target = promotion_targets.get(career, 8)
    promotion_result["target"] = target
    
    # Define characteristic bonuses for each career
    promotion_bonuses = {
        'Navy': [('education', 8, 1)],
        'Marines': [('social', 8, 1)],
        'Army': [('education', 7, 1)],
        'Merchants': [('intelligence', 9, 1)]
    }
    career_bonuses = promotion_bonuses.get(career, [])
    
    # Calculate modifiers based on characteristics
    modifier = 0
    modifier_details = []
    
    # Apply modifiers based on characteristics
    for char, req, bonus in career_bonuses:
        if characteristics.get(char, 0) >= req:
            modifier += bonus
            modifier_details.append(f"{char.capitalize()} {characteristics.get(char, 0)}≥{req} (+{bonus})")
    
    promotion_result["modifier"] = modifier
    promotion_result["modifier_details"] = modifier_details
    
    # Roll for promotion
    roll = roll_2d6(random_generator)
    total = roll + modifier
    promoted = total >= target
    
    promotion_result["roll"] = roll
    promotion_result["total"] = total
    promotion_result["success"] = promoted
    
    # Update character record based on outcome
    if promoted:
        new_rank = current_rank + 1
        character_record["rank"] = new_rank
        promotion_result["outcome"] = f"promoted to rank {new_rank}"
        
        # Grant +1 skill eligibility for successful promotion
        character_record["skill_eligibility"] = character_record.get("skill_eligibility", 0) + 1
        promotion_result["skill_eligibilities_granted"] = 1
        
        # Add promotion information to the current term
        if "terms" in character_record and character_record["terms"]:
            current_term = character_record["terms"][-1]
            if "promotions" not in current_term:
                current_term["promotions"] = []
            current_term["promotions"].append({
                "from_rank": current_rank,
                "to_rank": new_rank
            })
    else:
        promotion_result["outcome"] = "not promoted"
        promotion_result["skill_eligibilities_granted"] = 0
    
    # Add the promotion check to the character's career history
    character_record["career_history"].append(promotion_result)
    
    return character_record

def attempt_reenlistment(random_generator: random.Random, character_record: dict[str, Any], preference: str = 'reenlist') -> dict[str, Any]:
    """
    Attempt to reenlist a character for another term of service
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        character_record: The character's record
        preference: Character's preference ('reenlist', 'discharge', or 'retire')
        
    Returns:
        Updated character record with reenlistment results
        
    Raises:
        ValueError: If required fields are missing from the character record
    """
    # Validate required fields
    if "career" not in character_record:
        raise ValueError("Character record missing required field: 'career'")
    if "age" not in character_record:
        raise ValueError("Character record missing required field: 'age'")
    
    # Get career
    career = character_record["career"]
    age = character_record["age"]
    # Define reenlistment target numbers
    reenlistment_targets = {
        'Navy': 6,
        'Marines': 6,
        'Army': 7,
        'Scouts': 3,
        'Merchants': 4,
        'Others': 5
    }
    # Ensure career is one of the valid options
    assert career in reenlistment_targets, f"Invalid career: {career}"
    target = reenlistment_targets[career]
    
    # Roll for reenlistment
    roll = roll_2d6(random_generator)
    
    # Create the reenlistment result structure
    reenlistment_result = {
        "event_type": "reenlistment_attempt",
        "career": career,
        "age": character_record["age"],
        "preference": preference,
        "roll": roll,
        "target": target
    }
    
    # Determine outcome based on preference and roll
    if roll == 12:
        # Roll of 12 is always mandatory retention
        outcome = "retained"
        status_text = "retained (mandatory)"
        continue_career = True
    elif preference == "reenlist":
        # Character wants to stay
        if roll >= target:
            outcome = "reenlisted"
            status_text = "reenlisted"
            continue_career = True
        else:
            outcome = "discharged"
            status_text = "military discharge"
            continue_career = False
    elif preference in ["discharge", "retire"]:
        # Character wants to leave - gets their wish unless roll is 12
        if roll == 12:
            outcome = "retained"
            status_text = "retained (mandatory)"
            continue_career = True
        else:
            outcome = preference + "d" if preference == "discharge" else "retired"
            status_text = outcome
            continue_career = False
    
    # Add outcome information to the result
    reenlistment_result["outcome"] = outcome
    reenlistment_result["status_text"] = status_text
    reenlistment_result["continue_career"] = continue_career
    
    # Grant skill eligibilities for the NEXT term if continuing career
    if continue_career:
        # Subsequent terms get +1 eligibility (+2 for Scouts)
        skill_eligibilities_granted = 2 if career == "Scouts" else 1
        character_record["skill_eligibility"] = character_record.get("skill_eligibility", 0) + skill_eligibilities_granted
        reenlistment_result["skill_eligibilities_granted"] = skill_eligibilities_granted
    else:
        reenlistment_result["skill_eligibilities_granted"] = 0
    
    # Update the current term record with reenlistment information
    if "terms" in character_record and character_record["terms"]:
        current_term = character_record["terms"][-1]
        current_term["reenlistment"] = {
            "preference": preference,
            "roll": roll,
            "target": target,
            "outcome": outcome
        }
    
    # Add the reenlistment attempt to the character's career history
    character_record["career_history"].append(reenlistment_result)
    
    # If drafted and successfully reenlisted, change status to enlisted
    if character_record.get("drafted", False) and continue_career:
        character_record["drafted"] = False
        
        # Record the status change in career history
        status_change_event = {
            "event_type": "status_change",
            "career": career,
            "from": "drafted",
            "to": "enlisted",
            "reason": "successful reenlistment"
        }
        character_record["career_history"].append(status_change_event)
    
    return character_record

def get_available_skill_tables(character_record: dict[str, Any]) -> dict[str, bool]:
    """
    Determine which skill tables are available to the character
    
    Args:
        character_record: The character's record
        
    Returns:
        Dictionary of available skill tables with boolean values
    """
    # All characters have access to these three tables
    available_tables = {
        'personal': True,
        'service': True,
        'advanced': True,
        'education': False  # Default to False
    }
    
    # Check if character has education 8+ for education table
    education = character_record.get("characteristics", {}).get("education", 0)
    if education >= 8:
        available_tables['education'] = True
    
    return available_tables

def get_skill_eligibility_count(character_record: dict[str, Any]) -> int:
    """
    Get the number of skill eligibilities available to the character
    
    Args:
        character_record: The character's record
        
    Returns:
        Number of skill eligibilities available
    """
    return character_record.get("skill_eligibility", 0)

def resolve_skill(random_generator: random.Random, character_record: dict[str, Any], 
                  table_choice: Optional[str] = None) -> dict[str, Any]:
    """
    Resolve a skill gain for a character
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        character_record: The character's record
        table_choice: The player's chosen skill table (optional)
        
    Returns:
        Updated character record with the new skill and skill resolution event
    """
    # Validate required fields
    if "career" not in character_record:
        raise ValueError("Character record missing required field: 'career'")
    
    # Check if character has skill eligibilities available
    skill_eligibility = character_record.get("skill_eligibility", 0)
    if skill_eligibility <= 0:
        raise ValueError("Character has no skill eligibilities available")
    
    # Get career
    career = character_record["career"]
    
    # Define skill tables for each career
    skill_tables = {
        'Navy': {
            'personal': ['+1 STR', '+1 DEX', '+1 END', '+1 INT', '+1 EDU', '+1 SOC'],
            'service': ['Ship\'s Boat', 'Vacc Suit', 'Forward Observer', 'Gunnery', 'Blade Combat', 'Gun Combat'],
            'advanced': ['Vacc Suit', 'Mechanical', 'Electronic', 'Engineering', 'Gunnery', 'Jack-of-all-Trades'],
            'education': ['Medical', 'Navigation', 'Engineering', 'Computer', 'Pilot', 'Admin']
        },
        'Marines': {
            'personal': ['+1 STR', '+1 DEX', '+1 END', 'Gambling', 'Brawling', 'Blade Combat'],
            'service': ['Vehicle', 'Vacc Suit', 'Blade Combat', 'Gun Combat', 'Blade Combat', 'Gun Combat'],
            'advanced': ['Vehicle', 'Mechanical', 'Electronic', 'Tactics', 'Blade Combat', 'Gun Combat'],
            'education': ['Medical', 'Tactics', 'Tactics', 'Computer', 'Leader', 'Admin']
        },
        'Army': {
            'personal': ['+1 STR', '+1 DEX', '+1 END', 'Gambling', '+1 EDU', 'Brawling'],
            'service': ['Vehicle', 'Air/Raft', 'Gun Combat', 'Forward Observer', 'Blade Combat', 'Gun Combat'],
            'advanced': ['Vehicle', 'Mechanical', 'Electronic', 'Tactics', 'Blade Combat', 'Gun Combat'],
            'education': ['Medical', 'Tactics', 'Tactics', 'Computer', 'Leader', 'Admin']
        },
        'Scouts': {
            'personal': ['+1 STR', '+1 DEX', '+1 END', '+1 INT', '+1 EDU', 'Gun Combat'],
            'service': ['Vehicle', 'Vacc Suit', 'Mechanical', 'Navigation', 'Electronics', 'Jack-of-all-Trades'],
            'advanced': ['Vehicle', 'Mechanical', 'Electronic', 'Jack-of-all-Trades', 'Gunnery', 'Medical'],
            'education': ['Medical', 'Navigation', 'Engineering', 'Computer', 'Pilot', 'Jack-of-all-Trades']
        },
        'Merchants': {
            'personal': ['+1 STR', '+1 DEX', '+1 END', 'Blade Combat', 'Bribery', '+1 INT'],
            'service': ['Vehicle', 'Vacc Suit', 'Jack-of-all-Trades', 'Steward', 'Electronics', 'Gun Combat'],
            'advanced': ['Streetwise', 'Mechanical', 'Electronic', 'Navigation', 'Engineering', 'Computer'],
            'education': ['Medical', 'Navigation', 'Engineering', 'Computer', 'Pilot', 'Admin']
        },
        'Others': {
            'personal': ['+1 STR', '+1 DEX', '+1 END', 'Blade Combat', 'Brawling', '+1 SOC'],
            'service': ['Vehicle', 'Gambling', 'Brawling', 'Bribery', 'Blade Combat', 'Gun Combat'],
            'advanced': ['Streetwise', 'Mechanical', 'Electronic', 'Gambling', 'Brawling', 'Forgery'],
            'education': ['Medical', 'Forgery', 'Electronics', 'Computer', 'Streetwise', 'Jack-of-all-Trades']
        }
    }
    
    # Get available skill tables
    available_tables = get_available_skill_tables(character_record)
    
    # Create the skill resolution event
    skill_event = {
        "event_type": "skill_resolution",
        "career": career,
        "available_tables": available_tables,
    }
    
    # If no table choice provided, randomly select one
    if table_choice is None:
        # Filter to only available tables
        valid_tables = [table for table, available in available_tables.items() if available]
        if not valid_tables:
            raise ValueError("No valid skill tables available")
        table_choice = random_generator.choice(valid_tables)
        skill_event["table_choice_method"] = "random"
    else:
        # Validate table choice
        if table_choice not in available_tables:
            raise ValueError(f"Invalid table choice: {table_choice}")
        if not available_tables[table_choice]:
            raise ValueError(f"Table not available: {table_choice}")
        skill_event["table_choice_method"] = "player"
    
    skill_event["table_choice"] = table_choice
    
    # Get the skill table for the career
    career_tables = skill_tables.get(career, skill_tables['Others'])
    
    # Ensure the table exists for this career
    if table_choice not in career_tables:
        raise ValueError(f"Table {table_choice} not found for career {career}")
    
    table = career_tables[table_choice]
    
    # Roll 1d6 to determine which skill is gained
    roll = random_generator.randint(1, 6)
    # Ensure index is valid
    if roll < 1 or roll > 6 or roll > len(table):
        raise ValueError(f"Invalid roll {roll} for table with {len(table)} entries")
    
    # Get the skill result (guaranteed to be a string from our defined tables)
    skill_name = table[roll - 1]
    
    skill_event["roll"] = roll
    skill_event["skill_gained"] = skill_name
    
    # Process the skill result
    if skill_name.startswith('+1'):
        # This is a characteristic increase
        char_short = skill_name.split()[1]  # Get the short form (STR, DEX, etc.)
        
        # Map the short form to the full characteristic name
        char_map = {
            'STR': 'strength',
            'DEX': 'dexterity',
            'END': 'endurance',
            'INT': 'intelligence',
            'EDU': 'education',
            'SOC': 'social'
        }
        
        characteristic = char_map.get(char_short, '').lower()
        
        # Update the characteristic
        if characteristic and characteristic in character_record.get("characteristics", {}):
            old_value = character_record["characteristics"][characteristic]
            character_record["characteristics"][characteristic] += 1
            new_value = character_record["characteristics"][characteristic]
            
            skill_event["result_type"] = "characteristic_increase"
            skill_event["characteristic"] = characteristic
            skill_event["old_value"] = old_value
            skill_event["new_value"] = new_value
        else:
            # Characteristic not found, log error
            skill_event["result_type"] = "error"
            skill_event["error"] = f"Characteristic {char_short} could not be mapped or not found in character record"
    else:
        # This is a regular skill
        skill_event["result_type"] = "skill_gain"
        
        # Initialize skills if not present
        if "skills" not in character_record:
            character_record["skills"] = {}
        
        # Add skill or increase level
        if skill_name in character_record["skills"]:
            character_record["skills"][skill_name] += 1
        else:
            character_record["skills"][skill_name] = 1
    
    # Consume one skill eligibility
    character_record["skill_eligibility"] = character_record.get("skill_eligibility", 0) - 1
    skill_event["skill_eligibilities_consumed"] = 1
    skill_event["skill_eligibilities_remaining"] = character_record["skill_eligibility"]
    
    # Add the skill resolution event to the character's career history
    character_record["career_history"].append(skill_event)
    
    # Add skill information to the current term
    if "terms" in character_record and character_record["terms"]:
        current_term = character_record["terms"][-1]
        if "skills_gained" not in current_term:
            current_term["skills_gained"] = []
        
        if skill_event["result_type"] == "characteristic_increase":
            current_term["skills_gained"].append({
                "table": table_choice,
                "result": skill_name,
                "type": "characteristic_increase",
                "characteristic": skill_event["characteristic"],
                "old_value": skill_event["old_value"],
                "new_value": skill_event["new_value"]
            })
        else:
            # Get the skill level safely
            skill_level = character_record["skills"].get(skill_name, 0)
            current_term["skills_gained"].append({
                "table": table_choice,
                "result": skill_name,
                "type": "skill_gain",
                "skill": skill_name,
                "level": skill_level
            })
    
    return character_record

if __name__ == "__main__":
    """
    Module guard - this code only runs when the module is executed directly
    """
    print("Classic Traveller Character Generation API")
    print("This module is designed to be imported, not run directly.")
    print("See traveller_term_demo.py for example usage.")
