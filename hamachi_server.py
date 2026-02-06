# hamachi_server_fixed.py
import socket
import threading
import json
import random
import struct


class FixedHamachiServer:
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

        print("=" * 50)
        print("🐍 SERVEUR HAMACHI CORRIGÉ")
        print("=" * 50)
        print(f"IP: {self.get_hamachi_ip()}")
        print(f"Port: {self.port}")
        print("=" * 50)

    def get_hamachi_ip(self):
        """Retourne votre IP Hamachi"""
        return "25.40.67.39"  # Remplacez par votre IP si différente

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)

            print(f"✅ Serveur démarré sur {self.host}:{self.port}")
            print(f"📡 IP à donner: {self.get_hamachi_ip()}")
            print("👥 En attente de joueurs...")

            while True:
                conn, addr = self.server.accept()
                print(f"✅ {addr[0]} connecté!")

                client_id = len(self.clients)
                self.clients[client_id] = {
                    'conn': conn,
                    'addr': addr,
                    'name': f"Joueur {client_id + 1}",
                    'snake': {
                        'body': [[6, 9], [5, 9], [4, 9]],
                        'direction': [1, 0],
                        'score': 0
                    }
                }

                # Envoyer message de bienvenue SIMPLE (sans longueur)
                conn.send(json.dumps({
                    'type': 'welcome',
                    'client_id': client_id,
                    'message': 'Bienvenue!'
                }).encode())

                # Démarrer thread pour ce client
                thread = threading.Thread(target=self.handle_client, args=(client_id,))
                thread.daemon = True
                thread.start()

        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
        finally:
            self.server.close()

    def handle_client(self, client_id):
        client = self.clients[client_id]
        conn = client['conn']

        try:
            while True:
                try:
                    # Essayer de recevoir des données
                    data = conn.recv(4096)
                    if not data:
                        break

                    # Essayer de décoder le JSON
                    try:
                        message = json.loads(data.decode())
                        self.process_message(client_id, message)
                    except json.JSONDecodeError:
                        # Peut-être un message avec longueur, essayer de le parser
                        try:
                            if len(data) >= 4:
                                # Essayer d'extraire la longueur
                                message_length = struct.unpack('>I', data[:4])[0]
                                if len(data) >= 4 + message_length:
                                    message_data = data[4:4 + message_length]
                                    message = json.loads(message_data.decode())
                                    self.process_message(client_id, message)
                        except:
                            print(f"Message non reconnu de {client['name']}")
                            continue

                except ConnectionResetError:
                    break
                except Exception as e:
                    print(f"Erreur avec {client['name']}: {e}")
                    break

        except Exception as e:
            print(f"❌ Erreur client {client_id}: {e}")
        finally:
            self.remove_client(client_id)

    def process_message(self, client_id, message):
        msg_type = message.get('type')

        if msg_type == 'join':
            name = message.get('name', f"Joueur {client_id + 1}")
            self.clients[client_id]['name'] = name
            print(f"🎮 {name} a rejoint!")

            # Envoyer l'état initial
            self.send_game_state(client_id)

        elif msg_type == 'direction':
            self.clients[client_id]['snake']['direction'] = message['direction']

            # Mettre à jour la position
            self.update_snake(client_id)

            # Envoyer l'état mis à jour à tous
            self.broadcast_game_state()

    def update_snake(self, client_id):
        snake = self.clients[client_id]['snake']
        head = snake['body'][0]
        direction = snake['direction']

        # Nouvelle tête
        new_head = [
            (head[0] + direction[0]) % 20,
            (head[1] + direction[1]) % 20
        ]

        # Ajouter nouvelle tête
        snake['body'].insert(0, new_head)

        # Vérifier nourriture
        if new_head == self.game_state['food1']:
            snake['score'] += 10
            self.game_state['food1'] = self.generate_food_position()
        elif new_head == self.game_state['food2']:
            snake['score'] += 15
            self.game_state['food2'] = self.generate_food_position()
        else:
            # Retirer queue si pas mangé
            snake['body'].pop()

    def generate_food_position(self):
        while True:
            pos = [random.randint(0, 19), random.randint(0, 19)]

            # Vérifier qu'elle n'est pas sur un obstacle
            if pos in self.game_state['obstacles']:
                continue

            # Vérifier qu'elle n'est pas sur un serpent
            on_snake = False
            for client_id, client in self.clients.items():
                if pos in client['snake']['body']:
                    on_snake = True
                    break

            if not on_snake:
                return pos

    def send_game_state(self, client_id):
        if client_id in self.clients:
            try:
                # Préparer l'état du jeu
                game_state = self.prepare_game_state()

                # Envoyer au format simple (sans longueur)
                message = json.dumps({
                    'type': 'state',
                    'game_state': game_state
                }).encode()

                self.clients[client_id]['conn'].send(message)
            except:
                self.remove_client(client_id)

    def broadcast_game_state(self):
        game_state = self.prepare_game_state()

        message = json.dumps({
            'type': 'state',
            'game_state': game_state
        }).encode()

        dead_clients = []
        for client_id, client in self.clients.items():
            try:
                client['conn'].send(message)
            except:
                dead_clients.append(client_id)

        # Supprimer les clients morts
        for client_id in dead_clients:
            self.remove_client(client_id)

    def prepare_game_state(self):
        # Préparer l'état avec tous les joueurs
        players = {}
        for client_id, client in self.clients.items():
            players[client_id] = {
                'name': client['name'],
                'body': client['snake']['body'],
                'score': client['snake']['score'],
                'direction': client['snake']['direction']
            }

        return {
            'players': players,
            'food1': self.game_state['food1'],
            'food2': self.game_state['food2'],
            'obstacles': self.game_state['obstacles']
        }

    def remove_client(self, client_id):
        if client_id in self.clients:
            name = self.clients[client_id]['name']
            try:
                self.clients[client_id]['conn'].close()
            except:
                pass
            del self.clients[client_id]
            print(f"👋 {name} a quitté le jeu")


if __name__ == "__main__":
    print("=" * 50)
    print("🐍 SNAKE HAMACHI - SERVEUR SIMPLIFIÉ")
    print("=" * 50)
    print("Ce serveur est compatible avec l'ancien client.")
    print("\nInstructions:")
    print("1. Les autres doivent lancer snake_client.py")
    print("2. Entrer l'IP: 25.40.67.39")
    print("3. Port: 5555")
    print("=" * 50)

    server = FixedHamachiServer('0.0.0.0', 5555)
    server.start()
