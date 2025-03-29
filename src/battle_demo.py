from boi import BoiBuilder
from team import Team
from battle_system import BattleSystem


def main():
    # Create Team 0 with basic pets
    team0 = Team(
        [
            BoiBuilder().set_type_name("Ant").set_attack(2).set_health(1).build(),
            BoiBuilder().set_type_name("Fish").set_attack(3).set_health(2).build(),
        ]
    )

    # Create Team 1 with basic pets
    team1 = Team(
        [
            BoiBuilder().set_type_name("Mosquito").set_attack(2).set_health(2).build(),
            BoiBuilder().set_type_name("Cricket").set_attack(1).set_health(2).build(),
        ]
    )

    # Initialize the BattleSystem
    def log_event(event):
        print(f"Event: type={event.type}, data={event.data}")

    battle_system = BattleSystem(team0, team1, event_callbacks=[log_event])

    # Run the battle turn by turn
    while not battle_system.is_battle_over():
        print("Running a turn...")
        battle_system.run_turn()

    # Display the winner
    winner = battle_system.get_winner()
    if winner is None:
        print("The battle ended in a draw!")
    else:
        print(f"Team {winner} wins the battle!")


if __name__ == "__main__":
    main()
