import socket
import threading
import json
import pygame
from pygame.math import Vector2
import random

# Modern Color Palette
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

# Network Client Class
class NetworkClient:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.client_id = None
        self.game_state = {
            'players': {}, 
            'food1': None, 
            'food2': None, 
            'obstacles': []
        }
        self.connected = False
        
    def connect(self):
        """Connect to server"""
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            print(f"✅ Connected to {self.host}:{self.port}")
            
            threading.Thread(target=self.receive, daemon=True).start()
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def send(self, data):
        """Send data to server"""
        try:
            message = json.dumps(data).encode('utf-8')
            message_length = len(message).to_bytes(4, byteorder='big')
            self.client.sendall(message_length + message)
        except Exception as e:
            print(f"❌ Send error: {e}")
            self.connected = False
    
    def receive(self):
        """Receive data from server"""
        while self.connected:
            try:
                length_bytes = self.client.recv(4)
                if not length_bytes:
                    break
                
                message_length = int.from_bytes(length_bytes, byteorder='big')
                
                message = b''
                while len(message) < message_length:
                    chunk = self.client.recv(min(message_length - len(message), 4096))
                    if not chunk:
                        break
                    message += chunk
                
                data = json.loads(message.decode('utf-8'))
                self.process_message(data)
                
            except Exception as e:
                print(f"❌ Receive error: {e}")
                self.connected = False
                break
    
    def process_message(self, data):
        """Process messages from server"""
        msg_type = data.get('type')
        
        if msg_type == 'connection':
            self.client_id = data['client_id']
            print(f"🆔 Assigned ID: {self.client_id}")
        
        elif msg_type == 'state':
            self.game_state = data['game_state']


class MultiplayerGame:
    def __init__(self, network_client, player_name):
        self.network = network_client
        self.player_name = player_name
        
        pygame.init()
        self.cell_size = 20
        self.number_of_cells = 20
        self.OFFSET = 75
        
        self.screen = pygame.display.set_mode(
            (2*self.OFFSET + self.cell_size * self.number_of_cells, 
             2*self.OFFSET + self.cell_size * self.number_of_cells)
        )
        pygame.display.set_caption("🐍 Snake Game - Multiplayer")
        
        # Initialize local player - Server will manage movement
        self.my_direction = [1, 0]
        
        # Send join message
        self.network.send({
            'type': 'join',
            'name': player_name,
            'body': [[6, 9], [5, 9], [4, 9]],
            'direction': self.my_direction
        })
        
        self.title_font = pygame.font.Font(None, 70)
        self.score_font = pygame.font.Font(None, 45)
        self.small_font = pygame.font.Font(None, 28)
        self.info_font = pygame.font.Font(None, 32)
        
        # Load sounds
        try:
            self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
        except:
            self.eat_sound = None
            print("⚠️ Eat sound not found")
        
        self.last_score = 0
    
    def handle_input(self):
        """Handle keyboard input for snake direction"""
        keys = pygame.key.get_pressed()
        new_direction = None
        
        if keys[pygame.K_UP] and self.my_direction != [0, 1]:
            new_direction = [0, -1]
        elif keys[pygame.K_DOWN] and self.my_direction != [0, -1]:
            new_direction = [0, 1]
        elif keys[pygame.K_LEFT] and self.my_direction != [1, 0]:
            new_direction = [-1, 0]
        elif keys[pygame.K_RIGHT] and self.my_direction != [-1, 0]:
            new_direction = [1, 0]
        
        if new_direction:
            self.my_direction = new_direction
            self.network.send({
                'type': 'direction',
                'direction': new_direction
            })
    
    def draw(self):
        """Draw game state with modern design"""
        # Gradient background
        for y in range(2*self.OFFSET + self.cell_size * self.number_of_cells):
            ratio = y / (2*self.OFFSET + self.cell_size * self.number_of_cells)
            r = int(46 + (39 - 46) * ratio)
            g = int(204 + (174 - 204) * ratio)
            b = int(113 + (96 - 113) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), 
                           (2*self.OFFSET + self.cell_size * self.number_of_cells, y))
        
        # Game border
        pygame.draw.rect(self.screen, TEXT_DARK, 
                        (self.OFFSET-7, self.OFFSET-7, 
                         self.cell_size*self.number_of_cells+14, 
                         self.cell_size*self.number_of_cells+14),
                        border_radius=10)
        pygame.draw.rect(self.screen, BG_DARK, 
                        (self.OFFSET-5, self.OFFSET-5, 
                         self.cell_size*self.number_of_cells+10, 
                         self.cell_size*self.number_of_cells+10), 
                        5, border_radius=8)
        
        game_state = self.network.game_state
        
        # Draw food
        if game_state.get('food1'):
            food_rect = pygame.Rect(
                self.OFFSET + game_state['food1'][0] * self.cell_size,
                self.OFFSET + game_state['food1'][1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.circle(self.screen, RED, food_rect.center, self.cell_size // 2)
            # Highlight
            pygame.draw.circle(self.screen, WHITE, 
                             (food_rect.centerx - 3, food_rect.centery - 3), 3)
        
        if game_state.get('food2'):
            food_rect = pygame.Rect(
                self.OFFSET + game_state['food2'][0] * self.cell_size,
                self.OFFSET + game_state['food2'][1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.circle(self.screen, ORANGE, food_rect.center, self.cell_size // 2)
            # Highlight
            pygame.draw.circle(self.screen, WHITE,
                             (food_rect.centerx - 3, food_rect.centery - 3), 3)
        
        # Draw obstacles
        for obstacle in game_state.get('obstacles', []):
            obs_rect = pygame.Rect(
                self.OFFSET + obstacle[0] * self.cell_size,
                self.OFFSET + obstacle[1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, BRICK_RED, obs_rect, border_radius=4)
            pygame.draw.rect(self.screen, BRICK_DARK, obs_rect, 2, border_radius=4)
        
        # Draw all players
        for player_id, player_data in game_state.get('players', {}).items():
            is_me = (player_id == self.network.client_id)
            
            # Check if score increased (food eaten)
            if is_me and self.eat_sound:
                current_score = player_data.get('score', 0)
                if current_score > self.last_score:
                    self.eat_sound.play()
                self.last_score = current_score
            
            for i, segment in enumerate(player_data['body']):
                seg_rect = pygame.Rect(
                    self.OFFSET + segment[0] * self.cell_size,
                    self.OFFSET + segment[1] * self.cell_size,
                    self.cell_size, 
                    self.cell_size
                )
                
                # Choose color based on player
                if is_me:
                    color = SNAKE_MY_HEAD if i == 0 else SNAKE_MY_COLOR
                else:
                    color = SNAKE_OTHER_HEAD if i == 0 else SNAKE_OTHER_COLOR
                
                pygame.draw.rect(self.screen, color, seg_rect, border_radius=7)
                
                # Add shine to head
                if i == 0:
                    shine_rect = pygame.Rect(seg_rect.x + 4, seg_rect.y + 4, 6, 6)
                    pygame.draw.rect(self.screen, WHITE, shine_rect, border_radius=3)
            
            # Draw player name tag
            if player_data.get('name'):
                head = player_data['body'][0]
                name_text = f"{player_data['name']}"
                score_text = f"({player_data.get('score', 0)})"
                
                # Background for name
                name_surface = self.small_font.render(name_text, True, WHITE)
                score_surface = self.small_font.render(score_text, True, GOLD)
                
                name_x = self.OFFSET + head[0] * self.cell_size
                name_y = self.OFFSET + head[1] * self.cell_size - 25
                
                # Draw name background
                bg_rect = pygame.Rect(name_x - 5, name_y - 2, 
                                     name_surface.get_width() + score_surface.get_width() + 15, 
                                     name_surface.get_height() + 4)
                pygame.draw.rect(self.screen, UI_BG, bg_rect, border_radius=4)
                
                self.screen.blit(name_surface, (name_x, name_y))
                self.screen.blit(score_surface, (name_x + name_surface.get_width() + 5, name_y))
        
        # Draw UI title
        title_shadow = self.title_font.render("MULTIPLAYER", True, TEXT_DARK)
        title_surface = self.title_font.render("MULTIPLAYER", True, WHITE)
        self.screen.blit(title_shadow, (self.OFFSET-3, 18))
        self.screen.blit(title_surface, (self.OFFSET-5, 15))
        
        # Get my score from server
        my_score = 0
        if self.network.client_id in game_state.get('players', {}):
            my_score = game_state['players'][self.network.client_id].get('score', 0)
        
        # Score display
        score_bg_rect = pygame.Rect(self.OFFSET-10, 
                                    self.OFFSET + self.cell_size*self.number_of_cells+5, 
                                    220, 50)
        pygame.draw.rect(self.screen, UI_BG, score_bg_rect, border_radius=8)
        score_surface = self.score_font.render(f"Score: {my_score}", True, GOLD)
        self.screen.blit(score_surface, 
                        (self.OFFSET, self.OFFSET + self.cell_size*self.number_of_cells+15))
        
        # Players count
        players_text = self.info_font.render(
            f"Players: {len(game_state.get('players', {}))}", 
            True, 
            WHITE
        )
        self.screen.blit(players_text, 
                        (self.OFFSET + 240, self.OFFSET + self.cell_size*self.number_of_cells+20))
        
        pygame.display.update()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running and self.network.connected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    self.handle_input()
            
            self.draw()
            clock.tick(60)
        
        pygame.quit()


def get_connection_info():
    """Get server connection information"""
    pygame.init()
    screen = pygame.display.set_mode((700, 500))
    pygame.display.set_caption("🌐 Multiplayer Connection")
    
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    server_ip = "localhost"
    server_port = "5555"
    player_name = ""
    active_field = "ip"
    
    clock = pygame.time.Clock()
    
    while True:
        # Gradient background
        for y in range(500):
            ratio = y / 500
            r = int(52 + (44 - 52) * ratio)
            g = int(152 + (62 - 152) * ratio)
            b = int(219 + (80 - 219) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (700, y))
        
        # Title
        title = font.render("🌐 MULTIPLAYER", True, WHITE)
        title_rect = title.get_rect(center=(350, 50))
        screen.blit(title, title_rect)
        
        subtitle = small_font.render("Enter Connection Info", True, (189, 195, 199))
        subtitle_rect = subtitle.get_rect(center=(350, 100))
        screen.blit(subtitle, subtitle_rect)
        
        # Server IP field
        ip_label = small_font.render("Server IP:", True, WHITE)
        screen.blit(ip_label, (100, 150))
        
        ip_color = WHITE if active_field == "ip" else (149, 165, 166)
        pygame.draw.rect(screen, UI_BG, (100, 180, 500, 45), border_radius=8)
        pygame.draw.rect(screen, ip_color, (100, 180, 500, 45), 3, border_radius=8)
        ip_text = small_font.render(server_ip, True, WHITE)
        screen.blit(ip_text, (115, 192))
        
        # Server Port field
        port_label = small_font.render("Server Port:", True, WHITE)
        screen.blit(port_label, (100, 250))
        
        port_color = WHITE if active_field == "port" else (149, 165, 166)
        pygame.draw.rect(screen, UI_BG, (100, 280, 500, 45), border_radius=8)
        pygame.draw.rect(screen, port_color, (100, 280, 500, 45), 3, border_radius=8)
        port_text = small_font.render(server_port, True, WHITE)
        screen.blit(port_text, (115, 292))
        
        # Player Name field
        name_label = small_font.render("Your Name:", True, WHITE)
        screen.blit(name_label, (100, 350))
        
        name_color = WHITE if active_field == "name" else (149, 165, 166)
        pygame.draw.rect(screen, UI_BG, (100, 380, 500, 45), border_radius=8)
        pygame.draw.rect(screen, name_color, (100, 380, 500, 45), 3, border_radius=8)
        name_text = small_font.render(player_name, True, WHITE)
        screen.blit(name_text, (115, 392))
        
        # Instructions
        inst_font = pygame.font.Font(None, 24)
        inst_text = inst_font.render("Press ENTER to Connect | TAB to switch", True, (189, 195, 199))
        screen.blit(inst_text, (160, 450))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 100 <= mouse_pos[0] <= 600:
                    if 180 <= mouse_pos[1] <= 225:
                        active_field = "ip"
                    elif 280 <= mouse_pos[1] <= 325:
                        active_field = "port"
                    elif 380 <= mouse_pos[1] <= 425:
                        active_field = "name"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if server_ip and server_port and player_name:
                        pygame.quit()
                        return server_ip, int(server_port), player_name
                elif event.key == pygame.K_TAB:
                    if active_field == "ip":
                        active_field = "port"
                    elif active_field == "port":
                        active_field = "name"
                    else:
                        active_field = "ip"
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "ip":
                        server_ip = server_ip[:-1]
                    elif active_field == "port":
                        server_port = server_port[:-1]
                    else:
                        player_name = player_name[:-1]
                else:
                    if active_field == "ip" and len(server_ip) < 30:
                        server_ip += event.unicode
                    elif active_field == "port" and len(server_port) < 10 and event.unicode.isdigit():
                        server_port += event.unicode
                    elif active_field == "name" and len(player_name) < 20:
                        player_name += event.unicode
        
        clock.tick(30)


def main():
    print("=" * 50)
    print("🐍 SNAKE GAME - MULTIPLAYER CLIENT")
    print("=" * 50)
    
    # Get connection info
    server_host, server_port, player_name = get_connection_info()
    
    # Connect to server
    network = NetworkClient(server_host, server_port)
    if network.connect():
        # Start game
        game = MultiplayerGame(network, player_name)
        game.run()
    else:
        print("❌ Could not connect to server")


if __name__ == "__main__":
    main()