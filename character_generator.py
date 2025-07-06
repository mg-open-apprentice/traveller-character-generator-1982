import random
import json
from typing import Literal


def set_random_seed(seed=None):
    """Set a random seed for reproducible results during testing"""
    if seed is not None:
        random.seed(seed)
        print(f"Random seed set to: {seed}")
    else:
        # Use current time for truly random results
        import time
        random.seed(time.time())
        print("Using random seed based on current time")

class Character:
    def __init__(self):
        self.age = 18  # Starting age (Traveller standard)
        self.terms_served: int | float = 0
        self.characteristics = {}
        self.career : Literal["Navy", "Marines", "Army", "Scouts", "Merchants", "Others"] | None = None
        self.name = self.get_random_name()
        self.career_history = []
        self.skills = {}  # Dict of skill_name: level
        self.mustering_out_benefits = {'cash': 0, 'items': []}
        self.ageing_log = []  # List of dicts: {'term': int, 'age': int, 'effects': [str]}
        self.term_log = []  # List of dicts: {'term': int, 'age': int, 'skills': [(table, result)], 'ageing': [str]}
        self.skill_acquisition_log = []  # List of dicts: {'term': int, 'event': str, 'skill': str, 'level': int}
        self.automatic_skills_granted = set()  # Track which automatic skills have been granted
        self.commissioned = False  # Officer status
        self.rank = 0  # 0 = enlisted, 1+ = officer ranks
        self.drafted = False  # Track if drafted in first term
        self.promotions = 0  # Number of promotions (after commission)
        self.generation_log = []  # Track all generation events for JSON output
        self.skill_eligibility = 0  # Running tally of non-automatic skills character may roll for

    def update_skill_eligibility_for_career_start(self, career):
        """Update skill eligibility when career is first assigned"""
        if career in ['Navy', 'Marines', 'Army', 'Merchants', 'Others']:
            # First term gets +2 skills for these careers
            self.skill_eligibility += 2
            self.log_event('skill_eligibility_update', {
                'reason': 'career_first_term',
                'career': career,
                'bonus': 2,
                'new_total': self.skill_eligibility
            })
        elif career == 'Scouts':
            # Scouts get +2 for all terms
            self.skill_eligibility += 2
            self.log_event('skill_eligibility_update', {
                'reason': 'scouts_term',
                'career': career,
                'bonus': 2,
                'new_total': self.skill_eligibility
            })

    def update_skill_eligibility_for_term_completion(self, career):
        """Update skill eligibility when a term is completed"""
        if career in ['Navy', 'Marines', 'Army', 'Merchants', 'Others']:
            # After first term, these careers get +1 per term
            if self.terms_served > 1:
                self.skill_eligibility += 1
                self.log_event('skill_eligibility_update', {
                    'reason': 'career_subsequent_term',
                    'career': career,
                    'term': self.terms_served,
                    'bonus': 1,
                    'new_total': self.skill_eligibility
                })
        elif career == 'Scouts':
            # Scouts get +2 for all terms (including first)
            self.skill_eligibility += 2
            self.log_event('skill_eligibility_update', {
                'reason': 'scouts_term',
                'career': career,
                'term': self.terms_served,
                'bonus': 2,
                'new_total': self.skill_eligibility
            })

    def update_skill_eligibility_for_commission(self):
        """Update skill eligibility when character is commissioned"""
        self.skill_eligibility += 1
        self.log_event('skill_eligibility_update', {
            'reason': 'commission',
            'career': self.career,
            'bonus': 1,
            'new_total': self.skill_eligibility
        })

    def update_skill_eligibility_for_promotion(self):
        """Update skill eligibility when character is promoted"""
        self.skill_eligibility += 1
        self.log_event('skill_eligibility_update', {
            'reason': 'promotion',
            'career': self.career,
            'rank': self.rank,
            'bonus': 1,
            'new_total': self.skill_eligibility
        })

    def get_skill_eligibility(self):
        """Get current skill eligibility count"""
        return self.skill_eligibility

    def complete_term(self):
        """Complete a 4-year term of service"""
        # Note: Age and terms_served are now updated in attempt_reenlistment() 
        # when the term is actually completed, not during term processing
        # self.age += 4  # Removed - now handled in attempt_reenlistment()
        # self.terms_served += 1  # Removed - now handled in attempt_reenlistment()

        # Update skill eligibility for term completion
        if self.career:
            self.update_skill_eligibility_for_term_completion(self.career)

        # Note: Ageing checks are now handled elsewhere in the flow
        # Check for ageing effects
        # ageing_effects = self.check_ageing()
        # ... rest of ageing logic commented out or moved

    def get_age(self):
        return self.age

    def check_ageing(self):
        """Check for ageing effects when crossing age thresholds"""
        ageing_thresholds = [34, 38, 42, 46, 50, 54, 58, 62]
        advanced_ageing_start = 66
    
        # Check which thresholds we've crossed this term
        previous_age = self.age - 4
        current_age = self.age
    
        ageing_effects = []
        checks_performed = []  # Track all checks performed

        # Log the ageing check start
        self.log_event('ageing_check_start', {
            'term': self.terms_served,
            'previous_age': previous_age,
            'current_age': current_age,
            'age_increase': 4
        })

        # Check standard thresholds (34 - 62)
        for threshold in ageing_thresholds:
            if previous_age < threshold <= current_age:
#               print(f"\n⏰ Ageing check at age {threshold}:")
                # Log that we're performing an ageing check
                self.log_event('ageing_threshold_check', {
                    'age': threshold,
                    'previous_age': previous_age,
                    'current_age': current_age,
                    'phase': 'standard',
                    'threshold_crossed': True
                })
                checks_performed.append(threshold)
                effects = self.apply_ageing_effects(threshold)
                ageing_effects.extend(effects)
            else:
                # Log that this threshold was not crossed
                self.log_event('ageing_threshold_check', {
                    'age': threshold,
                    'previous_age': previous_age,
                    'current_age': current_age,
                    'phase': 'standard',
                    'threshold_crossed': False,
                    'reason': f'Threshold {threshold} not crossed (previous_age={previous_age}, current_age={current_age})'
                })

        # Check advanced ageing (66+)
        if current_age >= advanced_ageing_start:
            for age in range(max(66, ((previous_age // 4) + 1) * 4), current_age + 1, 4):
                if age >= advanced_ageing_start:
#                   print(f"\n⚰️  Advanced ageing check at age {age}:")
                    # Log that we're performing an advanced ageing check
                    self.log_event('ageing_threshold_check', {
                        'age': age,
                        'previous_age': previous_age,
                        'current_age': current_age,
                        'phase': 'advanced',
                        'threshold_crossed': True
                    })
                    checks_performed.append(age)
                    effects = self.apply_advanced_ageing_effects(age)
                    ageing_effects.extend(effects)
        else:
            # Log that advanced ageing was not reached
            self.log_event('ageing_threshold_check', {
                'age': advanced_ageing_start,
                'previous_age': previous_age,
                'current_age': current_age,
                'phase': 'advanced',
                'threshold_crossed': False,
                'reason': f'Advanced ageing not reached (current_age={current_age} < {advanced_ageing_start})'
            })

        # Log if no ageing checks were performed this term
        if not checks_performed:
            self.log_event('ageing_threshold_check', {
                'age': current_age,
                'previous_age': previous_age,
                'current_age': current_age,
                'phase': 'none',
                'threshold_crossed': False,
                'note': 'No ageing thresholds crossed this term'
            })

        # Log the ageing check completion
        self.log_event('ageing_check_complete', {
            'term': self.terms_served,
            'checks_performed': checks_performed,
            'ageing_effects': ageing_effects,
            'total_effects': len(ageing_effects)
        })

        return ageing_effects

    def apply_ageing_effects(self, age):
        """Apply ageing effects at a specific age"""
        effects = []

        if age in [34, 38, 42, 46]:
            # Phase 1: Early ageing
            checks = [
                ('str', 8, 1), ('dex', 7, 1), ('end', 8, 1)
            ]
        elif age in [50, 54, 58, 62]:
            # Phase 2: Advanced ageing  
            checks = [
                ('str', 9, 1), ('dex', 8, 1), ('end', 9, 1)  # Using 'end' to match your existing code
            ]
        
        for stat, target, loss in checks:
            roll = self.roll_2d6()
            if roll < target:
                old_value = self.characteristics[stat]
                self.characteristics[stat] = max(0, self.characteristics[stat] - loss)  # Prevent negative
                actual_loss = old_value - self.characteristics[stat]
#               print(f"  {stat.upper()}: Roll {roll} < {target} → Lost {actual_loss} point(s) ({old_value} → {self.characteristics[stat]})")
                effects.append(f"-{actual_loss} {stat.upper()}")
                # Log individual ageing check
                self.log_event('ageing_check', {
                    'age': age,
                    'stat': stat.upper(),
                    'roll': roll,
                    'target': target,
                    'old_value': old_value,
                    'new_value': self.characteristics[stat],
                    'loss': actual_loss,
                    'phase': 'standard'
                })
            else:
#               print(f"  {stat.upper()}: Roll {roll} ≥ {target} → No loss")
                # Log individual ageing check (no loss)
                self.log_event('ageing_check', {
                    'age': age,
                    'stat': stat.upper(),
                    'roll': roll,
                    'target': target,
                    'old_value': self.characteristics[stat],
                    'new_value': self.characteristics[stat],
                    'loss': 0,
                    'phase': 'standard'
                })
        
        return effects

    def apply_advanced_ageing_effects(self, age):
        """Apply advanced ageing effects for ages 66+"""
        effects = []
        
        # Advanced ageing affects STR, DEX, END, and INT
        checks = [
            ('str', 9, 2), ('dex', 9, 2), ('end', 9, 2), ('int', 9, 1)
        ]
        
        for stat, target, loss in checks:
            roll = self.roll_2d6()
            if roll < target:
                old_value = self.characteristics[stat]
                self.characteristics[stat] = max(0, self.characteristics[stat] - loss)  # Prevent negative
                actual_loss = old_value - self.characteristics[stat]
#                print(f"  {stat.upper()}: Roll {roll} < {target} → Lost {actual_loss} point(s) ({old_value} → {self.characteristics[stat]})")
                effects.append(f"-{actual_loss} {stat.upper()}")
                # Log individual advanced ageing check
                self.log_event('ageing_check', {
                    'age': age,
                    'stat': stat.upper(),
                    'roll': roll,
                    'target': target,
                    'old_value': old_value,
                    'new_value': self.characteristics[stat],
                    'loss': actual_loss,
                    'phase': 'advanced'
                })
            else:
#                print(f"  {stat.upper()}: Roll {roll} ≥ {target} → No loss")
                # Log individual advanced ageing check (no loss)
                self.log_event('ageing_check', {
                    'age': age,
                    'stat': stat.upper(),
                    'roll': roll,
                    'target': target,
                    'old_value': self.characteristics[stat],
                    'new_value': self.characteristics[stat],
                    'loss': 0,
                    'phase': 'advanced'
                })
        
        return effects

    def get_terms_served(self):
        return self.terms_served

    # --- CHARACTERISTIC GETTER METHODS ---
    
    def get_str_decimal(self):
        """Get Strength characteristic in decimal format"""
        return self.characteristics.get('str', 0)
    
    def get_str_hexadecimal(self):
        """Get Strength characteristic in hexadecimal format (10-15 become A-F)"""
        value = self.characteristics.get('str', 0)
        return hex(value)[2:].upper() if 10 <= value <= 15 else str(value)
    
    def get_dex_decimal(self):
        """Get Dexterity characteristic in decimal format"""
        return self.characteristics.get('dex', 0)
    
    def get_dex_hexadecimal(self):
        """Get Dexterity characteristic in hexadecimal format (10-15 become A-F)"""
        value = self.characteristics.get('dex', 0)
        return hex(value)[2:].upper() if 10 <= value <= 15 else str(value)
    
    def get_end_decimal(self):
        """Get Endurance characteristic in decimal format"""
        return self.characteristics.get('end', 0)
    
    def get_end_hexadecimal(self):
        """Get Endurance characteristic in hexadecimal format (10-15 become A-F)"""
        value = self.characteristics.get('end', 0)
        return hex(value)[2:].upper() if 10 <= value <= 15 else str(value)
    
    def get_int_decimal(self):
        """Get Intelligence characteristic in decimal format"""
        return self.characteristics.get('int', 0)
    
    def get_int_hexadecimal(self):
        """Get Intelligence characteristic in hexadecimal format (10-15 become A-F)"""
        value = self.characteristics.get('int', 0)
        return hex(value)[2:].upper() if 10 <= value <= 15 else str(value)
    
    def get_edu_decimal(self):
        """Get Education characteristic in decimal format"""
        return self.characteristics.get('edu', 0)
    
    def get_edu_hexadecimal(self):
        """Get Education characteristic in hexadecimal format (10-15 become A-F)"""
        value = self.characteristics.get('edu', 0)
        return hex(value)[2:].upper() if 10 <= value <= 15 else str(value)
    
    def get_soc_decimal(self):
        """Get Social Standing characteristic in decimal format"""
        return self.characteristics.get('soc', 0)
    
    def get_soc_hexadecimal(self):
        """Get Social Standing characteristic in hexadecimal format (10-15 become A-F)"""
        value = self.characteristics.get('soc', 0)
        return hex(value)[2:].upper() if 10 <= value <= 15 else str(value)

    @staticmethod
    def roll_2d6():
        """Roll 2d6 (standard Traveller dice mechanic)"""
        return random.randint(1, 6) + random.randint(1, 6)

    @staticmethod
    def generate_characteristics():
        """Generate the six basic characteristics"""
        characteristics_order = ['str', 'dex', 'end', 'int', 'edu', 'soc']
        return {attr: Character.roll_2d6() for attr in characteristics_order}

    @staticmethod
    def convert_characteristics_to_hex(characteristics):
        """Convert characteristics to hexadecimal notation (10-15 become A-F)"""
        return {
            k: hex(v)[2:].upper() if 10 <= v <= 15 else str(v)
            for k, v in characteristics.items()
        }

    @staticmethod
    def create_hex_string(hex_values):
        """Create UPP (Universal Personality Profile) string"""
        # Use the correct order: STR, DEX, END, INT, EDU, SOC
        characteristic_order = ['str', 'dex', 'end', 'int', 'edu', 'soc']
        return ''.join(hex_values[attr] for attr in characteristic_order)

    # --- CAREER LOGIC ---

    @staticmethod
    def get_available_careers() -> list[Literal["Navy", "Marines", "Army", "Scouts", "Merchants", "Others"]]:
        """Return list of available careers"""
        return ['Navy', 'Marines', 'Army', 'Scouts', 'Merchants', 'Others']

    @staticmethod
    def get_random_career():
        """Get a random career for testing"""
        return random.choice(Character.get_available_careers())

    @staticmethod
    def enlistment_roll(service_choice):
        """Get the target number for enlistment in a career"""
        career_dict = {
            'Navy': 8,
            'Marines': 9,
            'Army': 5,
            'Scouts': 7,
            'Merchants': 7,
            'Others': 3
        }
        return career_dict.get(service_choice, 5)

    @staticmethod
    def get_career_bonuses(service_choice):
        """Get characteristic requirements and bonuses for enlistment"""
        career_choice_bonuses = {
            'Navy': {'int': (8, 1), 'edu': (9, 2)},
            'Marines': {'int': (8, 1), 'str': (8, 2)},
            'Army': {'dex': (6, 1), 'end': (5, 2)},
            'Scouts': {'int': (6, 1), 'str': (8, 2)},
            'Merchants': {'str': (7, 1), 'int': (6, 2)},
            'Others': {}
        }
        return career_choice_bonuses.get(service_choice, {})

    @staticmethod
    def get_career_choice_modifiers(characteristics, service_choice):
        """Calculate enlistment modifiers based on characteristics"""
        bonuses = Character.get_career_bonuses(service_choice)
        return sum(
            bonus for attr, (req, bonus) in bonuses.items()
            if characteristics.get(attr, 0) >= req
        )

    @staticmethod
    def attempt_enlistment(characteristics, service_choice) -> tuple[Literal["Navy", "Marines", "Army", "Scouts", "Merchants", "Others"], str, int, int, int]:
    # existing code...
        """Attempt to enlist in chosen career"""
        required_roll = Character.enlistment_roll(service_choice)
        enlistment_roll = Character.roll_2d6()
        modifier = Character.get_career_choice_modifiers(characteristics, service_choice)
        successful = enlistment_roll + modifier >= required_roll

        if successful:
            enlistment_status = 'enlisted'
            career = service_choice
        else:
            enlistment_status = 'drafted'
            career = Character.get_draft_career()

        return career, enlistment_status, required_roll, enlistment_roll, modifier

    @staticmethod
    def get_draft_career():
        """Get randomly assigned career when enlistment fails"""
        return random.choice(Character.get_available_careers()) 

    # --- SURVIVAL LOGIC ---

    @staticmethod
    def survival_roll(career):
        """Get the target number for survival in a career"""
        survival_dict = {
            'Navy': 5,
            'Marines': 6,
            'Army': 5,
            'Scouts': 7,
            'Merchants': 5,
            'Others': 5
        }

        if career not in survival_dict:
            print(f"WARNING: Unknown career '{career}' in survival_roll")

        return survival_dict.get(career, 5)

    @staticmethod
    def survival_bonuses(career):
        """Get characteristic requirements and bonuses for survival"""
        survival_bonuses = {
            'Navy': {'intelligence': (7, 2)},
            'Marines': {'endurance': (8, 2)},
            'Army': {'education': (6, 2)},
            'Scouts': {'endurance': (9, 2)},
            'Merchants': {'intelligence': (7, 2)},
            'Others': {'intelligence': (9, 2)}
        }
        return survival_bonuses.get(career, {})

    @staticmethod
    def check_survival_detailed(career, characteristics, death_rule_enabled=False):
        """Check if character survives the term with detailed roll information"""
        required_roll = Character.survival_roll(career)
        roll = Character.roll_2d6()
        bonus = 0
        bonus_details = []

        bonuses = Character.survival_bonuses(career)
        for char, (req, bns) in bonuses.items():
            if characteristics.get(char, 0) >= req:
                bonus += bns
                bonus_details.append(f"{char.capitalize()} {characteristics.get(char, 0)}≥{req} (+{bns})")

        total = roll + bonus
        survived = total >= required_roll

        result = {
            'roll': roll,
            'bonus': bonus,
            'bonus_details': bonus_details,
            'total': total,
            'required': required_roll,
            'survived': survived,
            'outcome': 'survived' if survived else ('died' if death_rule_enabled else 'injured')
        }

        return result

    @staticmethod
    def check_survival(career, characteristics, death_rule_enabled=False):
        """Check if character survives the term"""
        required_roll = Character.survival_roll(career)
        roll = Character.roll_2d6()
        bonus = 0
        bonus_details = []

        bonuses = Character.survival_bonuses(career)
        for char, (req, bns) in bonuses.items():
            if characteristics.get(char, 0) >= req:
                bonus += bns
                bonus_details.append(f"{char.capitalize()} {characteristics.get(char, 0)}≥{req} (+{bns})")

        total = roll + bonus
        survived = total >= required_roll

        if survived:
            print(f"❤️  [SURVIVAL] {career} | Roll: {roll}+{bonus}={total} (need {required_roll}) → SURVIVED")
            return 'survived'
        else:
            if death_rule_enabled:
                print(f"💀 [SURVIVAL] {career} | Roll: {roll}+{bonus}={total} (need {required_roll}) → DIED")
                return 'died'
            else:
                print(f"🩹 [SURVIVAL] {career} | Roll: {roll}+{bonus}={total} (need {required_roll}) → INJURED")
                return 'injured'

    @staticmethod
    def reenlistment_roll(career):
        """Get the target number for reenlistment"""
        reenlistment_targets = {
            'Navy': 6,
            'Marines': 6,
            'Army': 7,
            'Scouts': 3,
            'Merchants': 4,
            'Others': 5
        }
        return reenlistment_targets.get(career, 5)

    @staticmethod
    def attempt_reenlistment(career, age, preference='reenlist'):
        """Attempt to reenlist for another term with character preference"""
        target = Character.reenlistment_roll(career)
        roll = Character.roll_2d6()
    
        # Determine outcome based on preference and roll
        if roll == 12:
        # Roll of 12 is always mandatory retention
            outcome = 'retained'
            status_text = 'retained (mandatory)'
            continue_career = True
        elif preference == 'reenlist':
        # Wants to stay
            if roll >= target:
                outcome = 'reenlisted'
                status_text = 'reenlisted'
                continue_career = True
            else:
                outcome = 'military-discharge'
                status_text = 'military-discharge'
                continue_career = False
        elif preference in ['discharge', 'retire']:
            # Wants to leave - gets their wish unless roll is 12
            if roll == 12:
                outcome = 'retained'
                status_text = 'retained (mandatory)'
                continue_career = True
            else:
                outcome = preference + 'd' if preference == 'discharge' else 'retired'
                status_text = outcome
                continue_career = False
    
    # Print the result
        print(f"🔄 [REENLISTMENT] {career} | {preference} | Roll: {roll} (need {target}) → {status_text}")
    
    # Return values that match what the main loop expects
        if continue_career:
            return 'approved' if outcome == 'reenlisted' else 'mandatory'
        else:
            return 'denied'

    @staticmethod
    def get_random_name():
        """Generate a random sci-fi name"""
        sci_fi_names = [
            "Zara Xylo", "Orion Pax", "Nova Kin", "Elexis Vortex",
            "Jaxon Starfire", "Lyra Nebulae", "Nyx Solaris", "Ryker Quantum",
            "Elara Galaxy", "Caelum Void", "Vega Stardust", "Draco Cosmos",
            "Aurora Hyperdrive", "Cassius Meteor", "Astra Comet", "Kaius Eclipse",
            "Seren Andromeda", "Altair Nebular", "Selene Astraeus", "Maximus Ion"
        ]
        return random.choice(sci_fi_names)

    def add_career_term(self, career, term_number, partial_term=False):
        """Add a career term to history"""
        years_served = 2 if partial_term else 4
        self.career_history.append({
            'career': career,
            'term': term_number,
            'age_start': self.age - years_served,
            'age_end': self.age,
            'partial_term': partial_term
        })

    def add_skill(self, skill_name, levels=1, reason='term', table='automatic', roll=None, description='Skill gain', term_override=None):
        """Add or increase a skill with logging"""
        if skill_name in self.skills:
            self.skills[skill_name] += levels
        else:
            self.skills[skill_name] = levels
        
        # Log skill acquisition
        self.log_skill_acquisition(reason, table, roll, skill_name, levels, description, term_override)

    def log_skill_acquisition(self, reason, table, roll, skill, modifier, description, term_override=None):
        """Log a skill acquisition with full metadata"""
        # Use provided term or current term (enlistment skills go in term 1)
        term = term_override if term_override is not None else self.terms_served
        
        self.skill_acquisition_log.append({
            'term': term,
            'event': reason,
            'table': table,
            'roll': roll,
            'skill': skill,
            'level': modifier,
            'description': description
        })

    # --- SKILL TABLES ---
    
    @staticmethod
    def get_skill_tables(career):
        """Get all skill tables for a career"""
        # Personal Development tables (same structure for all careers, values differ)
        personal_development = {
            'Navy': {1: '+1 STR', 2: '+1 DEX', 3: '+1 END', 4: '+1 INT', 5: '+1 EDU', 6: '+1 SOC'},
            'Marines': {1: '+1 STR', 2: '+1 DEX', 3: '+1 END', 4: 'Gambling', 5: 'Brawling', 6: 'Blade Combat'},
            'Army': {1: '+1 STR', 2: '+1 DEX', 3: '+1 END', 4: 'Gambling', 5: '+1 EDU', 6: 'Brawling'},
            'Scouts': {1: '+1 STR', 2: '+1 DEX', 3: '+1 END', 4: '+1 INT', 5: '+1 EDU', 6: 'Gun Combat'},
            'Merchants': {1: '+1 STR', 2: '+1 DEX', 3: '+1 END', 4: 'Blade Combat', 5: 'Bribery', 6: '+1 INT'},
            'Others': {1: '+1 STR', 2: '+1 DEX', 3: '+1 END', 4: 'Blade Combat', 5: 'Brawling', 6: '+1 SOC'}
        }
        
        # Service Skills
        service_skills = {
            'Navy': {1: 'Ship\'s Boat', 2: 'Vacc Suit', 3: 'Forward Observer', 4: 'Gunnery', 5: 'Blade Combat', 6: 'Gun Combat'},
            'Marines': {1: 'Vehicle', 2: 'Vacc Suit', 3: 'Blade Combat', 4: 'Gun Combat', 5: 'Blade Combat', 6: 'Gun Combat'},
            'Army': {1: 'Vehicle', 2: 'Air/Raft', 3: 'Gun Combat', 4: 'Forward Observer', 5: 'Blade Combat', 6: 'Gun Combat'},
            'Scouts': {1: 'Vehicle', 2: 'Vacc Suit', 3: 'Mechanical', 4: 'Navigation', 5: 'Electronics', 6: 'Jack-o-T'},
            'Merchants': {1: 'Vehicle', 2: 'Vacc Suit', 3: 'Jack-o-T', 4: 'Steward', 5: 'Electronics', 6: 'Gun Combat'},
            'Others': {1: 'Vehicle', 2: 'Gambling', 3: 'Brawling', 4: 'Bribery', 5: 'Blade Combat', 6: 'Gun Combat'}
        }
        
        # Advanced (Specialist) Skills
        advanced = {
            'Navy': {1: 'Vacc Suit', 2: 'Mechanical', 3: 'Electronics', 4: 'Engineering', 5: 'Gunnery', 6: 'Computer'},
            'Marines': {1: 'Vehicle', 2: 'Mechanical', 3: 'Electronics', 4: 'Tactics', 5: 'Blade Combat', 6: 'Gun Combat'},
            'Army': {1: 'Vehicle', 2: 'Mechanical', 3: 'Electronics', 4: 'Tactics', 5: 'Blade Combat', 6: 'Gun Combat'},
            'Scouts': {1: 'Vehicle', 2: 'Mechanical', 3: 'Electronics', 4: 'Jack-o-T', 5: 'Gunnery', 6: 'Medical'},
            'Merchants': {1: 'Streetwise', 2: 'Mechanical', 3: 'Electronics', 4: 'Navigation', 5: 'Engineering', 6: 'Computer'},
            'Others': {1: 'Streetwise', 2: 'Mechanical', 3: 'Electronics', 4: 'Gambling', 5: 'Brawling', 6: 'Forgery'}
        }
        
        # Advanced Education (EDU 8+)
        advanced_education = {
            'Navy': {1: 'Medical', 2: 'Navigation', 3: 'Engineering', 4: 'Computer', 5: 'Pilot', 6: 'Admin'},
            'Marines': {1: 'Medical', 2: 'Tactics', 3: 'Tactics', 4: 'Computer', 5: 'Leader', 6: 'Admin'},
            'Army': {1: 'Medical', 2: 'Tactics', 3: 'Tactics', 4: 'Computer', 5: 'Leader', 6: 'Admin'},
            'Scouts': {1: 'Medical', 2: 'Navigation', 3: 'Engineering', 4: 'Computer', 5: 'Pilot', 6: 'Jack-o-T'},
            'Merchants': {1: 'Medical', 2: 'Navigation', 3: 'Engineering', 4: 'Computer', 5: 'Pilot', 6: 'Admin'},
            'Others': {1: 'Medical', 2: 'Forgery', 3: 'Electronics', 4: 'Computer', 5: 'Streetwise', 6: 'Jack-o-T'}
        }
        
        return {
            'personal': personal_development,
            'service': service_skills,
            'advanced': advanced,
            'advanced_education': advanced_education
        }
    
    def roll_for_skills_detailed(self, career, num_skills=2, reason='term'):
        """Roll for skills during a term with detailed logging and return results"""
        tables = self.get_skill_tables(career)
        skill_rolls_this_term = []
        detailed_rolls = []
        
        for i in range(num_skills):
            # All characters may roll on personal, service, and advanced
            available_tables = ['personal', 'service', 'advanced']
            # Only add advanced_education if EDU >= 8
            if self.characteristics.get('edu', 0) >= 8:
                available_tables.append('advanced_education')
            
            # Choose a random table
            chosen_table = random.choice(available_tables)
            table = tables[chosen_table][career]
            
            # Roll on the table
            roll = random.randint(1, 6)
            result = table.get(roll, 'No skill')
            
            # Record detailed roll information
            roll_detail = {
                'roll_number': i + 1,
                'table': chosen_table,
                'roll': roll,
                'result': result,
                'table_contents': table
            }
            detailed_rolls.append(roll_detail)
            
            skill_rolls_this_term.append((chosen_table, result))
            
            # Apply the result
            if result.startswith('+1'):
                # Characteristic increase
                stat = result.split()[1].lower()
                if stat in self.characteristics:
                    self.characteristics[stat] += 1
                    self.log_skill_acquisition(reason, chosen_table, roll, f'+1 {stat.upper()}', 1, 'Characteristic boost')
            else:
                # Skill gain
                self.add_skill(result, 1, reason, chosen_table, roll, 'Skill gain')
        
        # Store skill rolls for this term in term_log
        self.term_log.append({'term': self.terms_served, 'age': self.age, 'skills': skill_rolls_this_term, 'ageing': []})
        
        return detailed_rolls

    def display_character_sheet(self, skill_format='hierarchical'):
        """Display character information with consolidated skill reporting"""
        print(f"\n{'='*50}")
        print(f"CHARACTER SHEET")
        print(f"{'='*50}")
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"Terms Served: {self.terms_served}")
        print(f"\nCharacteristics:")
        # Display characteristics in the correct order: STR, DEX, END, INT, EDU, SOC
        characteristic_order = ['str', 'dex', 'end', 'int', 'edu', 'soc']
        for attr in characteristic_order:
            value = self.characteristics[attr]
            hex_val = hex(value)[2:].upper() if 10 <= value <= 15 else str(value)
            print(f"  {attr.upper()}: {value} ({hex_val})")
        
        hex_chars = self.convert_characteristics_to_hex(self.characteristics)
        upp = self.create_hex_string(hex_chars)
        print(f"\nUPP: {upp}")
        
        if self.skills:
            print(f"\nFinal Skills:")
            for skill, level in sorted(self.skills.items()):
                print(f"  {skill}-{level}")
        else:
            print(f"\nNo skills acquired")
        
        if self.career_history:
            print(f"\nCareer History:")
            for term in self.career_history:
                if term.get('partial_term', False):
                    injury_term = int(term['term'] + 0.5)
                    print(f"  Injured Term {injury_term}: {term['career']} (Age {term['age_start']}-{term['age_end']})")
                else:
                    print(f"  Term {term['term']}: {term['career']} (Age {term['age_start']}-{term['age_end']})")
        
        # Display consolidated skill acquisitions
        if skill_format == 'tabular':
            self.display_skill_acquisitions_tabular()
        else:
            self.display_skill_acquisitions_hierarchical()
        
        if self.ageing_log:
            print(f"\n⏰ Ageing Effects History:")
            for entry in self.ageing_log:
                print(f"  Term {entry['term']} (Age {entry['age']}): {', '.join(entry['effects'])}")
        
        if self.mustering_out_benefits:
            print(f"\nMustering Out Benefits:")
            print(f"  Cash: Cr{self.mustering_out_benefits['cash']:,}")
            if self.mustering_out_benefits.get('characteristic_boosts'):
                boosts = self.mustering_out_benefits['characteristic_boosts']
                print(f"  Characteristic Boosts: {', '.join(f'{k.upper()} +{v}' for k, v in boosts.items())}")
            if self.mustering_out_benefits.get('items'):
                print(f"  Items: {', '.join(self.mustering_out_benefits['items'])}")
            else:
                print(f"  Items: None")
        
        print(f"{'='*50}\n")

    def grant_automatic_enlistment_skill(self, career, output_format='text'):
        """Grant automatic skill on enlistment or draft, only once per character"""
        if career == 'Army' and 'army_enlist' not in self.automatic_skills_granted:
            self.add_skill('Rifle', 1, 'enlistment', 'automatic', None, f'{career} basic training', term_override=1)
            self.automatic_skills_granted.add('army_enlist')
            # Display skills acquired this term
            self.display_current_term_skills(output_format)
        elif career == 'Marines' and 'marines_enlist' not in self.automatic_skills_granted:
            self.add_skill('Cutlass', 1, 'enlistment', 'automatic', None, f'{career} basic training', term_override=1)
            self.automatic_skills_granted.add('marines_enlist')
            # Display skills acquired this term
            self.display_current_term_skills(output_format)
        elif career == 'Scouts' and 'scouts_enlist' not in self.automatic_skills_granted:
            self.add_skill('Pilot', 1, 'enlistment', 'automatic', None, f'{career} basic training', term_override=1)
            self.automatic_skills_granted.add('scouts_enlist')
            # Display skills acquired this term
            self.display_current_term_skills(output_format)

    def grant_automatic_commission_skill(self, career, output_format='text'):
        """Grant automatic skill on commission, only once per character"""
        if career == 'Army' and 'army_commission' not in self.automatic_skills_granted:
            self.add_skill('SMG', 1, 'commission', 'automatic', None, f'{career} commission')
            self.automatic_skills_granted.add('army_commission')
            # Display skills acquired this term
            self.display_current_term_skills(output_format)
        elif career == 'Marines' and 'marines_commission' not in self.automatic_skills_granted:
            self.add_skill('Revolver', 1, 'commission', 'automatic', None, f'{career} commission')
            self.automatic_skills_granted.add('marines_commission')
            # Display skills acquired this term
            self.display_current_term_skills(output_format)

    def grant_automatic_rank_skill(self, career, rank, output_format='text'):
        """Grant automatic skill for specific ranks, only once per character/rank"""
        if career == 'Merchants' and rank == 4 and 'merchants_rank4' not in self.automatic_skills_granted:
            self.add_skill('Pilot', 1, f'rank_{rank}', 'automatic', None, f'Merchant rank {rank}')
            self.automatic_skills_granted.add('merchants_rank4')
        elif career == 'Navy' and rank == 5 and 'navy_rank5' not in self.automatic_skills_granted:
            self.characteristics['soc'] += 1
            self.log_skill_acquisition(f'rank_{rank}', 'automatic', None, '+1 SOC', 1, f'Navy rank {rank}')
            self.automatic_skills_granted.add('navy_rank5')
        elif career == 'Navy' and rank == 6 and 'navy_rank6' not in self.automatic_skills_granted:
            self.characteristics['soc'] += 1
            self.log_skill_acquisition(f'rank_{rank}', 'automatic', None, '+1 SOC', 1, f'Navy rank {rank}')
            self.automatic_skills_granted.add('navy_rank6')

    def calculate_mustering_out_rolls(self):
        """Calculate number of mustering out rolls based on terms and rank"""
        # Count full terms only (half terms don't count)
        full_terms = int(self.terms_served)
        term_rolls = full_terms
        
        # Rank-based rolls
        rank_rolls = 0
        if self.rank >= 1 and self.rank <= 2:
            rank_rolls = 1
        elif self.rank >= 3 and self.rank <= 4:
            rank_rolls = 2
        elif self.rank >= 5 and self.rank <= 6:
            rank_rolls = 3
        
        total_rolls = term_rolls + rank_rolls
        return total_rolls

    def display_skill_acquisitions_hierarchical(self):
        """Display skill acquisitions in hierarchical format grouped by term"""
        if not self.skill_acquisition_log:
            print("\nNo skill acquisitions recorded")
            return
        
        print(f"\n📚 Skill Acquisition History:")
        
        # Group by term
        term_groups = {}
        for entry in self.skill_acquisition_log:
            term = entry['term']
            if term not in term_groups:
                term_groups[term] = []
            term_groups[term].append(entry)
        
        # Display each term's skills
        for term in sorted(term_groups.keys()):
            age = 18 + (term * 4)  # Calculate age for this term
            print(f"\nTerm {term} (Age {age}):")
            
            for entry in term_groups[term]:
                event = entry['event'].upper()
                table = entry['table']
                roll = entry['roll'] if entry['roll'] is not None else '-'
                skill = entry['skill']
                level = entry['level']
                description = entry['description']
                
                if roll == '-':
                    print(f"  [{event}] {table}: {skill} +{level} ({description})")
                else:
                    print(f"  [{event}] {table}: {roll} → {skill} +{level} ({description})")

    def display_skill_acquisitions_tabular(self):
        """Display skill acquisitions in tabular format"""
        if not self.skill_acquisition_log:
            print("\nNo skill acquisitions recorded")
            return
        
        print(f"\n📊 Skill Acquisition Table:")
        print("┌─────────────┬─────────────┬──────┬─────────────┬─────────┬─────────────┐")
        print("│ Term        │ Event       │ Table│ Roll        │ Skill   │ Description │")
        print("├─────────────┼─────────────┼──────┼─────────────┼─────────┼─────────────┤")
        
        for entry in self.skill_acquisition_log:
            term = entry['term']
            event = entry['event'].upper()
            table = entry['table']
            roll = str(entry['roll']) if entry['roll'] is not None else '-'
            skill = entry['skill']
            level = entry['level']
            description = entry['description']
            
            # Truncate long descriptions
            if len(description) > 10:
                description = description[:7] + "..."
            
            print(f"│ {term:<11} │ {event:<11} │ {table:<6} │ {roll:<11} │ {skill:<7} │ {description:<11} │")
        
        print("└─────────────┴─────────────┴──────┴─────────────┴─────────┴─────────────┘")

    def log_event(self, event_type, data):
        """Log an event during character generation"""
        event = {
            'event_type': event_type,
            'term': self.terms_served,
            'age': self.age,
            'data': data
        }
        self.generation_log.append(event)

    def to_json(self):
        """Convert character to JSON format"""
        # Convert characteristics to hex for UPP (only if characteristics exist)
        if self.characteristics:
            hex_chars = self.convert_characteristics_to_hex(self.characteristics)
            upp = self.create_hex_string(hex_chars)
        else:
            upp = "------"  # Placeholder for unrolled characteristics
        
        # Convert skills dict to list format for better JSON structure
        skills_list = [{'name': skill, 'level': level} for skill, level in self.skills.items()]
        
        # Convert career history to more detailed format
        career_history_detailed = []
        for term in self.career_history:
            career_history_detailed.append({
                'term': term['term'],
                'career': term['career'],
                'age_start': term['age_start'],
                'age_end': term['age_end'],
                'partial_term': term.get('partial_term', False)
            })
        
        character_data = {
            'name': self.name,
            'age': self.age,
            'terms_served': self.terms_served,
            'characteristics': self.characteristics,
            'upp': upp,
            'career': self.career,
            'commissioned': self.commissioned,
            'rank': self.rank,
            'drafted': self.drafted,
            'promotions': self.promotions,
            'skill_eligibility': self.skill_eligibility,
            'skills': skills_list,
            'career_history': career_history_detailed,
            'ageing_log': self.ageing_log,
            'skill_acquisition_log': self.skill_acquisition_log,
            'generation_log': self.generation_log,
            'mustering_out_rolls': self.calculate_mustering_out_rolls(),
            'mustering_out_benefits': self.mustering_out_benefits
        }
        
        return character_data

    def display_current_term_skills(self, output_format='text'):
        """Display skill acquisitions for the current term"""
        if not self.skill_acquisition_log:
            return
        
        # Get skills for the current term
        current_term_skills = [entry for entry in self.skill_acquisition_log if entry['term'] == self.terms_served]
        
        if not current_term_skills:
            return
        
        if output_format == 'text':
            print(f"📚 [SKILLS]")
            for entry in current_term_skills:
                event = entry['event'].upper()
                table = entry['table']
                roll = entry['roll'] if entry['roll'] is not None else '-'
                skill = entry['skill']
                level = entry['level']
                description = entry['description']
                
                if roll == '-':
                    print(f"  [{event}] {table}: {skill} +{level} ({description})")
                else:
                    print(f"  [{event}] {table}: {roll} → {skill} +{level} ({description})")

    def display_current_term_ageing(self, output_format='text'):
        """Display ageing effects for the current term"""
        if output_format != 'text':
            return
    
        # Check for ageing checks in the generation log (this captures all checkprint(f"🎖️ [Promotion Check] {career}: Roll {roll} + {modifier} = {roll + modifier} (Need {target}) → {'PROMOTED' if success else 'FAILED'}")s, not just losses)
        ageing_checks = [event for event in self.generation_log 
                  if event['event_type'] == 'ageing_check' and event['term'] == self.terms_served]
    
        if ageing_checks:
            print(f"⏰ [AGEING]")
            for check in ageing_checks:
                data = check['data']
                stat = data['stat']
                roll = data['roll']
                target = data['target']
                old_value = data['old_value']
                new_value = data['new_value']
                loss = data['loss']
            
                if loss > 0:
                    print(f"  {stat}: {roll} < {target} → Lost {loss} point(s) ({old_value} → {new_value})") #
                else:
                    print(f"  {stat}: {roll} ≥ {target} → No loss")

    def roll_mustering_out(self, career, gambling_skill=0, output_format='text'):
        """Perform mustering out rolls according to classic Traveller rules."""
        # 1. Calculate total rolls
        total_rolls = int(self.terms_served)
        if 1 <= self.rank <= 2:
            total_rolls += 1
        elif 3 <= self.rank <= 4:
            total_rolls += 2
        elif 5 <= self.rank <= 6:
            total_rolls += 3

        # 2. Decide how many cash rolls (max 3)
        cash_rolls = min(3, total_rolls)
        benefit_rolls = total_rolls - cash_rolls

        # 3. Get tables
        cash_table = {
            'Navy':     {1: 1000, 2: 5000, 3: 5000, 4: 10000, 5: 20000, 6: 50000, 7: 50000},
            'Marines':  {1: 2000, 2: 5000, 3: 5000, 4: 10000, 5: 20000, 6: 30000, 7: 40000},
            'Army':     {1: 2000, 2: 5000, 3: 10000, 4: 10000, 5: 10000, 6: 20000, 7: 30000},
            'Scouts':   {1: 20000, 2: 20000, 3: 30000, 4: 30000, 5: 50000, 6: 50000, 7: 50000},
            'Merchant': {1: 1000, 2: 5000, 3: 10000, 4: 20000, 5: 20000, 6: 40000, 7: 40000},
            'Other':    {1: 1000, 2: 5000, 3: 10000, 4: 10000, 5: 10000, 6: 50000, 7: 100000},
        }
        benefit_table = {
            'Navy':     {1: 'Low Psg', 2: 'INT +1', 3: 'EDU +2', 4: 'Blade', 5: 'Travellers', 6: 'High Psg', 7: 'SOC +2'},
            'Marines':  {1: 'Low Psg', 2: 'INT +2', 3: 'EDU +1', 4: 'Blade', 5: 'Traveller', 6: 'High Psg', 7: 'SOC +2'},
            'Army':     {1: 'Low Psg', 2: 'INT +1', 3: 'EDU +2', 4: 'Gun', 5: 'High Psg', 6: 'Mid Psg', 7: 'SOC +1'},
            'Scouts':   {1: 'Low Psg', 2: 'INT +2', 3: 'EDU +2', 4: 'Blade', 5: 'Gun', 6: 'Scout Ship'},
            'Merchant': {1: 'Low Psg', 2: 'INT +1', 3: 'EDU +1', 4: 'Gun', 5: 'Blade', 6: 'Low Psg', 7: 'Free Trader'},
            'Other':    {1: 'Low Psg', 2: 'INT +1', 3: 'EDU +1', 4: 'Gun', 5: 'High Psg', 6: '-'},
        }
        cash_table = cash_table.get(career, cash_table['Other'])
        benefit_table = benefit_table.get(career, benefit_table['Other'])

        # 4. Roll for cash
        cash_total = 0
        items = []
        char_boosts = {}
        rank_bonus = 1 if self.rank >= 5 else 0

        if output_format == 'text':
            print(f'\n💰 [MUSTERING OUT]: {career} |{total_rolls} rolls ({cash_rolls} cash, {benefit_rolls} benefits)')

        for i in range(cash_rolls):
            roll = random.randint(1, 6) + rank_bonus + gambling_skill
            roll = min(7, roll)  # Max table value is 7
            amount = cash_table.get(roll, 0)
            cash_total += amount
            if output_format == 'text':
                print(f' [cash] Roll {i+1}: {roll} → Cr{amount:,}')
            # Log cash roll
            self.log_event('mustering_out_cash_roll', {
                'roll_number': i + 1,
                'base_roll': roll - rank_bonus - gambling_skill,
                'rank_bonus': rank_bonus,
                'gambling_bonus': gambling_skill,
                'total_roll': roll,
                'amount': amount,
                'career': career
            })

        # 5. Roll for benefits
        for i in range(benefit_rolls):
            roll = random.randint(1, 6) + rank_bonus
            roll = min(7, roll)
            benefit = benefit_table.get(roll, 'Low Psg')
            if output_format == 'text':
                print(f' [benefit] Roll {i+1}: {roll} → {benefit}')
            # Log benefit roll
            self.log_event('mustering_out_benefit_roll', {
                'roll_number': i + 1,
                'base_roll': roll - rank_bonus,
                'rank_bonus': rank_bonus,
                'total_roll': roll,
                'benefit': benefit,
                'career': career
            })
            # Apply characteristic boosts
            if benefit.startswith('INT +'):
                boost = int(benefit.split('+')[1])
                char_boosts['int'] = char_boosts.get('int', 0) + boost
                self.characteristics['int'] += boost
                # Log characteristic boost
                self.log_event('mustering_out_characteristic_boost', {
                    'stat': 'INT',
                    'boost': boost,
                    'old_value': self.characteristics['int'] - boost,
                    'new_value': self.characteristics['int'],
                    'source': 'mustering_out_benefit'
                })
            elif benefit.startswith('EDU +'):
                boost = int(benefit.split('+')[1])
                char_boosts['edu'] = char_boosts.get('edu', 0) + boost
                self.characteristics['edu'] += boost
                # Log characteristic boost
                self.log_event('mustering_out_characteristic_boost', {
                    'stat': 'EDU',
                    'boost': boost,
                    'old_value': self.characteristics['edu'] - boost,
                    'new_value': self.characteristics['edu'],
                    'source': 'mustering_out_benefit'
                })
            elif benefit.startswith('SOC +'):
                boost = int(benefit.split('+')[1])
                char_boosts['soc'] = char_boosts.get('soc', 0) + boost
                self.characteristics['soc'] += boost
                # Log characteristic boost
                self.log_event('mustering_out_characteristic_boost', {
                    'stat': 'SOC',
                    'boost': boost,
                    'old_value': self.characteristics['soc'] - boost,
                    'new_value': self.characteristics['soc'],
                    'source': 'mustering_out_benefit'
                })
            elif benefit != '-':
                items.append(benefit)
                # Log item acquisition
                self.log_event('mustering_out_item', {
                    'item': benefit,
                    'source': 'mustering_out_benefit'
                })

        self.mustering_out_benefits = {
            'cash': cash_total,
            'items': items,
            'characteristic_boosts': char_boosts
        }

        # Log final mustering out summary
        self.log_event('mustering_out_summary', {
            'career': career,
            'total_rolls': total_rolls,
            'cash_rolls': cash_rolls,
            'benefit_rolls': benefit_rolls,
            'total_cash': cash_total,
            'items': items,
            'characteristic_boosts': char_boosts,
            'rank_bonus': rank_bonus,
            'gambling_skill': gambling_skill
        })

        if output_format == 'text':
        # Build summary parts
            summary_parts = [f'Cr{cash_total:,} cash']
        if char_boosts:
            boosts_str = ', '.join(f'{k.upper()} +{v}' for k, v in char_boosts.items())
            summary_parts.append(f'{boosts_str} boosts')
        if items:
            summary_parts.append(f'{", ".join(items)} items')
    
        print(f'✅ [MUSTERING OUT] {career} | {", ".join(summary_parts)}')

    @staticmethod
    def check_commission(career, characteristics, drafted=False):
        if drafted:
            return False
        if career in ['Scouts', 'Others']:
            return False
            
        commission_target = {
            'Navy': 10,
            'Marines': 9,
            'Army': 5,
            'Merchants': 4
        }
        
        roll = Character.roll_2d6()
        target = commission_target.get(career, 12)
        
        # Add modifiers based on characteristics
        modifier = 0
        modifier_details = []
        if career == 'Navy' and characteristics.get('soc', 0) >= 9:
            modifier += 1
            modifier_details.append(f"SOC {characteristics.get('soc', 0)}≥9 (+1)")
        elif career == 'Marines' and characteristics.get('edu', 0) >= 7:
            modifier += 1
            modifier_details.append(f"EDU {characteristics.get('edu', 0)}≥7 (+1)")
        elif career == 'Army' and characteristics.get('end', 0) >= 7:
            modifier += 1
            modifier_details.append(f"END {characteristics.get('end', 0)}≥7 (+1)")
        elif career == 'Merchants' and characteristics.get('int', 0) >= 9:
            modifier += 1
            modifier_details.append(f"INT {characteristics.get('int', 0)}≥9 (+1)")
            
        total = roll + modifier
        success = total >= target
        if success:
            print(f"🗡️  [COMMISSION] {career} | Roll: {roll}+{modifier}={roll + modifier} (need {target}) → COMMISSIONED (Rank 1)")
        else:
            print(f"🗡️  [COMMISSION] {career} | Roll: {roll}+{modifier}={roll + modifier} (need {target}) → FAILED")
        
        return success

    def roll_for_skills(self, career, num_skills=2, reason='term'):
        """Roll for skills during a term with enhanced logging"""
        tables = self.get_skill_tables(career)
        skill_rolls_this_term = []
        
        for i in range(num_skills):
            # All characters may roll on personal, service, and advanced
            available_tables = ['personal', 'service', 'advanced']
            # Only add advanced_education if EDU >= 8
            if self.characteristics.get('edu', 0) >= 8:
                available_tables.append('advanced_education')
            # Choose a random table
            chosen_table = random.choice(available_tables)
            table = tables[chosen_table][career]
            # Roll on the table
            roll = random.randint(1, 6)
            result = table.get(roll, 'No skill')
            skill_rolls_this_term.append((chosen_table, result))
            
            # Apply the result
            if result.startswith('+1'):
                # Characteristic increase
                stat = result.split()[1].lower()
                if stat in self.characteristics:
                    self.characteristics[stat] += 1
                    self.log_skill_acquisition(reason, chosen_table, roll, f'+1 {stat.upper()}', 1, 'Characteristic boost')
            else:
                # Skill gain
                self.add_skill(result, 1, reason, chosen_table, roll, 'Skill gain')
        
        # Store skill rolls for this term in term_log
        self.term_log.append({'term': self.terms_served, 'age': self.age, 'skills': skill_rolls_this_term, 'ageing': []})

    @staticmethod
    def check_promotion_detailed(career, characteristics, current_rank, drafted=False):
        if drafted:
            return {
                'applicable': False,
                'reason': 'Drafted characters cannot be promoted'
            }
        if career in ['Scouts', 'Others']:
            return {
                'applicable': False,
                'reason': f'{career} does not have promotions'
            }
        
        # Promotion targets by career and current rank
        promotion_targets = {
            'Navy': {1: 10, 2: 9, 3: 8, 4: 7, 5: 6},
            'Marines': {1: 9, 2: 8, 3: 7, 4: 6, 5: 5},
            'Army': {1: 5, 2: 5, 3: 5, 4: 5, 5: 5},
            'Merchants': {1: 4, 2: 4, 3: 4, 4: 4, 5: 4}
        }
        
        if current_rank not in promotion_targets.get(career, {}):
            return {
                'applicable': False,
                'reason': f'No promotion available for {career} rank {current_rank}'
            }
        
        roll = Character.roll_2d6()
        target = promotion_targets[career][current_rank]
        
        # Add modifiers based on characteristics
        modifier = 0
        modifier_details = []
        if career == 'Navy' and characteristics.get('soc', 0) >= 9:
            modifier += 1
            modifier_details.append(f"SOC {characteristics.get('soc', 0)}≥9 (+1)")
        elif career == 'Marines' and characteristics.get('edu', 0) >= 7:
            modifier += 1
            modifier_details.append(f"EDU {characteristics.get('edu', 0)}≥7 (+1)")
        elif career == 'Army' and characteristics.get('end', 0) >= 7:
            modifier += 1
            modifier_details.append(f"END {characteristics.get('end', 0)}≥7 (+1)")
        elif career == 'Merchants' and characteristics.get('int', 0) >= 9:
            modifier += 1
            modifier_details.append(f"INT {characteristics.get('int', 0)}≥9 (+1)")
            
        total = roll + modifier
        success = total >= target
        
        result = {
            'applicable': True,
            'current_rank': current_rank,
            'new_rank': current_rank + 1 if success else current_rank,
            'roll': roll,
            'modifier': modifier,
            'modifier_details': modifier_details,
            'total': total,
            'target': target,
            'success': success
        }
        
        return result

    @classmethod
    def from_json(cls, data):
        """Reconstruct a Character object from a dictionary (as produced by to_json)"""
        obj = cls()
        obj.name = data.get('name', obj.get_random_name())
        obj.age = data.get('age', 18)
        obj.terms_served = data.get('terms_served', 0)
        obj.characteristics = data.get('characteristics', {})
        obj.career = data.get('career', None)
        obj.commissioned = data.get('commissioned', False)
        obj.rank = data.get('rank', 0)
        obj.drafted = data.get('drafted', False)
        obj.promotions = data.get('promotions', 0)
        obj.skill_eligibility = data.get('skill_eligibility', 0)
        # Convert skills list back to dict if needed
        skills = data.get('skills', [])
        if isinstance(skills, list):
            obj.skills = {s['name']: s['level'] for s in skills}
        else:
            obj.skills = skills
        obj.career_history = data.get('career_history', [])
        obj.ageing_log = data.get('ageing_log', [])
        obj.skill_acquisition_log = data.get('skill_acquisition_log', [])
        obj.generation_log = data.get('generation_log', [])
        obj.term_log = data.get('term_log', [])
        obj.mustering_out_benefits = data.get('mustering_out_benefits', {'cash': 0, 'items': []})
        # Handle automatic_skills_granted as set
        auto_skills = data.get('automatic_skills_granted', set())
        if isinstance(auto_skills, list):
            obj.automatic_skills_granted = set(auto_skills)
        else:
            obj.automatic_skills_granted = auto_skills
        return obj

    def roll_for_skill_on_table(self, table_name):
        """Roll for a skill on a specific table"""
        if not self.career:
            return {'error': 'No career set'}
        
        tables = self.get_skill_tables(self.career)
        if table_name not in tables:
            return {'error': f'Invalid table: {table_name}'}
        
        # Get the table for this career
        table = tables[table_name][self.career]
        
        # Roll 1d6
        roll = random.randint(1, 6)
        result = table.get(roll, 'No skill')
        
        # Apply the result
        if result.startswith('+1'):
            # Characteristic increase
            stat = result.split()[1].lower()
            if stat in self.characteristics:
                old_value = self.characteristics[stat]
                self.characteristics[stat] += 1
                self.log_skill_acquisition('skill_roll', table_name, roll, f'+1 {stat.upper()}', 1, 'Characteristic boost')
                return {
                    'table': table_name,
                    'roll': roll,
                    'result': result,
                    'type': 'characteristic',
                    'stat': stat.upper(),
                    'old_value': old_value,
                    'new_value': self.characteristics[stat],
                    'table_contents': table
                }
        else:
            # Skill gain
            self.add_skill(result, 1, 'skill_roll', table_name, roll, 'Skill gain')
            return {
                'table': table_name,
                'roll': roll,
                'result': result,
                'type': 'skill',
                'skill': result,
                'table_contents': table
            }

    def calculate_term_skills(self, survival_outcome='survived', commission_success=False, promotion_success=False):
        """Calculate skills for a term based on outcomes, returning breakdown without rolling"""
        skill_breakdown = {}
        total_skills = 0
        
        # 1. Survival skills
        if survival_outcome == 'survived':
            if self.career == 'Scouts':
                survival_skills = 2  # Scouts always get 2
            else:
                survival_skills = 2 if self.terms_served == 0 else 1  # Others: 2 for first term, 1 for subsequent
            total_skills += survival_skills
            skill_breakdown['survival'] = survival_skills
        else:
            skill_breakdown['survival'] = 0
        
        # 2. Commission skills
        if commission_success and self.career in ['Navy', 'Marines', 'Army', 'Merchants']:
            commission_skills = 1
            total_skills += commission_skills
            skill_breakdown['commission'] = commission_skills
        else:
            skill_breakdown['commission'] = 0
        
        # 3. Promotion skills
        if promotion_success and self.career in ['Navy', 'Marines', 'Army', 'Merchants']:
            promotion_skills = 1
            total_skills += promotion_skills
            skill_breakdown['promotion'] = promotion_skills
        else:
            skill_breakdown['promotion'] = 0
        
        return {
            'skill_breakdown': skill_breakdown,
            'total_skills': total_skills,
            'available_tables': self._get_available_tables()
        }
    
    def _get_available_tables(self):
        """Get available skill tables based on character's education"""
        available_tables = ['personal', 'service', 'advanced']
        if self.characteristics.get('edu', 0) >= 8:
            available_tables.append('advanced_education')
        return available_tables


# --- TEST FUNCTIONS ---
def test_character_stats():
    """Test characteristic generation"""
    characteristics = Character.generate_characteristics()
    
    # Test that all required characteristics are present
    required_stats = ['str', 'dex', 'end', 'int', 'edu', 'soc']
    for stat in required_stats:
        assert stat in characteristics, f"Missing characteristic: {stat}"
        assert 2 <= characteristics[stat] <= 12, f"Invalid {stat} value: {characteristics[stat]}"
    
    # Test hex conversion
    hex_chars = Character.convert_characteristics_to_hex(characteristics)
    for stat, value in characteristics.items():
        if 10 <= value <= 15:
            assert hex_chars[stat] in 'ABCDEF', f"Invalid hex conversion for {stat}: {value} -> {hex_chars[stat]}"
        else:
            assert hex_chars[stat] == str(value), f"Invalid hex conversion for {stat}: {value} -> {hex_chars[stat]}"
    
    # Test UPP string creation
    upp = Character.create_hex_string(hex_chars)
    assert len(upp) == 6, f"UPP string should be 6 characters, got: {len(upp)}"
    
    print("✅ Character stats test passed")

def test_career_choice_modifiers():
    """Test career modifier calculation"""
    # Test with high stats that should get bonuses
    high_stats = {'str': 10, 'dex': 10, 'end': 10, 'int': 10, 'edu': 10, 'soc': 10}
    
    # Navy should get +3 (INT 8+ = +1, EDU 9+ = +2)
    navy_mod = Character.get_career_choice_modifiers(high_stats, 'Navy')
    assert navy_mod == 3, f"Navy should get +3 with high stats, got +{navy_mod}"
    
    # Marines should get +3 (INT 8+ = +1, STR 8+ = +2)
    marines_mod = Character.get_career_choice_modifiers(high_stats, 'Marines')
    assert marines_mod == 3, f"Marines should get +3 with high stats, got +{marines_mod}"
    
    # Army should get +3 (DEX 6+ = +1, END 5+ = +2)
    army_mod = Character.get_career_choice_modifiers(high_stats, 'Army')
    assert army_mod == 3, f"Army should get +3 with high stats, got +{army_mod}"
    
    # Test with low stats that should get no bonuses
    # Use stats below all requirements: DEX < 6, END < 5, INT < 6, EDU < 9, STR < 7, SOC < 9
    low_stats = {'str': 4, 'dex': 4, 'end': 4, 'int': 4, 'edu': 4, 'soc': 4}
    for career in Character.get_available_careers():
        mod = Character.get_career_choice_modifiers(low_stats, career)
        assert mod == 0, f"{career} should get +0 with low stats, got +{mod}"
    
    print("✅ Career choice modifiers test passed")

def test_enlistment_logic():
    """Test enlistment process"""
    # Test with guaranteed success stats
    high_stats = {'str': 10, 'dex': 10, 'end': 10, 'int': 10, 'edu': 10, 'soc': 10}
    
    # Army has target 5, with +3 modifier, even roll of 2 would succeed
    career, status, required_roll, roll, modifier = Character.attempt_enlistment(high_stats, 'Army')
    assert status in ['enlisted', 'drafted'], f"Invalid enlistment status: {status}"
    assert career in Character.get_available_careers(), f"Invalid career: {career}"
    assert required_roll == 5, f"Army enlistment target should be 5, got {required_roll}"
    assert modifier >= 3, f"High stats should give at least +3 modifier, got +{modifier}"
    
    print("✅ Enlistment logic test passed")

def test_survival_logic():
    """Test survival check"""
    # Test with high stats that should survive easily
    high_stats = {'strength': 10, 'dexterity': 10, 'endurance': 10, 'intelligence': 10, 'education': 10, 'social': 10}
    
    # Marines have target 6, with +2 endurance bonus, even roll of 4 would survive
    outcome = Character.check_survival('Marines', high_stats)
    assert outcome in ['survived', 'died', 'injured'], f"Invalid survival outcome: {outcome}"
    
    # Test with death rule enabled
    outcome_with_death = Character.check_survival('Marines', high_stats, death_rule_enabled=True)
    assert outcome_with_death in ['survived', 'died'], f"Invalid survival outcome with death rule: {outcome_with_death}"
    
    print("✅ Survival logic test passed")

def test_ageing_effects():
    """Test ageing effects"""
    c = Character()
    c.characteristics = {'strength': 10, 'dexterity': 10, 'endurance': 10, 'intelligence': 10, 'education': 10, 'social': 10}
    
    # Test ageing at 34 (should affect strength, dexterity, endurance)
    effects = c.apply_ageing_effects(34)
    assert isinstance(effects, list), "Ageing effects should be a list"
    
    # Test advanced ageing at 66 (should affect strength, dexterity, endurance, intelligence)
    advanced_effects = c.apply_advanced_ageing_effects(66)
    assert isinstance(advanced_effects, list), "Advanced ageing effects should be a list"
    
    print("✅ Ageing effects test passed")

def test_skill_acquisition():
    """Test skill acquisition"""
    c = Character()
    c.characteristics = {'str': 10, 'dex': 10, 'end': 10, 'int': 10, 'edu': 10, 'soc': 10}
    
    # Test adding skills
    initial_skills = len(c.skills)
    c.add_skill('Pilot')
    assert len(c.skills) == initial_skills + 1, "Skill count should increase by 1"
    assert c.skills['Pilot'] == 1, "Pilot should be level 1"
    
    # Test skill level increase
    c.add_skill('Pilot', 2)
    assert c.skills['Pilot'] == 3, "Pilot should be level 3 after adding 2 more levels"
    
    print("✅ Skill acquisition test passed")

def test_commission_and_promotion():
    """Test commission and promotion logic"""
    # Test commission check
    high_stats = {'strength': 10, 'dexterity': 10, 'endurance': 10, 'intelligence': 10, 'education': 10, 'social': 10}
    
    # Navy commission target is 10, with high stats should have good chance
    commission_success = Character.check_commission('Navy', high_stats)
    assert isinstance(commission_success, bool), "Commission check should return boolean"
    
    # Test that Scouts and Others can't be commissioned
    scouts_commission = Character.check_commission('Scouts', high_stats)
    assert not scouts_commission, "Scouts should not be able to be commissioned"
    
    others_commission = Character.check_commission('Others', high_stats)
    assert not others_commission, "Others should not be able to be commissioned"
    
    print("✅ Commission and promotion test passed")

def test_reenlistment_logic():
    """Test reenlistment logic"""
    # Test mandatory reenlistment (roll of 12)
    # Note: This would require mocking the random roll, but we can test the logic
    
    # Test age limit (46+ can only continue on roll of 12)
    result = Character.attempt_reenlistment('Navy', 50)
    assert result in ['denied', 'mandatory'], f"Invalid reenlistment result for age 50: {result}"
    
    print("✅ Reenlistment logic test passed")

def test_mustering_out_calculation():
    """Test mustering out roll calculation"""
    c = Character()
    c.terms_served = 3
    c.rank = 2
    
    rolls = c.calculate_mustering_out_rolls()
    # 3 terms + 1 rank roll (rank 1-2) = 4 total
    assert rolls == 4, f"Should get 4 mustering out rolls (3 terms + 1 rank), got {rolls}"
    
    # Test higher rank
    c.rank = 5
    rolls = c.calculate_mustering_out_rolls()
    # 3 terms + 3 rank rolls (rank 5-6) = 6 total
    assert rolls == 6, f"Should get 6 mustering out rolls (3 terms + 3 rank), got {rolls}"
    
    print("✅ Mustering out calculation test passed")

def test_skill_eligibility():
    """Test skill eligibility tracking"""
    c = Character()
    
    # Test initial state
    assert c.skill_eligibility == 0, f"Initial skill eligibility should be 0, got {c.skill_eligibility}"
    
    # Test career start (Navy)
    c.update_skill_eligibility_for_career_start('Navy')
    assert c.skill_eligibility == 2, f"Navy career start should give +2, got {c.skill_eligibility}"
    
    # Test term completion (Navy, first term)
    c.terms_served = 1
    c.update_skill_eligibility_for_term_completion('Navy')
    assert c.skill_eligibility == 2, f"Navy first term should not add more, got {c.skill_eligibility}"
    
    # Test term completion (Navy, second term)
    c.terms_served = 2
    c.update_skill_eligibility_for_term_completion('Navy')
    assert c.skill_eligibility == 3, f"Navy second term should add +1, got {c.skill_eligibility}"
    
    # Test commission
    c.career = 'Navy'
    c.update_skill_eligibility_for_commission()
    assert c.skill_eligibility == 4, f"Commission should add +1, got {c.skill_eligibility}"
    
    # Test promotion
    c.update_skill_eligibility_for_promotion()
    assert c.skill_eligibility == 5, f"Promotion should add +1, got {c.skill_eligibility}"
    
    # Test Scouts (different rules)
    c2 = Character()
    c2.update_skill_eligibility_for_career_start('Scouts')
    assert c2.skill_eligibility == 2, f"Scouts career start should give +2, got {c2.skill_eligibility}"
    
    c2.terms_served = 1
    c2.update_skill_eligibility_for_term_completion('Scouts')
    assert c2.skill_eligibility == 4, f"Scouts first term should add +2, got {c2.skill_eligibility}"
    
    c2.terms_served = 2
    c2.update_skill_eligibility_for_term_completion('Scouts')
    assert c2.skill_eligibility == 6, f"Scouts second term should add +2, got {c2.skill_eligibility}"
    
    print("✅ Skill eligibility test passed")

def run_full_character_generation(death_rule_enabled=False, service_choice=None, seed=None, output_format='text'):
    """Run a complete character generation"""
    # Set seed if provided
    if seed is not None:
        set_random_seed(seed)
        if output_format == 'text':
            print(f"Using seed: {seed}")
    
    if output_format == 'text':
        print("\n" + "="*60)
        print("TRAVELLER CHARACTER GENERATION")
        print("="*60 + "\n")
    
    # Create character
    c = Character()
    c.characteristics = c.generate_characteristics()
    
    if output_format == 'text':
        print(f"Character Name: {c.name}")
        print("Generated Stats:", c.characteristics)
    
    # Use specified service or pick random one
    if service_choice:
        if service_choice not in Character.get_available_careers():
            if output_format == 'text':
                print(f"Error: Invalid career '{service_choice}'")
                print(f"Available careers: {', '.join(Character.get_available_careers())}")
            return None
        if output_format == 'text':
            print(f"\nAttempting to enlist in: {service_choice}")
    else:
        service_choice = Character.get_random_career()
        if output_format == 'text':
            print(f"\nAttempting to enlist in: {service_choice}")
    
    # Log enlistment attempt
    c.log_event('enlistment_attempt', {
        'service_choice': service_choice,
        'characteristics': c.characteristics.copy()
    })
    
    # Attempt enlistment
    career, status, required_roll, roll, modifier = Character.attempt_enlistment(c.characteristics, service_choice)
    
    if output_format == 'text':
        print(f"🎯 [ENLISTMENT] {service_choice} | Roll: {roll}+{modifier}={roll + modifier} (need {required_roll}) → {status.upper()} as {career}")
    
    # Log enlistment result
    c.log_event('enlistment_result', {
        'service_choice': service_choice,
        'career': career,
        'status': status,
        'roll': roll,
        'modifier': modifier,
        'required_roll': required_roll,
        'total': roll + modifier
    })
    
    if status == "drafted":          
        c.drafted = True
    
    c.career = career
    # Update skill eligibility for career start
    c.update_skill_eligibility_for_career_start(career)
    print()
    # Grant automatic skill for enlistment/draft
    c.grant_automatic_enlistment_skill(career, output_format)
    
    # Commission and promotion logic
    MAX_PROMOTIONS = {'Navy': 5, 'Marines': 5, 'Army': 5, 'Merchants': 4}
    eligible_for_commission = career in ['Navy', 'Marines', 'Army', 'Merchants']
    eligible_for_promotion = career in ['Navy', 'Marines', 'Army', 'Merchants']
    # Track commission attempt eligibility (not in first term if drafted)
    commission_attempted = False
    # Remove MAX_TERMS limit - characters can continue if they roll 12
    while True:  # Continue until career ends naturally
        if output_format == 'text':
            print(f"\n--- Term {c.terms_served + 1} in {career} ---")
        
        # Log term start
        c.log_event('term_start', {
            'term': c.terms_served + 1,
            'career': career,
            'age': c.age
        })
        
        # Check survival
        survived = Character.check_survival(career, c.characteristics, death_rule_enabled)
        
        # Log survival check
        c.log_event('survival_check', {
            'career': career,
            'outcome': survived,
            'characteristics': c.characteristics.copy()
        })
        
        # Handle different survival outcomes
        if survived == 'died':
            if output_format == 'text':
                print(f"\u2620\ufe0f  Died during term {c.terms_served + 1} in {career}. Final Age: {c.age}")
            c.log_event('death', {
                'term': c.terms_served + 1,
                'career': career,
                'age': c.age
            })
            break
        elif survived == 'injured':
            if output_format == 'text':
                print(f"\u26d4\ufe0f  Injured during term {c.terms_served + 1} in {career}. Must muster out immediately.")
            # Note: Age and terms_served are now updated in attempt_reenlistment() 
            # when the term is actually completed, not during injury handling
            # Then add career term with current ages
            c.add_career_term(career, c.terms_served + 1, partial_term=True)
            if output_format == 'text':
                print(f"Final Age: {c.age}, Terms Served: {c.terms_served}")
            c.log_event('injury', {
                'term': c.terms_served + 1,
                'career': career,
                'age': c.age,
                'partial_term': True
            })
            break
        else:  # survived == 'survived'
            # Complete the term normally
            c.complete_term()
            c.add_career_term(career, c.terms_served)
            
            # 2.1 Commission attempt (if not already commissioned, not first term if drafted, and eligible career)
            commission_this_term = False
            if eligible_for_commission and not c.commissioned and not c.drafted:
                # Explicitly prevent commission for Scouts and Others
                if career in ['Navy', 'Marines', 'Army', 'Merchants']:
                    commission_this_term = Character.check_commission(career, c.characteristics)
                    if commission_this_term:
                        c.commissioned = True
                        c.rank = 1
                        c.update_skill_eligibility_for_commission()
                        c.log_event('commission', {
                            'career': career,
                            'rank': c.rank
                        })
                    else:
                        c.log_event('commission_failed', {
                            'career': career
                        })
                    commission_attempted = True
            
            # 2.2 Promotion attempt (if commissioned, not at max promotions)
            promotion_this_term = False
            max_rank = {'Navy': 6, 'Marines': 6, 'Army': 6, 'Merchants': 5}
            current_max_rank = max_rank.get(career, 0)
            
            if eligible_for_promotion and c.commissioned and c.rank < current_max_rank:
                # Explicitly prevent promotion for Scouts and Others
                if career in ['Navy', 'Marines', 'Army', 'Merchants']:
                    promotion_target = {'Navy': 8, 'Marines': 9, 'Army': 6, 'Merchants': 10}
                    roll = Character.roll_2d6()
                    target = promotion_target.get(career, 12)
                    modifier = 0
                    if career == 'Navy' and c.characteristics.get('edu', 0) >= 8:
                        modifier += 1
                    elif career == 'Marines' and c.characteristics.get('int', 0) >= 8:
                        modifier += 1
                    elif career == 'Army' and c.characteristics.get('edu', 0) >= 7:
                        modifier += 1
                    elif career == 'Merchants' and c.characteristics.get('int', 0) >= 9:
                        modifier += 1
                    success = (roll + modifier) >= target
                    if output_format == 'text':
                        print(f"⭐ [PROMOTION] {career}: Roll {roll} + {modifier} = {roll + modifier} (Need {target}) → {'PROMOTED' if success else 'FAILED'}")
                    if success:
                        c.promotions += 1
                        c.rank += 1
                        c.update_skill_eligibility_for_promotion()
                        c.log_event('promotion', {
                            'career': career,
                            'rank': c.rank,
                            'roll': roll,
                            'modifier': modifier,
                            'target': target
                        })
                        promotion_this_term = True
                    else:
                        c.log_event('promotion_failed', {
                            'career': career,
                            'roll': roll,
                            'modifier': modifier,
                            'target': target
                        })
            
            # 3. Determine skills (service + commission + promotion + automatic)
            # 3a) Service skills
            if career == 'Scouts':
                num_skills = 2
            else:
                num_skills = 2 if c.terms_served == 1 else 1
            c.roll_for_skills_detailed(career, num_skills)
            
            # 3b) Commission skills
            if commission_this_term:
                c.grant_automatic_commission_skill(career, output_format)
                c.roll_for_skills_detailed(career, 1, 'commission')
            
            # 3c) Promotion skills
            if promotion_this_term:
                c.grant_automatic_rank_skill(career, c.rank, output_format)
                c.roll_for_skills_detailed(career, 1, 'promotion')
            
            # 3d) Automatic skills (by virtue of rank) - already handled in grant_automatic_rank_skill
            
            # Report skills
            c.display_current_term_skills(output_format)
            
            # Report ageing effects
            c.display_current_term_ageing(output_format)

            if output_format == 'text':
                print(f"✅ [TERM COMPLETED] Term: {c.terms_served}. Age: {c.age}")

            # Roll to re-enlist
            if output_format == 'text':
                preference = 'reenlist'
                reenlistment_result = Character.attempt_reenlistment(career, c.age, preference)

            c.log_event('reenlistment_attempt', {
                'career': career,
                'age': c.age,
                'result': reenlistment_result
            })
            
            # Report outcome of re-enlistment attempt
            if reenlistment_result == 'denied':
                if output_format == 'text':
                    pass
            #       print(f"🔄 Reenlistment denied. Career ends after {c.terms_served} terms at age {c.age}.")
                break
            elif reenlistment_result == 'mandatory':
                # Continue to next term regardless of term count
                pass             # Continue to next term regardless of term count
            elif reenlistment_result == 'approved':
                # Continue to next term
                pass
        
            
         # If drafted and successfully re-enlisted, change status to enlisted
            if c.drafted and reenlistment_result in ['approved', 'mandatory']:
                if output_format == 'text':
                    print(f"[Status Change] {career}: Drafted → Enlisted (successful re-enlistment)")
                c.drafted = False
                c.log_event('status_change', {
                    'career': career,
                    'from': 'drafted',
                    'to': 'enlisted'
                })
    
    # Calculate mustering out rolls at the very end
    mustering_rolls = c.calculate_mustering_out_rolls()
    c.log_event('mustering_out', {
        'total_rolls': mustering_rolls,
        'term_rolls': int(c.terms_served),
        'rank_rolls': mustering_rolls - int(c.terms_served)
    })

    # Perform mustering out process
    gambling_skill = c.skills.get('Gambling', 0)
    c.roll_mustering_out(career, gambling_skill=gambling_skill, output_format=output_format)

    if output_format == 'json':
        return c.to_json()
    else:
        # Display final character sheet
        c.display_character_sheet()
        return c

def run_all_tests():
    """Run all unit tests"""
    print("\n" + "="*50)
    print("RUNNING UNIT TESTS")
    print("="*50)
    
    tests = [
        test_character_stats,
        test_career_choice_modifiers,
        test_enlistment_logic,
        test_survival_logic,
        test_ageing_effects,
        test_skill_acquisition,
        test_commission_and_promotion,
        test_reenlistment_logic,
        test_mustering_out_calculation,
        test_skill_eligibility
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {failed} test(s) failed")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    
    # Check command line arguments for different modes
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "generate"  # Default mode
    
    # Set the random seed for reproducible results
    # Change this number to get different but reproducible results
    # Set to None for truly random results
    set_random_seed(42)  # Use seed=42 for testing, or seed=None for random
    
    if mode == "test" or mode == "tests":
        # Run all unit tests
        success = run_all_tests()
        if not success:
            sys.exit(1)  # Exit with error code if tests fail
    
    elif mode == "generate":
        # Parse additional arguments for career and seed
        service_choice = None
        seed = None
        death_rule = False
        output_format = 'text'  # Default to text output
        
        # Parse arguments
        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i].lower()
            if arg == "--career" or arg == "-c":
                if i + 1 < len(sys.argv):
                    service_choice = sys.argv[i + 1]
                    i += 2
                else:
                    print("Error: --career requires a career name")
                    sys.exit(1)
            elif arg == "--seed" or arg == "-s":
                if i + 1 < len(sys.argv):
                    try:
                        seed = int(sys.argv[i + 1])
                        i += 2
                    except ValueError:
                        print("Error: --seed requires a number")
                        sys.exit(1)
                else:
                    print("Error: --seed requires a number")
                    sys.exit(1)
            elif arg == "--death" or arg == "-d":
                death_rule = True
                i += 1
            elif arg == "--json" or arg == "-j":
                output_format = 'json'
                i += 1
            elif arg == "--help" or arg == "-h":
                print("Traveller Character Generator - Generate Mode Options:")
                print("  python character_generator.py generate                    # Generate random character")
                print("  python character_generator.py generate --career Navy     # Generate Navy character")
                print("  python character_generator.py generate --seed 123        # Generate with seed 123")
                print("  python character_generator.py generate -c Marines -s 456 # Generate Marine with seed 456")
                print("  python character_generator.py generate --death           # Enable death rule")
                print("  python character_generator.py generate --json            # Output in JSON format")
                print("\nAvailable careers: Navy, Marines, Army, Scouts, Merchants, Others")
                sys.exit(0)
            else:
                print(f"Unknown argument: {sys.argv[i]}")
                print("Use --help for usage information")
                sys.exit(1)
        
        # Run full character generation
        result = run_full_character_generation(death_rule_enabled=death_rule, service_choice=service_choice, seed=seed, output_format=output_format)
        
        if output_format == 'json' and result:
            print(json.dumps(result, indent=2))
    
    elif mode == "test-single":
        # Run a specific test function
        if len(sys.argv) > 2:
            test_name = sys.argv[2]
            test_functions = {
                'stats': test_character_stats,
                'career': test_career_choice_modifiers,
                'enlistment': test_enlistment_logic,
                'survival': test_survival_logic,
                'ageing': test_ageing_effects,
                'skills': test_skill_acquisition,
                'commission': test_commission_and_promotion,
                'reenlistment': test_reenlistment_logic,
                'mustering': test_mustering_out_calculation,
                'skill_eligibility': test_skill_eligibility
            }
            
            if test_name in test_functions:
                print(f"Running test: {test_name}")
                test_functions[test_name]()
            else:
                print(f"Unknown test: {test_name}")
                print(f"Available tests: {', '.join(test_functions.keys())}")
        else:
            print("Usage: python character_generator.py test-single <test_name>")
            print("Available tests: stats, career, enlistment, survival, ageing, skills, commission, reenlistment, mustering")
    
    elif mode == "help":
        print("Traveller Character Generator - Usage Options:")
        print("  python character_generator.py                                    # Generate a character (default)")
        print("  python character_generator.py generate                           # Generate a character")
        print("  python character_generator.py generate --career Navy            # Generate Navy character")
        print("  python character_generator.py generate --seed 123               # Generate with seed 123")
        print("  python character_generator.py generate --json                   # Output in JSON format")
        print("  python character_generator.py test                              # Run all unit tests")
        print("  python character_generator.py test-single <test>                # Run specific test")
        print("  python character_generator.py help                              # Show this help")
        print("\nAvailable careers: Navy, Marines, Army, Scouts, Merchants, Others")
        print("Available single tests: stats, career, enlistment, survival, ageing, skills, commission, reenlistment, mustering")
    
    else:
        print(f"Unknown mode: {mode}")
        print("Use 'python character_generator.py help' for usage information")
        sys.exit(1)