import math

def calculate_expected_result(rating_a, rating_b):
    """Calculate expected outcome based on Elo ratings"""
    return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / 400))

def update_elo(rating, expected, actual, k_factor=20):
    """Update Elo rating based on game result"""
    return rating + k_factor * (actual - expected)

def calculate_new_ratings(team_a_rating, team_b_rating, team_a_score, team_b_score, k_factor=32):
    """Calculate new Elo ratings after a game"""
    # Determine actual result (1 for win, 0.5 for tie, 0 for loss)
    if team_a_score > team_b_score:
        actual_a = 1.0
    elif team_a_score == team_b_score:
        actual_a = 0.5
    else:
        actual_a = 0.0
    
    actual_b = 1.0 - actual_a
    
    # Calculate expected results
    expected_a = calculate_expected_result(team_a_rating, team_b_rating)
    expected_b = calculate_expected_result(team_b_rating, team_a_rating)
    
    # Update ratings
    new_rating_a = update_elo(team_a_rating, expected_a, actual_a, k_factor)
    new_rating_b = update_elo(team_b_rating, expected_b, actual_b, k_factor)
    
    return new_rating_a, new_rating_b