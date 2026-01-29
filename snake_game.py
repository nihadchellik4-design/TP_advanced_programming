import sys
import random
import pygame
from pygame.math import Vector2
import json
import os

pygame.init()

# Modern Color Palette
BG_LIGHT = (46, 204, 113)      # Modern green
BG_DARK = (39, 174, 96)         # Darker green
SNAKE_COLOR = (22, 160, 133)    # Teal for snake
SNAKE_HEAD = (26, 188, 156)     # Lighter teal for head
RED = (231, 76, 60)             # Modern red
ORANGE = (230, 126, 34)         # Orange for special food
WHITE = (236, 240, 241)         # Off-white
BLACK = (44, 62, 80)            # Dark blue-gray
GOLD = (241, 196, 15)           # Modern gold
BRICK_RED = (192, 57, 43)
BRICK_DARK = (169, 50, 38)
BRICK_LIGHT = (205, 97, 85)
TEXT_DARK = (44, 62, 80)
UI_BG = (52, 73, 94)

title_font = pygame.font.Font(None, 70)
score_font = pygame.font.Font(None, 45)
info_font = pygame.font.Font(None, 32)

cell_size = 20
number_of_cells = 20
OFFSET = 75

FOOD_TYPES = {
    'apple': {'image': 'snake_food.png', 'points': 10},
    'mushroom': {'image': 'snake_game2.png', 'points': 15}
}

class PlayerManager:
    def __init__(self):
        self.scores_file = 'scores.json'
        self.load_scores()
    
    def load_scores(self):
        if os.path.exists(self.scores_file):
            with open(self.scores_file, 'r') as f:
                self.scores = json.load(f)
        else:
            self.scores = {}
    
    def save_score(self, player_id, player_name, score):
        player_key = f"{player_id}_{player_name}"
        if player_key not in self.scores or score > self.scores[player_key]['score']:
            self.scores[player_key] = {
                'id': player_id,
                'name': player_name,
                'score': score
            }
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f, indent=4)
    
    def get_player_high_score(self, player_id, player_name):
        player_key = f"{player_id}_{player_name}"
        if player_key in self.scores:
            return self.scores[player_key]['score']
        return None


class Food:
    def __init__(self, snake_body, obstacles_positions=None, food_type=None, existing_food_positions=None):
        self.obstacles_positions = obstacles_positions or []
        self.existing_food_positions = existing_food_positions or []
        self.food_type = food_type if food_type else random.choice(list(FOOD_TYPES.keys()))
        self.position = self.generate_random_pos(snake_body)
        self.load_image()
    
    def load_image(self):
        try:
            image_path = FOOD_TYPES[self.food_type]['image']
            self.surface = pygame.image.load(image_path)
            self.surface = pygame.transform.scale(self.surface, (cell_size, cell_size))
        except:
            # Create a colored circle as fallback
            self.surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            color = RED if self.food_type == 'apple' else ORANGE
            pygame.draw.circle(self.surface, color, (cell_size//2, cell_size//2), cell_size//2)

    def draw(self, screen):
        food_rec = pygame.Rect(OFFSET + self.position.x * cell_size, 
                               OFFSET + self.position.y * cell_size, 
                               cell_size, cell_size)
        screen.blit(self.surface, food_rec)

    def generate_random_cell(self):
        x = random.randint(0, number_of_cells - 1)
        y = random.randint(0, number_of_cells - 1)
        return Vector2(x, y)

    def generate_random_pos(self, snake_body):
        position = self.generate_random_cell()
        while (position in snake_body or 
               position in self.obstacles_positions or 
               position in self.existing_food_positions):
            position = self.generate_random_cell()
        return position
    
    def get_points(self):
        return FOOD_TYPES[self.food_type]['points']


class Obstacle:
    def __init__(self, position):
        self.position = position
    
    def draw(self, screen):
        x = OFFSET + self.position.x * cell_size
        y = OFFSET + self.position.y * cell_size
        
        obstacle_rect = pygame.Rect(x, y, cell_size, cell_size)
        pygame.draw.rect(screen, BRICK_RED, obstacle_rect, border_radius=4)
        
        # Add brick pattern
        brick_height = cell_size // 3
        brick_width = cell_size // 2
        
        pygame.draw.rect(screen, BRICK_DARK, (x, y, brick_width - 1, brick_height - 1))
        pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y, brick_width - 1, brick_height - 1))
        pygame.draw.rect(screen, BRICK_LIGHT, (x, y + brick_height, cell_size, brick_height - 1))
        pygame.draw.rect(screen, BRICK_DARK, (x, y + 2 * brick_height, brick_width - 1, brick_height))
        pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y + 2 * brick_height, brick_width - 1, brick_height))
        
        pygame.draw.rect(screen, BRICK_DARK, obstacle_rect, 2, border_radius=4)


class Snake:
    def __init__(self):
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        try:
            self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
            self.wall_hit_sound = pygame.mixer.Sound("snake_collision.wav")
        except:
            self.eat_sound = None
            self.wall_hit_sound = None
            print("⚠️ Sound files not found")
    
    def draw(self, screen):
        for i, seg in enumerate(self.snake_body):
            seg_rect = pygame.Rect(OFFSET + seg.x * cell_size,
                                   OFFSET + seg.y * cell_size, 
                                   cell_size, cell_size)
            # Head is lighter
            color = SNAKE_HEAD if i == 0 else SNAKE_COLOR
            pygame.draw.rect(screen, color, seg_rect, border_radius=7)
            
            # Add shine effect to head
            if i == 0:
                shine_rect = pygame.Rect(seg_rect.x + 4, seg_rect.y + 4, 6, 6)
                pygame.draw.rect(screen, WHITE, shine_rect, border_radius=3)

    def update(self):
        new_head = self.snake_body[0] + self.direction
        new_head.x = new_head.x % number_of_cells
        new_head.y = new_head.y % number_of_cells
        
        self.snake_body.insert(0, new_head)
        if self.add_segment == True:
            self.add_segment = False
        else:
            self.snake_body = self.snake_body[:-1]
    
    def reset(self):
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
    
    def check_collision_with_obstacles(self, obstacles):
        for obstacle in obstacles:
            if self.snake_body[0] == obstacle.position:
                return True
        return False


class Game:
    def __init__(self, player_id, player_name):
        self.player_id = player_id
        self.player_name = player_name
        self.player_manager = PlayerManager()
        
        self.snake = Snake()
        self.state = "RUNNING"
        self.score = 0
        self.obstacles = self.generate_obstacles()
        self.obstacles_positions = [obs.position for obs in self.obstacles]
        
        self.food1 = Food(self.snake.snake_body, self.obstacles_positions, 'apple')
        self.food2 = Food(self.snake.snake_body, self.obstacles_positions, 'mushroom', [self.food1.position])

    def generate_obstacles(self):
        obstacles = []
        num_obstacles = 5
        
        for _ in range(num_obstacles):
            while True:
                x = random.randint(0, number_of_cells - 1)
                y = random.randint(0, number_of_cells - 1)
                position = Vector2(x, y)
                
                # Don't place on starting snake position
                if position not in [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]:
                    if all(obs.position != position for obs in obstacles):
                        obstacles.append(Obstacle(position))
                        break
        
        return obstacles

    def draw(self, screen):
        self.snake.draw(screen)
        self.food1.draw(screen)
        self.food2.draw(screen)
        for obstacle in self.obstacles:
            obstacle.draw(screen)

    def update(self):
        if self.state == "RUNNING":
            self.snake.update()
            self.check_collision_with_food()
            self.check_collision_with_tail()
            if self.snake.check_collision_with_obstacles(self.obstacles):
                self.game_over()
    
    def check_collision_with_food(self):
        if self.snake.snake_body[0] == self.food1.position:
            self.food1.position = self.food1.generate_random_pos(self.snake.snake_body)
            self.snake.add_segment = True
            self.score += self.food1.get_points()
            if self.snake.eat_sound:
                self.snake.eat_sound.play()
        
        if self.snake.snake_body[0] == self.food2.position:
            self.food2.position = self.food2.generate_random_pos(self.snake.snake_body)
            self.snake.add_segment = True
            self.score += self.food2.get_points()
            if self.snake.eat_sound:
                self.snake.eat_sound.play()

    def game_over(self):
        self.player_manager.save_score(self.player_id, self.player_name, self.score)
        
        self.snake.reset()
        self.food1.position = self.food1.generate_random_pos(self.snake.snake_body)
        self.food2.position = self.food2.generate_random_pos(self.snake.snake_body)
        self.state = "STOPPED"
        self.score = 0
        if self.snake.wall_hit_sound:
            self.snake.wall_hit_sound.play()

    def check_collision_with_tail(self):
        headless_body = self.snake.snake_body[1:]        
        if self.snake.snake_body[0] in headless_body:
            self.game_over()
    
    def draw_game_over(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((cell_size * number_of_cells, cell_size * number_of_cells))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (OFFSET, OFFSET))
        
        # Game Over text with shadow
        font = pygame.font.Font(None, 80)
        shadow_text = font.render('GAME OVER', True, BLACK)
        shadow_rect = shadow_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2 + 2, 
                                                     OFFSET + number_of_cells * cell_size // 2 - 78))
        screen.blit(shadow_text, shadow_rect)
        
        text = font.render('GAME OVER', True, RED)
        text_rect = text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                         OFFSET + number_of_cells * cell_size // 2 - 80))
        screen.blit(text, text_rect)
        
        # Player name
        name_font = pygame.font.Font(None, 40)
        name_text = name_font.render(f'Player: {self.player_name}', True, WHITE)
        name_rect = name_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                               OFFSET + number_of_cells * cell_size // 2 - 20))
        screen.blit(name_text, name_rect)
        
        # High score
        player_high_score = self.player_manager.get_player_high_score(self.player_id, self.player_name)
        if player_high_score:
            hs_font = pygame.font.Font(None, 38)
            hs_text = hs_font.render(f'Your Best: {player_high_score} pts', True, GOLD)
            hs_rect = hs_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                              OFFSET + number_of_cells * cell_size // 2 + 30))
            screen.blit(hs_text, hs_rect)
        
        # Restart instruction
        restart_font = pygame.font.Font(None, 34)
        restart_text = restart_font.render('Press Any Key to Continue', True, WHITE)
        restart_rect = restart_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                                     OFFSET + number_of_cells * cell_size // 2 + 80))
        screen.blit(restart_text, restart_rect)


def get_player_info():
    """Modern player info screen"""
    screen_temp = pygame.display.set_mode((700, 500))
    pygame.display.set_caption("🐍 Snake Game - Player Info")
    
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    player_id = ""
    player_name = ""
    active_field = "id"
    
    clock = pygame.time.Clock()
    
    while True:
        # Gradient background
        for y in range(500):
            ratio = y / 500
            r = int(39 + (52 - 39) * ratio)
            g = int(174 + (73 - 174) * ratio)
            b = int(96 + (94 - 96) * ratio)
            pygame.draw.line(screen_temp, (r, g, b), (0, y), (700, y))
        
        # Title
        title = font.render("🐍 SNAKE GAME", True, WHITE)
        title_rect = title.get_rect(center=(350, 60))
        screen_temp.blit(title, title_rect)
        
        subtitle = small_font.render("Enter Your Information", True, (189, 195, 199))
        subtitle_rect = subtitle.get_rect(center=(350, 110))
        screen_temp.blit(subtitle, subtitle_rect)
        
        # Player ID field
        id_label = small_font.render("Player ID:", True, WHITE)
        screen_temp.blit(id_label, (100, 170))
        
        id_color = WHITE if active_field == "id" else (149, 165, 166)
        pygame.draw.rect(screen_temp, UI_BG, (100, 200, 500, 50), border_radius=8)
        pygame.draw.rect(screen_temp, id_color, (100, 200, 500, 50), 3, border_radius=8)
        id_text = small_font.render(player_id, True, WHITE)
        screen_temp.blit(id_text, (115, 215))
        
        # Player Name field
        name_label = small_font.render("Player Name:", True, WHITE)
        screen_temp.blit(name_label, (100, 280))
        
        name_color = WHITE if active_field == "name" else (149, 165, 166)
        pygame.draw.rect(screen_temp, UI_BG, (100, 310, 500, 50), border_radius=8)
        pygame.draw.rect(screen_temp, name_color, (100, 310, 500, 50), 3, border_radius=8)
        name_text = small_font.render(player_name, True, WHITE)
        screen_temp.blit(name_text, (115, 325))
        
        # Instructions
        instruction_font = pygame.font.Font(None, 26)
        start_text = instruction_font.render("Press ENTER to Start | TAB to switch fields", True, (189, 195, 199))
        screen_temp.blit(start_text, (130, 410))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 100 <= mouse_pos[0] <= 600:
                    if 200 <= mouse_pos[1] <= 250:
                        active_field = "id"
                    elif 310 <= mouse_pos[1] <= 360:
                        active_field = "name"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_id and player_name:
                        return player_id, player_name
                elif event.key == pygame.K_TAB:
                    active_field = "name" if active_field == "id" else "id"
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "id":
                        player_id = player_id[:-1]
                    else:
                        player_name = player_name[:-1]
                else:
                    if active_field == "id" and len(player_id) < 20:
                        player_id += event.unicode
                    elif active_field == "name" and len(player_name) < 20:
                        player_name += event.unicode
        
        clock.tick(30)


# Get player info
player_id, player_name = get_player_info()

# Create main game window
screen = pygame.display.set_mode((2*OFFSET + cell_size * number_of_cells, 
                                  2*OFFSET + cell_size * number_of_cells))
pygame.display.set_caption("🐍 Snake Game - Single Player")

game = Game(player_id, player_name)
clock = pygame.time.Clock()
running = True

SNAKE_MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SNAKE_MOVE_EVENT, 200)

while running:
    for event in pygame.event.get():
        if event.type == SNAKE_MOVE_EVENT:
            game.update()

        if event.type == pygame.KEYDOWN:
            if game.state == "STOPPED":
                game.state = "RUNNING"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game.snake.direction != Vector2(0, 1):
                game.snake.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and game.snake.direction != Vector2(0, -1):
                game.snake.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT and game.snake.direction != Vector2(1, 0):
                game.snake.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1, 0):
                game.snake.direction = Vector2(1, 0)

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Draw gradient background
    for y in range(2*OFFSET + cell_size * number_of_cells):
        ratio = y / (2*OFFSET + cell_size * number_of_cells)
        r = int(46 + (39 - 46) * ratio)
        g = int(204 + (174 - 204) * ratio)
        b = int(113 + (96 - 113) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (2*OFFSET + cell_size * number_of_cells, y))
    
    # Game border with shadow
    pygame.draw.rect(screen, BLACK, (OFFSET-7, OFFSET-7, 
                                      cell_size*number_of_cells+14, 
                                      cell_size*number_of_cells+14), 
                     border_radius=10)
    pygame.draw.rect(screen, BG_DARK, (OFFSET-5, OFFSET-5, 
                                        cell_size*number_of_cells+10,
                                        cell_size*number_of_cells+10), 
                     5, border_radius=8)
    
    game.draw(screen)

    if game.state == "STOPPED":
        game.draw_game_over(screen)

    # UI with shadows
    title_shadow = title_font.render("SNAKE GAME", True, BLACK)
    title_surface = title_font.render("SNAKE GAME", True, WHITE)
    screen.blit(title_shadow, (OFFSET-3, 18))
    screen.blit(title_surface, (OFFSET-5, 15))
    
    # Score display
    score_bg_rect = pygame.Rect(OFFSET-10, OFFSET + cell_size*number_of_cells+5, 200, 50)
    pygame.draw.rect(screen, UI_BG, score_bg_rect, border_radius=8)
    score_surface = score_font.render(f"Score: {game.score}", True, GOLD)
    screen.blit(score_surface, (OFFSET, OFFSET + cell_size*number_of_cells+15))
    
    # Player name display
    name_surface = info_font.render(f"Player: {player_name}", True, WHITE)
    screen.blit(name_surface, (OFFSET + 250, OFFSET + cell_size*number_of_cells+20))

    pygame.display.update()
    clock.tick(60)
