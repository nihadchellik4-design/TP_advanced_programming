# debug_server.py
import socket
import threading
import json
import time
import traceback


class DebugServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}

        print("=" * 60)
        print("🐍 DEBUG SERVEUR - Version ultra verbose")
        print("=" * 60)

    def start(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)

            print(f"✅ Serveur démarré sur {self.host}:{self.port}")
            print(f"📡 IP Hamachi: 25.40.67.39")
            print("=" * 60)
            print("👥 En attente de joueurs...")

            while True:
                conn, addr = self.server.accept()
                print(f"\n" + "=" * 60)
                print(f"✅ NOUVELLE CONNEXION: {addr[0]}:{addr[1]}")
                print("=" * 60)

                client_id = len(self.clients)

                # Enregistrer le client
                self.clients[client_id] = {
                    'conn': conn,
                    'addr': addr,
                    'name': f"Joueur{client_id}",
                    'connected_at': time.time()
                }

                # Thread pour ce client
                thread = threading.Thread(target=self.handle_client_debug, args=(client_id,))
                thread.daemon = True
                thread.start()

        except Exception as e:
            print(f"❌ ERREUR SERVEUR: {e}")
            traceback.print_exc()

    def handle_client_debug(self, client_id):
        client = self.clients[client_id]
        conn = client['conn']
        addr = client['addr']

        print(f"[DEBUG] Début handle_client pour {addr}")

        try:
            # Étape 1: Envoyer le message de bienvenue
            welcome_msg = json.dumps({
                'type': 'welcome',
                'client_id': client_id,
                'message': f'Bienvenue Joueur {client_id}!',
                'timestamp': time.time()
            }).encode()

            print(f"[DEBUG] Envoi welcome ({len(welcome_msg)} bytes)...")
            conn.send(welcome_msg)
            print(f"[DEBUG] Welcome envoyé à {addr}")

            # Étape 2: Attendre le message 'join' du client
            print(f"[DEBUG] Attente message 'join' de {addr}...")
            conn.settimeout(5.0)  # Timeout de 5 secondes

            try:
                data = conn.recv(4096)
                print(f"[DEBUG] Reçu {len(data)} bytes de {addr}")

                if data:
                    print(f"[DEBUG] Données brutes: {data[:100]}...")

                    try:
                        message = json.loads(data.decode())
                        print(f"[DEBUG] Message JSON décodé: {message}")

                        if message.get('type') == 'join':
                            name = message.get('name', f'Joueur{client_id}')
                            client['name'] = name
                            print(f"🎮 {name} a rejoint avec succès!")

                            # Envoyer un état de jeu simple
                            game_state = {
                                'type': 'state',
                                'game_state': {
                                    'players': {
                                        client_id: {
                                            'name': name,
                                            'body': [[6, 9], [5, 9], [4, 9]],
                                            'score': 0,
                                            'direction': [1, 0]
                                        }
                                    },
                                    'food1': [10, 10],
                                    'food2': [15, 15],
                                    'obstacles': []
                                }
                            }

                            state_msg = json.dumps(game_state).encode()
                            print(f"[DEBUG] Envoi state ({len(state_msg)} bytes)...")
                            conn.send(state_msg)
                            print(f"[DEBUG] State envoyé à {name}")

                            # Maintenant attendre les commandes de direction
                            print(f"[DEBUG] Attente commandes de {name}...")
                            conn.settimeout(None)  # Pas de timeout

                            while True:
                                data = conn.recv(4096)
                                if not data:
                                    print(f"[DEBUG] {name}: Aucune donnée (déconnexion?)")
                                    break

                                print(f"[DEBUG] {name}: Reçu {len(data)} bytes")
                                print(f"[DEBUG] {name}: Données: {data[:50]}...")

                                try:
                                    msg = json.loads(data.decode())
                                    print(f"[DEBUG] {name}: Message: {msg}")

                                    if msg.get('type') == 'direction':
                                        print(f"[DEBUG] {name}: Direction: {msg['direction']}")
                                        # Simuler un retour
                                        response = json.dumps({
                                            'type': 'ack',
                                            'message': 'Direction reçue',
                                            'timestamp': time.time()
                                        }).encode()
                                        conn.send(response)

                                except json.JSONDecodeError as e:
                                    print(f"[DEBUG] {name}: Erreur JSON: {e}")
                                    print(f"[DEBUG] {name}: Données brutes: {data}")

                        else:
                            print(f"[DEBUG] {addr}: Mauvais type de message: {message.get('type')}")

                    except json.JSONDecodeError as e:
                        print(f"[DEBUG] {addr}: Impossible de décoder JSON: {e}")
                        print(f"[DEBUG] {addr}: Données reçues: {data}")

                else:
                    print(f"[DEBUG] {addr}: Aucune donnée reçue (connexion fermée?)")

            except socket.timeout:
                print(f"[DEBUG] {addr}: Timeout en attente du message 'join'")
            except ConnectionResetError:
                print(f"[DEBUG] {addr}: Connexion réinitialisée par le pair")
            except Exception as e:
                print(f"[DEBUG] {addr}: Erreur lors de la réception: {e}")
                traceback.print_exc()

        except Exception as e:
            print(f"[DEBUG] {addr}: Erreur générale: {e}")
            traceback.print_exc()

        finally:
            # Nettoyage
            duration = time.time() - client.get('connected_at', time.time())
            print(f"\n" + "=" * 60)
            print(f"👋 {client.get('name', 'Inconnu')} a quitté")
            print(f"⏱️  Durée de connexion: {duration:.2f} secondes")
            print(f"📡 Adresse: {addr}")
            print("=" * 60)

            try:
                conn.close()
            except:
                pass

            if client_id in self.clients:
                del self.clients[client_id]


if __name__ == "__main__":
    print("Lancement du serveur de debug...")
    server = DebugServer('0.0.0.0', 5555)
    server.start()