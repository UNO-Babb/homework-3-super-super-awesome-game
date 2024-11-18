from flask import Flask, render_template, redirect, url_for, request, session
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Secret key for session management

# Constants
BOARD_SIZE = 25
MAX_PLAYERS = 4
CHARACTER_IMAGES = {
    'alien': 'alien.png',
    'astronaut': 'astronaut.png'
}

# Helper functions
def roll_die():
    """Simulate rolling a 6-sided die."""
    return random.randint(1, 6)

def initialize_game():
    """Initialize game state."""
    return {
        'players': [],  # List of players and their positions
        'turn': 0,      # Index of the current player's turn
        'game_over': False
    }

@app.route('/')
def index():
    """Display the homepage with game setup."""
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    """Start the game by initializing player names."""
    num_players = int(request.form.get('num_players'))
    if num_players < 2 or num_players > MAX_PLAYERS:
        return "You need between 2 and 4 players", 400

    # Initialize player positions (all start at position -1, the "Start" space)
    session['game'] = initialize_game()
    for i in range(num_players):
        player_name = request.form.get(f'player{i+1}_name')
        character_type = 'alien' if i % 2 == 0 else 'astronaut'  # Alternate between alien and astronaut
        session['game']['players'].append({
            'name': player_name,
            'position': -1,  # Players start at position -1, before the first space
            'character': CHARACTER_IMAGES[character_type]  # Assign character
        })
    
    session['game']['turn'] = 0  # Start with the first player
    return redirect(url_for('game'))

@app.route('/game')
def game():
    """Render the game board and player info."""
    game = session.get('game')
    if game is None or game['game_over']:
        return redirect(url_for('index'))

    current_player = game['players'][game['turn']]
    return render_template('game.html', game=game, current_player=current_player)

@app.route('/roll_die')
def roll_die_action():
    """Handle the die roll and move the player."""
    game = session.get('game')
    if game is None or game['game_over']:
        return redirect(url_for('index'))

    current_player = game['players'][game['turn']]
    die_roll = roll_die()
    
    # Move the player, starting from position -1 (before the first space)
    current_player['position'] += die_roll
    if current_player['position'] >= BOARD_SIZE:
        current_player['position'] = BOARD_SIZE  # Cap position at the board size
        game['game_over'] = True  # End the game if a player reaches the last space

    # Move to the next player
    game['turn'] = (game['turn'] + 1) % len(game['players'])

    session['game'] = game  # Save game state back to session
    return redirect(url_for('game'))

@app.route('/restart')
def restart():
    """Restart the game."""
    session.pop('game', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
