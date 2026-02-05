import socket
import threading
import json
import random


class HamachiSnakeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}
        self.game_state = {
            'players': {},
            'food': [[10, 10], [15, 15]],
            'obstacles': []
        }

        print("=" * 50)
        print("🐍 SERVEUR SNAKE HAMACHI")
        print("=" * 50)

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)

            print(f"✅ Serveur démarré sur le port {self.port}")
            print(f"📡 IP HAMACHI à donner à ton ami :")
            print(f"   - Regarde dans l'application Hamachi")
            print(f"   - C'est l'adresse qui commence par 25.x.x.x ou 5.x.x.x")
            print(f"   - Port : {self.port}")
            print("=" * 50)
            print("👥 En attente de joueurs...")

            while True:
                conn, addr = self.server.accept()
                print(f"✅ {addr[0]} connecté!")

                # Ajouter le client
                client_id = len(self.clients)
                self.clients[client_id] = {
                    'conn': conn,
                    'addr': addr,
                    'name': f"Joueur {client_id + 1}"
                }

                # Envoyer ID
                conn.send(json.dumps({
                    'type': 'welcome',
                    'client_id': client_id,
                    'message': 'Bienvenue dans Snake Game!'
                }).encode())

                # Démarrer thread pour ce client
                thread = threading.Thread(target=self.handle_client, args=(client_id,))
                thread.start()

        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
        finally:
            self.server.close()

    def handle_client(self, client_id):
        client = self.clients[client_id]
        try:
            while True:
                data = client['conn'].recv(1024)
                if not data:
                    break

                message = json.loads(data.decode())

                if message.get('type') == 'join':
                    client['name'] = message.get('name', client['name'])
                    print(f"🎮 {client['name']} a rejoint!")

        except:
            pass
        finally:
            print(f"👋 {client['name']} a quitté")
            if client_id in self.clients:
                del self.clients[client_id]


if __name__ == "__main__":
    server = HamachiSnakeServer('0.0.0.0', 5555)
    server.start()