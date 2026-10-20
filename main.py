
from player import Player
from races import races
from jobs import jobs
from combat import start_combat


class Enemy:
    def __init__(
        self,
        name,
        hp=50,
        ac=10,
        damage=5,
        xp_reward=25
    ):
        self.name = name
        self.hp = hp
        self.ac = ac
        self.damage = damage
        self.xp_reward = xp_reward

    def take_damage(self, amount, element=None):
        self.hp = max(0, self.hp - amount)
        print(f"{self.name} takes {amount} damage!")

        if self.hp == 0:
            print(f"{self.name} has been defeated!")


player = Player(
    "Drake",
    races["Dragonborn"],
    jobs["Paladin"]
)

player.equipped["weapon"] = {
    "name": "Iron Sword",
    "damage": (1, 8),
    "stat": "strength"
}

goblin = Enemy(
    "Goblin",
    hp=50,
    ac=10,
    damage=5,
    xp_reward=25
)

start_combat(player, goblin)
