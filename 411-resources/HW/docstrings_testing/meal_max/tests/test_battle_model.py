import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_combatant1():
    """Fixture to provide a sample Meal combatant."""
    return Meal(id=1, meal="Spaghetti", price=15.0, cuisine="Italian", difficulty="MED")

@pytest.fixture
def sample_combatant2():
    """Fixture to provide another sample Meal combatant."""
    return Meal(id=2, meal="Sushi", price=20.0, cuisine="Japanese", difficulty="HIGH")

@pytest.fixture
def extra_combatant():
    """Fixture to provide an extra Meal combatant for more testing."""
    return Meal(id=3, meal="Tacos", price=10.0, cuisine="Mexican", difficulty="LOW")

@pytest.fixture
def mock_get_random(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.get_random")

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant(battle_model : BattleModel, sample_combatant1 : Meal):
    """Test preparing a combatant by adding it to the combatants list."""
    battle_model.prep_combatant(sample_combatant1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == sample_combatant1.meal

def test_prep_combatant_list_full(battle_model : BattleModel, sample_combatant1 : Meal, sample_combatant2 : Meal, extra_combatant : Meal):
    """Test error raised when attempting to add more than two combatants."""
    battle_model.prep_combatant(sample_combatant1)
    battle_model.prep_combatant(sample_combatant2)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(extra_combatant) 

def test_clear_combatants(battle_model : BattleModel, sample_combatant1 : Meal, sample_combatant2 : Meal):
    """Test clearing the combatants list."""
    battle_model.prep_combatant(sample_combatant1)
    battle_model.prep_combatant(sample_combatant2)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Expected combatants list to be empty after clearing"

def test_clear_combatants_no_combatants(battle_model : BattleModel):
    """Test clearing the combatants list when there are no combatants."""
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, "Expected combatants list to be empty after clearing"

##################################################
# Battle Logic Test Cases
##################################################

def test_battle_win_first_combatant(mock_update_meal_stats, mock_get_random, battle_model : BattleModel, sample_combatant1 : Meal, sample_combatant2: Meal):
    """Test the battle outcome when the first combatant wins."""
    mock_get_random.return_value = 0.1  # Set a low random value to make first combatant wins
    battle_model.prep_combatant(sample_combatant1)
    battle_model.prep_combatant(sample_combatant2)
    
    winner = battle_model.battle()
    
    assert winner == sample_combatant1.meal, "Expected Spaghetti to win the battle"
    assert len(battle_model.combatants) == 1, "Expected one combatant after battle"
    assert battle_model.combatants[0].meal == sample_combatant1.meal, "Expected first combatant to remain"
    mock_update_meal_stats.assert_any_call(sample_combatant1.id, "win")
    mock_update_meal_stats.assert_any_call(sample_combatant2.id, "loss")

def test_battle_win_second_combatant(mock_update_meal_stats, mock_get_random, battle_model: BattleModel, sample_combatant1: Meal, sample_combatant2: Meal):
    """Test the battle outcome when the second combatant wins."""
    mock_get_random.return_value = 0.9  # Set a high random value to make sure second combatant wins
    battle_model.prep_combatant(sample_combatant1)
    battle_model.prep_combatant(sample_combatant2)
    
    winner = battle_model.battle()
    
    assert winner == sample_combatant2.meal, "Expected Sushi to win the battle"
    assert len(battle_model.combatants) == 1, "Expected one combatant after battle"
    assert battle_model.combatants[0].meal == sample_combatant2.meal, "Expected Sushi to remain"
    mock_update_meal_stats.assert_any_call(sample_combatant1.id, "loss")
    mock_update_meal_stats.assert_any_call(sample_combatant2.id, "win")

def test_battle_not_enough_combatants(battle_model : BattleModel, sample_combatant1 : Meal):
    """Test starting a battle with fewer than two combatants raises an error."""
    battle_model.prep_combatant(sample_combatant1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle"):
        battle_model.battle()

##################################################
# Score Calculation Test Cases
##################################################

def test_get_battle_score(battle_model : BattleModel, sample_combatant1 : Meal):
    """Test calculating the battle score for a combatant."""
    score = battle_model.get_battle_score(sample_combatant1)
    expected_score = (sample_combatant1.price * len(sample_combatant1.cuisine)) - 2  # MED difficulty
    assert score == expected_score, f"Expected score to be {expected_score}, but got {score}"

##################################################
# Combatant Retrieval Test Cases
##################################################

def test_get_combatants(battle_model : BattleModel, sample_combatant1 : Meal, sample_combatant2 : Meal):
    """Test retrieving the current list of combatants."""
    battle_model.prep_combatant(sample_combatant1)
    battle_model.prep_combatant(sample_combatant2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Spaghetti"
    assert combatants[1].meal == "Sushi"