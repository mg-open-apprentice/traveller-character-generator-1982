#!/usr/bin/env python3
"""
Simple test to verify the main fixes:
1. Terms increment on reenlistment
2. Commission only happens once
"""

import character_generation_rules as chargen
import random

def test_main_fixes():
    """Test the main fixes we made"""
    print("Testing Main Fixes")
    print("=" * 40)
    
    # Set up RNG
    rng = chargen.set_seed(42)
    
    # Create a character
    print("1. Creating character...")
    character = chargen.create_character_record()
    character["name"] = chargen.generate_character_name(rng)
    
    # Generate characteristics
    for char_name in ["strength", "dexterity", "endurance", "intelligence", "education", "social"]:
        value = chargen.generate_characteristic(rng, char_name)
        character["characteristics"][char_name] = value
    
    print(f"Character: {character['name']}")
    print(f"Initial age: {character['age']}, terms: {character.get('terms_served', 0)}")
    print(f"Commissioned: {character.get('commissioned', False)}")
    
    # Enlist in Navy
    print("\n2. Enlisting in Navy...")
    character = chargen.attempt_enlistment(rng, character, "Navy")
    print(f"Career: {character['career']}")
    
    # Complete first term
    print("\n3. Completing first term...")
    
    # Survival
    character = chargen.check_survival(rng, character)
    print(f"Survival: {character['career_history'][-1]['outcome']}")
    
    # Commission (should work)
    character = chargen.check_commission(rng, character)
    commission_result = character['career_history'][-1]
    print(f"Commission: {commission_result['outcome']}")
    print(f"Commissioned status: {character.get('commissioned', False)}")
    
    # Try commission again (should fail)
    print("\n4. Trying commission again...")
    character = chargen.check_commission(rng, character)
    commission_result2 = character['career_history'][-1]
    print(f"Second commission: {commission_result2['outcome']}")
    print(f"Reason: {commission_result2.get('reason', 'No reason')}")
    
    # Promotion
    character = chargen.check_promotion(rng, character)
    print(f"Promotion: {character['career_history'][-1]['outcome']}")
    
    # Reenlistment
    print("\n5. Reenlistment...")
    print(f"Terms before: {character.get('terms_served', 0)}")
    print(f"Age before: {character['age']}")
    
    character = chargen.attempt_reenlistment(rng, character, "reenlist")
    reenlistment_result = character['career_history'][-1]
    
    print(f"Reenlistment: {reenlistment_result['outcome']}")
    print(f"Terms after: {character.get('terms_served', 0)}")
    print(f"Age after: {character['age']}")
    print(f"Continue career: {reenlistment_result.get('continue_career', False)}")
    print(f"Commissioned: {character.get('commissioned', False)}")
    
    # Verify fixes
    print("\n" + "=" * 40)
    print("VERIFICATION:")
    
    # Check terms increment
    if character.get('terms_served', 0) > 0:
        print("✅ Terms increment: WORKING")
    else:
        print("❌ Terms increment: FAILED")
    
    # Check commission only once
    if character.get('commissioned', False) and commission_result2.get('outcome') == 'not applicable':
        print("✅ Commission once: WORKING")
    else:
        print("❌ Commission once: FAILED")
    
    # Check age increment
    if character['age'] > 18:
        print("✅ Age increment: WORKING")
    else:
        print("❌ Age increment: FAILED")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_main_fixes() 