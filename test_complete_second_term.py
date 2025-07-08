#!/usr/bin/env python3
"""
Test script to verify complete second term flow including survival
"""

import character_generation_rules as chargen

def test_complete_second_term():
    """Test the complete second term flow"""
    print("Testing Complete Second Term Flow")
    print("=" * 40)
    
    # Create character
    rng = chargen.set_seed(42)
    character = chargen.create_character_record()
    character["name"] = chargen.generate_character_name(rng)
    
    # Generate characteristics
    for char in ["strength", "dexterity", "endurance", "intelligence", "education", "social"]:
        character["characteristics"][char] = chargen.generate_characteristic(rng, char)
    
    print(f"Character: {character['name']}")
    print(f"Characteristics: {character['characteristics']}")
    
    # Enlist
    print("\n1. Enlistment...")
    character = chargen.attempt_enlistment(rng, character, "Navy")
    enlistment_result = character['career_history'][-1]
    print(f"Enlistment: {enlistment_result['outcome']}")
    
    # First term
    print("\n2. First Term...")
    
    # Survival
    print("   Survival...")
    character = chargen.check_survival(rng, character)
    survival_result = character['career_history'][-1]
    print(f"   Survival: {survival_result['outcome']}")
    
    # Commission
    print("   Commission...")
    character = chargen.check_commission(rng, character)
    commission_result = character['career_history'][-1]
    print(f"   Commission: {commission_result['outcome']}")
    
    # Promotion
    print("   Promotion...")
    character = chargen.check_promotion(rng, character)
    promotion_result = character['career_history'][-1]
    print(f"   Promotion: {promotion_result['outcome']}")
    
    # Skills
    print("   Skills...")
    available_tables = chargen.get_available_skill_tables(character)
    skill_eligibility = character.get("skill_eligibility", 0)
    ready_for_skills = chargen.is_ready_for_skills(character)
    print(f"   Skill eligibility: {skill_eligibility}")
    print(f"   Ready for skills: {ready_for_skills}")
    print(f"   Available tables: {available_tables}")
    
    # Use all skills
    while skill_eligibility > 0:
        character = chargen.resolve_skill(rng, character, "personal")
        skill_eligibility = character.get("skill_eligibility", 0)
        print(f"   Used skill, remaining: {skill_eligibility}")
    
    # Reenlistment
    print("\n3. Reenlistment...")
    print(f"Terms served before: {character.get('terms_served', 0)}")
    print(f"Age before: {character['age']}")
    
    character = chargen.attempt_reenlistment(rng, character, "reenlist")
    reenlistment_result = character['career_history'][-1]
    print(f"Reenlistment: {reenlistment_result['outcome']}")
    print(f"Terms served after: {character.get('terms_served', 0)}")
    print(f"Age after: {character['age']}")
    print(f"Continue career: {reenlistment_result.get('continue_career', False)}")
    
    if reenlistment_result.get('continue_career', False):
        # Check skills immediately after reenlistment
        print("\n4. Skills Immediately After Reenlistment...")
        available_tables = chargen.get_available_skill_tables(character)
        skill_eligibility = character.get("skill_eligibility", 0)
        ready_for_skills = chargen.is_ready_for_skills(character)
        print(f"Skill eligibility: {skill_eligibility}")
        print(f"Ready for skills: {ready_for_skills}")
        print(f"Available tables: {available_tables}")
        
        # Second term - Survival
        print("\n5. Second Term - Survival...")
        character = chargen.check_survival(rng, character)
        survival_result = character['career_history'][-1]
        print(f"Survival: {survival_result['outcome']}")
        
        # Check skills after survival
        print("\n6. Skills After Survival in Second Term...")
        available_tables = chargen.get_available_skill_tables(character)
        skill_eligibility = character.get("skill_eligibility", 0)
        ready_for_skills = chargen.is_ready_for_skills(character)
        print(f"Skill eligibility: {skill_eligibility}")
        print(f"Ready for skills: {ready_for_skills}")
        print(f"Available tables: {available_tables}")
        
        if ready_for_skills and skill_eligibility > 0:
            print("✅ SUCCESS: Skills are available after survival in second term!")
        else:
            print("❌ FAILURE: Skills are not available after survival in second term!")
            print(f"   Ready for skills: {ready_for_skills}")
            print(f"   Skill eligibility: {skill_eligibility}")
    else:
        print("❌ FAILURE: Character did not continue career!")

if __name__ == "__main__":
    test_complete_second_term() 