"""
FOODIE Beverage Assets

Hard-coded backward-chaining rule base and fallback beverage data
for the FOODIE_SPA expert module (Goal C).
"""

# *** constants

# ** constant: BEVERAGE_RULES
BEVERAGE_RULES = [
    # R1: Liquor rules
    {'id': 'R1', 'conclusion': 'LIQUOR is indicated',
     'conditions': [('occasion', 'celebration'), ('guest_age', 'adult')],
     'beverage_type': 'liquor'},

    # R2: Specific liquor - Polish Vodka for formal celebration
    {'id': 'R2', 'conclusion': 'CHOOSE Polish Vodka',
     'conditions': [('LIQUOR is indicated', True), ('formality', 'formal')],
     'beverage_type': 'liquor'},

    # R3: Beer rules
    {'id': 'R3', 'conclusion': 'BEER is indicated',
     'conditions': [('occasion', 'casual'), ('guest_age', 'adult')],
     'beverage_type': 'beer'},

    # R4: Specific beer - Dos Equis for casual adult gathering
    {'id': 'R4', 'conclusion': 'CHOOSE Dos Equis',
     'conditions': [('BEER is indicated', True)],
     'beverage_type': 'beer'},

    # R5: Specific beer - Corona for summer/outdoor
    {'id': 'R5', 'conclusion': 'CHOOSE Corona Beer',
     'conditions': [('BEER is indicated', True), ('setting', 'outdoor')],
     'beverage_type': 'beer'},

    # R6: Wine rules
    {'id': 'R6', 'conclusion': 'WINE is indicated',
     'conditions': [('entree', 'steak'), ('guest_age', 'adult')],
     'beverage_type': 'wine'},

    # R7: Wine for chicken dinner
    {'id': 'R7', 'conclusion': 'WINE is indicated',
     'conditions': [('entree', 'chicken'), ('guest_age', 'adult')],
     'beverage_type': 'wine'},

    # R8: Health-nut juice selection
    {'id': 'R8', 'conclusion': 'JUICE is indicated',
     'conditions': [('health_nut', True)],
     'beverage_type': 'juice'},

    # R9: Carrot juice for health nut with citrus allergy
    {'id': 'R9', 'conclusion': 'CHOOSE Carrot Juice',
     'conditions': [('JUICE is indicated', True), ('allergies_citrus', True)],
     'beverage_type': 'juice'},

    # R10: Orange juice for health nut without citrus allergy
    {'id': 'R10', 'conclusion': 'CHOOSE Orange Juice',
     'conditions': [('JUICE is indicated', True), ('allergies_citrus', False)],
     'beverage_type': 'juice'},

    # R11: Water as universal safe option
    {'id': 'R11', 'conclusion': 'WATER is indicated',
     'conditions': [('guest_age', 'minor')],
     'beverage_type': 'water'},

    # R12: Sparkling water for formal setting
    {'id': 'R12', 'conclusion': 'CHOOSE Sparkling Water',
     'conditions': [('WATER is indicated', True), ('formality', 'formal')],
     'beverage_type': 'water'},

    # R13: Guest not well liked -> cheap beer
    {'id': 'R13', 'conclusion': 'CHOOSE Cheap Beer',
     'conditions': [('guest_liked', False), ('guest_age', 'adult')],
     'beverage_type': 'beer'},

    # R14: New Year's Eve celebration -> champagne
    {'id': 'R14', 'conclusion': 'CHOOSE Champagne',
     'conditions': [('occasion', 'new_years_eve'), ('guest_age', 'adult')],
     'beverage_type': 'liquor'},

    # R15: Default water for any remaining case
    {'id': 'R15', 'conclusion': 'CHOOSE Sparkling Water',
     'conditions': [],
     'beverage_type': 'water'},
]

# ** constant: FALLBACK_BEVERAGE
FALLBACK_BEVERAGE = {
    'name': 'Sparkling Water',
    'beverage_type': 'water',
    'brand': 'San Pellegrino',
    'is_health_friendly': True,
}
