from poke_env.player import Player
from poke_env import RandomPlayer
import asyncio


class MaxDamagePlayer(Player):
    """
    A simple bot that chooses moves with the highest base power,
    or switches to Pokemon with more HP when needed.
    """

    def choose_move(self, battle):
        # If we have available moves, pick the strongest one
        if battle.available_moves:
            # Find move with highest base power
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            return self.create_order(best_move)

        # If no moves available, try to switch to a healthier Pokemon
        elif battle.available_switches:
            # Switch to Pokemon with highest HP percentage
            best_switch = max(
                battle.available_switches,
                key=lambda pokemon: pokemon.current_hp_fraction,
            )
            return self.create_order(best_switch)

        # Fallback to random move
        return self.choose_random_move(battle)


# Create players
max_damage_bot = MaxDamagePlayer()
random_bot = RandomPlayer()


async def main():
    # Battle them against each other
    await max_damage_bot.battle_against(random_bot, n_battles=10)

    print(f"Max Damage Bot win rate: {max_damage_bot.n_won_battles / 10}")
    print(f"Random Bot win rate: {random_bot.n_won_battles / 10}")


# Run the battles
asyncio.run(main())
