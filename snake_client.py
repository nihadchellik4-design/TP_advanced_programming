# Ce fichier implémente le CLIENT du jeu Snake multijoueur.
# Rôle : Se connecter au serveur, afficher le jeu, envoyer les commandes
# Communication bidirectionnelle avec le serveur via sockets

import socket  # Module réseau - connexion au serveur
import threading  # Threading - réception asynchrone des messages
import json  # JSON - décodage des messages du serveur
import pygame  # Pygame - interface graphique et affichage
from pygame.math import Vector2  # Vecteurs 2D pour positions/directions
import random  # Aléatoire - non utilisé mais conservé

# PALETTE DE COULEURS MODERNE
BG_LIGHT = (46, 204, 113)
BG_DARK = (39, 174, 96)
SNAKE_MY_COLOR = (22, 160, 133)
SNAKE_MY_HEAD = (26, 188, 156)
SNAKE_OTHER_COLOR = (52, 152, 219)
SNAKE_OTHER_HEAD = (41, 128, 185)
RED = (231, 76, 60)
WHITE = (236, 240, 241)
ORANGE = (230, 126, 34)
BRICK_RED = (192, 57, 43)
BRICK_DARK = (169, 50, 38)
UI_BG = (52, 73, 94)
TEXT_DARK = (44, 62, 80)
GOLD = (241, 196, 15)


class NetworkClient:
    """
    CLASSE DE COMMUNICATION RÉSEAU
    Gère toute la communication avec le serveur :
    - Connexion TCP
    - Envoi de messages (join, direction)
    - Réception asynchrone des mises à jour
    - Maintien de l'état du jeu synchronisé
    """

    def __init__(self, host, port):
        """
        Constructeur : initialise le client réseau
        Paramètres :
            host : IP du serveur (ex: 25.40.67.39)
            port : Port du serveur (5555)
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.client_id = None  # Sera assigné par le serveur
        self.game_state = {  # État du jeu synchronisé
            'players': {},
            'food1': None,
            'food2': None,
            'obstacles': []
        }
        self.connected = False
        self.lock = threading.Lock()  # Verrou pour accès thread-safe

    def connect(self):
        """
        MÉTHODE : Établit la connexion avec le serveur
        Étapes :
        1. Connexion TCP au serveur
        2. Réception du message 'welcome' avec l'ID
        3. Démarrage du thread de réception
        """
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            print(f"✅ Connected to {self.host}:{self.port}")

            # === RÉCEPTION DU WELCOME ===
            # Le serveur envoie l'ID immédiatement après connexion
            data = self.client.recv(4096)
            if data:
                welcome = json.loads(data.decode('utf-8'))
                self.client_id = welcome.get('client_id')
                print(f"🆔 Assigned ID: {self.client_id}")

            # === THREAD DE RÉCEPTION ===
            # S'exécute en parallèle pour écouter le serveur en continu
            threading.Thread(target=self.receive, daemon=True).start()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def send(self, data):
        """
        MÉTHODE : Envoie des données au serveur
        Utilisé pour envoyer 'join' et 'direction'
        """
        try:
            message = json.dumps(data).encode('utf-8')
            self.client.send(message)
        except Exception as e:
            print(f"❌ Send error: {e}")
            self.connected = False

    def receive(self):
        """
        MÉTHODE : Thread de réception continue
        Boucle tant que connecté :
        1. Attend des données du serveur
        2. Parse le JSON
        3. Traite le message selon son type
        """
        while self.connected:
            try:
                self.client.settimeout(0.1)  # Timeout pour vérifier connected
                data = self.client.recv(4096)

                if data:
                    try:
                        data_json = json.loads(data.decode('utf-8'))
                        self.process_message(data_json)
                    except json.JSONDecodeError:
                        print(f"❌ Invalid JSON received: {data[:100]}")

            except socket.timeout:
                # Timeout normal, on continue
                continue
            except Exception as e:
                print(f"❌ Receive error: {e}")
                self.connected = False
                break

    def process_message(self, data):
        """
        MÉTHODE : Traite les messages reçus du serveur
        Types de messages :
        - 'state' : mise à jour de l'état du jeu
        """
        msg_type = data.get('type')

        if msg_type == 'state':
            # Mise à jour thread-safe de l'état du jeu
            with self.lock:
                self.game_state = data['game_state']


class MultiplayerGame:
    """
    CLASSE PRINCIPALE DU JEU CÔTÉ CLIENT
    Gère :
    - L'affichage graphique (pygame)
    - Les entrées clavier
    - La communication avec NetworkClient
    - Le rendu des serpents, nourriture, obstacles
    """

    def __init__(self, network_client, player_name):
        """
        Constructeur : initialise le jeu
        Paramètres :
            network_client : instance de NetworkClient déjà connecté
            player_name : nom choisi par le joueur
        """
        self.network = network_client
        self.player_name = player_name

        # === INITIALISATION PYGAME ===
        pygame.init()
        self.cell_size = 20
        self.number_of_cells = 20
        self.OFFSET = 75

        # === CRÉATION DE LA FENÊTRE ===
        self.screen = pygame.display.set_mode(
            (2 * self.OFFSET + self.cell_size * self.number_of_cells,
             2 * self.OFFSET + self.cell_size * self.number_of_cells)
        )
        pygame.display.set_caption("🐍 Snake Game - Multiplayer")

        # === DIRECTION DU SERPENT ===
        self.my_direction = [1, 0]  # Direction actuelle (droite)
        self.last_direction = [1, 0]  # Dernière direction (pour anti-retour)

        # === ENVOI DU MESSAGE 'join' ===
        # IMPORTANT : Le client s'identifie auprès du serveur
        self.network.send({
            'type': 'join',
            'name': player_name,
            'body': [[6, 9], [5, 9], [4, 9]],
            'direction': self.my_direction
        })

        # === POLICES D'AFFICHAGE ===
        self.title_font = pygame.font.Font(None, 70)
        self.score_font = pygame.font.Font(None, 45)
        self.small_font = pygame.font.Font(None, 28)
        self.info_font = pygame.font.Font(None, 32)

        # === CHARGEMENT DES SONS ===
        try:
            self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
        except:
            self.eat_sound = None
            print("⚠️ Eat sound not found")

        self.last_score = 0

    def handle_input(self):
        """
        MÉTHODE : Gère les entrées clavier pour la direction
        Règles :
        - Flèches directionnelles
        - Empêche le demi-tour (ne pas pouvoir aller dans la direction opposée)
        - Envoie immédiatement la nouvelle direction au serveur
        """
        keys = pygame.key.get_pressed()
        new_direction = None

        # Flèche HAUT : direction [0, -1] (y négatif = haut dans pygame)
        if keys[pygame.K_UP] and self.last_direction != [0, 1]:
            new_direction = [0, -1]
        # Flèche BAS : direction [0, 1]
        elif keys[pygame.K_DOWN] and self.last_direction != [0, -1]:
            new_direction = [0, 1]
        # Flèche GAUCHE : direction [-1, 0]
        elif keys[pygame.K_LEFT] and self.last_direction != [1, 0]:
            new_direction = [-1, 0]
        # Flèche DROITE : direction [1, 0]
        elif keys[pygame.K_RIGHT] and self.last_direction != [-1, 0]:
            new_direction = [1, 0]

        if new_direction:
            self.my_direction = new_direction
            self.last_direction = new_direction
            # Envoi immédiat au serveur
            self.network.send({
                'type': 'direction',
                'direction': new_direction
            })

    def draw(self):
        """
        MÉTHODE : Rendu graphique complet
        Dessine :
        1. Arrière-plan dégradé
        2. Bordures du terrain
        3. Nourriture
        4. Obstacles
        5. Tous les joueurs (serpents)
        6. Interface utilisateur (score, connexion)
        """
        # === RÉCUPÉRATION THREAD-SAFE DE L'ÉTAT ===
        with self.network.lock:
            game_state = self.network.game_state.copy()

        # === 1. ARRIÈRE-PLAN DÉGRADÉ ===
        for y in range(2 * self.OFFSET + self.cell_size * self.number_of_cells):
            ratio = y / (2 * self.OFFSET + self.cell_size * self.number_of_cells)
            r = int(46 + (39 - 46) * ratio)
            g = int(204 + (174 - 204) * ratio)
            b = int(113 + (96 - 113) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y),
                             (2 * self.OFFSET + self.cell_size * self.number_of_cells, y))

        # === 2. BORDURE DU TERRAIN ===
        # Bordure externe (noire)
        pygame.draw.rect(self.screen, TEXT_DARK,
                         (self.OFFSET - 7, self.OFFSET - 7,
                          self.cell_size * self.number_of_cells + 14,
                          self.cell_size * self.number_of_cells + 14),
                         border_radius=10)
        # Bordure interne (verte foncée)
        pygame.draw.rect(self.screen, BG_DARK,
                         (self.OFFSET - 5, self.OFFSET - 5,
                          self.cell_size * self.number_of_cells + 10,
                          self.cell_size * self.number_of_cells + 10),
                         5, border_radius=8)

        # === 3. NOURRITURE ===
        # Pomme (food1) - rouge
        if game_state.get('food1'):
            food_rect = pygame.Rect(
                self.OFFSET + game_state['food1'][0] * self.cell_size,
                self.OFFSET + game_state['food1'][1] * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.circle(self.screen, RED, food_rect.center, self.cell_size // 2)
            # Reflet blanc
            pygame.draw.circle(self.screen, WHITE,
                               (food_rect.centerx - 3, food_rect.centery - 3), 3)

        # Champignon (food2) - orange
        if game_state.get('food2'):
            food_rect = pygame.Rect(
                self.OFFSET + game_state['food2'][0] * self.cell_size,
                self.OFFSET + game_state['food2'][1] * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.circle(self.screen, ORANGE, food_rect.center, self.cell_size // 2)
            pygame.draw.circle(self.screen, WHITE,
                               (food_rect.centerx - 3, food_rect.centery - 3), 3)

        # === 4. OBSTACLES ===
        for obstacle in game_state.get('obstacles', []):
            obs_rect = pygame.Rect(
                self.OFFSET + obstacle[0] * self.cell_size,
                self.OFFSET + obstacle[1] * self.cell_size,
                self.cell_size, self.cell_size
            )
            pygame.draw.rect(self.screen, BRICK_RED, obs_rect, border_radius=4)
            pygame.draw.rect(self.screen, BRICK_DARK, obs_rect, 2, border_radius=4)

        # === 5. TOUS LES JOUEURS ===
        players = game_state.get('players', {})

        for player_id, player_data in players.items():
            is_me = (str(player_id) == str(self.network.client_id))

            # === VÉRIFICATION SI NOURRITURE MANGÉE ===
            if is_me and self.eat_sound:
                current_score = player_data.get('score', 0)
                if current_score > self.last_score:
                    self.eat_sound.play()
                self.last_score = current_score

            # === DESSIN DU CORPS DU SERPENT ===
            body = player_data.get('body', [])
            for i, segment in enumerate(body):
                seg_rect = pygame.Rect(
                    self.OFFSET + segment[0] * self.cell_size,
                    self.OFFSET + segment[1] * self.cell_size,
                    self.cell_size, self.cell_size
                )

                # Sélection de la couleur selon joueur et segment
                if is_me:
                    # MON serpent : teal
                    color = SNAKE_MY_HEAD if i == 0 else SNAKE_MY_COLOR
                else:
                    # AUTRES serpents : bleu
                    color = SNAKE_OTHER_HEAD if i == 0 else SNAKE_OTHER_COLOR

                pygame.draw.rect(self.screen, color, seg_rect, border_radius=7)

                # Effet de brillance sur la tête
                if i == 0:
                    shine_rect = pygame.Rect(seg_rect.x + 4, seg_rect.y + 4, 6, 6)
                    pygame.draw.rect(self.screen, WHITE, shine_rect, border_radius=3)

            # === ÉTIQUETTE DU NOM DU JOUEUR ===
            if player_data.get('name') and body:
                head = body[0]
                name_text = f"{player_data['name']}"
                score_text = f"({player_data.get('score', 0)})"

                name_surface = self.small_font.render(name_text, True, WHITE)
                score_surface = self.small_font.render(score_text, True, GOLD)

                name_x = self.OFFSET + head[0] * self.cell_size
                name_y = self.OFFSET + head[1] * self.cell_size - 25

                # Fond de l'étiquette
                total_width = name_surface.get_width() + score_surface.get_width() + 10
                bg_rect = pygame.Rect(name_x - 5, name_y - 2,
                                      total_width, name_surface.get_height() + 4)
                pygame.draw.rect(self.screen, UI_BG, bg_rect, border_radius=4)
                pygame.draw.rect(self.screen, WHITE, bg_rect, 1, border_radius=4)

                self.screen.blit(name_surface, (name_x, name_y))
                self.screen.blit(score_surface, (name_x + name_surface.get_width() + 5, name_y))

        # === 6. INTERFACE UTILISATEUR ===
        # Titre "MULTIPLAYER"
        title_shadow = self.title_font.render("MULTIPLAYER", True, TEXT_DARK)
        title_surface = self.title_font.render("MULTIPLAYER", True, WHITE)
        self.screen.blit(title_shadow, (self.OFFSET - 3, 18))
        self.screen.blit(title_surface, (self.OFFSET - 5, 15))

        # Score du joueur
        my_score = 0
        if str(self.network.client_id) in players:
            my_score = players[str(self.network.client_id)].get('score', 0)

        score_bg_rect = pygame.Rect(self.OFFSET - 10,
                                    self.OFFSET + self.cell_size * self.number_of_cells + 5,
                                    220, 50)
        pygame.draw.rect(self.screen, UI_BG, score_bg_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, score_bg_rect, 2, border_radius=8)
        score_surface = self.score_font.render(f"Score: {my_score}", True, GOLD)
        self.screen.blit(score_surface,
                         (self.OFFSET, self.OFFSET + self.cell_size * self.number_of_cells + 15))

        # Nombre de joueurs
        players_text = self.info_font.render(f"Players: {len(players)}", True, WHITE)
        self.screen.blit(players_text,
                         (self.OFFSET + 240, self.OFFSET + self.cell_size * self.number_of_cells + 20))

        # État de la connexion
        status_color = (100, 255, 100) if self.network.connected else (255, 100, 100)
        status_text = self.small_font.render(f"Connected to: {self.network.host}", True, status_color)
        self.screen.blit(status_text,
                         (self.OFFSET + 400, self.OFFSET + self.cell_size * self.number_of_cells + 25))

        pygame.display.update()

    def run(self):
        """
        MÉTHODE : Boucle principale du jeu
        S'exécute tant que :
        - La fenêtre est ouverte
        - La connexion est active
        """
        clock = pygame.time.Clock()
        running = True

        while running and self.network.connected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    self.handle_input()

            self.draw()
            clock.tick(60)  # 60 FPS

        pygame.quit()


def get_connection_info():
    """
    FONCTION : Interface de saisie des informations de connexion
    Affiche une fenêtre pygame pour que le joueur entre :
    - IP du serveur (pré-remplie avec l'IP Hamachi)
    - Port (5555 par défaut)
    - Son nom
    Navigation : TAB pour changer de champ, ENTER pour valider
    """
    pygame.init()
    screen = pygame.display.set_mode((700, 500))
    pygame.display.set_caption("🌐 Multiplayer Connection")

    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)

    # Valeurs par défaut
    server_ip = "25.40.67.39"  # IP Hamachi
    server_port = "5555"
    player_name = ""
    active_field = "name"  # Champ actif par défaut

    clock = pygame.time.Clock()

    while True:
        # === ARRIÈRE-PLAN DÉGRADÉ ===
        for y in range(500):
            ratio = y / 500
            r = int(52 + (44 - 52) * ratio)
            g = int(152 + (62 - 152) * ratio)
            b = int(219 + (80 - 219) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (700, y))

        # === TITRE ===
        title = font.render("🌐 MULTIPLAYER", True, WHITE)
        title_rect = title.get_rect(center=(350, 50))
        screen.blit(title, title_rect)

        subtitle = small_font.render("Enter Connection Info", True, (189, 195, 199))
        subtitle_rect = subtitle.get_rect(center=(350, 100))
        screen.blit(subtitle, subtitle_rect)

        # === CHAMP IP (non éditable) ===
        ip_label = small_font.render("Server IP (Hamachi):", True, WHITE)
        screen.blit(ip_label, (100, 150))

        pygame.draw.rect(screen, UI_BG, (100, 180, 500, 45), border_radius=8)
        pygame.draw.rect(screen, (100, 150, 200), (100, 180, 500, 45), 3, border_radius=8)
        ip_text = small_font.render(server_ip, True, WHITE)
        screen.blit(ip_text, (115, 192))

        # === CHAMP PORT ===
        port_label = small_font.render("Server Port:", True, WHITE)
        screen.blit(port_label, (100, 250))

        port_color = WHITE if active_field == "port" else (149, 165, 166)
        pygame.draw.rect(screen, UI_BG, (100, 280, 500, 45), border_radius=8)
        pygame.draw.rect(screen, port_color, (100, 280, 500, 45), 3, border_radius=8)
        port_text = small_font.render(server_port, True, WHITE)
        screen.blit(port_text, (115, 292))

        # === CHAMP NOM ===
        name_label = small_font.render("Your Name:", True, WHITE)
        screen.blit(name_label, (100, 350))

        name_color = WHITE if active_field == "name" else (149, 165, 166)
        pygame.draw.rect(screen, UI_BG, (100, 380, 500, 45), border_radius=8)
        pygame.draw.rect(screen, name_color, (100, 380, 500, 45), 3, border_radius=8)
        name_text = small_font.render(player_name, True, WHITE)
        screen.blit(name_text, (115, 392))

        # === INSTRUCTIONS ===
        inst_font = pygame.font.Font(None, 24)
        inst_text = inst_font.render("Press ENTER to Connect | TAB to switch", True, (189, 195, 199))
        screen.blit(inst_text, (160, 450))

        pygame.display.update()

        # === GESTION DES ÉVÉNEMENTS ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 100 <= mouse_pos[0] <= 600:
                    if 280 <= mouse_pos[1] <= 325:
                        active_field = "port"
                    elif 380 <= mouse_pos[1] <= 425:
                        active_field = "name"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if server_ip and server_port and player_name:
                        pygame.quit()
                        return server_ip, int(server_port), player_name
                elif event.key == pygame.K_TAB:
                    if active_field == "port":
                        active_field = "name"
                    elif active_field == "name":
                        active_field = "port"
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "port":
                        server_port = server_port[:-1]
                    elif active_field == "name":
                        player_name = player_name[:-1]
                else:
                    if active_field == "port" and len(server_port) < 10 and event.unicode.isdigit():
                        server_port += event.unicode
                    elif active_field == "name" and len(player_name) < 20:
                        player_name += event.unicode

        clock.tick(30)


def main():
    """
    FONCTION PRINCIPALE
    Orchestre le déroulement du client :
    1. Affiche les instructions
    2. Récupère les infos de connexion
    3. Établit la connexion
    4. Lance le jeu
    """
    print("🐍 SNAKE GAME - MULTIPLAYER CLIENT")
    print("\nInstructions:")
    print("1. Server must run 'Multiplayer Host (Server)' first")
    print(f"2. Server IP: 25.40.67.39 (your Hamachi IP)")
    print("3. Port: 5555")

    # Récupération des informations
    server_host, server_port, player_name = get_connection_info()

    # Connexion au serveur
    network = NetworkClient(server_host, server_port)
    if network.connect():
        # Lancement du jeu
        game = MultiplayerGame(network, player_name)
        game.run()
    else:
        print("❌ Could not connect to server")
        input("Press Enter to continue...")


def launch_multiplayer_client():
    """
    Fonction d'entrée pour le lanceur principal
    Permet d'appeler main() depuis snake_launcher.py
    """
    main()


if __name__ == "__main__":
    main()