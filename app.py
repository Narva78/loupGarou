from flask import Flask, render_template, request, redirect
import random
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///players.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return self.name

roles = {}


@app.route('/')
def home():
    players = Player.query.all()
    return render_template('index.html', players=players)


@app.route('/register', methods=['POST'])
def register():
    player_name = request.form['name']
    player = Player(name=player_name)
    db.session.add(player)
    db.session.commit()
    return redirect('/')


@app.route('/start')
def start_game():
    all_players = Player.query.all()
    num_players = len(all_players)
    
    if num_players < 5 or num_players > 12:
        return "Le jeu nécessite entre 5 et 12 joueurs."

    # Distribution des rôles
    random.shuffle(all_players)
    
    if num_players >= 5 and num_players <= 7:
        roles['loups_garous'] = [player.name for player in all_players[:2]]
    elif num_players >= 8 and num_players <= 12:
        roles['loups_garous'] = [player.name for player in all_players[:3]]
    
    roles['voyante'] = all_players[num_players - 3].name
    roles['villageois'] = [player.name for player in all_players[num_players - 2:]]
    
    if num_players >= 8:
        roles['chasseur'] = all_players[-1].name
        
    if num_players >= 9:
        roles['sorciere'] = all_players[-2].name
        
    if num_players == 10:
        roles['petite_fille'] = all_players[-3].name
        
    if num_players >= 6:
        roles['cupidon'] = all_players[-4].name

    return redirect('/night')


@app.route('/night')
def night_phase():
    return render_template('night.html', players=roles['villageois'], roles=roles)


@app.route('/night_action', methods=['POST'])
def process_night_action():
    # Traitement des actions de la nuit
    # ...
    return redirect('/wolf_vote')


@app.route('/wolf_vote')
def wolf_vote():
    # Affichage du vote des loups-garous
    return render_template('wolf_vote.html', players=roles['loups_garous'])


@app.route('/wolf_vote_action', methods=['POST'])
def process_wolf_vote():
    # Traitement du vote des loups-garous
    # ...
    return redirect('/witch_action')


@app.route('/witch_action')
def witch_action():
    # Affichage de l'action de la sorcière
    return render_template('witch_action.html', players=roles['sorciere'])


@app.route('/witch_action_action', methods=['POST'])
def process_witch_action():
    # Traitement de l'action de la sorcière
    # ...
    return redirect('/day')


@app.route('/day')
def day_phase():
    return render_template('day.html', players=roles['villageois'])


@app.route('/vote', methods=['POST'])
def vote():
    eliminated_player = request.form['eliminated_player']
    # Effectuer les vérifications et les actions nécessaires pour le vote
    return redirect('/result')


@app.route('/result')
def show_result():
    eliminated_player = request.args.get('eliminated_player')
    return render_template('result.html', eliminated_player=eliminated_player)


@app.route('/recap')
def recap():
    return render_template('recap.html', roles=roles)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
