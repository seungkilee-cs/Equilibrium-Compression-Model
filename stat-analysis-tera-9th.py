import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, chi2_contingency
from sklearn.preprocessing import StandardScaler
from dython.nominal import associations
import plotly.express as px

required_fields = [
    # Base Statistics
    'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'bst',
    # Type Information  
    'type1', 'type2', 'has_4x_weakness',
    # Terastallization Data
    'primary_tera_type', 'tera_usage_rate', 'stab_tera_percentage',
    # Competitive Metrics
    'usage_rate', 'win_rate', 'tier',
    # Derived Features
    'is_offensive' (attack + sp_attack > 140),
    'is_fast' (speed > 100),
    'is_bulky' (hp + defense + sp_defense > 200)
]

# Load and merge datasets
def load_pokemon_data():
    # Base stats from Kaggle
    base_df = pd.read_csv('pokemon_base_stats.csv')
    
    # Competitive usage from Pikalytics/Smogon
    usage_df = pd.read_csv('competitive_usage.csv') 
    
    # Tera type data (you'll need to scrape/compile this)
    tera_df = pd.read_csv('tera_usage_data.csv')
    
    # Merge datasets
    pokemon_df = base_df.merge(usage_df, on='name', how='left')
    pokemon_df = pokemon_df.merge(tera_df, on='name', how='left')
    
    return pokemon_df

# Create derived features
def engineer_features(df):
    df['bst'] = df[['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']].sum(axis=1)
    df['has_4x_weakness'] = df.apply(check_4x_weakness, axis=1)  # Custom function
    df['offensive_stat'] = df[['attack', 'sp_attack']].max(axis=1)
    df['defensive_stat'] = df[['defense', 'sp_defense']].mean(axis=1)
    
    return df

# Handle both categorical and numerical variables
def create_comprehensive_correlation_matrix(df):
    """
    Uses dython library to handle mixed data types
    - Pearson's r for numeric-numeric
    - Cramér's V for categorical-categorical  
    - Correlation ratio for categorical-numeric
    """
    
    # Define column types
    numerical_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'bst']
    categorical_cols = ['type1', 'type2', 'primary_tera_type', 'has_4x_weakness']
    
    # Create correlation matrix
    corr_matrix = associations(df[numerical_cols + categorical_cols], 
                              nominal_columns=categorical_cols,
                              figsize=(12, 10),
                              title='Pokemon Features Correlation Matrix')
    
    return corr_matrix

# Pairplot for numeric relationships
def explore_numeric_relationships(df):
    numeric_features = ['bst', 'speed', 'offensive_stat', 'tera_usage_rate', 'stab_tera_percentage']
    
    # Pairplot with regression lines
    g = sns.pairplot(df[numeric_features + ['has_4x_weakness']], 
                     hue='has_4x_weakness',
                     diag_kind='kde')
    g.fig.suptitle('Pokemon Stats vs Tera Usage Patterns', y=1.02)
    plt.show()

# Categorical analysis
def analyze_categorical_relationships(df):
    # BST categories vs Tera type preferences  
    df['bst_category'] = pd.cut(df['bst'], bins=[0, 500, 550, 600, 800], 
                               labels=['Low', 'Mid', 'High', 'Very High'])
    
    # Cross-tabulation heatmap
    ct = pd.crosstab(df['bst_category'], df['primary_tera_type'])
    plt.figure(figsize=(12, 6))
    sns.heatmap(ct, annot=True, fmt='d', cmap='viridis')
    plt.title('BST Category vs Primary Tera Type Usage')
    plt.show()

    # Interactive correlation heatmap
def create_interactive_correlation_matrix(df):
    # Compute correlation matrix
    corr = df.select_dtypes(include=[np.number]).corr()
    
    # Interactive heatmap with Plotly
    fig = px.imshow(corr, 
                    title='Pokemon Features Correlation Matrix',
                    color_continuous_scale='RdBu_r',
                    aspect='auto')
    
    fig.update_layout(width=800, height=800)
    fig.show()

# Clustered correlation matrix  
def create_clustered_heatmap(df):
    # Compute correlation and cluster
    corr = df.select_dtypes(include=[np.number]).corr()
    
    # Hierarchical clustering
    g = sns.clustermap(corr, 
                       cmap='coolwarm',
                       center=0,
                       square=True,
                       figsize=(10, 10),
                       cbar_kws={'shrink': 0.8})
    
    g.fig.suptitle('Clustered Pokemon Features Correlation Matrix', y=0.98)
    plt.show()

    def test_bst_stab_correlation(df):
    # Filter out Pokemon with 4x weaknesses to isolate BST effect
    no_4x_df = df[df['has_4x_weakness'] == False]
    
    # Correlation between BST and STAB Tera percentage
    correlation, p_value = pearsonr(no_4x_df['bst'], no_4x_df['stab_tera_percentage'])
    
    # Visualization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=no_4x_df, x='bst', y='stab_tera_percentage', 
                    hue='tier', size='usage_rate', alpha=0.7)
    sns.regplot(data=no_4x_df, x='bst', y='stab_tera_percentage', 
                scatter=False, color='red')
    
    plt.title(f'BST vs STAB Tera Usage (r={correlation:.3f}, p={p_value:.3f})')
    plt.xlabel('Base Stat Total')
    plt.ylabel('Percentage of STAB Tera Usage')
    plt.show()
    
    return correlation, p_value

def analyze_offensive_stats_tera_preference(df):
    # Create offensive capability metric
    df['offensive_capability'] = df[['attack', 'sp_attack']].max(axis=1) + df['speed'] * 0.5
    
    # Bin into categories
    df['offensive_category'] = pd.qcut(df['offensive_capability'], 
                                      q=4, labels=['Low', 'Mid', 'High', 'Elite'])
    
    # Analyze STAB Tera usage by offensive category
    stab_by_offense = df.groupby('offensive_category')['stab_tera_percentage'].mean()
    
    # Visualization
    plt.figure(figsize=(8, 6))
    stab_by_offense.plot(kind='bar', color='skyblue')
    plt.title('STAB Tera Usage by Offensive Capability')
    plt.ylabel('Average STAB Tera Percentage')
    plt.xticks(rotation=45)
    plt.show()
    
    return stab_by_offense


