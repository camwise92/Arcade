"""
Scoreboard Manager

File: scoreboard_manager.py
Description: create/update/display scoreboards
Author: Cameron Carlisle
Date created: 12/02/2025
Last modified: 25/02/2025
Version: 1.1

This script allows you to create and update scoreboards for multiple games. Each game's scoreboard is stored in a CSV file (with headers - "Player" and "Score"),
and only the top 10 scores are kept. The script ensures that the scoreboard is always up-to-date and sorted in descending order.
The filename for each scoreboard is dynamically generated taking into account the game name set by game's programmer.

Usage:
1. Call 'create_scoreboard(game_name)' to initialize a scoreboard for a new game.
2. Call 'update_scoreboard(game_name, player_name, score)' to add a new score to the scoreboard.
3. Call 'display_scoreboard(game_name)' to view the current top 10 scores.

Contact: cameroncarlisle1992@gmail.com
"""
import os
import csv

SCOREBOARD_DIR = os.path.join(os.path.dirname(__file__), 'scoreboards')

# Ensure the scoreboards directory exists
if not os.path.exists(SCOREBOARD_DIR):
    os.makedirs(SCOREBOARD_DIR)

def create_scoreboard(game_name):
    scoreboard_file = os.path.join(SCOREBOARD_DIR, f"{game_name}_scoreboard.csv")
    if not os.path.exists(scoreboard_file):
        with open(scoreboard_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Player", "Score"])

def update_scoreboard(game_name, player_name, score):
    scoreboard_file = os.path.join(SCOREBOARD_DIR, f"{game_name}_scoreboard.csv")
    with open(scoreboard_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([player_name, score])

def display_scoreboard(game_name):
    scoreboard_file = os.path.join(SCOREBOARD_DIR, f"{game_name}_scoreboard.csv")
    if not os.path.exists(scoreboard_file):
        return []

    with open(scoreboard_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        return [(row[0], int(row[1])) for row in reader]