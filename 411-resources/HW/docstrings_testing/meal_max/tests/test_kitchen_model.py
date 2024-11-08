import pytest
import sqlite3

from meal_max.models.kitchen_model import (Meal, create_meal, clear_meals, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats)
from sqlite3 import IntegrityError

@pytest.fixture
def mock_create_meal(mocker):
    """Mock the database interaction within create_meal."""
    return mocker.patch("meal_max.models.kitchen_model.create_meal")

@pytest.fixture
def mock_clear_meals(mocker):
    """Mock the database interaction within clear_meals."""
    return mocker.patch("meal_max.models.kitchen_model.clear_meals")

@pytest.fixture
def mock_delete_meal(mocker):
    """Mock the database interaction within delete_meal."""
    return mocker.patch("meal_max.models.kitchen_model.delete_meal")

@pytest.fixture
def mock_get_leaderboard(mocker):
    """Mock the database interaction within get_leaderboard."""
    return mocker.patch("meal_max.models.kitchen_model.get_leaderboard")

@pytest.fixture
def mock_get_meal_by_id(mocker):
    """Mock the database interaction within get_meal_by_id."""
    return mocker.patch("meal_max.models.kitchen_model.get_meal_by_id")

@pytest.fixture
def mock_get_meal_by_name(mocker):
    """Mock the database interaction within get_meal_by_name."""
    return mocker.patch("meal_max.models.kitchen_model.get_meal_by_name")

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the database interaction within update_meal_stats."""
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")



def test_clear_meals(mock_clear_meals, mock_get_meal_by_name):
    """
    Test that clear_meals deletes all entries in the meals table.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    create_meal("Pizza", "Italian", 8.99, "LOW")

    assert mock_get_meal_by_name("Spaghetti") is not None
    assert mock_get_meal_by_name("Pizza") is not None

    clear_meals()
    mock_clear_meals.assert_called_once()

    with pytest.raises(ValueError, match="not found"):
        get_meal_by_name("Spaghetti")
    with pytest.raises(ValueError, match="not found"):
        get_meal_by_name("Pizza")


def test_delete_meal(mock_delete_meal, mock_get_meal_by_name, mock_get_meal_by_id):
    """
    Test that delete_meal soft deletes a meal by marking it as deleted,
    and raises errors for non-existent or already-deleted meals.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    meal = mock_get_meal_by_name("Spaghetti")

    delete_meal(meal.id)
    mock_delete_meal.assert_called_once_with(meal.id)
    with pytest.raises(ValueError, match="has been deleted"):
        mock_get_meal_by_id(meal.id)

    with pytest.raises(ValueError, match="not found"):
        delete_meal(999)

    with pytest.raises(ValueError, match="has been deleted"):
        delete_meal(meal.id)


def test_get_leaderboard(mock_get_leaderboard, mock_update_meal_stats, mock_get_meal_by_name):
    """
    Test that get_leaderboard retrieves meals sorted by the specified field
    and handles invalid sort parameters.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    create_meal("Pizza", "Italian", 8.99, "LOW")
    create_meal("Sushi", "Japanese", 12.99, "HIGH")
    
    meal1 = mock_get_meal_by_name("Spaghetti")
    meal2 = mock_get_meal_by_name("Pizza")
    meal3 = mock_get_meal_by_name("Sushi")
    
    update_meal_stats(meal1.id, "win")
    update_meal_stats(meal2.id, "loss")
    update_meal_stats(meal3.id, "win")
    update_meal_stats(meal3.id, "win") 
    
    leaderboard = get_leaderboard()
    assert mock_get_leaderboard()[0]["meal"] == "Sushi"


def test_get_meal_by_id(mock_get_meal_by_id, mock_delete_meal):
    """
    Test that get_meal_by_id retrieves a meal by its ID and handles cases where
    the meal is not found or is marked as deleted.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    meal = mock_get_meal_by_id(1)
    
    retrieved_meal = get_meal_by_id(meal.id)
    assert retrieved_meal == meal

    delete_meal(meal.id)
    with pytest.raises(ValueError, match="has been deleted"):
        get_meal_by_id(meal.id)


def test_get_meal_by_name(mock_get_meal_by_name, mock_delete_meal):
    """
    Test that get_meal_by_name retrieves a meal by its name and handles cases where
    the meal does not exist or is marked as deleted.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    
    meal = mock_get_meal_by_name("Spaghetti")
    assert meal.meal == "Spaghetti"
    assert meal.cuisine == "Italian"
    assert meal.price == 10.99
    assert meal.difficulty == "MED"
    
    delete_meal(meal.id)
    with pytest.raises(ValueError, match="has been deleted"):
        get_meal_by_name("Spaghetti")


def test_update_meal_stats(mock_update_meal_stats, mock_get_meal_by_id):
    """
    Test that update_meal_stats correctly updates battles and wins for a meal,
    and raises errors for invalid inputs.
    """
    create_meal("Spaghetti", "Italian", 10.99, "MED")
    meal = mock_get_meal_by_id(1)

    update_meal_stats(meal.id, "win")
    mock_update_meal_stats.assert_called_once_with(meal.id, "win")

    with pytest.raises(ValueError, match="Invalid result"):
        update_meal_stats(meal.id, "draw")