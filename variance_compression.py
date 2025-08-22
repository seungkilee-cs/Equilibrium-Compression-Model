class VarianceCompressionModel:
    def __init__(self, right_wall_constraint, left_tail_pruning_rate):
        self.right_wall = right_wall_constraint
        self.pruning_rate = left_tail_pruning_rate
        
    def simulate_compression(self, initial_mean, initial_variance, time_steps):
        """Simulate necessary variance compression in relational system"""
        means = [initial_mean]
        variances = [initial_variance]
        
        for t in range(1, time_steps):
            # Co-evolutionary pressure increases mean (baseline rise)
            new_mean = means[-1] + self.calculate_coevolution_pressure(t)
            
            # Left tail pruning (weak strategies eliminated)
            pruned_variance = variances[-1] * (1 - self.pruning_rate)
            
            # Right wall constraint (physical/design limitations)
            max_possible_variance = self.calculate_right_wall_constraint(new_mean)
            
            # Variance compression is the minimum of these constraints
            new_variance = min(pruned_variance, max_possible_variance)
            
            means.append(new_mean)
            variances.append(max(new_variance, 0.001))  # Prevent zero variance
            
        return np.array(means), np.array(variances)
    
    def calculate_coevolution_pressure(self, time_step):
        """Model how co-evolutionary arms race increases performance baseline"""
        return 0.02 * np.log(1 + time_step * 0.1)  # Diminishing returns
    
    def calculate_right_wall_constraint(self, current_mean):
        """Physical/design limitations create variance ceiling"""
        distance_to_wall = max(0, self.right_wall - current_mean)
        return (distance_to_wall ** 2) / 4  # Parabolic constraint
