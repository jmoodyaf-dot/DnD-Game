
import random as r

from abilities import abilities
from racial_abilities import racial_abilities
from spells import spells



class Player:

    def __init__(self, name: str, race: dict, job: dict, lvl=1):

        # Basic information
        self.name = name
        self.race = race["name"]
        self.job = job["name"]
        self.lvl = lvl
        self.xp = 0

        # Character stats: job base stats + racial modifiers
        stats = job["stats"]
        modifiers = race["stat_modifiers"]

        self.strength = stats["strength"] + modifiers["strength"]
        self.dexterity = stats["dexterity"] + modifiers["dexterity"]
        self.constitution = stats["constitution"] + modifiers["constitution"]
        self.intelligence = stats["intelligence"] + modifiers["intelligence"]
        self.wisdom = stats["wisdom"] + modifiers["wisdom"]
        self.charisma = stats["charisma"] + modifiers["charisma"]

        # Abilities
        self.proficiencies = []
        self.saving_throws = []
        self.skills = []
        self.feats_traits = []

        self.abilities = job["abilities"]
        self.racial_abilities = race["abilities"]
        self.spells = job["spells"]

        # Equipment
        self.equipped = {
            "armor": 0,
            "shield": 0,
            "weapon": None
        }

        # Combat stats
        self.ac = (
            self.equipped["armor"]
            + self.get_modifier(self.dexterity)
            + self.equipped["shield"]
        )

        self.hp = (
            self.constitution + self.roll_health()
        ) * lvl

        self.max_hp = self.hp
        self.initiative = self.get_modifier(self.dexterity)
        self.speed = race["speed"]

        # Active effects and bonuses
        self.resistances = set()
        self.active_effects = set()

        self.bonus_damage = 0
        self.bonus_ac = 0
        self.bonus_speed = 0

        self.rage = False
        self.stone_skin = False
        self.blood_rage = False
        self.lucky = False
        self.quick_step = False
        self.has_wings = False
        self.flying = False
        self.night_vision = False
        self.keen_senses = False
        self.charming = False

        # Combat and inventory
        self.attacks = {}
        self.inventory = []

    # ==============================================
    # DICE
    # ==============================================

    def roll_dice(self, num_of_die, sides):
        total = 0

        for _ in range(num_of_die):
            total += r.randint(1, sides)

        return total

    def roll_health(self):
        return self.roll_dice(1, 10)

    # ==============================================
    # STAT MODIFIERS
    # ==============================================

    def get_modifier(self, stat):
        return (stat - 10) // 2

    # ==============================================
    # DAMAGE AND DEFEAT
    # ==============================================

    def take_damage(self, amount, element=None):

        if self.hp <= 0:
            print(f"{self.name} is already defeated!")
            return

        original_damage = amount

        # Matching resistance halves damage.
        if (
            element is not None
            and (
                element in self.resistances
                or "elemental" in self.resistances
            )
        ):
            amount //= 2

            print(
                f"{self.name}'s resistance reduces "
                f"{original_damage} damage to {amount}!"
            )

        # Stone Skin reduces incoming damage.
        if self.stone_skin:
            amount = max(0, amount - 2)

        self.hp = max(0, self.hp - amount)

        print(f"{self.name} takes {amount} damage!")
        print(f"HP: {self.hp}/{self.max_hp}")

        if self.hp == 0:
            print(f"{self.name} has been defeated!")

    def damage_target(self, target, amount, element=None):

        if target.hp <= 0:
            print(f"{target.name} is already defeated!")
            return

        # Route damage through target's resistance system.
        if hasattr(target, "take_damage"):
            target.take_damage(amount, element)
        else:
            target.hp = max(0, target.hp - amount)

            print(f"{target.name} takes {amount} damage!")

            if target.hp == 0:
                print(f"{target.name} has been defeated!")

    # ==============================================
    # WEAPON ATTACK
    # ==============================================

    def attack(self, target):

        if target.hp <= 0:
            print(f"{target.name} is already defeated!")
            return

        weapon = self.equipped["weapon"]

        if weapon is None:
            print(f"{self.name} doesn't have a weapon!")
            return

        # Attack roll
        attack_roll = self.roll_dice(1, 20)

        stat = getattr(self, weapon["stat"])
        modifier = self.get_modifier(stat)

        # Lucky gives one reroll when the first roll is 1.
        if self.lucky and attack_roll == 1:
            attack_roll = self.roll_dice(1, 20)
            print(f"{self.name} uses Lucky to reroll!")

        attack_total = attack_roll + modifier

        print(
            f"{self.name} rolls {attack_roll} + "
            f"{modifier} = {attack_total}"
        )

        if attack_total < target.ac:
            print(f"{self.name} misses {target.name}!")
            return

        # Damage roll
        damage_roll = self.roll_dice(
            weapon["damage"][0],
            weapon["damage"][1]
        )

        damage = damage_roll + modifier + self.bonus_damage

        if getattr(target, "marked_by", None) is self:
            damage += 3
            print("Nature's Mark adds 3 bonus damage!")

        if getattr(self, "cursed", False):
            damage = max(0, damage - 2)
            print("Curse reduces your damage by 2!")
        
        damage = max(0, damage)

        print(
            f"{self.name} hits {target.name} "
            f"for {damage} damage!"
        )

        self.damage_target(
            target,
            damage,
            weapon.get("element")
        )

    # ==============================================
    # SHARED ABILITY EXECUTION
    # ==============================================

    def execute_ability(self, ability, ability_data, target=None):

        ability_type = ability_data["type"]

        # Attack abilities
        if ability_type == "attack":

            if target is None:
                print("You need a target!")
                return

            if target.hp <= 0:
                print(f"{target.name} is already defeated!")
                return

            damage_roll = self.roll_dice(
                ability_data["damage"][0],
                ability_data["damage"][1]
            )

            stat = ability_data.get("stat", "strength")
            modifier = self.get_modifier(getattr(self, stat))

            damage = max(
                0,
                damage_roll + modifier + self.bonus_damage
            )

            print(f"{self.name} uses {ability}!")

            self.damage_target(
                target,
                damage,
                ability_data.get("element")
            )

        # Healing abilities
        elif ability_type == "heal":

            if self.hp <= 0:
                print("A defeated character cannot heal.")
                return

            heal = self.roll_dice(
                ability_data["amount"][0],
                ability_data["amount"][1]
            )

            actual_heal = min(heal, self.max_hp - self.hp)
            self.hp += actual_heal

            print(f"{self.name} uses {ability}!")
            print(f"{self.name} heals {actual_heal} HP.")
            print(f"HP: {self.hp}/{self.max_hp}")

        # Lifesteal abilities
        elif ability_type == "lifesteal":

            if target is None:
                print("You need a target!")
                return

            if target.hp <= 0:
                print(f"{target.name} is already defeated!")
                return

            damage = self.roll_dice(
                ability_data["damage"][0],
                ability_data["damage"][1]
            )

            # Record actual HP lost after resistance.
            old_hp = target.hp

            self.damage_target(
                target,
                damage,
                ability_data.get("element")
            )

            actual_damage = old_hp - target.hp
            actual_heal = min(
                actual_damage,
                self.max_hp - self.hp
            )

            self.hp += actual_heal

            print(f"{self.name} absorbs {actual_heal} HP.")
            print(f"HP: {self.hp}/{self.max_hp}")

        # Buff abilities
        elif ability_type == "buff":

            effect = ability_data["effect"]

            if effect in ("curse", "nature_mark"):
                if target is None:
                    print("You need a target!")
                    return

                if target.hp <= 0:
                    print(f"{target.name} is already defeated!")
                    return

                if effect == "curse":
                    target.cursed = True
                    print(f"{target.name} is cursed!")

                elif effect == "nature_mark":
                    target.marked_by = self
                    print(f"{self.name} marks {target.name} with nature magic!")

            else:
                self.apply_buff(effect, ability)


        # Resistance abilities
        elif ability_type == "resistance":

            element = ability_data["element"]

            if element in self.resistances:
                print(f"{self.name} already resists {element}.")
                return

            self.resistances.add(element)

            print(f"{self.name} gains {element} resistance!")

        # Utility abilities
        elif ability_type == "utility":

            effect = ability_data["effect"]

            if effect == "charm":
                if target is None:
                    print("You need a target!")
                    return

                if target.hp <= 0:
                    print(f"{target.name} is already defeated!")
                    return

                target.charmed = True
                print(f"{target.name} is charmed!")

            else:
                self.apply_utility(effect, ability)

        else:
            print(f"Unknown ability type: {ability_type}")

    # ==============================================
    # BUFF EFFECTS
    # ==============================================

    def apply_buff(self, effect, ability):

        if effect in self.active_effects:
            print(f"{ability} is already active!")
            return

        self.active_effects.add(effect)

        print(f"{self.name} uses {ability}!")

        if effect == "stone_skin":
            self.stone_skin = True
            self.bonus_ac += 2
            self.ac += 2
            print("Defense increased by 2!")

        elif effect in ("brutal_strength", "demonic_strength"):
            self.bonus_damage += 2
            print("Damage increased by 2!")

        elif effect in ("blood_rage", "demonic_rage", "rage"):
            self.rage = True
            self.blood_rage = effect == "blood_rage"
            self.bonus_damage += 3
            print("Rage activated! Damage increased by 3!")

        elif effect == "quick_step":
            self.quick_step = True
            self.bonus_speed += 10
            self.speed += 10
            print("Speed increased by 10!")

        elif effect == "wings":
            self.has_wings = True
            print("You spread your wings!")

        elif effect == "flight":
            self.flying = True
            print("You take flight!")

        elif effect == "lucky":
            self.lucky = True
            print("Your next natural 1 attack roll can be rerolled.")

        elif effect == "keen_senses":
            self.keen_senses = True
            print("Your senses sharpen!")

        elif effect == "enhanced_senses":
            self.keen_senses = True
            print("Your senses sharpen!")

        elif effect == "adaptable":
            print("You are adaptable!")

        elif effect == "arcane_mind":
            print("Your arcane mind awakens!")

        elif effect == "small_frame":
            print("Your small frame may help you in tight spaces!")

        elif effect == "predator":
            print("Your predatory instincts awaken!")

        elif effect == "curse":
            print("Curse must be applied to a target.")

        elif effect == "nature_mark":
            print("Nature's Mark must be applied to a target.")

        else:
            print(f"{ability} activates: {effect}!")

    # ==============================================
    # UTILITY EFFECTS
    # ==============================================

    def apply_utility(self, effect, ability):

        print(f"{self.name} uses {ability}!")

        if effect == "night_vision":
            self.night_vision = True
            print("You can see in darkness!")

        elif effect == "keen_senses":
            self.keen_senses = True
            print("Your senses sharpen!")

        elif effect == "charm":
            self.charming = True
            print("You become more persuasive!")

        else:
            print(f"Utility effect activated: {effect}!")

    # ==============================================
    # JOB ABILITY
    # ==============================================

    def use_ability(self, ability, target=None):

        if ability not in self.abilities:
            print(f"{self.name} doesn't have {ability}!")
            return

        ability_data = abilities.get(ability)

        if ability_data is None:
            print(f"No data exists for ability: {ability}")
            return

        self.execute_ability(ability, ability_data, target)

    # ==============================================
    # RACIAL ABILITY
    # ==============================================

    def use_racial_ability(self, ability, target=None):

        if ability not in self.racial_abilities:
            print(
                f"{self.name} doesn't have "
                f"the racial ability {ability}!"
            )
            return

        ability_data = racial_abilities.get(ability)

        if ability_data is None:
            print(f"No data exists for racial ability: {ability}")
            return

        self.execute_ability(ability, ability_data, target)

    # ==============================================
    # SPELLCASTING
    # ==============================================

    def spellcast(self, spell, target=None):
         # Check whether the character knows this spell.
        if spell not in self.spells:
            print(f"{self.name} doesn't know {spell}!")
            return

        # Find the spell's definition.
        spell_data = spells.get(spell)

        if spell_data is None:
            print(f"No data exists for spell: {spell}")
            return

        # Execute the spell using the shared ability system.
        self.execute_ability(spell, spell_data, target)

      

    # ==============================================
    # INVENTORY
    # ==============================================

    def add_inventory(self, item):

        self.inventory.append(item)
        print(f"{item['name']} added to {self.name}'s inventory.")

    def remove_inventory(self, item):

        if item in self.inventory:
            self.inventory.remove(item)
            print(f"{item['name']} removed from {self.name}'s inventory.")
        else:
            print(f"{item['name']} isn't in the inventory.")

    def use_item(self, item):

        if item not in self.inventory:
            print(f"{item['name']} isn't in the inventory.")
            return

        print(f"{self.name} uses {item['name']}.")
        self.inventory.remove(item)

    # ==============================================
    # MOVEMENT
    # ==============================================

    def move(self, direction):

        print(f"{self.name} moves {direction}.")

    # ==============================================
    # XP
    # ==============================================

    def gain_xp(self, amount):

        self.xp += amount
        print(f"{self.name} gained {amount} XP!")

        while self.xp >= 100:
            self.xp -= 100
            self.level_up()

    # ==============================================
    # LEVEL UP
    # ==============================================

    def level_up(self):

        self.lvl += 1
        self.max_hp += self.constitution
        self.hp = self.max_hp

        print(f"{self.name} reached level {self.lvl}!")
        print(f"Max HP: {self.max_hp}")
        print(f"XP remaining: {self.xp}")

    # ==============================================
    # CHARACTER INFO
    # ==============================================

    def show_stats(self):

        print("\n========== CHARACTER ==========")
        print(f"Name:  {self.name}")
        print(f"Race:  {self.race}")
        print(f"Job:   {self.job}")
        print(f"Level: {self.lvl}")
        print(f"XP:    {self.xp}/100")

        print("\n---------- STATS ----------")
        print(f"Strength:     {self.strength}")
        print(f"Dexterity:    {self.dexterity}")
        print(f"Constitution: {self.constitution}")
        print(f"Intelligence: {self.intelligence}")
        print(f"Wisdom:       {self.wisdom}")
        print(f"Charisma:     {self.charisma}")

        print("\n---------- COMBAT ----------")
        print(f"HP:         {self.hp}/{self.max_hp}")
        print(f"AC:         {self.ac}")
        print(f"Initiative: {self.initiative}")
        print(f"Speed:      {self.speed}")
        print(f"Bonus damage: {self.bonus_damage}")
        print(f"Resistances: {self.resistances}")

        print("\n---------- JOB ----------")
        print(f"Abilities: {self.abilities}")
        print(f"Spells: {self.spells}")

        print("\n---------- RACE ----------")
        print(f"Racial abilities: {self.racial_abilities}")
        print(f"Active effects: {self.active_effects}")

        print("\n---------- INVENTORY ----------")
        print(self.inventory)
        print("\n===============================\n")
