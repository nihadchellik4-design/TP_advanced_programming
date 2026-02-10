# test_client.py
import socket
import json
import time

SERVER_IP = "25.40.67.39"
SERVER_PORT = 5555

print("=" * 50)
print("🧪 CLIENT DE TEST ULTRA SIMPLE")
print("=" * 50)
print(f"Connexion à {SERVER_IP}:{SERVER_PORT}")

try:
    # 1. Connexion
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((SERVER_IP, SERVER_PORT))
    print("✅ Connecté au serveur")

    # 2. Recevoir le welcome
    print("📥 Attente du message de bienvenue...")
    data = sock.recv(4096)
    if data:
        print(f"📥 Reçu {len(data)} bytes")
        try:
            welcome = json.loads(data.decode())
            print(f"🎉 Message de bienvenue: {welcome}")

            client_id = welcome.get('client_id', 0)

            # 3. Envoyer join
            join_msg = {
                'type': 'join',
                'name': 'Testeur',
                'timestamp': time.time()
            }
            sock.send(json.dumps(join_msg).encode())
            print("📤 Envoyé: join")

            # 4. Attendre l'état du jeu
            print("📥 Attente de l'état du jeu...")
            data = sock.recv(4096)
            if data:
                print(f"📥 Reçu {len(data)} bytes (état)")
                try:
                    state = json.loads(data.decode())
                    print(f"🎮 État du jeu reçu! Type: {state.get('type')}")

                    # 5. Envoyer quelques directions
                    for i in range(5):
                        direction = {
                            'type': 'direction',
                            'direction': [1, 0],
                            'sequence': i
                        }
                        sock.send(json.dumps(direction).encode())
                        print(f"📤 Direction {i} envoyée")

                        # Attendre un peu
                        time.sleep(1)

                        # Essayer de recevoir une réponse
                        sock.settimeout(0.5)
                        try:
                            resp = sock.recv(4096)
                            if resp:
                                print(f"📥 Réponse: {len(resp)} bytes")
                        except socket.timeout:
                            print("⏱️  Pas de réponse (timeout)")
                        except:
                            pass

                except json.JSONDecodeError as e:
                    print(f"❌ Erreur JSON état: {e}")
                    print(f"Données: {data}")
            else:
                print("❌ Pas d'état reçu")

        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON welcome: {e}")
            print(f"Données: {data}")
    else:
        print("❌ Pas de welcome reçu")

except ConnectionRefusedError:
    print("❌ Connexion refusée - Le serveur est-il lancé?")
except socket.timeout:
    print("❌ Timeout de connexion")
except Exception as e:
    print(f"❌ Erreur: {e}")

finally:
    print("\n" + "=" * 50)
    print("Fin du test")
    print("=" * 50)
    try:
        sock.close()
        print("Socket fermé")
    except:
        pass

input("Appuyez sur Entrée pour quitter...")