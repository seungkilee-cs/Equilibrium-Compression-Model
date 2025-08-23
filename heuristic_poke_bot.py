from poke_env.player import Player
from poke_env.environment import Move
import numpy as np


class SmartHeuristicPlayer(Player):
    """
    A more sophisticated bot using multiple heuristics:
    - Type effectiveness
    - Pokemon health
    - Move accuracy and power
    - Status conditions
    """

    def choose_move(self, battle):
        # Get current state
        active_pokemon = battle.active_pokemon
        opponent_pokemon = battle.opponent_active_pokemon

        # Evaluate available moves
        if battle.available_moves:
            move_scores = {}

            for move in battle.available_moves:
                score = self.evaluate_move(
                    move, active_pokemon, opponent_pokemon, battle
                )
                move_scores[move] = score

            # Choose move with highest score
            best_move = max(move_scores, key=move_scores.get)
            return self.create_order(best_move)

        # Evaluate switches if no good moves
        elif battle.available_switches:
            switch_scores = {}

            for switch in battle.available_switches:
                score = self.evaluate_switch(switch, opponent_pokemon, battle)
                switch_scores[switch] = score

            best_switch = max(switch_scores, key=switch_scores.get)
            return self.create_order(best_switch)

        return self.choose_random_move(battle)

    def evaluate_move(self, move, active_pokemon, opponent_pokemon, battle):
        """Evaluate a move's effectiveness"""
        score = 0

        # Base power
        if move.base_power:
            score += move.base_power

        # Type effectiveness
        if opponent_pokemon:
            effectiveness = move.type.damage_multiplier(
                opponent_pokemon.type_1,
                opponent_pokemon.type_2,
                type_chart=battle.battle_format.type_chart,
            )
            score *= effectiveness

        # STAB (Same Type Attack Bonus)
        if move.type in [active_pokemon.type_1, active_pokemon.type_2]:
            score *= 1.5

        # Accuracy consideration
        if move.accuracy:
            score *= move.accuracy / 100

        # Priority moves bonus
        if move.priority > 0:
            score += 50

        # Status moves evaluation
        if move.category.name == "STATUS":
            if opponent_pokemon and opponent_pokemon.current_hp_fraction > 0.7:
                score += 30  # Status moves better against healthy opponents

        return score

    def evaluate_switch(self, switch_pokemon, opponent_pokemon, battle):
        """Evaluate switching to a Pokemon"""
        score = 0

        # Health consideration
        score += switch_pokemon.current_hp_fraction * 100

        # Type advantage
        if opponent_pokemon:
            # Check if our Pokemon resists opponent's likely moves
            for move_name in opponent_pokemon.moves:
                move = Move(move_name)
                if move.type:
                    resistance = move.type.damage_multiplier(
                        switch_pokemon.type_1,
                        switch_pokemon.type_2,
                        type_chart=battle.battle_format.type_chart,
                    )
                    if resistance < 1:
                        score += 50  # Bonus for resisting moves

        return score


# Usage
smart_bot = SmartHeuristicPlayer()
