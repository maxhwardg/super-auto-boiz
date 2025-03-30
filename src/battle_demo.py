"""
Demo script for battle system implementing Super Auto Pets characters.
"""

from boi import BoiBuilder
from team import Team
from battle_system import BattleSystem
from system import Event


def ant_faint_callback(boi, system, event):
    """Give a random friend +2/+1 when the ant faints."""
    # Find our team
    team_idx = system.boi_team(boi)
    if team_idx is not None and len(system.teams[team_idx].bois) > 0:
        # Get the first teammate (if there are any left)
        target = system.teams[team_idx].bois[0]
        # Buff them
        target.attack += 2
        target.health += 1
        print(f"{boi.type_name} gave buff to {target.type_name} (+2/+1)")


def cricket_faint_callback(boi, system, event):
    """Summon a 1/1 zombie cricket on faint."""
    team_idx = system.boi_team(boi)
    if team_idx is not None:
        # Create a zombie cricket
        zombie = (
            BoiBuilder()
            .set_type_name("Zombie Cricket")
            .set_attack(1)
            .set_health(1)
            .build()
        )

        # Add the zombie to the same team
        system.replace_boi(boi, zombie)
        print(f"{boi.type_name} summoned a {zombie}")


def beaver_end_turn_callback(boi, system, event):
    """Give two random friends +1 health at end of turn."""
    team_idx = system.boi_team(boi)
    if team_idx is not None:
        teammates = [b for b in system.teams[team_idx].bois if b != boi]
        # Buff up to 2 teammates
        for i in range(min(2, len(teammates))):
            if i < len(teammates):
                teammates[i].health += 1
                print(f"{boi.type_name} gave +1 health to {teammates[i].type_name}")


def mosquito_start_battle_callback(boi, system, event):
    """Deal 1 damage to a random enemy."""
    # Find enemy team
    enemy_team = system.other_team(boi)
    if len(enemy_team.bois) > 0:
        # Target the first enemy
        target = enemy_team.bois[0]
        # Deal 1 damage
        system.send_event(
            Event(
                type="damage",
                target=target,
                source=boi,
                damage=1,
            )
        )
        print(f"{boi.type_name} dealt 1 damage to {target.type_name}")


def dodo_start_turn_callback(boi, system, event):
    """Give 50% of attack to friend ahead."""
    team_idx = system.boi_team(boi)
    if team_idx is not None:
        teammates = system.teams[team_idx].bois
        # Find our position
        boi_idx = teammates.index(boi)
        # If we have a friend ahead
        if boi_idx > 0:
            target = teammates[boi_idx - 1]
            bonus = boi.attack // 2
            target.attack += bonus
            print(f"{boi.type_name} gave +{bonus} attack to {target.type_name}")


def print_event(event):
    """Print event information for debugging."""
    if event.type == "attack":
        if "target" in event.data:
            print(f"{event.data['target']} is attacking")
    elif event.type == "damage":
        if "target" in event.data and "damage" in event.data:
            print(f"{event.data['target']} took {event.data['damage']} damage")
    elif event.type == "death":
        if "target" in event.data:
            print(f"{event.data['target']} has fainted")
    elif event.type == "battle_start":
        print("Battle is starting!")
    elif event.type == "battle_turn_start":
        print("Turn is starting!")
    elif event.type == "battle_turn_end":
        print("Turn is ending!")


def create_ant():
    """Create an Ant Boi."""
    return (
        BoiBuilder()
        .set_type_name("Ant")
        .set_attack(2)
        .set_health(1)
        .add_trigger("death", ant_faint_callback)
        .build()
    )


def create_cricket():
    """Create a Cricket Boi."""
    return (
        BoiBuilder()
        .set_type_name("Cricket")
        .set_attack(1)
        .set_health(2)
        .add_trigger("death", cricket_faint_callback)
        .build()
    )


def create_beaver():
    """Create a Beaver Boi."""
    return (
        BoiBuilder()
        .set_type_name("Beaver")
        .set_attack(2)
        .set_health(2)
        .add_trigger("battle_turn_end", beaver_end_turn_callback)
        .build()
    )


def create_mosquito():
    """Create a Mosquito Boi."""
    return (
        BoiBuilder()
        .set_type_name("Mosquito")
        .set_attack(2)
        .set_health(2)
        .add_trigger("battle_start", mosquito_start_battle_callback)
        .build()
    )


def create_dodo():
    """Create a Dodo Boi."""
    return (
        BoiBuilder()
        .set_type_name("Dodo")
        .set_attack(2)
        .set_health(3)
        .add_trigger("battle_turn_start", dodo_start_turn_callback)
        .build()
    )


def print_team(team_name, team):
    """Print the current state of a team."""
    print(f"\n{team_name} Team:")
    for i, boi in enumerate(team.bois):
        print(f"  {i+1}. {boi}")


def main():
    """Main function to run the battle demo."""
    print("Creating Teams...")

    # Create team 1 with Ant, Cricket, and Beaver
    team1 = Team([create_ant(), create_cricket(), create_beaver()])

    # Create team 2 with Mosquito and Dodo
    team2 = Team([create_mosquito(), create_dodo()])

    print("Teams created!")
    print_team("Team 1", team1)
    print_team("Team 2", team2)

    print("\n--- STARTING BATTLE ---\n")

    # Create battle system
    battle = BattleSystem(team1, team2, [print_event])

    # Run turns until battle is over
    turn_number = 1
    while not battle.is_battle_over():
        print(f"\n--- TURN {turn_number} ---")
        battle.run_turn()

        print("\nAfter turn:")
        print_team("Team 1", team1)
        print_team("Team 2", team2)

        turn_number += 1

    # Print the winner
    winner = battle.get_winner()
    print("\n--- BATTLE OVER ---")
    if winner is None:
        print("It's a draw!")
    else:
        print(f"Team {winner + 1} wins!")


if __name__ == "__main__":
    main()
