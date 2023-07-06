from flask import Flask, render_template, request, redirect, url_for
import random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, not_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdd_loupGarou.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Text)
    encouple = db.Column(db.String(100))
    alive = db.Column(db.String(100))

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_nb = db.Column(db.Integer)



@app.route('/')
def home():
    players = Player.query.all()
    return render_template('index.html', players=players)

@app.route('/accueil0')
def init():
    # Supprimer toutes les entrées de la table Player
    db.session.query(Player).delete()
    db.session.commit()

    # Réinitialiser l'auto-incrémentation de l'ID (pour SQLite)
    db.session.execute("DELETE FROM sqlite_sequence WHERE name='Player'")
    db.session.commit()

    db.session.query(Game).delete()
    db.session.commit()

    db.session.execute("DELETE FROM sqlite_sequence WHERE name='Game'")
    db.session.commit()

    game = Game(day_nb=1)
    db.session.add(game) 
    db.session.commit()
    return render_template('accueil.html')

@app.route('/accueil')
def accueil():
    players = Player.query.all()
    return render_template('accueil.html', players=players)


@app.route('/register', methods=['POST'])
def register():
    player_name = request.form['nom']
    player = Player(nom=player_name)
    db.session.add(player)
    db.session.commit()
    return redirect('/accueil')


@app.route('/supprimer_joueur', methods=['POST'])
def supprimer_joueur():
    joueur_id = request.form.get('joueur_id')

    joueur = Player.query.get(joueur_id)
    db.session.delete(joueur)
    db.session.commit()

    return redirect('/accueil')


def attribuer_roles():
    # Liste des rôles disponibles
    roles_disponibles = ['Voyante', 'Chasseur', 'Sorciere', 'PetiteFille', 'Cupidon', 'Loup', 'Villageois', 'Voleur']

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

        if nombre_loups > 0 and 'Loup' in roles_disponibles:
            # Attribuer un rôle de loup
            joueur.role = 'Loup'
            nombre_loups -= 1

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
            
        elif 'Voleur' in roles_disponibles:
            joueur.role = 'Voleur'
            roles_disponibles.remove('Voleur')

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

    if index_joueur_suivant == 0:
        # Si on est arrivé au dernier joueur
        
        return redirect('/night1')

    # Rediriger vers la page de divulgation du rôle du joueur suivant
    return redirect(url_for('divulguer_role', player_id=joueur_suivant.id))

@app.route('/night', methods=['POST', 'GET'])
def night_phase():

    
    roles = get_roles()
    role_array = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Loup")).all()

    if request.method == "POST":
        #joueur_tokill_id = request.form.get('voted_player')
        return redirect('/witch_action')            
        
    return render_template('night.html', players=roles['loups_garous'], roles=roles, ortherPlayer = role_array)

@app.route('/night1', methods=['POST', 'GET'])
def night_phase1():

    
    roles = get_roles()
    role_array = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Loup")).all()

    if request.method == "POST":
        #joueur_tokill_id = request.form.get('voted_player')
        return redirect('/witch_action1')            
        
    return render_template('night.html', players=roles['loups_garous'], roles=roles, ortherPlayer = role_array)


@app.route('/wolf_voted', methods=['POST'])
def wolf_voted():
    update_player_alive(request.form.get('voted_player'),"loup")
    player = Player.query.get(request.form.get('voted_player'))
    players = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Sorciere")).all()
    return render_template('witch_action.html', voted_player=player, players=players)

@app.route('/wolf_vote')
def wolf_vote():
    roles = get_roles()
    role_array = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Loup")).all()

    return render_template('wolf_vote.html', players=roles['loups_garous'], other_player=role_array)


@app.route('/wolf_vote_action', methods=['POST'])
def process_wolf_vote():

    return redirect('/witch_action')

@app.route('/chasseur')
def chasseur():
    players_for_chasseur = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Chasseur")).all()
    return render_template('/chasseur_action.html', players_for_chasseur=players_for_chasseur)

@app.route('/chasseur_action')
def chasseur_action():
    update_player_alive(request.form.get('player'), "chasseur")
    return redirect('/day')

@app.route('/voyante')
def voyante():
    players = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Voyante")).all()
    voyante = Player.query.filter(Player.role == "Voyante").first()
    return render_template('voyante.html', players=players, voyante=voyante)

@app.route('/voyante_action', methods=['POST'])
def voyante_action():
    player_id = request.form['player_id']
    player = Player.query.get(player_id)
    return render_template('voyante_action.html', player=player)

@app.route('/voleur')
def voleur():
    players = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Voleur")).all()
    voleur = Player.query.filter(Player.role == "Voleur").first()
    return render_template('voleur.html', players=players, voleur=voleur)

@app.route('/voleur_action', methods=['POST'])
def voleur_action():
    player_id = request.form['player_id']
    player = Player.query.get(player_id)
    voleur = Player.query.filter(Player.role == "Voleur").first()

    # On échange les rôles
    voleur.role = player.role
    player.role = "Voleur"

    db.session.commit()
    
    return render_template('voleur_action.html', player=player, voleur=voleur)


@app.route('/witch_action', methods=['POST', 'GET'])
def witch_action():
    players_alive_for_witch = Player.query.filter(((Player.alive == None) | (Player.alive.startswith("ressucite"))) & (Player.role != "Sorciere")).all()
    player_dead = Player.query.filter(Player.alive != None).all()
    players = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Sorciere")).all()

    if request.method == "POST":
        return redirect('/day')

    return render_template('witch_action.html', players=players)

@app.route('/witch_action1', methods=['POST', 'GET'])
def witch_action1():
    players_alive_for_witch = Player.query.filter(((Player.alive == None) | (Player.alive.startswith("ressucite"))) & (Player.role != "Sorciere")).all()
    player_dead = Player.query.filter(Player.alive != None).all()
    players = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite"))) & (Player.role != "Sorciere")).all()

    if request.method == "POST":
        return redirect('/voyante')   

    return render_template('witch_action.html', players=players)

@app.route('/maire')
def maire():
    roles=get_roles()
    # Affichage de l'action du maire
    return render_template('maire_action.html', players=roles['villageois'])

def get_player_resurrected(jour):
    joueur = Player.query.filter(Player.alive == f"ressuscite {jour}").first()
    return joueur

def get_chasseur_dead(jour):
    joueur = Player.query.filter(Player.role == "chasseur").filter(func.substr(Player.alive, -1, 1) == str(jour)).first()
    return joueur

def get_couple():
    couple_players = Player.query.filter(Player.encouple == str(1)).all()
    return couple_players

@app.route('/day')
def day_phase():
    roles = get_roles()
    role_array = []
    day_nb = get_day_nb()
    players_dead = get_players_dead(day_nb)
    player_resurrected = get_player_resurrected(day_nb)
    chasseur_dead = get_chasseur_dead(day_nb)
    couple = get_couple()
    role_array = Player.query.filter(((Player.alive.is_(None)) | (Player.alive.startswith("ressuscite")))).all()
    bilan = ""
    if len(players_dead) == 0:
        bilan = "personne n\'est mort"
    #elif len(players_dead) >= 1 :
    #    for i in len(players_dead):
    #        bilan = bilan + players_dead[i].nom + " a été tué dans la nuit par " + players_dead[i].raison + " c\'était " + players_dead[i].role

    if player_resurrected is not None:
        bilan = bilan + player_resurrected.nom + " a été sauvé des loups par la sorcière en utilisant sa potion de résurrection"
    
    if day_nb == 1:
        bilan = bilan + "Cupidon a fondé un couple : " + couple[0].nom + " - " + couple[1].nom

    if chasseur_dead:
        redirect('/chasseur')  
    
    return render_template('day.html', players=role_array, day_nb=day_nb, bilan=bilan)


@app.route('/cupidon')
def cupidon():
    roles = get_roles()
    return render_template('cupidon_action.html', players=Player.query.all())

@app.route('/cupidon_action2', methods=['POST'])
def lien_joueurs():
    joueur1_nom = request.form['player1']
    joueur2_nom = request.form['player2']
    joueur1 = Player.query.filter_by(nom=joueur1_nom).first()
    joueur2 = Player.query.filter_by(nom=joueur2_nom).first()
    if joueur1 is not None and joueur2 is not None:
        joueur1.encouple = "1"
        joueur2.encouple = "1"
        db.session.commit()
    return redirect('/day')

def update_player_alive(player_id, reason):
    player = Player.query.get(player_id)
    game = Game.query.first()
    day_number = game.day_nb
    player.alive = f"{reason} {day_number}"
    db.session.commit()


@app.route('/vote', methods=['POST'])
def vote():
    update_player_alive(request.form.get('eliminated_player'),"conseil")
    player = Player.query.get(request.form.get('eliminated_player'))
    return render_template('villageRendort.html', voted_player=player)


@app.route('/recap')
def recap():
    loup = Player.query.filter(Player.role == "Loup").all()
    villageois = Player.query.filter(Player.role == "Villageois").all()
    sorciere = Player.query.filter(Player.role == "Sorciere").first()
    chasseur = Player.query.filter(Player.role == "Chasseur").first()
    voyante = Player.query.filter(Player.role == "Voyante").first()
    petite_fille = Player.query.filter(Player.role == "PetiteFille").first()
    cupidon = Player.query.filter(Player.role == "Cupidon").first()
    voleur = Player.query.filter(Player.role == "Voleur").first()
    return render_template('recap.html', loup=loup, villageois=villageois, sorciere=sorciere, chasseur=chasseur, voyante=voyante, petite_fille=petite_fille, cupidon=cupidon, voleur=voleur)



def get_day_nb():
    game = Game.query.first()
    return game.day_nb

def get_players_dead(day):
    players_dead = Player.query.filter(((not_(Player.alive.is_(None))) | (not_((Player.alive.startswith("ressuscite")))))).all()
    players_info = []
    
    for player in players_dead:
        if player.alive[-1] == str(day):
            player_info = {
                "id": player.id,
                "nom": player.nom,
                "role": player.role,
                "encouple": player.encouple,
                "raison": player.alive[:-1], 
                "day_of_death": day
            }
            players_info.append(player_info)
    
    return players_info

def get_roles():
    roles = {
        'villageois': [],
        'loups_garous': [],
        'sorciere': [],
        'chasseur': [],
        'voyante': [],
        'petite_fille': [],
        'cupidon': []
    }

    players = Player.query.all()

    for player in players:
        if player.role == 'Villageois':
            roles['villageois'].append(player)
        elif player.role == 'Loup':
            roles['loups_garous'].append(player)
        elif player.role == 'Sorciere':
            roles['sorciere'].append(player)
        elif player.role == 'Chasseur':
            roles['chasseur'].append(player)
        elif player.role == 'Voyante':
            roles['voyante'].append(player)
        elif player.role == 'PetiteFille':
            roles['petite_fille'].append(player)
        elif player.role == 'Cupidon':
            roles['cupidon'].append(player)

    return roles

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
