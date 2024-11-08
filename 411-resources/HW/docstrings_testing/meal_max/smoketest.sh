#!/bin/bash

BASE_URL="http://localhost:5000/api"
ECHO_JSON=false

while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

#####################################################
#
# Healthchecks
#
#####################################################

check_health() {
  echo "Checking health status..."
  response=$(curl -s -X GET "$BASE_URL/health")
  if echo "$response" | grep -q '"status": "healthy"'; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  response=$(curl -s -X GET "$BASE_URL/db-check")
  if echo "$response" | grep -q '"database_status": "healthy"'; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

#####################################################
#
# Meals Management
#
#####################################################

clear_catalog() {
  echo "Clearing all meals..."
  response=$(curl -s -X DELETE "$BASE_URL/clear-meals")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meals cleared successfully."
  else
    echo "Failed to clear meals."
    exit 1
  fi
}

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4
  echo "Creating meal ($meal, $cuisine, $price, $difficulty)..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" \
    -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal created successfully."
  else
    echo "Failed to create meal."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1
  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to retrieve meal by ID."
    exit 1
  fi
}

get_meal_by_name() {
  name=$1
  echo "Retrieving meal by name..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$name")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo $response
    echo "Failed to retrieve meal by name."
    exit 1
  fi
}

delete_meal() {
  meal_id=$1
  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully."
  else
    echo "Failed to delete meal."
    exit 1
  fi
}

#####################################################
#
# Battle Management
#
#####################################################

battle() {
  echo "Initiating battle..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle completed successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to complete battle."
    exit 1
  fi
}

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

prep_combatant() {
  meal_name=$1
  echo "Preparing combatant: $meal_name..."
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" \
    -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_name\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatant prepared successfully."
  else
    echo "Failed to prepare combatant."
    exit 1
  fi
}

get_combatants() {
  echo "Getting all combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to get combatants."
    exit 1
  fi
}

#####################################################
#
# Leaderboard
#
#####################################################

get_leaderboard() {
  echo "Getting leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    [ "$ECHO_JSON" = true ] && echo "$response" | jq .
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}

#####################################################
#
# Execute Tests
#
#####################################################

check_health
check_db
clear_catalog

create_meal "Spaghetti" "Italian" 12.50 "MED"
create_meal "Raamen" "Chinese" 10.00 "HIGH"
get_meal_by_id 1
get_meal_by_name "Raamen"

clear_combatants
prep_combatant "Spaghetti"
prep_combatant "Raamen"
get_combatants
battle
get_leaderboard
delete_meal 1
echo "All tests passed successfully."