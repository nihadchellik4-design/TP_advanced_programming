# hamachi_server.py - VERSION CORRIGÉE
import socket
import threading
import json
import random
import time


class HamachiSnakeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}
        self.game_state = {
            'players': {},
            'food1': [10, 10],
            'food2': [15, 15],
            'obstacles': [[5, 5], [10, 15], [15, 5]]
        }
        self.running = True

        print("=" * 50)
        print("🐍 SERVEUR SNAKE HAMACHI")
        print("=" * 50)

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)

            hamachi_ip = self.get_hamachi_ip()

            print(f"✅ Serveur démarré sur le port {self.port}")
            print(f"📡 IP HAMACHI à donner : {hamachi_ip}")
            print(f"   Port : {self.port}")
            print("=" * 50)
            print("👥 En attente de joueurs...")

            # Démarrer la boucle de jeu
            game_thread = threading.Thread(target=self.game_loop)
            game_thread.daemon = True
            game_thread.start()

            while True:
                conn, addr = self.server.accept()
                print(f"✅ {addr[0]} connecté!")

                # Ajouter le client
                client_id = len(self.clients)
                self.clients[client_id] = {
                    'conn': conn,
                    'addr': addr,
                    'name': f"Joueur {client_id + 1}",
                    'snake': {
                        'body': [[6 + client_id * 2, 9], [5 + client_id * 2, 9], [4 + client_id * 2, 9]],
                        'direction': [1, 0],
                        'score': 0,
                        'alive': True
                    },
                    'last_update': time.time()
                }

                # Envoyer ID IMMÉDIATEMENT
                self.send_json(conn, {
                    'type': 'welcome',
                    'client_id': client_id,
                    'message': 'Bienvenue dans Snake Game!'
                })

                # Démarrer thread pour ce client
                thread = threading.Thread(target=self.handle_client, args=(client_id,))
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
            self.running = False
        finally:
            self.server.close()

    def get_hamachi_ip(self):
        """Essaie de détecter l'IP Hamachi"""
        try:
            import socket as s
            hostname = s.gethostname()
            ip_list = s.gethostbyname_ex(hostname)[2]

            hamachi_ips = [ip for ip in ip_list if ip.startswith('25.') or ip.startswith('5.')]
            return hamachi_ips[0] if hamachi_ips else ip_list[0]
        except:
            return "25.40.67.39"  # Votre IP Hamachi

    def send_json(self, conn, data):
        """Envoie des données JSON"""
        try:
            message = json.dumps(data).encode('utf-8')
            conn.send(message)
            return True
        except:
            return False

    def handle_client(self, client_id):
        client = self.clients[client_id]
        try:
            while client_id in self.clients:
                data = client['conn'].recv(1024)
                if not data:
                    break

                try:
                    message = json.loads(data.decode())

                    if message.get('type') == 'join':
                        client['name'] = message.get('name', client['name'])
                        print(f"🎮 {client['name']} a rejoint!")

                        # IMPORTANT: Envoyer l'état du jeu après join
                        self.send_game_state_to_client(client_id)

                    elif message.get('type') == 'direction':
                        client['snake']['direction'] = message.get('direction', [1, 0])

                except json.JSONDecodeError:
                    pass

        except:
            pass
        finally:
            print(f"👋 {client['name']} a quitté")
            if client_id in self.clients:
                self.remove_client(client_id)

    def send_game_state_to_client(self, client_id):
        """Envoie l'état du jeu à un client spécifique"""
        if client_id in self.clients:
            try:
                game_state = self.prepare_game_state()
                self.send_json(self.clients[client_id]['conn'], {
                    'type': 'state',
                    'game_state': game_state
                })
            except:
                self.remove_client(client_id)

    def game_loop(self):
        """Boucle principale du jeu"""
        while self.running:
            try:
                # Mettre à jour tous les serpents
                for client_id, client in list(self.clients.items()):
                    if not client['snake']['alive']:
                        continue

                    snake = client['snake']
                    head = snake['body'][0]
                    direction = snake['direction']

                    # Nouvelle tête
                    new_head = [
                        (head[0] + direction[0]) % 20,
                        (head[1] + direction[1]) % 20
                    ]

                    snake['body'].insert(0, new_head)

                    # Vérifier nourriture
                    if new_head == self.game_state['food1']:
                        snake['score'] += 10
                        self.game_state['food1'] = self.generate_food_position()
                    elif new_head == self.game_state['food2']:
                        snake['score'] += 15
                        self.game_state['food2'] = self.generate_food_position()
                    else:
                        snake['body'].pop()

                # Envoyer l'état à tous les clients
                self.broadcast_game_state()

                time.sleep(0.1)  # 10 FPS

            except Exception as e:
                print(f"Erreur game loop: {e}")
                time.sleep(1)

    def generate_food_position(self):
        while True:
            pos = [random.randint(0, 19), random.randint(0, 19)]

            if pos in self.game_state['obstacles']:
                continue

            on_snake = False
            for client in self.clients.values():
                if pos in client['snake']['body']:
                    on_snake = True
                    break

            if not on_snake:
                return pos

    def prepare_game_state(self):
        """Prépare l'état du jeu pour l'envoi"""
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
        """Envoie l'état du jeu à tous les clients"""
        if not self.clients:
            return

        game_state = self.prepare_game_state()
        message = {
            'type': 'state',
            'game_state': game_state
        }

        dead_clients = []
        for client_id, client in self.clients.items():
            try:
                self.send_json(client['conn'], message)
            except:
                dead_clients.append(client_id)

        for client_id in dead_clients:
            self.remove_client(client_id)

    def remove_client(self, client_id):
        if client_id in self.clients:
            try:
                self.clients[client_id]['conn'].close()
            except:
                pass
            del self.clients[client_id]


if __name__ == "__main__":
    server = HamachiSnakeServer('0.0.0.0', 5555)
    server.start()