import pytest
import sqlite3

from meal_max.models.kitchen_model import (Meal, create_meal, clear_meals, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats)
from sqlite3 import IntegrityError

@pytest.fixture()
def setup_database():
    """Fixture to clear the meals table before each test."""
    clear_meals()

@pytest.fixture
def sample_meal_data():
    """Fixture for sample meal data."""
    return {"meal": "Spaghetti", "cuisine": "Italian", "price": 10.99, "difficulty": "MED"}

@pytest.fixture
def sample_meal_in_db(sample_meal_data):
    create_meal(**sample_meal_data)
    return get_meal_by_name(sample_meal_data["meal"])



def test_create_meal():
    """
    Test that create_meal adds a new meal to the database with valid arguments,
    and raises errors for invalid inputs and duplicate entries.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    meal = get_meal_by_name("Spaghetti")
    assert meal.meal == "Spaghetti"
    assert meal.cuisine == "Italian"
    assert meal.price == 10.99
    assert meal.difficulty == "MED"

    with pytest.raises(ValueError, match="Price must be a positive value"):
        create_meal("InvalidMeal", "French", -5.99, "MED")

    with pytest.raises(ValueError, match="Difficulty must be 'LOW', 'MED', or 'HIGH'"):
        create_meal("DifficultMeal", "Asian", 12.99, "EXTREME")

    with pytest.raises(ValueError, match="Meal with name 'Spaghetti' already exists"):
        create_meal("Spaghetti", "Italian", 10.99, "MED")


def test_clear_meals():
    """
    Test that clear_meals deletes all entries in the meals table.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    create_meal("Pizza", "Italian", 8.99, "LOW")

    assert get_meal_by_name("Spaghetti") is not None
    assert get_meal_by_name("Pizza") is not None

    clear_meals()

    with pytest.raises(ValueError, match="not found"):
        get_meal_by_name("Spaghetti")
    with pytest.raises(ValueError, match="not found"):
        get_meal_by_name("Pizza")


def test_delete_meal():
    """
    Test that delete_meal soft deletes a meal by marking it as deleted,
    and raises errors for non-existent or already-deleted meals.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    meal = get_meal_by_name("Spaghetti")

    delete_meal(meal.id)
    with pytest.raises(ValueError, match="has been deleted"):
        get_meal_by_id(meal.id)

    with pytest.raises(ValueError, match="not found"):
        delete_meal(999)

    with pytest.raises(ValueError, match="has been deleted"):
        delete_meal(meal.id)


def test_get_leaderboard():
    """
    Test that get_leaderboard retrieves meals sorted by the specified field
    and handles invalid sort parameters.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    create_meal("Pizza", "Italian", 8.99, "LOW")
    create_meal("Sushi", "Japanese", 12.99, "HIGH")
    
    meal1 = get_meal_by_name("Spaghetti")
    meal2 = get_meal_by_name("Pizza")
    meal3 = get_meal_by_name("Sushi")
    
    update_meal_stats(meal1.id, "win")
    update_meal_stats(meal2.id, "loss")
    update_meal_stats(meal3.id, "win")
    update_meal_stats(meal3.id, "win") 
    
    leaderboard = get_leaderboard()
    assert leaderboard[0]["meal"] == "Sushi"
    assert leaderboard[1]["meal"] == "Spaghetti"
    
    leaderboard = get_leaderboard(sort_by="win_pct")
    assert leaderboard[0]["meal"] == "Sushi" 
    
    leaderboard = get_leaderboard(sort_by="battles")
    assert leaderboard[0]["meal"] == "Sushi"
    
    with pytest.raises(ValueError, match="Invalid sort_by parameter"):
        get_leaderboard(sort_by="invalid")


def test_get_meal_by_id():
    """
    Test that get_meal_by_id retrieves a meal by its ID and handles cases where
    the meal is not found or is marked as deleted.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    meal = get_meal_by_name("Spaghetti")
    
    retrieved_meal = get_meal_by_id(meal.id)
    assert retrieved_meal.meal == "Spaghetti"
    assert retrieved_meal.cuisine == "Italian"
    assert retrieved_meal.price == 10.99
    assert retrieved_meal.difficulty == "MED"
    
    delete_meal(meal.id)
    with pytest.raises(ValueError, match="has been deleted"):
        get_meal_by_id(meal.id)
    
    with pytest.raises(ValueError, match="not found"):
        get_meal_by_id(9999)


def test_get_meal_by_name():
    """
    Test that get_meal_by_name retrieves a meal by its name and handles cases where
    the meal does not exist or is marked as deleted.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    
    meal = get_meal_by_name("Spaghetti")
    assert meal.meal == "Spaghetti"
    assert meal.cuisine == "Italian"
    assert meal.price == 10.99
    assert meal.difficulty == "MED"
    
    delete_meal(meal.id)
    with pytest.raises(ValueError, match="has been deleted"):
        get_meal_by_name("Spaghetti")
    
    with pytest.raises(ValueError, match="not found"):
        get_meal_by_name("NonExistentMeal")


def test_update_meal_stats():
    """
    Test that update_meal_stats correctly updates battles and wins for a meal,
    and raises errors for invalid inputs.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    meal = get_meal_by_name("Spaghetti")

    update_meal_stats(meal.id, "win")
    updated_meal = get_meal_by_id(meal.id)
    assert updated_meal.wins == 1, "Expected 1 win after a win update"
    assert updated_meal.battles == 1, "Expected 1 battle after a win update"

    update_meal_stats(meal.id, "loss")
    updated_meal = get_meal_by_id(meal.id)
    assert updated_meal.wins == 1, "Expected wins to remain the same after a loss update"
    assert updated_meal.battles == 2, "Expected battles to increase to 2 after a loss update"

    with pytest.raises(ValueError, match="Invalid result"):
        update_meal_stats(meal.id, "draw")

    with pytest.raises(ValueError, match="not found"):
        update_meal_stats(9999, "win")

