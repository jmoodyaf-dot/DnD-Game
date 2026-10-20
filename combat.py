
# combat.py

from abilities import abilities as job_ability_data
from racial_abilities import racial_abilities as racial_ability_data
from spells import spells


def select_ability(ability_list, menu_title):
    """Display abilities and return the selected ability name."""

    if not ability_list:
        print("You have no abilities available!")
        return None

    print(f"\n--- {menu_title} ---")

    for number, ability in enumerate(ability_list, start=1):
        print(f"{number}. {ability}")

    print("0. Cancel")

    try:
        choice = int(input("\nChoose an ability: ").strip())
    except ValueError:
        print("Please enter a number!")
        return None

    if choice == 0:
        print("Selection cancelled.")
        return None

    if 1 <= choice <= len(ability_list):
        return ability_list[choice - 1]

    print("Invalid ability number!")
    return None


def use_selected_ability(player, enemy, ability, racial=False):
    """Choose the correct target based on the ability type."""

    data = racial_ability_data if racial else job_ability_data
    ability_info = data.get(ability)

    if ability_info is None:
        print(f"Ability data not found for {ability}!")
        return False

    ability_type = ability_info.get("type")

    # Attacks require a living enemy target.
    if ability_type in ("attack", "lifesteal"):
        if enemy.hp <= 0:
            print("There is no enemy to target!")
            return False

        if racial:
            player.use_racial_ability(ability, enemy)
        else:
            player.use_ability(ability, enemy)

    # Healing and other self-effects don't target the enemy.
    elif ability_type in ("heal", "buff", "resistance", "utility"):
        if racial:
            player.use_racial_ability(ability)
        else:
            player.use_ability(ability)

    else:
        print(f"Unknown ability type: {ability_type}")
        return False

    return True


def cast_selected_spell(player, enemy, spell):
    """Cast a spell on the appropriate target."""

    spell_info = spells.get(spell)

    if spell_info is None:
        print(f"Spell data not found for {spell}!")
        return False

    spell_type = spell_info.get("type")

    if spell_type in ("attack", "lifesteal"):
        if enemy.hp <= 0:
            print("There is no enemy to target!")
            return False

        player.execute_ability(spell, spell_info, enemy)

    
    elif spell_type == "heal":
        player.execute_ability(spell, spell_info)

    elif spell_type in ("buff", "utility", "resistance"):
        effect = spell_info.get("effect")

        # These spells affect the enemy.
        if effect in ("charm", "curse", "nature_mark"):
            if enemy.hp <= 0:
                print("There is no enemy to target!")
                return False

            player.execute_ability(spell, spell_info, enemy)

        else:
            player.execute_ability(spell, spell_info)


    else:
        print(f"Unknown spell type: {spell_type}")
        return False

    return True

def start_combat(player, enemy):
    print(f"\nA {enemy.name} appears!")

    while player.hp > 0 and enemy.hp > 0:

        # PLAYER TURN
        print("\n" + "=" * 30)
        print("YOUR TURN")
        print("=" * 30)

        print(f"\n{player.name}: {player.hp}/{player.max_hp} HP")
        print(f"{enemy.name}: {enemy.hp} HP")

        print("\n1. Attack")
        print("2. Racial ability")
        print("3. Job ability")
        print("4. Cast spell")
        print("5. Run away")

        choice = input("\nChoose an action: ").strip()

        # Track whether the player used an action.
        action_used = False

        if choice == "1":
            player.attack(enemy)
            action_used = True

        elif choice == "2":
            ability = select_ability(
                player.racial_abilities,
                "RACIAL ABILITIES"
            )

            if ability is not None:
                action_used = use_selected_ability(
                    player, enemy, ability, racial=True
                )

        elif choice == "3":
            ability = select_ability(
                player.abilities,
                "JOB ABILITIES"
            )

            if ability is not None:
                action_used = use_selected_ability(
                    player, enemy, ability
                )

        elif choice == "4":
            spell = select_ability(player.spells, "SPELLS")

            if spell is not None:
                action_used = cast_selected_spell(
                    player, enemy, spell
                )

        elif choice == '5':
            print(f"{player.name} escaped from {enemy.name}!")
            return

        else:
            print("Invalid choice!")
            continue

        # Cancelled or invalid ability selections don't
        # give the enemy a free turn.
        if not action_used:
            continue

        # Check whether the enemy was defeated.
        if enemy.hp <= 0:
            break

        
        
        # ENEMY TURN
        print("\n" + "-" * 30)
        print(f"{enemy.name.upper()}'S TURN")
        print("-" * 30)

        if getattr(enemy, "charmed", False):
            print(f"{enemy.name} is charmed and cannot attack!")

            # Charm wears off after preventing one attack.
            enemy.charmed = False
            print(f"{enemy.name} is no longer charmed.")

        else:
            damage = getattr(enemy, "damage", 5)

            print(f"{enemy.name} attacks for {damage} damage!")
            player.take_damage(damage)

        if player.hp <= 0:
            print(f"\n{player.name} has been defeated!")
            return


    # VICTORY
    if enemy.hp <= 0:
        print("\n" + "=" * 30)
        print(f"VICTORY! You defeated {enemy.name}!")
        print("=" * 30)

        xp_reward = getattr(enemy, "xp_reward", 25)

        print(f"You earned {xp_reward} XP!")
        player.gain_xp(xp_reward)
