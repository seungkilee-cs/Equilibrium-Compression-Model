import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

class SystemicEntropyModel:
    def __init__(self):
        self.entropy_model = None
        self.compression_model = None
        
    def calculate_strategic_entropy(self, strategy_distribution):
        """Calculate H(p*) = -Σ p_i * log(p_i)"""
        p = np.array(strategy_distribution)
        p = p[p > 0]  # Remove zero probabilities
        return -np.sum(p * np.log(p))
    
    def calculate_viability_compression_index(self, viabilities_before, viabilities_after):
        """VCI = Var[before] / Var[after]"""
        var_before = np.var(viabilities_before)
        var_after = np.var(viabilities_after)
        return var_before / var_after if var_after > 0 else np.inf
    
    def calculate_boringness_metric(self, H_entropy, VCI, counterplay_index, 
                                  alpha=0.4, beta=0.4, gamma=0.2):
        """B = α·(1/H) + β·VCI + γ·(1/C)"""
        return alpha * (1/H_entropy) + beta * VCI + gamma * (1/counterplay_index)
