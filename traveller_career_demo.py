#!/usr/bin/env python3
# Classic Traveller Character Generation Demo - Career Flow
# This script demonstrates the integrated career flow from enlistment through terms

import random
import json
from typing import Any, List

# Import the character generation functions directly
from character_generation_rules import (
    set_seed,
    generate_characteristic,
    create_character_record,
    generate_character_name,
    get_available_services,
    get_enlistment_target,
    get_enlistment_modifiers,
    attempt_enlistment,
    check_survival,
    check_commission,
    check_promotion,
    attempt_reenlistment,
    get_available_skill_tables,
    resolve_skill
)

def calculate_2d6_probability(target: int, modifier: int = 0) -> float:
    """
    Calculate the probability of rolling target or higher on 2d6 with a modifier
    
    Args:
        target: The target number to meet or exceed
        modifier: Any modifier to add to the roll
        
    Returns:
        Probability as a percentage (0-100)
    """
    # Adjust target by modifier
    adjusted_target = max(2, target - modifier)
    
    # Count favorable outcomes
    favorable_outcomes = 0
    total_outcomes = 36  # 6x6 possible combinations on 2d6
    
    # Count how many combinations meet or exceed the target
    for die1 in range(1, 7):
        for die2 in range(1, 7):
            if die1 + die2 >= adjusted_target:
                favorable_outcomes += 1
    
    # Calculate probability as percentage
    probability = (favorable_outcomes / total_outcomes) * 100
    
    return probability

def generate_characteristics_set(random_generator: random.Random) -> dict[str, int]:
    """
    Generate a complete set of characteristics for a character
    
    Args:
        random_generator: An instance of random.Random with the user's seed
        
    Returns:
        Dictionary of characteristics
    """
    characteristics = {}
    for char in ["strength", "dexterity", "endurance", "intelligence", "education", "social"]:
        characteristics[char] = generate_characteristic(random_generator, char)
    return characteristics

def display_characteristics(characteristics: dict[str, int]) -> None:
    """
    Display a character's characteristics in a readable format
    
    Args:
        characteristics: Dictionary of characteristics
    """
    print("Characteristics:")
    print(f"  Strength:     {characteristics.get('strength', 0)}")
    print(f"  Dexterity:    {characteristics.get('dexterity', 0)}")
    print(f"  Endurance:    {characteristics.get('endurance', 0)}")
    print(f"  Intelligence: {characteristics.get('intelligence', 0)}")
    print(f"  Education:    {characteristics.get('education', 0)}")
    print(f"  Social:       {characteristics.get('social', 0)}")

def display_enlistment_result(result: dict[str, Any]) -> None:
    """
    Display the results of an enlistment attempt
    
    Args:
        result: Dictionary containing enlistment result details
    """
    print(f"\nEnlistment attempt for {result['service']}:")
    print(f"  Target: {result['target']}")
    
    # Calculate and display probability
    probability = calculate_2d6_probability(result['target'], result['modifier'])
    print(f"  Probability: {probability:.1f}%")
    
    print(f"  Roll: {result['roll']}")
    
    if result['modifier_details']:
        print("  Modifiers:")
        for mod in result['modifier_details']:
            print(f"    {mod}")
        print(f"  Total modifier: +{result['modifier']}")
    else:
        print("  No modifiers apply")
    
    print(f"  Final roll: {result['total']}")
    
    if result['success']:
        print(f"✅ SUCCESS: Enlisted in {result['assigned_service']}")
    else:
        print(f"❌ FAILED: Drafted into {result['assigned_service']}")

def display_survival_result(result: dict[str, Any]) -> None:
    """
    Display the results of a survival check
    
    Args:
        result: Dictionary containing survival check result details
    """
    print(f"\nSurvival check for {result['career']}:")
    print(f"  Target: {result['target']}")
    
    # Calculate and display probability
    probability = calculate_2d6_probability(result['target'], result['modifier'])
    print(f"  Probability: {probability:.1f}%")
    
    print(f"  Roll: {result['roll']}")
    
    if result['modifier_details']:
        print("  Modifiers:")
        for mod in result['modifier_details']:
            print(f"    {mod}")
        print(f"  Total modifier: +{result['modifier']}")
    else:
        print("  No modifiers apply")
    
    print(f"  Final roll: {result['total']}")
    
    if result['success']:
        print(f"✅ SUCCESS: Character survived the term")
    else:
        print(f"❌ FAILED: Character {result['outcome']}")

def display_commission_result(result: dict[str, Any]) -> None:
    """
    Display the results of a commission check
    
    Args:
        result: Dictionary containing commission check result details
    """
    print(f"\nCommission check for {result['career']}:")
    
    if not result.get('applicable', True):
        print(f"  Not applicable: {result.get('reason', 'Unknown reason')}")
        return
    
    print(f"  Target: {result['target']}")
    
    # Calculate and display probability
    probability = calculate_2d6_probability(result['target'], result['modifier'])
    print(f"  Probability: {probability:.1f}%")
    
    print(f"  Roll: {result['roll']}")
    
    if result['modifier_details']:
        print("  Modifiers:")
        for mod in result['modifier_details']:
            print(f"    {mod}")
        print(f"  Total modifier: +{result['modifier']}")
    else:
        print("  No modifiers apply")
    
    print(f"  Final roll: {result['total']}")
    
    if result['success']:
        print(f"✅ SUCCESS: Character commissioned as officer (Rank 1)")
    else:
        print(f"❌ FAILED: Character not commissioned")

def display_promotion_result(result: dict[str, Any]) -> None:
    """
    Display the results of a promotion check
    
    Args:
        result: Dictionary containing promotion check result details
    """
    print(f"\nPromotion check for {result['career']}:")
    
    if not result.get('applicable', True):
        print(f"  Not applicable: {result.get('reason', 'Unknown reason')}")
        return
    
    print(f"  Current rank: {result['current_rank']}")
    print(f"  Target: {result['target']}")
    
    # Calculate and display probability
    probability = calculate_2d6_probability(result['target'], result['modifier'])
    print(f"  Probability: {probability:.1f}%")
    
    print(f"  Roll: {result['roll']}")
    
    if result['modifier_details']:
        print("  Modifiers:")
        for mod in result['modifier_details']:
            print(f"    {mod}")
        print(f"  Total modifier: +{result['modifier']}")
    else:
        print("  No modifiers apply")
    
    print(f"  Final roll: {result['total']}")
    
    if result['success']:
        print(f"✅ SUCCESS: {result['outcome']}")
    else:
        print(f"❌ FAILED: Character not promoted")

def display_reenlistment_result(result: dict[str, Any]) -> None:
    """
    Display the results of a reenlistment attempt
    
    Args:
        result: Dictionary containing reenlistment result details
    """
    print(f"\nReenlistment attempt for {result['career']}:")
    if 'age' in result:
        print(f"  Age: {result['age']}")
    print(f"  Preference: {result['preference'].capitalize()}")
    print(f"  Target: {result['target']}")
    print(f"  Roll: {result['roll']}")
    
    # Display outcome with appropriate emoji
    if result['outcome'] == 'reenlisted':
        print(f"✅ SUCCESS: Character reenlisted")
    elif result['outcome'] == 'retained':
        print(f"⚠️ RETAINED: Character retained despite preference (roll of 12)")
    elif result['outcome'] == 'discharged':
        print(f"❌ FAILED: Character discharged from service")
    elif result['outcome'] == 'retired':
        print(f"🏆 RETIRED: Character retired from service")
    else:
        print(f"  Outcome: {result['status_text']}")

def display_service_options(character: dict[str, Any]) -> None:
    """
    Display available service options with enlistment targets and modifiers
    
    Args:
        character: Character record with characteristics
    """
    services = get_available_services()
    characteristics = character["characteristics"]
    
    print("\n🚀 Available Service Options:")
    print(f"{'Service':<10} {'Target':<8} {'Modifiers':<40}")
    print("-" * 60)
    
    for service in services:
        target = get_enlistment_target(service)
        modifier, modifier_details = get_enlistment_modifiers(characteristics, service)
        
        modifier_text = ", ".join([mod.split(" ")[0] for mod in modifier_details]) if modifier_details else "None"
        if len(modifier_text) > 38:
            modifier_text = modifier_text[:35] + "..."
            
        print(f"{service:<10} {target:<8} {modifier_text}")

def display_skill_resolution_result(result: dict[str, Any]) -> None:
    """
    Display the results of a skill resolution
    
    Args:
        result: Dictionary containing skill resolution result details
    """
    print(f"\n📚 Skill Resolution:")
    print(f"  Career: {result['career']}")
    print(f"  Table: {result['table_choice']} ({result['table_choice_method']})")
    print(f"  Roll: {result['roll']}")
    
    if result['result_type'] == 'characteristic_increase':
        print(f"✅ Characteristic increase: {result['skill_gained']}")
        print(f"  {result['characteristic'].capitalize()}: {result['old_value']} → {result['new_value']}")
    elif result['result_type'] == 'skill_gain':
        print(f"✅ Skill gained: {result['skill_gained']}")
    else:
        print(f"❌ ERROR: {result.get('error', 'Unknown error')}")

def run_career_demo(seed: int | None = None, preferred_service: str | None = None, num_terms: int = 1, reenlistment_preference: str = 'reenlist') -> dict[str, Any]:
    """
    Run a full career demonstration including enlistment and terms
    
    Args:
        seed: Random seed for reproducible results (optional)
        preferred_service: The service the character prefers to join (optional)
        num_terms: Number of terms to serve (default: 1)
        reenlistment_preference: Character's preference for reenlistment ('reenlist', 'discharge', or 'retire')
        
    Returns:
        The character record with all career results
    """
    # Set up random generator with seed
    if seed is None:
        seed = random.randint(1, 999999)
    
    print(f"🎲 Using random seed: {seed}")
    random_generator = set_seed(seed)
    
    # Create a new character
    character = create_character_record()
    character["name"] = generate_character_name(random_generator)
    character["seed"] = seed
    
    # Generate characteristics
    character["characteristics"] = generate_characteristics_set(random_generator)
    
    # Display character information
    print(f"\n👤 Character: {character['name']}")
    display_characteristics(character["characteristics"])
    
    # Display service options
    display_service_options(character)
    
    # If no preferred service is provided, randomly choose one using the seed
    if preferred_service is None:
        services = get_available_services()
        preferred_service = random_generator.choice(services)
        print(f"\n🚀 No service preference provided. Randomly selected: {preferred_service}")
    else:
        print(f"\n🚀 Attempting to enlist in {preferred_service}...")
    
    # Attempt enlistment
    character = attempt_enlistment(random_generator, character, preferred_service)
    
    # Get the enlistment result
    enlistment_result = character["career_history"][-1]
    display_enlistment_result(enlistment_result)
    
    # Process terms
    for term in range(1, num_terms + 1):
        print(f"\n\n{'='*60}")
        print(f"Term {term} in {character['career']}")
        print(f"{'='*60}")
        
        # Track if commission or promotion happens in this term
        commissioned_this_term = False
        promoted_this_term = False
        
        # Check survival
        print("\n⚔️ Checking survival...")
        character = check_survival(random_generator, character)
        
        # Get the survival result
        survival_result = character["career_history"][-1]
        display_survival_result(survival_result)
        
        # If character didn't survive, end career
        if not survival_result["success"]:
            print(f"\n⚠️ Career ended due to {survival_result['outcome']}.")
            break
        
        # Check for commission (if not already commissioned)
        if not character.get("commissioned", False):
            print("\n🎖️ Checking for commission...")
            character = check_commission(random_generator, character)
            
            # Get the commission result
            commission_result = character["career_history"][-1]
            display_commission_result(commission_result)
            
            # Track if commissioned this term
            if commission_result.get("success", False):
                commissioned_this_term = True
        
        # Check for promotion (if commissioned)
        if character.get("commissioned", False):
            print("\n⭐ Checking for promotion...")
            character = check_promotion(random_generator, character)
            
            # Get the promotion result
            promotion_result = character["career_history"][-1]
            display_promotion_result(promotion_result)
            
            # Track if promoted this term
            if promotion_result.get("success", False):
                promoted_this_term = True
        
        # Determine how many skills to gain this term
        skill_count = 1  # Default: 1 skill per term
        
        # First term or Scouts get an extra skill
        if term == 1 or character['career'] == 'Scouts':
            skill_count = 2
        
        # Commission grants an extra skill
        if commissioned_this_term:
            skill_count += 1
        
        # Promotion grants an extra skill
        if promoted_this_term:
            skill_count += 1
        
        # Process skill gains
        print(f"\n📚 Gaining {skill_count} skills this term...")
        
        # Show available skill tables
        available_tables = get_available_skill_tables(character)
        print("  Available skill tables:")
        for table, available in available_tables.items():
            if available:
                print(f"    - {table}")
        
        for i in range(skill_count):
            print(f"\n  Skill #{i+1}:")
            # For demo purposes, randomly select a table
            character = resolve_skill(random_generator, character)
            
            # Get the skill resolution result
            skill_result = character["career_history"][-1]
            display_skill_resolution_result(skill_result)
        
        # Attempt reenlistment if not the last term
        if term < num_terms:
            print("\n🔄 Checking for reenlistment...")
            character = attempt_reenlistment(random_generator, character, preference=reenlistment_preference)
            
            # Get the reenlistment result
            reenlistment_result = character["career_history"][-1]
            display_reenlistment_result(reenlistment_result)
            
            # If character was not allowed to continue, end career
            if not reenlistment_result.get("continue_career", False):
                print(f"\n⚠️ Career ended due to failed reenlistment.")
                break
        
        # Display term summary
        print(f"\n📊 Term {term} Summary:")
        print(f"  Age: {character['age']}")
        print(f"  Terms served: {character['terms_served']}")
        if character.get("commissioned", False):
            print(f"  Rank: {character.get('rank', 1)}")
        
        # Display skills gained this term
        if "terms" in character and len(character["terms"]) >= term:
            current_term = character["terms"][term-1]
            if "skills_gained" in current_term:
                print("  Skills gained this term:")
                for skill_entry in current_term["skills_gained"]:
                    if skill_entry["type"] == "characteristic_increase":
                        print(f"    - {skill_entry['result']} ({skill_entry['characteristic'].capitalize()}: {skill_entry['old_value']} → {skill_entry['new_value']})")
                    else:
                        print(f"    - {skill_entry['skill']} (Level {skill_entry['level']})")
    
    # Final career summary
    print(f"\n\n{'='*60}")
    print(f"Final Career Summary for {character['name']}")
    print(f"{'='*60}")
    print(f"  Career: {character['career']}")
    print(f"  Age: {character['age']}")
    print(f"  Terms completed: {character['terms_served']}")
    if character.get("commissioned", False):
        print(f"  Final rank: {character.get('rank', 1)}")
    else:
        print("  Not commissioned")
    
    # Display final characteristics
    print("\n  Final Characteristics:")
    display_characteristics(character["characteristics"])
    
    # Display final skills
    if character.get("skills"):
        print("\n  Final Skills:")
        for skill, level in sorted(character["skills"].items()):
            print(f"    - {skill}: {level}")
    else:
        print("\n  No skills acquired")
    
    return character


# Execute the demo if the script is run directly
if __name__ == "__main__":
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Run a Classic Traveller character career demo")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible results")
    parser.add_argument("--service", type=str, choices=["Navy", "Marines", "Army", "Scouts", "Merchants", "Others"], 
                        help="Preferred service to enlist in")
    parser.add_argument("--terms", type=int, default=4, help="Number of terms to serve (default: 4)")
    parser.add_argument("--reenlist", type=str, choices=["reenlist", "discharge", "retire"], default="reenlist",
                        help="Reenlistment preference (default: reenlist)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the demo
    character = run_career_demo(
        seed=args.seed,
        preferred_service=args.service,
        num_terms=args.terms,
        reenlistment_preference=args.reenlist
    )
    
    # Save the character to a JSON file
    filename = f"traveller_character_{args.seed if args.seed else random.randint(1, 999999)}.json"
    with open(filename, "w") as f:
        json.dump(character, f, indent=2)
    print(f"\nCharacter saved to {filename}")

