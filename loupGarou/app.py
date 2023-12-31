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

players = []
roles = {}


@app.route('/')
def home():
    return render_template('index.html')


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
    if len(all_players) < 5:
        return "Le jeu nécessite au moins 5 joueurs."

    # Distribuer les rôles
    random.shuffle(all_players)
    roles['loups_garous'] = [player.name for player in all_players[:2]]
    roles['voyante'] = all_players[2].name
    roles['villageois'] = [player.name for player in all_players[3:]]

    return redirect('/night')


@app.route('/night')
def night_phase():
    return render_template('night.html', players=roles['villageois'], roles=roles)


@app.route('/vote', methods=['POST'])
def vote():
    eliminated_player = request.form['eliminated_player']
    # Effectuer les vérifications et les actions nécessaires pour le vote
    return redirect('/result')


@app.route('/result')
def show_result():
    eliminated_player = request.args.get('eliminated_player')
    return render_template('result.html', eliminated_player=eliminated_player)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
