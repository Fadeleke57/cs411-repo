import logging
from typing import List

from meal_max.models.kitchen_model import Meal, update_meal_stats
from meal_max.utils.logger import configure_logger
from meal_max.utils.random_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class BattleModel:

    def __init__(self):
        """
        Initializes the BattleModel object.

        Sets the combatants list to an empty list.
        """
        self.combatants: List[Meal] = []

    def battle(self) -> str:
        """
        Initiates a battle between two combatants and returns the name of the winner.

        The battle is determined by the delta between the two combatants' scores.
        A random number is generated from random.org and the normalized delta is
        compared to the random number. If the normalized delta is greater than the
        random number, the first combatant is declared the winner. Otherwise, the
        second combatant is declared the winner.

        The winner's stats are updated with a win and the loser's stats are updated
        with a loss. The loser is then removed from the combatants list.

        Returns:
            str: The name of the winner.
        Raises:
            ValueError: Two combatants must be prepped for a battle.
        """
        logger.info("Two meals enter, one meal leaves!")

        if len(self.combatants) < 2:
            logger.error("Not enough combatants to start a battle.")
            raise ValueError("Two combatants must be prepped for a battle.")

        combatant_1 = self.combatants[0]
        combatant_2 = self.combatants[1]

        # Log the start of the battle
        logger.info("Battle started between %s and %s", combatant_1.meal, combatant_2.meal)

        # Get battle scores for both combatants
        score_1 = self.get_battle_score(combatant_1)
        score_2 = self.get_battle_score(combatant_2)

        # Log the scores for both combatants
        logger.info("Score for %s: %.3f", combatant_1.meal, score_1)
        logger.info("Score for %s: %.3f", combatant_2.meal, score_2)

        # Compute the delta and normalize between 0 and 1
        delta = abs(score_1 - score_2) / 100

        # Log the delta and normalized delta
        logger.info("Delta between scores: %.3f", delta)

        # Get random number from random.org
        random_number = get_random()

        # Log the random number
        logger.info("Random number from random.org: %.3f", random_number)

        # Determine the winner based on the normalized delta
        if delta > random_number:
            winner = combatant_1
            loser = combatant_2
        else:
            winner = combatant_2
            loser = combatant_1

        # Log the winner
        logger.info("The winner is: %s", winner.meal)

        # Update stats for both combatants
        update_meal_stats(winner.id, 'win')
        update_meal_stats(loser.id, 'loss')

        # Remove the losing combatant from combatants
        self.combatants.remove(loser)

        return winner.meal

    def clear_combatants(self):
        """
        Clear the list of combatants for the battle.

        Returns:
            None
        """
        logger.info("Clearing the combatants list.")
        self.combatants.clear()

    def get_battle_score(self, combatant: Meal) -> float:
        """
        Calculate the battle score for a given combatant.

        The score is computed based on the price of the meal, the length of the cuisine
        string, and a difficulty modifier. The difficulty modifier is subtracted from
        the product of the price and cuisine length, where the modifier is determined
        by the difficulty level of the meal.

        Args:
            combatant (Meal): The combatant whose battle score is to be calculated.

        Returns:
            float: The calculated battle score for the combatant.
        """
        difficulty_modifier = {"HIGH": 1, "MED": 2, "LOW": 3}

        # Log the calculation process
        logger.info("Calculating battle score for %s: price=%.3f, cuisine=%s, difficulty=%s",
                    combatant.meal, combatant.price, combatant.cuisine, combatant.difficulty)

        # Calculate score
        score = (combatant.price * len(combatant.cuisine)) - difficulty_modifier[combatant.difficulty]

        # Log the calculated score
        logger.info("Battle score for %s: %.3f", combatant.meal, score)

        return score

    def get_combatants(self) -> List[Meal]:
        """
        Retrieves the current list of combatants.

        Returns:
            List[Meal]: A list of Meal objects representing the combatants.
        """
        logger.info("Retrieving current list of combatants.")
        return self.combatants

    def prep_combatant(self, combatant_data: Meal):
        """
        Prepares a combatant by adding it to the combatants list.

        Args:
            combatant_data (Meal): The Meal object to be added as a combatant.

        Raises:
            ValueError: If the combatants list is already full (at least 2 combatants).
        """
        if len(self.combatants) >= 2:
            logger.error("Attempted to add combatant '%s' but combatants list is full", combatant_data.meal)
            raise ValueError("Combatant list is full, cannot add more combatants.")

        # Log the addition of the combatant
        logger.info("Adding combatant '%s' to combatants list", combatant_data.meal)

        self.combatants.append(combatant_data)

        # Log the current state of combatants
        logger.info("Current combatants list: %s", [combatant.meal for combatant in self.combatants])
