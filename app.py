from flask import Flask, render_template, request, redirect, url_for
import random
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdd_loupGarou.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Text)
    encouple = db.Column(db.Text)


@app.route('/')
def home():
    players = Player.query.all()
    return render_template('index.html', players=players)


@app.route('/register', methods=['POST'])
def register():
    player_name = request.form['nom']
    player = Player(nom=player_name)
    db.session.add(player)
    db.session.commit()
    return redirect('/')


@app.route('/supprimer_joueur', methods=['POST'])
def supprimer_joueur():
    joueur_id = request.form.get('joueur_id')

    joueur = Player.query.get(joueur_id)
    db.session.delete(joueur)
    db.session.commit()

    return redirect('/')


def attribuer_roles():
    # Liste des rôles disponibles
    roles_disponibles = ['Voyante', 'Chasseur', 'Sorciere', 'PetiteFille', 'Cupidon', 'Loup', 'Villageois']

    # Récupérer la liste des joueurs depuis la base de données
    joueurs = Player.query.all()
    random.shuffle(joueurs)
    # Vérifier s'il y a suffisamment de joueurs pour attribuer les rôles
    if len(joueurs) < 8:
        raise Exception("Il n'y a pas suffisamment de joueurs pour attribuer les rôles.")

    # Calculer le nombre de loups à attribuer
    nombre_loups = len(joueurs) // 2

    # Attribuer les rôles aux joueurs
    for i in range(len(joueurs)):
        joueur = joueurs[i]

        if nombre_loups > 0:
            # Attribuer un rôle de loup
            joueur.role = 'Loup'
            nombre_loups -= 1
            if nombre_loups == 0 :
                if 'Loup' in roles_disponibles :
                    roles_disponibles.remove('Loup')

        elif 'Sorciere' in roles_disponibles:
            joueur.role = 'Sorciere'
            roles_disponibles.remove('Sorciere')

        elif 'Chasseur' in roles_disponibles:
            joueur.role = 'Chasseur'
            roles_disponibles.remove('Chasseur')

        elif 'Cupidon' in roles_disponibles:
            joueur.role = 'Cupidon'
            roles_disponibles.remove('Cupidon')

        elif 'Voyante' in roles_disponibles:
            joueur.role = 'Voyante'
            roles_disponibles.remove('Voyante')

        elif 'PetiteFille' in roles_disponibles:
            joueur.role = 'PetiteFille'
            roles_disponibles.remove('PetiteFille')

        else:
            # Attribuer le rôle villageois aux autres joueurs
            joueur.role = 'Villageois'

    # Enregistrer les modifications dans la base de données
    db.session.commit()

@app.route('/start')
def start_game():
    attribuer_roles()
    return redirect('/divulguer_role/1')

@app.route('/divulguer_role/<int:player_id>', methods=['GET', 'POST'])
def divulguer_role(player_id):
    player = Player.query.get(player_id)  # Récupère le joueur par son ID

    if player is None:
        return redirect('/')

    if request.method == 'POST':
        next_player_id = player_id + 1  # ID du joueur suivant
        next_player = Player.query.get(next_player_id)

        if next_player is None:  # Si le joueur suivant n'existe pas, la partie est terminée

            return redirect('/')

        return redirect(url_for('divulguer_role', player_id=next_player_id))

    return render_template('divulgation_role.html', player=player)


@app.route('/passer_au_joueur_suivant/<int:player_id>', methods=['POST'])
def passer_au_joueur_suivant(player_id):
    # Récupérer le joueur suivant dans la liste des joueurs
    joueurs = Player.query.all()
    joueur_courant = Player.query.get(player_id)
    index_joueur_suivant = (joueurs.index(joueur_courant) + 1) % len(joueurs)
    joueur_suivant = joueurs[index_joueur_suivant]

    # Rediriger vers la page de divulgation du rôle du joueur suivant
    return redirect(url_for('divulguer_role', player_id=joueur_suivant.id))

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

@app.route('/cupidon')
def cupidon():
    return render_template('cupidon_action.html', players=roles['cupidon'])


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
