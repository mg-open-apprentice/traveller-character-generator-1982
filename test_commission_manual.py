#!/usr/bin/env python3
"""
Test to verify commission only happens once by manually setting up a character
"""

import character_generation_rules as chargen
import random

def test_commission_once_manual():
    """Test that commission only happens once with manual setup"""
    print("Testing Commission Only Once (Manual Setup)")
    print("=" * 50)
    
    # Set up RNG
    rng = chargen.set_seed(42)
    
    # Create a character manually
    print("1. Creating character manually...")
    character = chargen.create_character_record()
    character["name"] = "Test Character"
    
    # Set good characteristics for Navy commission
    character["characteristics"] = {
        "strength": 8,
        "dexterity": 8, 
        "endurance": 8,
        "intelligence": 8,
        "education": 8,
        "social": 10  # Good for Navy commission
    }
    
    print(f"Character: {character['name']}")
    print(f"Social: {character['characteristics']['social']} (needs 9+ for Navy commission)")
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
    print("\n" + "=" * 50)
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
    test_commission_once_manual() 