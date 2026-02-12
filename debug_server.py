# Ce fichier est un SERVEUR DE DÉBOGAGE ultra-verbose.
# Rôle : Tester la communication client-serveur en détail
# Affiche TOUT ce qui se passe (connexions, messages, erreurs)
# Utilisé pendant le développement pour identifier les bugs

import socket  # Sockets TCP/IP
import threading  # Threads pour clients multiples
import json  # Encodage/décodage JSON
import time  # Horodatage
import traceback  # Affichage détaillé des erreurs


class DebugServer:
    """
    CLASSE SERVEUR DE DÉBOGAGE
    Version ultra-détaillée du serveur qui affiche :
    - Chaque connexion/déconnexion
    - Chaque message reçu (brut et décodé)
    - Chaque envoi de données
    - Les erreurs avec pile d'appels complète
    """

    def __init__(self, host='0.0.0.0', port=5555):
        """
        Constructeur : identique au serveur normal
        """
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}

        print("🐍 DEBUG SERVEUR ")

    def start(self):
        """
        MÉTHODE : Démarre le serveur de débogage
        Affiche chaque étape en détail
        """
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)

            print(f"✅ Serveur démarré sur {self.host}:{self.port}")
            print(f"📡 IP Hamachi: 25.40.67.39")
            print("👥 En attente de joueurs...")

            while True:
                # Attente de connexion
                conn, addr = self.server.accept()
                print(f"✅ NOUVELLE CONNEXION: {addr[0]}:{addr[1]}")

                client_id = len(self.clients)

                # Enregistrement du client
                self.clients[client_id] = {
                    'conn': conn,
                    'addr': addr,
                    'name': f"Joueur{client_id}",
                    'connected_at': time.time()
                }

                # Thread dédié avec affichage DEBUG
                thread = threading.Thread(target=self.handle_client_debug, args=(client_id,))
                thread.daemon = True
                thread.start()

        except Exception as e:
            print(f"❌ ERREUR SERVEUR: {e}")
            traceback.print_exc()  # Affiche la pile d'appels complète

    def handle_client_debug(self, client_id):
        """
        MÉTHODE : Version DEBUG du gestionnaire client
        Affiche ABSOLUMENT TOUT ce qui se passe
        """
        client = self.clients[client_id]
        conn = client['conn']
        addr = client['addr']

        print(f"[DEBUG] Début handle_client pour {addr}")

        try:
            # === ÉTAPE 1 : ENVOI DU WELCOME ===
            welcome_msg = json.dumps({
                'type': 'welcome',
                'client_id': client_id,
                'message': f'Bienvenue Joueur {client_id}!',
                'timestamp': time.time()
            }).encode()

            print(f"[DEBUG] Envoi welcome ({len(welcome_msg)} bytes)...")
            conn.send(welcome_msg)
            print(f"[DEBUG] Welcome envoyé à {addr}")

            # === ÉTAPE 2 : ATTENTE DU 'join' ===
            print(f"[DEBUG] Attente message 'join' de {addr}...")
            conn.settimeout(5.0)  # Timeout de 5 secondes

            try:
                data = conn.recv(4096)
                print(f"[DEBUG] Reçu {len(data)} bytes de {addr}")

                if data:
                    # Affiche les données brutes pour analyse
                    print(f"[DEBUG] Données brutes: {data[:100]}...")

                    try:
                        # Tentative de décodage JSON
                        message = json.loads(data.decode())
                        print(f"[DEBUG] Message JSON décodé: {message}")

                        if message.get('type') == 'join':
                            name = message.get('name', f'Joueur{client_id}')
                            client['name'] = name
                            print(f"🎮 {name} a rejoint avec succès!")

                            # === ENVOI D'UN ÉTAT DE JEU SIMPLE ===
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

                            # === ÉTAPE 3 : BOUCLE DE RÉCEPTION DES DIRECTIONS ===
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
                                        # Simule un accusé de réception
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
            # === NETTOYAGE ===
            duration = time.time() - client.get('connected_at', time.time())
            print(f"👋 {client.get('name', 'Inconnu')} a quitté")
            print(f"⏱️  Durée de connexion: {duration:.2f} secondes")
            print(f"📡 Adresse: {addr}")
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