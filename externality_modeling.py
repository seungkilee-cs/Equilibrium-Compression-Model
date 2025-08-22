class InterventionModel:
    def simulate_rule_change_impact(self, system_state, intervention_type):
        """Model how external changes reset variance compression"""
        
        if intervention_type == "threshold_shift":
            # Change what constitutes "viable" strategy
            system_state['viability_threshold'] *= 0.8
            system_state['strategy_viabilities'] = self.recalculate_viabilities(system_state)
            
        elif intervention_type == "new_mechanic":
            # Add complexity that advantages different strategies
            system_state['role_requirements'] = self.add_new_roles(system_state)
            
        elif intervention_type == "environmental_change":
            # Shift the basis of competition entirely
            system_state['payoff_matrix'] = self.modify_payoff_structure(system_state)
            
        return system_state
    
    def optimize_intervention_timing(self, boringness_trajectory):
        """Find optimal times to intervene to maintain diversity"""
        intervention_points = []
        for i in range(len(boringness_trajectory)):
            if boringness_trajectory[i] > 0.6:  # Before critical threshold
                intervention_points.append(i)
        return intervention_points
