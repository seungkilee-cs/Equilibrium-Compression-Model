from poke_env.player import RandomPlayer
from poke_env.environment import AbstractBattle
from poke_env import PlayerConfiguration
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
import numpy as np
from gym import spaces


class RLPlayer(Player):
    """
    Reinforcement Learning player that can be trained using OpenAI Gym interface
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_space = spaces.Discrete(
            22
        )  # 4 moves + 6 switches + 12 mega/z moves
        self.observation_space = spaces.Box(
            low=-1, high=1, shape=(100,), dtype=np.float32
        )

    def embed_battle(self, battle):
        """Convert battle state to numerical vector"""
        # Initialize observation vector
        obs = np.zeros(100)

        # Active Pokemon stats (normalized)
        if battle.active_pokemon:
            obs[0] = battle.active_pokemon.current_hp_fraction
            obs[12] = battle.active_pokemon.base_stats["atk"] / 200.0
            obs[13] = battle.active_pokemon.base_stats["def"] / 200.0
            obs[14] = battle.active_pokemon.base_stats["spa"] / 200.0
            obs[15] = battle.active_pokemon.base_stats["spd"] / 200.0
            obs[2] = battle.active_pokemon.base_stats["spe"] / 200.0

        # Opponent Pokemon stats
        if battle.opponent_active_pokemon:
            obs[16] = battle.opponent_active_pokemon.current_hp_fraction
            obs[17] = battle.opponent_active_pokemon.base_stats["atk"] / 200.0
            obs[18] = battle.opponent_active_pokemon.base_stats["def"] / 200.0
            obs[19] = battle.opponent_active_pokemon.base_stats["spa"] / 200.0
            obs[20] = battle.opponent_active_pokemon.base_stats["spd"] / 200.0
            obs[21] = battle.opponent_active_pokemon.base_stats["spe"] / 200.0

        # Available moves encoding
        for i, move in enumerate(battle.available_moves[:4]):
            if move.base_power:
                obs[12 + i] = move.base_power / 150.0
            obs[16 + i] = move.accuracy / 100.0 if move.accuracy else 1.0
            obs[20 + i] = move.pp / move.max_pp if move.max_pp else 0

        # Team health status
        for i, pokemon in enumerate(battle.team.values()):
            if i < 6:
                obs[24 + i] = pokemon.current_hp_fraction

        # Opponent team info (what we know)
        for i, pokemon in enumerate(battle.opponent_team.values()):
            if i < 6:
                obs[30 + i] = (
                    pokemon.current_hp_fraction if pokemon.current_hp_fraction else 1.0
                )

        # Weather and field conditions
        weather_conditions = ["raindance", "sunnyday", "sandstorm", "hail"]
        for i, weather in enumerate(weather_conditions):
            obs[36 + i] = 1.0 if battle.weather == weather else 0.0

        return obs

    def compute_reward(self, battle):
        """Compute reward based on battle outcome and state"""
        if battle.battle_tag:
            # Battle ended
            if battle.won:
                return 1.0
            else:
                return -1.0

        # Intermediate rewards based on HP differential
        our_hp = sum(p.current_hp_fraction for p in battle.team.values()) / 6
        opp_hp = sum(
            p.current_hp_fraction
            for p in battle.opponent_team.values()
            if p.current_hp_fraction
        ) / max(
            1, len([p for p in battle.opponent_team.values() if p.current_hp_fraction])
        )

        return (our_hp - opp_hp) * 0.1

    def choose_move(self, battle):
        """Choose move based on current policy"""
        if hasattr(self, "model"):
            obs = self.embed_battle(battle)
            action, _ = self.model.predict(obs, deterministic=True)
            return self.action_to_move(action, battle)
        else:
            return self.choose_random_move(battle)

    def action_to_move(self, action, battle):
        """Convert action number to actual move"""
        # Actions 0-3: use moves
        if action < len(battle.available_moves):
            return self.create_order(battle.available_moves[action])

        # Actions 4-9: switch Pokemon
        switch_action = action - 4
        if switch_action < len(battle.available_switches):
            return self.create_order(battle.available_switches[switch_action])

        # Fallback
        return self.choose_random_move(battle)


# Training setup
def train_rl_bot():
    # Create training environment
    training_player = RLPlayer()
    opponent = RandomPlayer()

    # Create and train model
    model = PPO("MlpPolicy", training_player, verbose=1)
    model.learn(total_timesteps=10000)

    # Save the trained model
    training_player.model = model
    return training_player


# Usage
trained_bot = train_rl_bot()
