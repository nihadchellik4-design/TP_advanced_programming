import socket
import threading
import json
import time
import random
from collections import defaultdict

class SnakeServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        self.clients = {}  # {client_id: socket}
        self.number_of_cells = 20
        self.game_state = {
            'players': {},  # {client_id: {name, body, direction, score}}
            'food1': None,
            'food2': None,
            'obstacles': []
        }
        self.client_counter = 0
        self.lock = threading.Lock()
        
        # Initialize food and obstacles AFTER number_of_cells is set
        self.game_state['food1'] = self.generate_food_position()
        self.game_state['food2'] = self.generate_food_position()
        self.game_state['obstacles'] = self.generate_obstacles()
        
    def generate_food_position(self):
        """Generate random food position"""
        return [random.randint(0, self.number_of_cells - 1), 
                random.randint(0, self.number_of_cells - 1)]
    
    def generate_obstacles(self):
        """Generate obstacles"""
        obstacles = []
        for _ in range(5):
            obstacles.append([
                random.randint(0, self.number_of_cells - 1),
                random.randint(0, self.number_of_cells - 1)
            ])
        return obstacles
        
    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"[SERVER] Listening on {self.host}:{self.port}")
        
        # Start game update thread
        threading.Thread(target=self.game_loop, daemon=True).start()
        
        while True:
            try:
                client_socket, address = self.server.accept()
                print(f"[NEW CONNECTION] {address}")
                
                client_id = self.client_counter
                self.client_counter += 1
                
                thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, client_id, address)
                )
                thread.start()
            except Exception as e:
                print(f"[ERROR] {e}")
    
    def handle_client(self, client_socket, client_id, address):
        """Handle individual client connection"""
        with self.lock:
            self.clients[client_id] = client_socket
        
        try:
            # Send client their ID
            self.send_message(client_socket, {
                'type': 'connection',
                'client_id': client_id
            })
            
            while True:
                data = self.receive_message(client_socket)
                if not data:
                    break
                
                self.process_client_message(client_id, data)
                
        except Exception as e:
            print(f"[ERROR] Client {client_id}: {e}")
        finally:
            self.disconnect_client(client_id)
            print(f"[DISCONNECTED] Client {client_id} from {address}")
    
    def process_client_message(self, client_id, data):
        """Process messages from clients"""
        msg_type = data.get('type')
        
        if msg_type == 'join':
            with self.lock:
                self.game_state['players'][client_id] = {
                    'name': data['name'],
                    'body': data['body'],
                    'direction': data['direction'],
                    'score': 0,
                    'alive': True
                }
                print(f"[JOIN] {data['name']} joined as client {client_id}")
        
        elif msg_type == 'update':
            with self.lock:
                if client_id in self.game_state['players']:
                    player = self.game_state['players'][client_id]
                    player.update(data['player'])
                    
                    # Check food collision
                    head = player['body'][0]
                    
                    if head == self.game_state['food1']:
                        player['score'] += 10
                        self.game_state['food1'] = self.generate_food_position()
                        print(f"[FOOD] {player['name']} ate food1! Score: {player['score']}")
                    
                    if head == self.game_state['food2']:
                        player['score'] += 15
                        self.game_state['food2'] = self.generate_food_position()
                        print(f"[FOOD] {player['name']} ate food2! Score: {player['score']}")
                    
                    # Check obstacle collision
                    if head in self.game_state['obstacles']:
                        print(f"[COLLISION] {player['name']} hit obstacle!")
                        player['alive'] = False
        
        elif msg_type == 'direction':
            with self.lock:
                if client_id in self.game_state['players']:
                    self.game_state['players'][client_id]['direction'] = data['direction']
    
    def game_loop(self):
        """Main game loop - broadcasts state to all clients"""
        while True:
            time.sleep(0.2)  # 5 updates per second
            
            with self.lock:
                # Broadcast game state to all clients
                state_message = {
                    'type': 'state',
                    'game_state': self.game_state
                }
                
                for client_id, client_socket in list(self.clients.items()):
                    try:
                        self.send_message(client_socket, state_message)
                    except:
                        self.disconnect_client(client_id)
    
    def disconnect_client(self, client_id):
        """Remove disconnected client"""
        with self.lock:
            if client_id in self.clients:
                try:
                    self.clients[client_id].close()
                except:
                    pass
                del self.clients[client_id]
            
            if client_id in self.game_state['players']:
                del self.game_state['players'][client_id]
    
    def send_message(self, client_socket, data):
        """Send JSON message to client"""
        message = json.dumps(data).encode('utf-8')
        message_length = len(message).to_bytes(4, byteorder='big')
        client_socket.sendall(message_length + message)
    
    def receive_message(self, client_socket):
        """Receive JSON message from client"""
        # First receive message length (4 bytes)
        length_bytes = client_socket.recv(4)
        if not length_bytes:
            return None
        
        message_length = int.from_bytes(length_bytes, byteorder='big')
        
        # Then receive the actual message
        message = b''
        while len(message) < message_length:
            chunk = client_socket.recv(min(message_length - len(message), 4096))
            if not chunk:
                return None
            message += chunk
        
        return json.loads(message.decode('utf-8'))


if __name__ == "__main__":
    server = SnakeServer()
    server.start()