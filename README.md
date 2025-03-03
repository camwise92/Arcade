GLCL Arcade
Welcome to the GLCL Arcade! This project is a collection of fun and interactive games built using Python and Pygame. Players can enter their names, select a game to play, view leaderboards, and enjoy a seamless gaming experience.

Table of Contents
Features
Installation
Usage
Games
Scoreboard
Contributing
License
Features
Multiple games to choose from
Player name input and personalized greetings
Dynamic game loading
Scoreboard management for each game
User-friendly interface with PyQt6
Installation
Clone the repository:

Install the required dependencies:

Ensure you have Python 3.8+ installed.

Usage
Run the main menu script to start the arcade:

Enter your name and proceed to the main menu.

Select a game to play or view the leaderboard.

Games
The following games are available in the GLCL Arcade:
Sen's Adventure Game


Scoreboard
The arcade includes a scoreboard feature to keep track of the top scores for each game. The scoreboards are stored in CSV files and can be viewed from the main menu.

Creating a Scoreboard
To initialize a scoreboard for a new game, call:
  create_scoreboard(game_name)
  
Updating the Scoreboard
To add a new score to the scoreboard, call:
  update_scoreboard(game_name, player_name, score)

Displaying the Scoreboard
To view the current top 10 scores, call:
  display_scoreboard(game_name)

Contributing
We welcome contributions to improve the GLCL Arcade. If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.
