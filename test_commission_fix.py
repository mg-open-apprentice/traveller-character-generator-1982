#!/usr/bin/env python3
"""
Test to verify commission only happens once by creating a character that will pass commission
"""

import character_generation_rules as chargen
import random

def test_commission_once():
    """Test that commission only happens once"""
    print("Testing Commission Only Once")
    print("=" * 40)
    
    # Set up RNG with a seed that gives good characteristics
    rng = chargen.set_seed(123)  # Different seed
    
    # Create a character
    print("1. Creating character...")
    character = chargen.create_character_record()
    character["name"] = chargen.generate_character_name(rng)
    
    # Generate characteristics
    for char_name in ["strength", "dexterity", "endurance", "intelligence", "education", "social"]:
        value = chargen.generate_characteristic(rng, char_name)
        character["characteristics"][char_name] = value
    
    print(f"Character: {character['name']}")
    print(f"Characteristics: {character['characteristics']}")
    print(f"Initial commissioned: {character.get('commissioned', False)}")
    
    # Enlist in Navy
    print("\n2. Enlisting in Navy...")
    character = chargen.attempt_enlistment(rng, character, "Navy")
    print(f"Career: {character['career']}")
    
    # Survival
    print("\n3. Survival check...")
    character = chargen.check_survival(rng, character)
    print(f"Survival: {character['career_history'][-1]['outcome']}")
    
    # Commission (first attempt)
    print("\n4. First commission attempt...")
    character = chargen.check_commission(rng, character)
    commission_result = character['career_history'][-1]
    print(f"Commission outcome: {commission_result['outcome']}")
    print(f"Commission success: {commission_result.get('success', False)}")
    print(f"Commissioned status: {character.get('commissioned', False)}")
    
    # Commission (second attempt - should fail)
    print("\n5. Second commission attempt...")
    character = chargen.check_commission(rng, character)
    commission_result2 = character['career_history'][-1]
    print(f"Second commission outcome: {commission_result2['outcome']}")
    print(f"Second commission success: {commission_result2.get('success', False)}")
    print(f"Reason: {commission_result2.get('reason', 'No reason')}")
    print(f"Commissioned status: {character.get('commissioned', False)}")
    
    # Verify the fix
    print("\n" + "=" * 40)
    print("VERIFICATION:")
    
    if commission_result.get('success', False):
        print("✅ First commission: SUCCESSFUL")
    else:
        print("❌ First commission: FAILED")
    
    if commission_result2.get('outcome') == 'not applicable' and 'Already commissioned' in commission_result2.get('reason', ''):
        print("✅ Second commission: CORRECTLY BLOCKED")
    else:
        print("❌ Second commission: NOT BLOCKED")
    
    if character.get('commissioned', False):
        print("✅ Character commissioned: TRUE")
    else:
        print("❌ Character commissioned: FALSE")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_commission_once() 