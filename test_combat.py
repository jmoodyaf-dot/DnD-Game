
from player import Player
from races import races
from jobs import jobs


class Enemy:
    def __init__(self, name, hp=50, ac=10):
        self.name = name
        self.hp = hp
        self.ac = ac

    def take_damage(self, amount, element=None):
        self.hp = max(0, self.hp - amount)

        print(f"{self.name} takes {amount} damage!")

        if self.hp <= 0:
            print(f"{self.name} has been defeated!")


# Create a player and an enemy
player = Player(
    name="Drake",
    race=races["Dragonborn"],
    job=jobs["Warrior"]
)

enemy = Enemy("Goblin")

# Display the character
player.show_stats()

print("\n--- COMBAT TEST ---")

# Test a racial ability
player.use_racial_ability("Dragon Breath", enemy)

print(f"\n{enemy.name} HP: {enemy.hp}")

# Test a normal weapon attack
player.equipped["weapon"] = {
    "name": "Iron Sword",
    "damage": (1, 8),
    "stat": "strength"
}

player.attack(enemy)

print(f"\n{enemy.name} HP: {enemy.hp}")



