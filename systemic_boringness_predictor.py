class BoringnessPredictor:
    def __init__(self, entropy_threshold=2.1, vci_threshold=2.5, counterplay_threshold=0.4):
        self.entropy_threshold = entropy_threshold
        self.vci_threshold = vci_threshold
        self.counterplay_threshold = counterplay_threshold
        
    def predict_long_term_boringness(self, system_trajectory):
        """Predict when system becomes 'boring' (low entropy, high compression)"""
        boringness_scores = []
        
        for time_point in system_trajectory:
            H = self.calculate_strategic_entropy(time_point['strategy_distribution'])
            VCI = self.calculate_viability_compression_index(
                time_point['viabilities_before'], time_point['viabilities_after'])
            C = time_point['counterplay_index']
            
            B = 0.4 * (1/H) + 0.4 * VCI + 0.2 * (1/C)
            boringness_scores.append(B)
            
        return np.array(boringness_scores)
    
    def identify_intervention_points(self, boringness_trajectory):
        """Identify when external intervention is needed"""
        critical_points = []
        for i, score in enumerate(boringness_trajectory):
            if score > 0.7:  # Critical boringness threshold
                critical_points.append(i)
        return critical_points
