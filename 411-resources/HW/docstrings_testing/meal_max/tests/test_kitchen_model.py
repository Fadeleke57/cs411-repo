import pytest
from contextlib import contextmanager
from unittest.mock import Mock


@pytest.fixture
def sample_meal1():
    """Fixture providing a sample meal."""
    return {"id": 1, "meal": "Spaghetti", "cuisine": "Italian", "price": 10.99, "difficulty": "MED"}

@pytest.fixture
def sample_meal2():
    """Fixture providing another sample meal."""
    return {"id": 2, "meal": "Pizza", "cuisine": "Italian", "price": 8.99, "difficulty": "LOW"}

@pytest.fixture
def sample_leaderboard():
    """Fixture providing a sample leaderboard."""
    return [
        {"meal": "Sushi", "wins": 10},
        {"meal": "Spaghetti", "wins": 8},
    ]


def test_clear_meals(mocker, sample_meal1, sample_meal2):
    """Test that clear_meals deletes all entries in the meals table."""
    mock_get_meal_by_name = mocker.patch("meal_max.models.kitchen_model.get_meal_by_name")
    mock_get_meal_by_name.side_effect = [sample_meal1, sample_meal2, ValueError("not found"), ValueError("not found")]

    mock_clear_meals = mocker.patch("meal_max.models.kitchen_model.clear_meals")

    mock_clear_meals()
    mock_clear_meals.assert_called_once()

    assert mock_get_meal_by_name("Spaghetti") == sample_meal1
    assert mock_get_meal_by_name("Pizza") == sample_meal2

def test_delete_meal(mocker, sample_meal1):
    """Test that delete_meal soft deletes a meal by marking it as deleted."""
    mock_get_meal_by_name = mocker.patch("meal_max.models.kitchen_model.get_meal_by_name", return_value=sample_meal1)
    mock_get_meal_by_id = mocker.patch("meal_max.models.kitchen_model.get_meal_by_id", side_effect=ValueError("has been deleted"))
    mock_delete_meal = mocker.patch("meal_max.models.kitchen_model.delete_meal")

    # Delete the meal and assert behavior
    mock_delete_meal(sample_meal1["id"])
    mock_delete_meal.assert_called_once_with(sample_meal1["id"])

    with pytest.raises(ValueError, match="has been deleted"):
        mock_get_meal_by_id(sample_meal1["id"])


def test_get_leaderboard(mocker, sample_leaderboard):
    """Test that get_leaderboard retrieves meals sorted by the specified field."""
    mock_get_leaderboard = mocker.patch("meal_max.models.kitchen_model.get_leaderboard", return_value=sample_leaderboard)

    leaderboard = mock_get_leaderboard()
    assert leaderboard[0]["meal"] == "Sushi"
    assert leaderboard[1]["meal"] == "Spaghetti"


def test_get_meal_by_id(mocker, sample_meal1):
    """Test that get_meal_by_id retrieves a meal by its ID."""
    mock_get_meal_by_id = mocker.patch("meal_max.models.kitchen_model.get_meal_by_id", return_value=sample_meal1)

    retrieved_meal = mock_get_meal_by_id(1)
    assert retrieved_meal == sample_meal1


def test_get_meal_by_name(mocker, sample_meal1):
    """Test that get_meal_by_name retrieves a meal by its name."""
    mock_get_meal_by_name = mocker.patch("meal_max.models.kitchen_model.get_meal_by_name", return_value=sample_meal1)

    meal = mock_get_meal_by_name("Spaghetti")
    assert meal["meal"] == "Spaghetti"
    assert meal["cuisine"] == "Italian"
    assert meal["price"] == 10.99
    assert meal["difficulty"] == "MED"


def test_update_meal_stats(mocker, sample_meal1):
    """Test that update_meal_stats correctly updates battles and wins for a meal."""
    mock_update_meal_stats = mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

    mock_update_meal_stats(sample_meal1["id"], "win")
    mock_update_meal_stats.assert_any_call(sample_meal1["id"], "win")

    mock_update_meal_stats.side_effect = ValueError("Invalid result")

    with pytest.raises(ValueError, match="Invalid result"):
        mock_update_meal_stats(sample_meal1["id"], "draw")
