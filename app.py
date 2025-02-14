from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random
from itertools import combinations

# Global dictionary to store match results
results = {}

app = Flask(__name__)

# Dictionary to map participant names to their classes
participant_classes = {
    "Yahya Toufalla": "PSI*",
    "Loujaine Errabie": "PCSI-3",
    "Abdessamad Sarih": "MP-2",
    "Younesse Boufdil": "MP-3",
    "Abdrrazzake Nrhioua": "PCSI-3",
    "Zakaria Benlgchairi": "PSI*",
    "Abdulbary El hansaly": "PSI-1",
    "Sara Razkani": "PCSI-1",
    "Hamza Khattaf": "PCSI-3",
    "Ilyass Jihi": "MPSI-1",
    "Mouad Ait Benaali": "PSI-1",
    "Akram Silouli": "MP-4",
    "Hassan Sakine": "PSI-1",
    "Fatim-Ezzahra Ouahssou": "MPSI-1",
    "Zayd Ouadllah": "MPSI-4",
    "Othmane Saoud": "MPSI-1",
    "Ayoub Jemali": "MP-4",
    "Youssef Ait Aadi": "MP-2",
    "Houda Matar": "PCSI-1",
    "Yahya Elhoulachi": "MPSI-2",
    "Mohmed Reda Agouram": "MPSI-3",
    "Saad Chiti": "1ECT-2",
    "Mohammed Adam Hazil": "1ECT-1",
    "Noussaiba Elforkani": "MPSI-1",
    "Anas Yatribi": "MP-1",
    "Waile El montaser": "MPSI-5",
    "Mounir Saidi": "MPSI-1",
    "Yassir El fardaoui": "MPSI-2",
    "Amine Elfahi": "PSI-1",
    "Yarnide Aouahchi": "PCSI-1"
}

participants = list(participant_classes.keys())

players = [
    "Yahya Toufalla", "Loujaine Errabie", "Abdessamad Sarih", "Younesse Boufdil",
    "Abdrrazzake Nrhioua", "Zakaria Benlgchairi", "Abdulbary El hansaly", "Sara Razkani",
    "Hamza Khattaf", "Ilyass Jihi", "Mouad Ait Benaali", "Akram Silouli",
    "Hassan Sakine", "Fatim-Ezzahra Ouahssou", "Zayd Ouadllah", "Othmane Saoud",
    "Ayoub Jemali", "Youssef Ait Aadi", "Houda Matar", "Yahya Elhoulachi",
    "Mohmed Reda Agouram", "Saad Chiti", "Mohammed Adam Hazil", "Noussaiba Elforkani",
    "Anas Yatribi", "Waile El montaser", "Mounir Saidi", "Yassir El fardaoui",
    "Amine Elfahi", "Yarnide Aouahchi"
]

# Define points for each participant
points = {
    participant: {
        'points': 0,  # Total points
        'matches_played': 0,  # Matches played (Pld)
        'wins': 0,  # Wins (W)
        'draws': 0,  # Draws (D)
        'loses': 0  # Loses (L)
    }
    for participant in participants
}

# Generate round-robin pairings (29 rounds, 15 matches per round)
def generate_round_robin_pairings(participants):
    pairings = []
    for i in range(len(participants) - 1):
        round_pairings = []
        for j in range(len(participants) // 2):
            round_pairings.append((participants[j], participants[-1 - j]))
        pairings.append(round_pairings)
        participants.insert(1, participants.pop())
    return pairings


@app.route("/rounds")
def show_rounds():
    pairings = generate_round_robin_pairings(participants)
    
    # Create a list of (round number, pairings) for the template
    rounds = [(i + 1, pairings[i]) for i in range(len(pairings))]
    
    return render_template("rounds.html", rounds=rounds)


@app.route('/')
def index():
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")

    # Filter results for today
    daily_summary = []
    for (round_num, match_num), result in results.items():
        if result['date'].startswith(today):  # Check if the result is from today
            daily_summary.append({
                'round_num': round_num,
                'match_num': match_num,
                'winner': result['winner'],
                'loser': result['loser'],
                'date': result['date']
            })

    return render_template('index.html', daily_summary=daily_summary)


@app.route('/participants')
def show_participants():
    return render_template('participants.html', participants=participants, participant_classes=participant_classes)


@app.route('/results')
def show_results():
    return render_template('results.html', results=results)


@app.route('/classification')
def show_classification():
    # Sort participants by points (descending order)
    sorted_participants = sorted(
        points.items(),
        key=lambda x: x[1]['points'],
        reverse=True
    )

    # Prepare classification data
    classification = []
    for rank, (participant, stats) in enumerate(sorted_participants, 1):
        classification.append({
            'rank': rank,
            'participant': participant,
            'class': participant_classes.get(participant, "N/A"),  # Get class from the dictionary
            'points': stats['points'],
            'matches_played': stats['matches_played'],
            'wins': stats['wins'],
            'draws': stats['draws'],
            'loses': stats['loses']
        })

    return render_template('classification.html', classification=classification)


@app.route('/submit_result/<int:round_num>/<int:match_num>', methods=['GET', 'POST'])
def submit_result(round_num, match_num):
    if request.method == 'POST':
        winner = request.form['winner']
        loser = request.form['loser']

        # Get the players for this match
        pairings = generate_round_robin_pairings(participants)  # Generate pairings on the fly
        player1, player2 = pairings[round_num - 1][match_num - 1]

        # Update statistics
        points[player1]['matches_played'] += 1
        points[player2]['matches_played'] += 1

        if winner == "Draw":
            # If it's a draw, both players get 0.5 points
            points[player1]['points'] += 0.5
            points[player2]['points'] += 0.5
            points[player1]['draws'] += 1
            points[player2]['draws'] += 1
        else:
            # If there's a winner, the winner gets 1 point, and the loser gets 0
            points[winner]['points'] += 1
            points[winner]['wins'] += 1
            points[loser]['loses'] += 1

        # Store the result with the date
        match_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results[(round_num, match_num)] = {
            'winner': winner,
            'loser': loser,
            'date': match_date
        }

        return redirect(url_for('show_results'))

    # If GET request, show the form
    return render_template('submit_result.html', round_num=round_num, match_num=match_num)


if __name__ == '__main__':
    app.run(debug=True)
