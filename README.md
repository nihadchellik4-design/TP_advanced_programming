🐍 Snake Game
Un jeu Snake avancé avec 3 modes de jeu : solo, multijoueur local et multijoueur réseau.
🎮 Fonctionnalités
 1. Single Player (`snake_game.py`)
- Mode solo classique
- Système de sauvegarde des scores
- Obstacles aléatoires
- 2 types de nourriture (10 pts et 15 pts)

 2. Premium Version (`snake_server.py`)
- 6 thèmes colorés différents
- 3 niveaux de difficulté
- Effets visuels avancés
- Particules et animations

3. Local Multiplayer (`snake_2players_local.py`)
- 2 joueurs sur le même PC
- Joueur 1 : Flèches directionnelles
- Joueur 2 : Touches WASD
- Choix de couleurs personnalisées
- 3 niveaux de difficulté

 4. Network Multiplayer
- Serveur : `hamachi_server.py`
- Client : `snake_client.py`
- Jusqu'à 4 joueurs en ligne
- Compatible Hamachi pour jouer sur internet

 🌐 Configuration Réseau (Hamachi)

 Pour jouer en ligne :
1. Tous les joueurs installent Hamachi
2. L'hôte crée un réseau et donne le nom/mot de passe
3. Tous rejoignent le même réseau Hamachi
4. L'hôte lance "Multiplayer Host (Server)"
5. Les autres lancent "Multiplayer Join (Client)"
6. Entrer l'IP Hamachi de l'hôte (ex: 25.40.67.39)
7. Port : 5555
 🚀 Installation

 1. Cloner le projet
git clone https://github.com/votre-nom/snake-game-python.git
cd snake-game-python

 2. Installer les dépendances
pip install pygame

 3. Lancer le jeu
python snake_launcher.py
