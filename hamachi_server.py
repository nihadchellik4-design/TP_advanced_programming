# Ce fichier implémente le SERVEUR du jeu Snake multijoueur.
# Rôle : Accepter les connexions des clients, gérer l'état du jeu,
#        synchroniser tous les joueurs en temps réel.
# Spécificité : Optimisé pour Hamachi (VPN) avec détection automatique d'IP

import socket  # Module réseau - permet de créer des sockets TCP/IP
import threading  # Module pour le multithreading - gère plusieurs clients simultanément
import json  # Module JSON - format d'échange de données entre client/serveur
import random  # Module aléatoire - génère des positions aléatoires pour la nourriture
import time  # Module temps - gère les timings et les boucles de jeu


class HamachiSnakeServer:
    """
    CLASSE PRINCIPALE DU SERVEUR
    Cette classe encapsule toute la logique serveur :
    - Gestion des connexions réseau
    - Maintien de l'état du jeu
    - Communication avec les clients
    - Boucle de jeu principale
    """

    def __init__(self, host='0.0.0.0', port=5555):
        """
        CONSTRUCTEUR : Initialise le serveur
        Paramètres :
            host : '0.0.0.0' signifie "écouter sur toutes les interfaces réseau"
            port : 5555 (port standard pour notre jeu)
        """
        self.host = host
        self.port = port

        # Création du socket serveur
        # AF_INET = IPv4, SOCK_STREAM = TCP (connexion fiable)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # SO_REUSEADDR = permet de réutiliser le port immédiatement après arrêt
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Dictionnaire des clients connectés
        # Structure : {client_id: {'conn': socket, 'addr': adresse, 'name': nom, 'snake': {...}, ...}}
        self.clients = {}

        # État du jeu partagé par tous les clients
        self.game_state = {
            'players': {},  # Informations de tous les joueurs
            'food1': [10, 10],  # Position de la pomme (10 points)
            'food2': [15, 15],  # Position du champignon (15 points)
            'obstacles': [[5, 5], [10, 15], [15, 5]]  # Obstacles fixes
        }

        self.running = True  # Flag pour la boucle principale

        print("🐍 SERVEUR SNAKE HAMACHI")

    def start(self):
        """
        MÉTHODE PRINCIPALE : Démarre le serveur
        Étapes :
        1. Bind le socket sur le port
        2. Écoute les connexions entrantes
        3. Détecte l'IP Hamachi
        4. Lance la boucle de jeu en thread séparé
        5. Accepte les connexions en boucle infinie
        """
        try:
            # Associe le socket à l'adresse et au port
            self.server.bind((self.host, self.port))
            # Met le serveur en écoute (max 5 connexions en attente)
            self.server.listen(5)

            # Récupère l'IP Hamachi à donner aux clients
            hamachi_ip = self.get_hamachi_ip()

            print(f"✅ Serveur démarré sur le port {self.port}")
            print(f"📡 IP HAMACHI à donner : {hamachi_ip}")
            print(f"   Port : {self.port}")
            print("👥 En attente de joueurs...")

            # === THREAD DE LA BOUCLE DE JEU ===
            # Daemon = True : ce thread s'arrête quand le thread principal s'arrête
            game_thread = threading.Thread(target=self.game_loop)
            game_thread.daemon = True
            game_thread.start()

            # === BOUCLE PRINCIPALE D'ACCEPTATION DES CONNEXIONS ===
            while True:
                # accept() est BLOQUANT - attend qu'un client se connecte
                conn, addr = self.server.accept()
                print(f"✅ {addr[0]} connecté!")

                # Attribue un ID unique au client (0, 1, 2...)
                client_id = len(self.clients)

                # Crée l'entrée du client dans le dictionnaire
                self.clients[client_id] = {
                    'conn': conn,  # Socket de communication
                    'addr': addr,  # Adresse (IP, port)
                    'name': f"Joueur {client_id + 1}",  # Nom par défaut
                    'snake': {
                        'body': [[6 + client_id * 2, 9], [5 + client_id * 2, 9], [4 + client_id * 2, 9]],
                        # Position de départ décalée selon l'ID
                        # Joueur 0 : [[6,9], [5,9], [4,9]]
                        # Joueur 1 : [[8,9], [7,9], [6,9]]
                        # etc.
                        'direction': [1, 0],  # Direction initiale (droite)
                        'score': 0,  # Score initial
                        'alive': True  # Le serpent est vivant
                    },
                    'last_update': time.time()  # Timestamp de dernière activité
                }

                # === ENVOI IMMÉDIAT DE L'ID AU CLIENT ===
                # TRÈS IMPORTANT : le client doit connaître son ID pour s'identifier
                self.send_json(conn, {
                    'type': 'welcome',
                    'client_id': client_id,
                    'message': 'Bienvenue dans Snake Game!'
                })

                # === THREAD DE GESTION DU CLIENT ===
                # Un thread par client pour gérer ses messages indépendamment
                thread = threading.Thread(target=self.handle_client, args=(client_id,))
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            # Interception de Ctrl+C pour arrêt propre
            print("\n🛑 Arrêt du serveur...")
            self.running = False
        finally:
            # Nettoyage : fermeture du socket
            self.server.close()

    def get_hamachi_ip(self):
        """
        MÉTHODE : Détecte automatiquement l'IP Hamachi
        Hamachi utilise généralement des IP commençant par 25.xx.xx.xx ou 5.xx.xx.xx
        Retourne l'IP à donner aux clients pour se connecter
        """
        try:
            import socket as s
            hostname = s.gethostname()
            # Récupère TOUTES les IP de la machine
            ip_list = s.gethostbyname_ex(hostname)[2]

            # Filtre les IP Hamachi (commencent par 25. ou 5.)
            hamachi_ips = [ip for ip in ip_list if ip.startswith('25.') or ip.startswith('5.')]

            # Si une IP Hamachi est trouvée, on la retourne, sinon la première IP
            return hamachi_ips[0] if hamachi_ips else ip_list[0]
        except:
            # En cas d'échec, retourne l'IP Hamachi par défaut
            return "25.40.67.39"  # Votre IP Hamachi

    def send_json(self, conn, data):
        """
        MÉTHODE : Envoie des données JSON au client
        Paramètres :
            conn : socket du client
            data : dictionnaire Python à envoyer
        Retourne : bool (True si succès, False si échec)
        """
        try:
            # Convertit le dictionnaire en chaîne JSON, puis en bytes
            message = json.dumps(data).encode('utf-8')
            # Envoie les données
            conn.send(message)
            return True
        except:
            return False

    def handle_client(self, client_id):
        """
        MÉTHODE : Gère la communication avec UN client spécifique
        S'exécute dans un thread séparé pour chaque client
        Boucle infinie : attend les messages du client
        """
        client = self.clients[client_id]
        try:
            while client_id in self.clients:
                # RECEVOIR : attend les données du client
                # 1024 = taille du buffer (octets)
                data = client['conn'].recv(1024)

                if not data:
                    # Si data est vide, le client s'est déconnecté
                    break

                try:
                    # Décode et parse le JSON reçu
                    message = json.loads(data.decode())

                    # === TRAITEMENT DU MESSAGE 'join' ===
                    if message.get('type') == 'join':
                        # Le client envoie son nom choisi
                        client['name'] = message.get('name', client['name'])
                        print(f"🎮 {client['name']} a rejoint!")

                        # IMPORTANT : Envoyer l'état du jeu immédiatement
                        # Le client a besoin de connaître l'état initial
                        self.send_game_state_to_client(client_id)

                    # === TRAITEMENT DU MESSAGE 'direction' ===
                    elif message.get('type') == 'direction':
                        # Le client change de direction
                        client['snake']['direction'] = message.get('direction', [1, 0])

                except json.JSONDecodeError:
                    # Données JSON invalides - on ignore
                    pass

        except:
            # Toute erreur = déconnexion du client
            pass
        finally:
            # Nettoyage : retirer le client
            print(f"👋 {client['name']} a quitté")
            if client_id in self.clients:
                self.remove_client(client_id)

    def send_game_state_to_client(self, client_id):
        """
        MÉTHODE : Envoie l'état complet du jeu à UN client spécifique
        Utilisé quand un client vient de se connecter
        """
        if client_id in self.clients:
            try:
                # Prépare l'état du jeu
                game_state = self.prepare_game_state()
                # Envoie avec le type 'state'
                self.send_json(self.clients[client_id]['conn'], {
                    'type': 'state',
                    'game_state': game_state
                })
            except:
                self.remove_client(client_id)

    def game_loop(self):
        """
        MÉTHODE : BOUCLE PRINCIPALE DU JEU
        S'exécute dans un thread séparé
        Fréquence : ~10 FPS (time.sleep(0.1) = 100ms)
        Rôle :
        1. Mettre à jour la position de tous les serpents
        2. Vérifier les collisions avec la nourriture
        3. Générer de nouvelle nourriture si nécessaire
        4. Envoyer l'état mis à jour à TOUS les clients
        """
        while self.running:
            try:
                # === MISE À JOUR DE TOUS LES SERPENTS ===
                # list() crée une copie pour éviter les erreurs si un client se déconnecte
                for client_id, client in list(self.clients.items()):
                    # Ignore les serpents morts
                    if not client['snake']['alive']:
                        continue

                    snake = client['snake']
                    head = snake['body'][0]
                    direction = snake['direction']

                    # NOUVELLE TÊTE : position actuelle + direction
                    new_head = [
                        (head[0] + direction[0]) % 20,  # wrap-around horizontal
                        (head[1] + direction[1]) % 20  # wrap-around vertical
                    ]

                    # Ajoute la nouvelle tête au début du corps
                    snake['body'].insert(0, new_head)

                    # === VÉRIFICATION DE LA NOURRITURE ===
                    if new_head == self.game_state['food1']:
                        # Mange la pomme : +10 points, génère nouvelle pomme
                        snake['score'] += 10
                        self.game_state['food1'] = self.generate_food_position()
                    elif new_head == self.game_state['food2']:
                        # Mange le champignon : +15 points, génère nouveau champignon
                        snake['score'] += 15
                        self.game_state['food2'] = self.generate_food_position()
                    else:
                        # Rien mangé : on retire la queue (longueur constante)
                        snake['body'].pop()

                # === BROADCAST : envoie l'état à tous les clients ===
                self.broadcast_game_state()

                # Vitesse du jeu : 100ms = 10 mouvements/seconde
                time.sleep(0.1)

            except Exception as e:
                print(f"Erreur game loop: {e}")
                time.sleep(1)

    def generate_food_position(self):
        """
        MÉTHODE : Génère une position aléatoire VALIDE pour la nourriture
        Critères de validité :
        - Ne pas être sur un obstacle
        - Ne pas être sur un serpent
        - Boucle jusqu'à trouver une position valide
        """
        while True:
            # Position aléatoire sur la grille 20x20
            pos = [random.randint(0, 19), random.randint(0, 19)]

            # Vérifie les obstacles
            if pos in self.game_state['obstacles']:
                continue

            # Vérifie tous les serpents
            on_snake = False
            for client in self.clients.values():
                if pos in client['snake']['body']:
                    on_snake = True
                    break

            if not on_snake:
                return pos

    def prepare_game_state(self):
        """
        MÉTHODE : Prépare l'état du jeu pour l'envoi aux clients
        Convertit les données internes en format JSON-friendly
        """
        players = {}
        for client_id, client in self.clients.items():
            players[client_id] = {
                'name': client['name'],
                'body': client['snake']['body'],
                'score': client['snake']['score'],
                'alive': client['snake']['alive'],
                'direction': client['snake']['direction']
            }

        return {
            'players': players,
            'food1': self.game_state['food1'],
            'food2': self.game_state['food2'],
            'obstacles': self.game_state['obstacles']
        }

    def broadcast_game_state(self):
        """
        MÉTHODE : Envoie l'état du jeu à TOUS les clients connectés
        Gère les clients déconnectés silencieusement
        """
        if not self.clients:
            return

        # Prépare l'état une fois pour tous les clients
        game_state = self.prepare_game_state()
        message = {
            'type': 'state',
            'game_state': game_state
        }

        # Liste des clients à supprimer
        dead_clients = []

        for client_id, client in self.clients.items():
            try:
                self.send_json(client['conn'], message)
            except:
                # Si l'envoi échoue, le client est déconnecté
                dead_clients.append(client_id)

        # Nettoie les clients déconnectés
        for client_id in dead_clients:
            self.remove_client(client_id)

    def remove_client(self, client_id):
        """
        MÉTHODE : Retire proprement un client déconnecté
        Ferme le socket et supprime du dictionnaire
        """
        if client_id in self.clients:
            try:
                self.clients[client_id]['conn'].close()
            except:
                pass
            del self.clients[client_id]


if __name__ == "__main__":
    """
    POINT D'ENTRÉE : S'exécute quand le fichier est lancé directement
    Crée et démarre le serveur
    """
    server = HamachiSnakeServer('0.0.0.0', 5555)
    server.start()