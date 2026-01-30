import sys
import random
import pygame
from pygame.math import Vector2
import json
import os

pygame.init()

# Modern Color Palette for Snakes
SNAKE_COLORS = {
    'teal': {'name': 'Teal', 'body': (22, 160, 133), 'head': (26, 188, 156)},
    'blue': {'name': 'Blue', 'body': (52, 152, 219), 'head': (41, 128, 185)},
    'red': {'name': 'Red', 'body': (231, 76, 60), 'head': (255, 100, 100)},
    'purple': {'name': 'Purple', 'body': (155, 89, 182), 'head': (187, 143, 206)},
    'orange': {'name': 'Orange', 'body': (230, 126, 34), 'head': (255, 160, 70)},
    'green': {'name': 'Green', 'body': (46, 204, 113), 'head': (100, 255, 150)},
    'pink': {'name': 'Pink', 'body': (255, 100, 150), 'head': (255, 150, 200)},
    'yellow': {'name': 'Yellow', 'body': (241, 196, 15), 'head': (255, 230, 100)}
}

# Game Colors
BG_LIGHT = (46, 204, 113)
BG_DARK = (39, 174, 96)
RED = (231, 76, 60)
ORANGE = (230, 126, 34)
WHITE = (236, 240, 241)
BLACK = (44, 62, 80)
GOLD = (241, 196, 15)
TEXT_DARK = (44, 62, 80)
UI_BG = (52, 73, 94)

title_font = pygame.font.Font(None, 60)
score_font = pygame.font.Font(None, 40)
info_font = pygame.font.Font(None, 28)

cell_size = 20
number_of_cells = 20
OFFSET = 75

# Level configurations
LEVELS = {
    1: {'name': 'Easy', 'speed': 200, 'obstacles': 5},
    2: {'name': 'Medium', 'speed': 150, 'obstacles': 8},
    3: {'name': 'Hard', 'speed': 100, 'obstacles': 12}
}

FOOD_TYPES = {
    'apple': {'image': 'snake_food.png', 'points': 10},
    'mushroom': {'image': 'snake_game2.png', 'points': 15}
}


class Food:
    def __init__(self, snake_bodies, obstacles_positions=None, food_type=None, existing_food_positions=None):
        self.obstacles_positions = obstacles_positions or []
        self.existing_food_positions = existing_food_positions or []
        self.snake_bodies = snake_bodies
        self.food_type = food_type if food_type else random.choice(list(FOOD_TYPES.keys()))
        self.position = self.generate_random_pos()
        self.load_image()
    
    def load_image(self):
        try:
            image_path = FOOD_TYPES[self.food_type]['image']
            self.surface = pygame.image.load(image_path)
            self.surface = pygame.transform.scale(self.surface, (cell_size, cell_size))
        except:
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

    def generate_random_pos(self):
        position = self.generate_random_cell()
        while self.is_position_occupied(position):
            position = self.generate_random_cell()
        return position
    
    def is_position_occupied(self, position):
        if position in self.obstacles_positions:
            return True
        
        for snake_body in self.snake_bodies:
            if position in snake_body:
                return True
        
        if position in self.existing_food_positions:
            return True
        
        return False
    
    def get_points(self):
        return FOOD_TYPES[self.food_type]['points']


class Obstacle:
    def __init__(self, position):
        self.position = position
        try:
            self.brick_image = pygame.image.load('barier.png')
            self.brick_image = pygame.transform.scale(self.brick_image, (cell_size, cell_size))
        except:
            self.brick_image = None
    
    def draw(self, screen):
        x = OFFSET + self.position.x * cell_size
        y = OFFSET + self.position.y * cell_size
        
        if self.brick_image:
            screen.blit(self.brick_image, (x, y))
        else:
            # Fallback brick pattern
            BRICK_RED = (192, 57, 43)
            BRICK_DARK = (169, 50, 38)
            BRICK_LIGHT = (205, 97, 85)
            
            obstacle_rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, BRICK_RED, obstacle_rect, border_radius=4)
            
            brick_height = cell_size // 3
            brick_width = cell_size // 2
            
            pygame.draw.rect(screen, BRICK_DARK, (x, y, brick_width - 1, brick_height - 1))
            pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y, brick_width - 1, brick_height - 1))
            pygame.draw.rect(screen, BRICK_LIGHT, (x, y + brick_height, cell_size, brick_height - 1))
            pygame.draw.rect(screen, BRICK_DARK, (x, y + 2 * brick_height, brick_width - 1, brick_height))
            pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y + 2 * brick_height, brick_width - 1, brick_height))
            
            pygame.draw.rect(screen, BRICK_DARK, obstacle_rect, 2, border_radius=4)


class Snake:
    def __init__(self, start_pos, color_key, player_name):
        self.snake_body = [Vector2(start_pos[0], start_pos[1]), 
                          Vector2(start_pos[0] - 1, start_pos[1]), 
                          Vector2(start_pos[0] - 2, start_pos[1])]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.color = SNAKE_COLORS[color_key]['body']
        self.head_color = SNAKE_COLORS[color_key]['head']
        self.player_name = player_name
        self.alive = True
        
        try:
            self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
            self.wall_hit_sound = pygame.mixer.Sound("snake_collision.wav")
        except:
            self.eat_sound = None
            self.wall_hit_sound = None
    
    def draw(self, screen):
        if not self.alive:
            return
            
        for i, seg in enumerate(self.snake_body):
            seg_rect = pygame.Rect(OFFSET + seg.x * cell_size,
                                   OFFSET + seg.y * cell_size, 
                                   cell_size, cell_size)
            color = self.head_color if i == 0 else self.color
            pygame.draw.rect(screen, color, seg_rect, border_radius=7)
            
            if i == 0:
                shine_rect = pygame.Rect(seg_rect.x + 4, seg_rect.y + 4, 6, 6)
                pygame.draw.rect(screen, WHITE, shine_rect, border_radius=3)

    def update(self):
        if not self.alive:
            return
            
        new_head = self.snake_body[0] + self.direction
        new_head.x = new_head.x % number_of_cells
        new_head.y = new_head.y % number_of_cells
        
        self.snake_body.insert(0, new_head)
        if self.add_segment:
            self.add_segment = False
        else:
            self.snake_body = self.snake_body[:-1]
    
    def reset(self, start_pos):
        self.snake_body = [Vector2(start_pos[0], start_pos[1]), 
                          Vector2(start_pos[0] - 1, start_pos[1]), 
                          Vector2(start_pos[0] - 2, start_pos[1])]
        self.direction = Vector2(1, 0)
        self.alive = True
    
    def check_collision_with_obstacles(self, obstacles):
        if not self.alive:
            return False
        for obstacle in obstacles:
            if self.snake_body[0] == obstacle.position:
                return True
        return False
    
    def check_collision_with_tail(self):
        if not self.alive:
            return False
        headless_body = self.snake_body[1:]
        return self.snake_body[0] in headless_body
    
    def check_collision_with_other_snake(self, other_snake):
        if not self.alive or not other_snake.alive:
            return False
        return self.snake_body[0] in other_snake.snake_body


class TwoPlayerGame:
    def __init__(self, player1_name, player2_name, p1_color, p2_color, level):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.level = level
        
        # Create two snakes at different positions
        self.snake1 = Snake([6, 9], p1_color, player1_name)
        self.snake2 = Snake([14, 9], p2_color, player2_name)
        
        # Generate obstacles
        num_obstacles = LEVELS[level]['obstacles']
        self.obstacles = self.generate_obstacles(num_obstacles)
        obstacle_positions = [obs.position for obs in self.obstacles]
        
        # Create food items
        self.food1 = Food([self.snake1.snake_body, self.snake2.snake_body], obstacle_positions, 'apple')
        self.food2 = Food([self.snake1.snake_body, self.snake2.snake_body], obstacle_positions, 'mushroom', 
                         [self.food1.position])
        
        self.score1 = 0
        self.score2 = 0
        self.state = "RUNNING"
    
    def generate_obstacles(self, count):
        """Generate random obstacles avoiding starting positions"""
        obstacles = []
        forbidden_positions = [
            Vector2(6, 9), Vector2(5, 9), Vector2(4, 9),  # Player 1 start
            Vector2(14, 9), Vector2(15, 9), Vector2(16, 9)  # Player 2 start
        ]
        
        for _ in range(count):
            max_attempts = 50
            for _ in range(max_attempts):
                pos = Vector2(random.randint(0, number_of_cells - 1),
                            random.randint(0, number_of_cells - 1))
                
                if pos not in forbidden_positions and pos not in [o.position for o in obstacles]:
                    obstacles.append(Obstacle(pos))
                    break
        
        return obstacles
    
    def draw(self, screen):
        # Draw game elements
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        self.food1.draw(screen)
        self.food2.draw(screen)
        self.snake1.draw(screen)
        self.snake2.draw(screen)
    
    def update(self):
        if self.state == "RUNNING":
            self.snake1.update()
            self.snake2.update()
            self.check_collisions()
    
    def check_collisions(self):
        # Player 1 eating food
        if self.snake1.snake_body[0] == self.food1.position:
            self.food1.position = self.food1.generate_random_pos()
            self.snake1.add_segment = True
            self.score1 += self.food1.get_points()
            if self.snake1.eat_sound:
                self.snake1.eat_sound.play()
        
        if self.snake1.snake_body[0] == self.food2.position:
            self.food2.position = self.food2.generate_random_pos()
            self.snake1.add_segment = True
            self.score1 += self.food2.get_points()
            if self.snake1.eat_sound:
                self.snake1.eat_sound.play()
        
        # Player 2 eating food
        if self.snake2.snake_body[0] == self.food1.position:
            self.food1.position = self.food1.generate_random_pos()
            self.snake2.add_segment = True
            self.score2 += self.food1.get_points()
            if self.snake2.eat_sound:
                self.snake2.eat_sound.play()
        
        if self.snake2.snake_body[0] == self.food2.position:
            self.food2.position = self.food2.generate_random_pos()
            self.snake2.add_segment = True
            self.score2 += self.food2.get_points()
            if self.snake2.eat_sound:
                self.snake2.eat_sound.play()
        
        # Player 1 collisions
        if (self.snake1.check_collision_with_obstacles(self.obstacles) or
            self.snake1.check_collision_with_tail() or
            self.snake1.check_collision_with_other_snake(self.snake2)):
            self.game_over_player(1)
        
        # Player 2 collisions
        if (self.snake2.check_collision_with_obstacles(self.obstacles) or
            self.snake2.check_collision_with_tail() or
            self.snake2.check_collision_with_other_snake(self.snake1)):
            self.game_over_player(2)
    
    def game_over_player(self, player_num):
        if player_num == 1:
            self.snake1.reset([6, 9])
            if self.snake1.wall_hit_sound:
                self.snake1.wall_hit_sound.play()
            self.score1 = 0
            print(f"{self.player1_name} died! Score reset.")
        else:
            self.snake2.reset([14, 9])
            if self.snake2.wall_hit_sound:
                self.snake2.wall_hit_sound.play()
            self.score2 = 0
            print(f"{self.player2_name} died! Score reset.")


def select_level():
    """Level selection screen"""
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Select Level")
    
    selected = 1
    clock = pygame.time.Clock()
    
    while True:
        # Gradient background
        for y in range(600):
            ratio = y / 600
            r = int(30 + (50 - 30) * ratio)
            g = int(40 + (70 - 40) * ratio)
            b = int(60 + (100 - 60) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (800, y))
        
        # Title
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("SELECT LEVEL", True, WHITE)
        title_rect = title.get_rect(center=(400, 80))
        screen.blit(title, title_rect)
        
        # Level cards
        card_width = 220
        card_height = 280
        x_start = (800 - (card_width * 3 + 60)) // 2
        y_pos = 180
        
        for level_num in [1, 2, 3]:
            x = x_start + (level_num - 1) * (card_width + 30)
            
            # Card
            card_rect = pygame.Rect(x, y_pos, card_width, card_height)
            
            if level_num == selected:
                # Selected glow
                glow_rect = pygame.Rect(x - 5, y_pos - 5, card_width + 10, card_height + 10)
                pygame.draw.rect(screen, GOLD, glow_rect, border_radius=15)
            
            pygame.draw.rect(screen, (40, 40, 60), card_rect, border_radius=12)
            pygame.draw.rect(screen, WHITE if level_num == selected else (100, 100, 120), 
                           card_rect, 3, border_radius=12)
            
            # Level number
            num_font = pygame.font.Font(None, 90)
            num_text = num_font.render(str(level_num), True, GOLD if level_num == selected else WHITE)
            num_rect = num_text.get_rect(center=(x + card_width // 2, y_pos + 60))
            screen.blit(num_text, num_rect)
            
            # Level name
            name_font = pygame.font.Font(None, 42)
            name = name_font.render(LEVELS[level_num]['name'], True, WHITE)
            name_rect = name.get_rect(center=(x + card_width // 2, y_pos + 130))
            screen.blit(name, name_rect)
            
            # Stats
            stats_font = pygame.font.Font(None, 28)
            speed_text = f"Speed: {LEVELS[level_num]['speed']}ms"
            obstacles_text = f"Obstacles: {LEVELS[level_num]['obstacles']}"
            
            speed = stats_font.render(speed_text, True, (200, 200, 200))
            obstacles = stats_font.render(obstacles_text, True, (200, 200, 200))
            
            speed_rect = speed.get_rect(center=(x + card_width // 2, y_pos + 190))
            obstacles_rect = obstacles.get_rect(center=(x + card_width // 2, y_pos + 230))
            
            screen.blit(speed, speed_rect)
            screen.blit(obstacles, obstacles_rect)
        
        # Instructions
        inst_font = pygame.font.Font(None, 32)
        inst = inst_font.render("Use Arrow Keys | Press ENTER to Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(400, 520))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = max(1, selected - 1)
                elif event.key == pygame.K_RIGHT:
                    selected = min(3, selected + 1)
                elif event.key == pygame.K_RETURN:
                    return selected
        
        clock.tick(60)


def select_colors():
    """Color selection screen for both players"""
    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Select Colors")
    
    color_keys = list(SNAKE_COLORS.keys())
    p1_selected = 0  # teal
    p2_selected = 1  # blue
    active_player = 1
    
    clock = pygame.time.Clock()
    
    while True:
        # Gradient background
        for y in range(700):
            ratio = y / 700
            r = int(30 + (50 - 30) * ratio)
            g = int(40 + (70 - 40) * ratio)
            b = int(60 + (100 - 60) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (900, y))
        
        # Title
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("SELECT COLORS", True, WHITE)
        title_rect = title.get_rect(center=(450, 60))
        screen.blit(title, title_rect)
        
        # Player 1 section
        font_medium = pygame.font.Font(None, 48)
        p1_title = font_medium.render("Player 1", True, WHITE if active_player == 1 else (150, 150, 150))
        screen.blit(p1_title, (100, 140))
        
        # Player 1 color boxes
        start_x = 100
        start_y = 200
        box_size = 80
        spacing = 100
        
        for i, key in enumerate(color_keys):
            x = start_x + (i % 4) * spacing
            y = start_y + (i // 4) * spacing
            
            color = SNAKE_COLORS[key]['body']
            
            # Draw box
            box_rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(screen, color, box_rect, border_radius=10)
            
            # Selected indicator for player 1
            if i == p1_selected:
                pygame.draw.rect(screen, WHITE, box_rect, 4, border_radius=10)
                # Checkmark
                font_check = pygame.font.Font(None, 60)
                check = font_check.render("✓", True, WHITE)
                check_rect = check.get_rect(center=box_rect.center)
                screen.blit(check, check_rect)
        
        # Player 2 section
        p2_title = font_medium.render("Player 2", True, WHITE if active_player == 2 else (150, 150, 150))
        screen.blit(p2_title, (100, 420))
        
        # Player 2 color boxes
        start_y2 = 480
        
        for i, key in enumerate(color_keys):
            x = start_x + (i % 4) * spacing
            y = start_y2 + (i // 4) * spacing
            
            color = SNAKE_COLORS[key]['body']
            
            # Draw box
            box_rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(screen, color, box_rect, border_radius=10)
            
            # Selected indicator for player 2
            if i == p2_selected:
                pygame.draw.rect(screen, WHITE, box_rect, 4, border_radius=10)
                # Checkmark
                font_check = pygame.font.Font(None, 60)
                check = font_check.render("✓", True, WHITE)
                check_rect = check.get_rect(center=box_rect.center)
                screen.blit(check, check_rect)
        
        # Instructions
        inst_font = pygame.font.Font(None, 28)
        inst = inst_font.render("Arrow Keys: Navigate | TAB: Switch Player | ENTER: Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(450, 650))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active_player = 2 if active_player == 1 else 1
                
                elif event.key == pygame.K_LEFT:
                    if active_player == 1:
                        p1_selected = (p1_selected - 1) % len(color_keys)
                    else:
                        p2_selected = (p2_selected - 1) % len(color_keys)
                
                elif event.key == pygame.K_RIGHT:
                    if active_player == 1:
                        p1_selected = (p1_selected + 1) % len(color_keys)
                    else:
                        p2_selected = (p2_selected + 1) % len(color_keys)
                
                elif event.key == pygame.K_UP:
                    if active_player == 1:
                        p1_selected = (p1_selected - 4) % len(color_keys)
                    else:
                        p2_selected = (p2_selected - 4) % len(color_keys)
                
                elif event.key == pygame.K_DOWN:
                    if active_player == 1:
                        p1_selected = (p1_selected + 4) % len(color_keys)
                    else:
                        p2_selected = (p2_selected + 4) % len(color_keys)
                
                elif event.key == pygame.K_RETURN:
                    return color_keys[p1_selected], color_keys[p2_selected]
        
        clock.tick(60)


def get_player_names():
    """Get player names"""
    screen_temp = pygame.display.set_mode((700, 450))
    pygame.display.set_caption("Enter Names")
    
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    player1_name = ""
    player2_name = ""
    active_field = "player1"
    
    clock = pygame.time.Clock()
    
    while True:
        # Gradient background
        for y in range(450):
            ratio = y / 450
            r = int(39 + (52 - 39) * ratio)
            g = int(174 + (73 - 174) * ratio)
            b = int(96 + (94 - 96) * ratio)
            pygame.draw.line(screen_temp, (r, g, b), (0, y), (700, y))
        
        # Title
        title = font.render("LOCAL MULTIPLAYER", True, WHITE)
        title_rect = title.get_rect(center=(350, 50))
        screen_temp.blit(title, title_rect)
        
        subtitle = small_font.render("Enter Player Names", True, (189, 195, 199))
        subtitle_rect = subtitle.get_rect(center=(350, 100))
        screen_temp.blit(subtitle, subtitle_rect)
        
        # Player 1 field
        p1_label = small_font.render("Player 1 (Arrow Keys):", True, WHITE)
        screen_temp.blit(p1_label, (100, 160))
        
        p1_color = WHITE if active_field == "player1" else (149, 165, 166)
        pygame.draw.rect(screen_temp, UI_BG, (100, 195, 500, 50), border_radius=8)
        pygame.draw.rect(screen_temp, p1_color, (100, 195, 500, 50), 3, border_radius=8)
        p1_text = small_font.render(player1_name, True, WHITE)
        screen_temp.blit(p1_text, (115, 210))
        
        # Player 2 field
        p2_label = small_font.render("Player 2 (WASD):", True, WHITE)
        screen_temp.blit(p2_label, (100, 270))
        
        p2_color = WHITE if active_field == "player2" else (149, 165, 166)
        pygame.draw.rect(screen_temp, UI_BG, (100, 305, 500, 50), border_radius=8)
        pygame.draw.rect(screen_temp, p2_color, (100, 305, 500, 50), 3, border_radius=8)
        p2_text = small_font.render(player2_name, True, WHITE)
        screen_temp.blit(p2_text, (115, 320))
        
        # Instructions
        instruction_font = pygame.font.Font(None, 26)
        start_text = instruction_font.render("Press ENTER to Start | TAB to switch fields", True, (189, 195, 199))
        screen_temp.blit(start_text, (130, 390))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 100 <= mouse_pos[0] <= 600:
                    if 195 <= mouse_pos[1] <= 245:
                        active_field = "player1"
                    elif 305 <= mouse_pos[1] <= 355:
                        active_field = "player2"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player1_name and player2_name:
                        return player1_name, player2_name
                elif event.key == pygame.K_TAB:
                    active_field = "player2" if active_field == "player1" else "player1"
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "player1":
                        player1_name = player1_name[:-1]
                    else:
                        player2_name = player2_name[:-1]
                else:
                    if active_field == "player1" and len(player1_name) < 15:
                        player1_name += event.unicode
                    elif active_field == "player2" and len(player2_name) < 15:
                        player2_name += event.unicode
        
        clock.tick(30)


# Game flow: Names -> Colors -> Level -> Play
player1_name, player2_name = get_player_names()
p1_color, p2_color = select_colors()
level = select_level()

# Create main game window
screen = pygame.display.set_mode((2*OFFSET + cell_size * number_of_cells, 
                                  2*OFFSET + cell_size * number_of_cells))
pygame.display.set_caption(f"Snake Game - Local Multiplayer - {LEVELS[level]['name']}")

game = TwoPlayerGame(player1_name, player2_name, p1_color, p2_color, level)
clock = pygame.time.Clock()
running = True

SNAKE_MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SNAKE_MOVE_EVENT, LEVELS[level]['speed'])

while running:
    for event in pygame.event.get():
        if event.type == SNAKE_MOVE_EVENT:
            game.update()

        if event.type == pygame.KEYDOWN:
            # Player 1 controls (ARROWS)
            if event.key == pygame.K_UP and game.snake1.direction != Vector2(0, 1):
                game.snake1.direction = Vector2(0, -1)
            if event.key == pygame.K_DOWN and game.snake1.direction != Vector2(0, -1):
                game.snake1.direction = Vector2(0, 1)
            if event.key == pygame.K_LEFT and game.snake1.direction != Vector2(1, 0):
                game.snake1.direction = Vector2(-1, 0)
            if event.key == pygame.K_RIGHT and game.snake1.direction != Vector2(-1, 0):
                game.snake1.direction = Vector2(1, 0)
            
            # Player 2 controls (WASD)
            if event.key == pygame.K_w and game.snake2.direction != Vector2(0, 1):
                game.snake2.direction = Vector2(0, -1)
            if event.key == pygame.K_s and game.snake2.direction != Vector2(0, -1):
                game.snake2.direction = Vector2(0, 1)
            if event.key == pygame.K_a and game.snake2.direction != Vector2(1, 0):
                game.snake2.direction = Vector2(-1, 0)
            if event.key == pygame.K_d and game.snake2.direction != Vector2(-1, 0):
                game.snake2.direction = Vector2(1, 0)

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
    
    # Game border
    pygame.draw.rect(screen, BLACK, (OFFSET-7, OFFSET-7, 
                                      cell_size*number_of_cells+14, 
                                      cell_size*number_of_cells+14), 
                     border_radius=10)
    pygame.draw.rect(screen, BG_DARK, (OFFSET-5, OFFSET-5, 
                                        cell_size*number_of_cells+10,
                                        cell_size*number_of_cells+10), 
                     5, border_radius=8)
    
    game.draw(screen)

    # UI Title
    title_shadow = title_font.render(f"{LEVELS[level]['name'].upper()} MODE", True, BLACK)
    title_surface = title_font.render(f"{LEVELS[level]['name'].upper()} MODE", True, WHITE)
    screen.blit(title_shadow, (OFFSET-3, 18))
    screen.blit(title_surface, (OFFSET-5, 15))
    
    # Player 1 Score (Left side)
    p1_bg_rect = pygame.Rect(OFFSET-10, OFFSET + cell_size*number_of_cells+5, 190, 50)
    pygame.draw.rect(screen, UI_BG, p1_bg_rect, border_radius=8)
    p1_score_text = f"{player1_name}: {game.score1}"
    p1_score_surface = score_font.render(p1_score_text, True, game.snake1.head_color)
    screen.blit(p1_score_surface, (OFFSET, OFFSET + cell_size*number_of_cells+15))
    
    # Player 2 Score (Right side)
    p2_score_text = f"{player2_name}: {game.score2}"
    p2_score_surface = score_font.render(p2_score_text, True, game.snake2.head_color)
    p2_width = p2_score_surface.get_width()
    p2_bg_rect = pygame.Rect(OFFSET + cell_size*number_of_cells - p2_width - 5, 
                             OFFSET + cell_size*number_of_cells+5, 
                             p2_width + 15, 50)
    pygame.draw.rect(screen, UI_BG, p2_bg_rect, border_radius=8)
    screen.blit(p2_score_surface, (OFFSET + cell_size*number_of_cells - p2_width, 
                                   OFFSET + cell_size*number_of_cells+15))

    pygame.display.update()
    clock.tick(60)