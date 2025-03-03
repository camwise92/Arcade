"""
GLCL Arcade Menu

File: menu.py
Description: Main menu for the GLCL Arcade application
Author: Cameron Carlisle + [Add any names of contributors who edit]
Date created: 26/02/2025
Last modified: 03/03/2025
Version: 1.1

This script provides the main menu for the GLCL Arcade application. It allows users to enter their name, select a game to play, view the leaderboard, and exit the application. The menu dynamically loads available games from the 'games' folder and passes the player's name to the selected game.

Usage:
1. Run the script to start the GLCL Arcade application.
2. Enter your name and proceed to the main menu.
3. Select a game to play or view the leaderboard.
4. Exit the application when done.

Open to any edits or suggestions to improve the application.

Contact: cameroncarlisle1992@gmail.com
"""

import csv
import os
import sys
import importlib
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QStackedWidget, QMessageBox, QListWidget, QHBoxLayout, QTableWidget,
    QTableWidgetItem
)
import scoreboard_manager as scoreboard  # Import the scoreboard module
from games_config import GAMES_CONFIG  # Import the games configuration

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class WelcomeScreen(QWidget):
    """First screen that asks for the player's name."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        # Create and configure the welcome label
        self.label = QLabel("Welcome to GLCL Arcade!")
        self.label.setFont(QFont("Arial", 24))  # Increase font size
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align
        
        # Create and configure the name input field
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name...")
        self.name_input.setFont(QFont("Arial", 14))

        # Create and configure the continue button
        self.continue_button = QPushButton("Continue")
        self.continue_button.setFont(QFont("Arial", 14))
        self.continue_button.clicked.connect(self.save_name)

        # Add widgets to the layout
        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.continue_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center everything
        self.setLayout(layout)

    def save_name(self):
        """Save the player's name and proceed to the main menu."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter your name!")
            return
        self.main_window.player_name = name
        self.main_window.show_main_menu()

class MainMenu(QWidget):
    """Main menu where players select a game or view the scoreboard."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.games = self.get_available_games()  # Dynamically get games

        layout = QVBoxLayout()
        
        # Create and configure the greeting label
        self.greeting_label = QLabel()
        self.greeting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.greeting_label)

        # Create and configure the games list
        self.games_list = QListWidget()
        for game in self.games:
            formatted_name = self.format_game_name(game)
            self.games_list.addItem(formatted_name)
        layout.addWidget(self.games_list)

        # Create and configure the play and scoreboard buttons
        btn_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_game)
        self.scoreboard_button = QPushButton("View Scoreboard")
        self.scoreboard_button.clicked.connect(self.view_scoreboard)

        btn_layout.addWidget(self.play_button)
        btn_layout.addWidget(self.scoreboard_button)
        layout.addLayout(btn_layout)

        # Create and configure the exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.main_window.close)
        layout.addWidget(self.exit_button)

        self.setLayout(layout)

    def update_greeting(self):
        """Update the greeting label with the player's name."""
        self.greeting_label.setText(f"Hello, {self.main_window.player_name}!")

    def get_available_games(self):
        """Scan the 'games/' folder in 'Arcade/' and return a list of game names."""
        games_path = os.path.join(os.path.dirname(__file__), "games")
        if not os.path.exists(games_path):
            return []  # No games folder found

        excluded_files = ["__init__.py", "questions.py"]  # Exclude specific files
        return [
            filename[:-3]  # Remove '.py' extension
            for filename in os.listdir(games_path)
            if filename.endswith(".py") and filename not in excluded_files
        ]

    def format_game_name(self, game_name):
        """Format the game name by replacing underscores with spaces and capitalizing it."""
        return game_name.replace('_', ' ').title()

    def play_game(self):
        """Dynamically load and start a selected game."""
        selected_game = self.games_list.currentItem()
        if selected_game:
            game_name = selected_game.text().replace(' ', '_').lower()  # Convert back to the original game name format
            self.main_window.play_game(game_name)

    def view_scoreboard(self):
        """Show the scoreboard for the selected game."""
        selected_game = self.games_list.currentItem()
        if selected_game:
            game_name = selected_game.text().replace(' ', '_').lower()  # Convert back to the original game name format
            self.main_window.show_scoreboard(game_name)

class ScoreboardScreen(QWidget):
    """Displays the scoreboard for a specific game."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        # Create and configure the scoreboard table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Player", "Score"])
        layout.addWidget(self.table)

        # Create and configure the back button
        self.back_button = QPushButton("Back to Menu")
        self.back_button.clicked.connect(self.main_window.show_main_menu)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def update_scores(self, game_name):
        """Update the scoreboard with the latest scores for the selected game."""
        scores = scoreboard.display_scoreboard(game_name)
        # Sort scores in descending order and take the top 10
        top_scores = sorted(scores, key=lambda x: x[1], reverse=True)[:10]
        self.table.setRowCount(len(top_scores))

        for row, (player, score) in enumerate(top_scores):
            self.table.setItem(row, 0, QTableWidgetItem(player))
            self.table.setItem(row, 1, QTableWidgetItem(str(score)))

class GameMenuApp(QWidget):
    """Manages different screens and navigation."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Hub")
        self.setGeometry(100, 100, 1200, 800)

        self.player_name = None
        self.stack = QStackedWidget(self)

        # Initialize the different screens
        self.welcome_screen = WelcomeScreen(self)
        self.main_menu = MainMenu(self)
        self.scoreboard_screen = ScoreboardScreen(self)

        # Add screens to the stack
        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.scoreboard_screen)

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.create_scoreboards()  # Create scoreboards for all games
        self.show_welcome_screen()

    def create_scoreboards(self):
        """Create scoreboards for all games."""
        games = self.main_menu.get_available_games()
        for game in games:
            if game == "questions":  # Skip the questions game
                continue
            scoreboard.create_scoreboard(game)

    def show_welcome_screen(self):
        """Show the welcome screen."""
        self.stack.setCurrentWidget(self.welcome_screen)

    def show_main_menu(self):
        """Show the main menu."""
        self.main_menu.update_greeting()
        self.stack.setCurrentWidget(self.main_menu)

    def show_scoreboard(self, game_name):
        """Show the scoreboard for the selected game."""
        self.scoreboard_screen.update_scores(game_name)
        self.stack.setCurrentWidget(self.scoreboard_screen)

    def play_game(self, game_name):
        """Start the selected game."""
        QMessageBox.information(self, "Playing Game", f"Starting {game_name}...")

        try:
            game_path = os.path.join(os.path.dirname(__file__), "games", f"{game_name}.py")
            new_terminal = GAMES_CONFIG.get(game_name, {}).get("new_terminal", False)
            subprocess.Popen([sys.executable, game_path, self.player_name], creationflags=subprocess.CREATE_NEW_CONSOLE if new_terminal else 0)
            
            self.show_scoreboard(game_name)  # Show the updated scoreboard
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to start the game {game_name}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameMenuApp()
    window.show()
    sys.exit(app.exec())