
spells = {

    # ==========================================
    # MAGE SPELLS
    # ==========================================

    "Fireball": {
        "type": "attack",
        "damage": (2, 8),
        "element": "fire",
        "stat": "intelligence"
    },

    "Ice Bolt": {
        "type": "attack",
        "damage": (2, 6),
        "element": "ice",
        "stat": "intelligence"
    },

    # ==========================================
    # PALADIN / CLERIC SPELLS
    # ==========================================

    "Holy Light": {
        "type": "heal",
        "amount": (3, 8)
    },

    "Heal": {
        "type": "heal",
        "amount": (2, 8)
    },

    # ==========================================
    # RANGER SPELLS
    # ==========================================

    "Nature's Mark": {
        "type": "buff",
        "effect": "nature_mark"
    },

    # ==========================================
    # BARD SPELLS
    # ==========================================

    "Charm": {
        "type": "utility",
        "effect": "charm"
    },

    "Inspire": {
        "type": "buff",
        "effect": "inspire"
    },

    # ==========================================
    # WARLOCK SPELLS
    # ==========================================

    "Dark Bolt": {
        "type": "attack",
        "damage": (2, 8),
        "element": "dark",
        "stat": "intelligence"
    },

    "Curse": {
        "type": "buff",
        "effect": "curse"
    }
}
