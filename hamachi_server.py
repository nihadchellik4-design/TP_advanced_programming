import socket
import threading
import json
import random
from datetime import datetime
import sys


class HamachiSnakeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}
        self.client_id_counter = 0
        self.game_state = {
            'players': {},
            'food1': [random.randint(0, 19), random.randint(0, 19)],
            'food2': [random.randint(0, 19), random.randint(0, 19)],
            'obstacles': self.generate_obstacles(8),
            'running': True
        }
        self.lock = threading.Lock()

        print("=" * 50)
        print("🐍 SERVEUR SNAKE HAMACHI/RÉSEAU")
        print("=" * 50)

    def generate_obstacles(self, count):
        obstacles = []
        for _ in range(count):
            obstacles.append([random.randint(0, 19), random.randint(0, 19)])
        return obstacles

    def get_hamachi_ip(self):
        """Try to get Hamachi IP automatically"""
        try:
            # Get local IP addresses
            import socket as s
            hostname = s.gethostname()
            ip_list = s.gethostbyname_ex(hostname)[2]

            # Look for Hamachi IPs (typically 25.x.x.x or 5.x.x.x)
            hamachi_ips = [ip for ip in ip_list if ip.startswith('25.') or ip.startswith('5.')]

            if hamachi_ips:
                return hamachi_ips[0]
            elif ip_list:
                return ip_list[0]  # Fallback to any IP
            else:
                return "127.0.0.1"
        except:
            return "127.0.0.1"

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)

            hamachi_ip = self.get_hamachi_ip()

            print(f"✅ Serveur démarré sur le port {self.port}")
            print(f"📡 Adresses IP disponibles :")
            print(f"   - Localhost: 127.0.0.1")
            print(f"   - Réseau local: {hamachi_ip}")
            print(f"   - Port : {self.port}")
            print(f"\n📝 Instructions pour les joueurs :")
            print(f"   1. Lancer 'Multiplayer Join (Client)'")
            print(f"   2. Entrer l'IP : {hamachi_ip}")
            print(f"   3. Port : {self.port}")
            print(f"   4. Entrer votre nom")
            print("=" * 50)
            print("👥 En attente de joueurs...")

            # Accept connections in main thread
            while True:
                conn, addr = self.server.accept()
                print(f"✅ Connexion de {addr[0]}:{addr[1]}")

                # Assign client ID
                client_id = self.client_id_counter
                self.client_id_counter += 1

                with self.lock:
                    self.clients[client_id] = {
                        'conn': conn,
                        'addr': addr,
                        'name': f"Joueur {client_id + 1}",
                        'snake': {
                            'body': [[6 + client_id * 2, 9], [5 + client_id * 2, 9], [4 + client_id * 2, 9]],
                            'direction': [1, 0],
                            'score': 0,
                            'alive': True
                        }
                    }

                # Send welcome message
                self.send_to_client(client_id, {
                    'type': 'connection',
                    'client_id': client_id,
                    'message': f'Bienvenue {self.clients[client_id]["name"]}!'
                })

                # Start client thread
                thread = threading.Thread(target=self.handle_client, args=(client_id,))
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
        except Exception as e:
            print(f"❌ Erreur serveur: {e}")
        finally:
            self.server.close()

    def handle_client(self, client_id):
        client = self.clients.get(client_id)
        if not client:
            return

        try:
            while client_id in self.clients:
                # Receive message length
                length_bytes = client['conn'].recv(4)
                if not length_bytes:
                    break

                message_length = int.from_bytes(length_bytes, byteorder='big')

                # Receive message
                message = b''
                while len(message) < message_length:
                    chunk = client['conn'].recv(min(message_length - len(message), 4096))
                    if not chunk:
                        break
                    message += chunk

                if not message:
                    break

                # Process message
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
                name = data.get('name', f"Joueur {client_id + 1}")
                self.clients[client_id]['name'] = name
                self.clients[client_id]['snake']['body'] = data.get('body', [[6, 9], [5, 9], [4, 9]])
                self.clients[client_id]['snake']['direction'] = data.get('direction', [1, 0])
                print(f"🎮 {name} a rejoint le jeu!")

            elif msg_type == 'direction':
                self.clients[client_id]['snake']['direction'] = data['direction']

    def game_loop(self):
        """Game logic loop - runs in separate thread"""
        while True:
            try:
                with self.lock:
                    # Update all snakes
                    for client_id, client_data in list(self.clients.items()):
                        if not client_data['snake']['alive']:
                            continue

                        snake = client_data['snake']
                        head = snake['body'][0]
                        direction = snake['direction']

                        # New head position
                        new_head = [
                            (head[0] + direction[0]) % 20,
                            (head[1] + direction[1]) % 20
                        ]

                        # Add new head
                        snake['body'].insert(0, new_head)

                        # Check food collisions
                        if new_head == self.game_state['food1']:
                            snake['score'] += 10
                            self.game_state['food1'] = self.generate_food_position()
                        elif new_head == self.game_state['food2']:
                            snake['score'] += 15
                            self.game_state['food2'] = self.generate_food_position()
                        else:
                            # Remove tail if no food eaten
                            snake['body'].pop()

                        # Check collisions
                        if self.check_collisions(client_id, new_head):
                            snake['alive'] = False
                            print(f"💀 {client_data['name']} est mort!")

                # Update game state
                self.update_game_state()

                # Broadcast to all clients
                self.broadcast_game_state()

                # Control game speed
                threading.Event().wait(0.1)  # 10 FPS

            except Exception as e:
                print(f"❌ Erreur game loop: {e}")
                break

    def generate_food_position(self):
        while True:
            pos = [random.randint(0, 19), random.randint(0, 19)]

            # Check if not on obstacle
            if pos in self.game_state['obstacles']:
                continue

            # Check if not on any snake
            on_snake = False
            for client_data in self.clients.values():
                if pos in client_data['snake']['body']:
                    on_snake = True
                    break

            if not on_snake:
                return pos

    def check_collisions(self, client_id, head):
        # Check obstacle collision
        if head in self.game_state['obstacles']:
            return True

        # Check collision with other snakes
        for other_id, other_data in self.clients.items():
            if other_id == client_id:
                # Skip self collision check (handled separately)
                continue
            if head in other_data['snake']['body']:
                return True

        return False

    def update_game_state(self):
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

            # Remove dead clients
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
    print("🐍 SERVEUR SNAKE HAMACHI")
    print("=" * 50)
    print("\nCe serveur permet de jouer via:")
    print("1. Réseau local (LAN)")
    print("2. Hamachi (IP 25.x.x.x)")
    print("3. Radmin VPN")
    print("4. Autres réseaux virtuels")
    print("=" * 50)

    # Configuration
    HOST = '0.0.0.0'  # Listen on all interfaces
    PORT = 5555

    print(f"\n🎮 Configuration:")
    print(f"   Hôte: {HOST}")
    print(f"   Port: {PORT}")
    print("\n⚡ Le serveur démarre...")

    server = HamachiSnakeServer(HOST, PORT)

    # Start game loop in separate thread
    game_thread = threading.Thread(target=server.game_loop)
    game_thread.daemon = True
    game_thread.start()

    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du serveur...")
        server.stop()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    main()