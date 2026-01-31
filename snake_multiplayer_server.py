import socket
import threading
import json
import random
from datetime import datetime


class SnakeMultiplayerServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}  # client_id: {'conn': socket, 'addr': address, 'name': str, 'snake': snake_data}
        self.client_id_counter = 0

        # Game state
        self.game_state = {
            'players': {},
            'food1': [random.randint(0, 19), random.randint(0, 19)],
            'food2': [random.randint(0, 19), random.randint(0, 19)],
            'obstacles': self.generate_obstacles(8),
            'running': True
        }

        self.lock = threading.Lock()

    def generate_obstacles(self, count):
        obstacles = []
        for _ in range(count):
            obstacles.append([random.randint(0, 19), random.randint(0, 19)])
        return obstacles

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            print(f"🎮 Serveur Snake démarré sur {self.host}:{self.port}")
            print("📡 En attente de connexions...")

            # Thread pour accepter les connexions
            accept_thread = threading.Thread(target=self.accept_connections)
            accept_thread.start()

            # Thread pour mettre à jour le jeu
            game_thread = threading.Thread(target=self.game_loop)
            game_thread.start()

            # Attendre les threads
            accept_thread.join()
            game_thread.join()

        except Exception as e:
            print(f"❌ Erreur serveur: {e}")
        finally:
            self.server.close()

    def accept_connections(self):
        while True:
            try:
                conn, addr = self.server.accept()
                print(f"✅ Connexion de {addr}")

                # Assigner un ID unique
                client_id = self.client_id_counter
                self.client_id_counter += 1

                # Ajouter le client
                with self.lock:
                    self.clients[client_id] = {
                        'conn': conn,
                        'addr': addr,
                        'name': f"Joueur {client_id}",
                        'snake': {
                            'body': [[6 + client_id * 2, 9], [5 + client_id * 2, 9], [4 + client_id * 2, 9]],
                            'direction': [1, 0],
                            'score': 0,
                            'alive': True
                        }
                    }

                # Envoyer l'ID au client
                self.send_to_client(client_id, {
                    'type': 'connection',
                    'client_id': client_id
                })

                # Thread pour ce client
                client_thread = threading.Thread(target=self.handle_client, args=(client_id,))
                client_thread.start()

            except Exception as e:
                print(f"❌ Erreur connexion: {e}")

    def handle_client(self, client_id):
        client = self.clients[client_id]

        try:
            while client_id in self.clients:
                # Recevoir la longueur du message
                length_bytes = client['conn'].recv(4)
                if not length_bytes:
                    break

                message_length = int.from_bytes(length_bytes, byteorder='big')

                # Recevoir le message
                message = b''
                while len(message) < message_length:
                    chunk = client['conn'].recv(min(message_length - len(message), 4096))
                    if not chunk:
                        break
                    message += chunk

                if not message:
                    break

                # Traiter le message
                data = json.loads(message.decode('utf-8'))
                self.process_client_message(client_id, data)

        except Exception as e:
            print(f"❌ Erreur client {client_id}: {e}")
        finally:
            self.remove_client(client_id)

    def process_client_message(self, client_id, data):
        msg_type = data.get('type')

        with self.lock:
            if client_id not in self.clients:
                return

            if msg_type == 'join':
                self.clients[client_id]['name'] = data.get('name', f"Joueur {client_id}")
                self.clients[client_id]['snake']['body'] = data.get('body', [[6, 9], [5, 9], [4, 9]])
                self.clients[client_id]['snake']['direction'] = data.get('direction', [1, 0])
                print(f"👤 {self.clients[client_id]['name']} a rejoint le jeu")

            elif msg_type == 'direction':
                self.clients[client_id]['snake']['direction'] = data['direction']

    def game_loop(self):
        while True:
            try:
                with self.lock:
                    # Mettre à jour tous les serpents
                    for client_id, client_data in list(self.clients.items()):
                        if not client_data['snake']['alive']:
                            continue

                        snake = client_data['snake']
                        head = snake['body'][0]
                        direction = snake['direction']

                        # Nouvelle tête
                        new_head = [
                            (head[0] + direction[0]) % 20,
                            (head[1] + direction[1]) % 20
                        ]

                        # Ajouter nouvelle tête
                        snake['body'].insert(0, new_head)

                        # Vérifier collision avec la nourriture
                        if new_head == self.game_state['food1']:
                            snake['score'] += 10
                            self.game_state['food1'] = self.generate_food_position()
                        elif new_head == self.game_state['food2']:
                            snake['score'] += 15
                            self.game_state['food2'] = self.generate_food_position()
                        else:
                            # Retirer queue si pas mangé
                            snake['body'].pop()

                        # Vérifier collisions
                        if self.check_collisions(client_id, new_head):
                            snake['alive'] = False
                            print(f"💀 {client_data['name']} est mort!")

                # Mettre à jour l'état du jeu
                self.update_game_state()

                # Envoyer l'état à tous les clients
                self.broadcast_game_state()

                # Sleep pour contrôler la vitesse
                threading.Event().wait(0.1)  # 10 FPS

            except Exception as e:
                print(f"❌ Erreur game loop: {e}")
                break

    def generate_food_position(self):
        while True:
            pos = [random.randint(0, 19), random.randint(0, 19)]

            # Vérifier que la nourriture n'est pas sur un obstacle
            if pos in self.game_state['obstacles']:
                continue

            # Vérifier qu'elle n'est pas sur un serpent
            on_snake = False
            for client_id, client_data in self.clients.items():
                if pos in client_data['snake']['body']:
                    on_snake = True
                    break

            if not on_snake:
                return pos

    def check_collisions(self, client_id, head):
        # Vérifier collision avec les obstacles
        if head in self.game_state['obstacles']:
            return True

        # Vérifier collision avec les autres serpents
        for other_id, other_data in self.clients.items():
            if other_id == client_id:
                continue

            if head in other_data['snake']['body']:
                return True

        return False

    def update_game_state(self):
        # Mettre à jour les joueurs dans game_state
        self.game_state['players'] = {}

        for client_id, client_data in self.clients.items():
            self.game_state['players'][client_id] = {
                'name': client_data['name'],
                'body': client_data['snake']['body'],
                'score': client_data['snake']['score'],
                'alive': client_data['snake']['alive'],
                'direction': client_data['snake']['direction']
            }

    def broadcast_game_state(self):
        message = json.dumps({
            'type': 'state',
            'game_state': self.game_state
        }).encode('utf-8')

        message_length = len(message).to_bytes(4, byteorder='big')

        with self.lock:
            dead_clients = []
            for client_id, client_data in list(self.clients.items()):
                try:
                    client_data['conn'].sendall(message_length + message)
                except:
                    dead_clients.append(client_id)

            # Supprimer les clients morts
            for client_id in dead_clients:
                self.remove_client(client_id)

    def send_to_client(self, client_id, data):
        if client_id in self.clients:
            try:
                message = json.dumps(data).encode('utf-8')
                message_length = len(message).to_bytes(4, byteorder='big')
                self.clients[client_id]['conn'].sendall(message_length + message)
            except:
                self.remove_client(client_id)

    def remove_client(self, client_id):
        with self.lock:
            if client_id in self.clients:
                name = self.clients[client_id]['name']
                try:
                    self.clients[client_id]['conn'].close()
                except:
                    pass
                del self.clients[client_id]
                print(f"👋 {name} a quitté le jeu")

    def stop(self):
        with self.lock:
            for client_id in list(self.clients.keys()):
                self.remove_client(client_id)
        self.server.close()


def main():
    print("=" * 50)
    print("🐍 SERVEUR SNAKE MULTIJOUEUR")
    print("=" * 50)

    # Configuration
    HOST = '0.0.0.0'  # Écoute sur toutes les interfaces
    PORT = 5555  # Port par défaut

    print(f"Hôte: {HOST}")
    print(f"Port: {PORT}")
    print("\nInstructions:")
    print("1. Démarrer ce serveur sur l'ordinateur principal")
    print("2. Sur les autres PC, lancer snake_client.py")
    print("3. Entrer l'IP du serveur (ex: 192.168.1.100)")
    print("4. Entrer le port {PORT}")
    print("=" * 50)

    server = SnakeMultiplayerServer(HOST, PORT)

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du serveur...")
        server.stop()


if __name__ == "__main__":
    main()