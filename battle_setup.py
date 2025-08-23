import asyncio
from poke_env.player import RandomPlayer


async def run_tournament():
    """Run a tournament between different bot types"""

    # Create different types of bots
    bots = {
        "Random": RandomPlayer(),
        "MaxDamage": MaxDamagePlayer(),
        "Smart": SmartHeuristicPlayer(),
    }

    # Results tracking
    results = {name: {"wins": 0, "battles": 0} for name in bots.keys()}

    # Round-robin tournament
    bot_names = list(bots.keys())
    for i in range(len(bot_names)):
        for j in range(i + 1, len(bot_names)):
            name1, name2 = bot_names[i], bot_names[j]
            bot1, bot2 = bots[name1], bots[name2]

            print(f"Battle: {name1} vs {name2}")

            # Reset battle counts
            bot1.reset_battles()
            bot2.reset_battles()

            # Battle
            await bot1.battle_against(bot2, n_battles=100)

            # Record results
            results[name1]["wins"] += bot1.n_won_battles
            results[name1]["battles"] += 100
            results[name2]["wins"] += bot2.n_won_battles
            results[name2]["battles"] += 100

            print(f"  {name1}: {bot1.n_won_battles}/100 wins")
            print(f"  {name2}: {bot2.n_won_battles}/100 wins")

    # Print final results
    print("\nTournament Results:")
    for name, stats in results.items():
        win_rate = stats["wins"] / stats["battles"] if stats["battles"] > 0 else 0
        print(f"{name}: {stats['wins']}/{stats['battles']} ({win_rate:.2%} win rate)")


# Run the tournament
asyncio.run(run_tournament())
