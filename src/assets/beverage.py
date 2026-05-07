"""
FOODIE Beverage Assets

Hard-coded backward-chaining rule base and fallback beverage data
for the FOODIE_SPA expert system (Goal C).
"""

# *** constants

# ** constant: BEVERAGE_RULES
BEVERAGE_RULES = [

    # --- Level 1: Category rules (establish intermediate conclusions) ---

    # R1: LIQUOR is indicated <- occasion=celebration, guest_age=adult
    {
        'id': 'R1',
        'conclusion': 'LIQUOR is indicated',
        'conditions': [
            ('occasion', 'celebration'),
            ('guest_age', 'adult'),
        ],
        'beverage_type': 'liquor',
    },

    # R3: BEER is indicated <- occasion=casual, guest_age=adult
    {
        'id': 'R3',
        'conclusion': 'BEER is indicated',
        'conditions': [
            ('occasion', 'casual'),
            ('guest_age', 'adult'),
        ],
        'beverage_type': 'beer',
    },

    # R6: WINE is indicated <- entree=steak, guest_age=adult
    {
        'id': 'R6',
        'conclusion': 'WINE is indicated',
        'conditions': [
            ('entree', 'steak'),
            ('guest_age', 'adult'),
        ],
        'beverage_type': 'wine',
    },

    # R7: WINE is indicated <- entree=chicken, guest_age=adult
    {
        'id': 'R7',
        'conclusion': 'WINE is indicated',
        'conditions': [
            ('entree', 'chicken'),
            ('guest_age', 'adult'),
        ],
        'beverage_type': 'wine',
    },

    # R8: JUICE is indicated <- health_nut=True
    {
        'id': 'R8',
        'conclusion': 'JUICE is indicated',
        'conditions': [
            ('health_nut', True),
        ],
        'beverage_type': 'juice',
    },

    # R11: WATER is indicated <- guest_age=minor
    {
        'id': 'R11',
        'conclusion': 'WATER is indicated',
        'conditions': [
            ('guest_age', 'minor'),
        ],
        'beverage_type': 'water',
    },

    # --- Level 2: Selection rules (establish CHOOSE conclusions) ---

    # R2: CHOOSE Polish Vodka <- LIQUOR is indicated, formality=formal
    {
        'id': 'R2',
        'conclusion': 'CHOOSE Polish Vodka',
        'conditions': [
            ('LIQUOR is indicated', True),
            ('formality', 'formal'),
        ],
        'beverage_type': 'liquor',
    },

    # R4: CHOOSE Dos Equis <- BEER is indicated
    {
        'id': 'R4',
        'conclusion': 'CHOOSE Dos Equis',
        'conditions': [
            ('BEER is indicated', True),
        ],
        'beverage_type': 'beer',
    },

    # R5: CHOOSE Corona Beer <- BEER is indicated, setting=outdoor
    {
        'id': 'R5',
        'conclusion': 'CHOOSE Corona Beer',
        'conditions': [
            ('BEER is indicated', True),
            ('setting', 'outdoor'),
        ],
        'beverage_type': 'beer',
    },

    # R9: CHOOSE Carrot Juice <- JUICE is indicated, allergies_citrus=True
    {
        'id': 'R9',
        'conclusion': 'CHOOSE Carrot Juice',
        'conditions': [
            ('JUICE is indicated', True),
            ('allergies_citrus', True),
        ],
        'beverage_type': 'juice',
    },

    # R10: CHOOSE Orange Juice <- JUICE is indicated, allergies_citrus=False
    {
        'id': 'R10',
        'conclusion': 'CHOOSE Orange Juice',
        'conditions': [
            ('JUICE is indicated', True),
            ('allergies_citrus', False),
        ],
        'beverage_type': 'juice',
    },

    # R12: CHOOSE Sparkling Water <- WATER is indicated, formality=formal
    {
        'id': 'R12',
        'conclusion': 'CHOOSE Sparkling Water',
        'conditions': [
            ('WATER is indicated', True),
            ('formality', 'formal'),
        ],
        'beverage_type': 'water',
    },

    # R13: CHOOSE Cheap Beer <- guest_liked=False, guest_age=adult (direct)
    {
        'id': 'R13',
        'conclusion': 'CHOOSE Cheap Beer',
        'conditions': [
            ('guest_liked', False),
            ('guest_age', 'adult'),
        ],
        'beverage_type': 'beer',
    },

    # R14: CHOOSE Champagne <- occasion=new_years_eve, guest_age=adult (direct)
    {
        'id': 'R14',
        'conclusion': 'CHOOSE Champagne',
        'conditions': [
            ('occasion', 'new_years_eve'),
            ('guest_age', 'adult'),
        ],
        'beverage_type': 'liquor',
    },

    # R15: CHOOSE Sparkling Water <- (universal fallback, empty conditions)
    {
        'id': 'R15',
        'conclusion': 'CHOOSE Sparkling Water',
        'conditions': [],
        'beverage_type': 'water',
    },
]

# ** constant: FALLBACK_BEVERAGE
FALLBACK_BEVERAGE = {
    'name': 'Sparkling Water',
    'beverage_type': 'water',
    'brand': 'San Pellegrino',
    'is_health_friendly': True,
}
