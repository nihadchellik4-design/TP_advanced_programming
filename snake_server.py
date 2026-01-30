import sys
import random
import pygame
from pygame.math import Vector2
import json
import os

pygame.init()

# PREMIUM COLOR PALETTES - Player can choose!
COLOR_THEMES = {
    'neon': {
        'name': 'Neon Cyber',
        'bg_start': (10, 10, 30),
        'bg_end': (30, 10, 50),
        'snake': (0, 255, 200),
        'snake_head': (100, 255, 255),
        'trail': (0, 200, 150),
        'accent': (255, 0, 200)
    },
    'sunset': {
        'name': 'Sunset Vibes',
        'bg_start': (255, 120, 80),
        'bg_end': (200, 60, 100),
        'snake': (255, 200, 50),
        'snake_head': (255, 240, 100),
        'trail': (255, 150, 50),
        'accent': (255, 100, 150)
    },
    'ocean': {
        'name': 'Deep Ocean',
        'bg_start': (10, 30, 80),
        'bg_end': (5, 60, 120),
        'snake': (50, 200, 255),
        'snake_head': (150, 230, 255),
        'trail': (30, 150, 200),
        'accent': (0, 255, 200)
    },
    'forest': {
        'name': 'Forest Spirit',
        'bg_start': (20, 60, 30),
        'bg_end': (10, 40, 20),
        'snake': (100, 255, 100),
        'snake_head': (180, 255, 180),
        'trail': (60, 200, 60),
        'accent': (255, 200, 100)
    },
    'fire': {
        'name': 'Fire Dragon',
        'bg_start': (80, 10, 10),
        'bg_end': (40, 5, 5),
        'snake': (255, 100, 0),
        'snake_head': (255, 200, 50),
        'trail': (255, 50, 0),
        'accent': (255, 255, 0)
    },
    'galaxy': {
        'name': 'Galaxy Dream',
        'bg_start': (20, 0, 40),
        'bg_end': (60, 0, 100),
        'snake': (200, 100, 255),
        'snake_head': (255, 150, 255),
        'trail': (150, 50, 200),
        'accent': (100, 255, 255)
    }
}

# Universal colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 70, 70)
ORANGE = (255, 150, 50)
GOLD = (255, 215, 0)

# Game constants
cell_size = 20
number_of_cells = 20
OFFSET = 75

# Level configurations
LEVELS = {
    1: {
        'name': 'Débutant',
        'speed': 200,  # milliseconds
        'obstacles': 3,
        'color': (100, 255, 100),
        'description': 'Facile - Vitesse normale'
    },
    2: {
        'name': 'Intermédiaire', 
        'speed': 150,
        'obstacles': 6,
        'color': (255, 200, 100),
        'description': 'Moyen - Plus rapide'
    },
    3: {
        'name': 'Expert',
        'speed': 100,
        'obstacles': 10,
        'color': (255, 100, 100),
        'description': 'Difficile - Très rapide!'
    }
}

FOOD_TYPES = {
    'apple': {'image': 'snake_food.png', 'points': 10},
    'mushroom': {'image': 'snake_game2.png', 'points': 15}
}


class ParticleEffect:
    """Beautiful particle effects for eating food"""
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(15):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': speed * pygame.math.Vector2(1, 0).rotate(angle).x,
                'vy': speed * pygame.math.Vector2(1, 0).rotate(angle).y,
                'life': 30,
                'color': color
            })
    
    def update(self):
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            p['vy'] += 0.2  # Gravity
        self.particles = [p for p in self.particles if p['life'] > 0]
    
    def draw(self, screen):
        for p in self.particles:
            alpha = int(255 * (p['life'] / 30))
            size = int(4 * (p['life'] / 30))
            if size > 0:
                color = (*p['color'][:3], alpha) if len(p['color']) > 3 else p['color']
                pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), size)


class Food:
    def __init__(self, snake_body, obstacles_positions=None, food_type=None, existing_food_positions=None):
        self.obstacles_positions = obstacles_positions or []
        self.existing_food_positions = existing_food_positions or []
        self.food_type = food_type if food_type else random.choice(list(FOOD_TYPES.keys()))
        self.position = self.generate_random_pos(snake_body)
        self.load_image()
        self.pulse = 0  # Animation
    
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
        # Pulsing animation
        self.pulse = (self.pulse + 0.1) % (2 * 3.14159)
        scale = 1 + 0.1 * abs(pygame.math.Vector2(0, 1).rotate(self.pulse * 50).y)
        
        size = int(cell_size * scale)
        offset_adjust = (cell_size - size) // 2
        
        scaled_surface = pygame.transform.scale(self.surface, (size, size))
        
        food_rec = pygame.Rect(
            OFFSET + self.position.x * cell_size + offset_adjust,
            OFFSET + self.position.y * cell_size + offset_adjust,
            size, size
        )
        
        # Glow effect
        glow_size = size + 6
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_color = (255, 255, 100, 50) if self.food_type == 'apple' else (255, 150, 50, 50)
        pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
        screen.blit(glow_surf, (food_rec.x - 3, food_rec.y - 3))
        
        screen.blit(scaled_surface, food_rec)

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
    def __init__(self, theme):
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.theme = theme
        self.trail = []  # Trail effect
        
        try:
            self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
            self.wall_hit_sound = pygame.mixer.Sound("snake_collision.wav")
        except:
            self.eat_sound = None
            self.wall_hit_sound = None
    
    def draw(self, screen):
        # Draw trail effect
        for i, pos in enumerate(self.trail):
            alpha = int(100 * (1 - i / len(self.trail)))
            trail_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            color = (*self.theme['trail'], alpha)
            pygame.draw.circle(trail_surf, color, (cell_size//2, cell_size//2), cell_size//3)
            screen.blit(trail_surf, (OFFSET + pos.x * cell_size, OFFSET + pos.y * cell_size))
        
        # Draw body with gradient
        for i, seg in enumerate(self.snake_body):
            seg_rect = pygame.Rect(OFFSET + seg.x * cell_size,
                                   OFFSET + seg.y * cell_size, 
                                   cell_size, cell_size)
            
            if i == 0:  # Head
                # Glow around head
                glow_surf = pygame.Surface((cell_size + 10, cell_size + 10), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.theme['snake_head'], 80), 
                                 ((cell_size + 10)//2, (cell_size + 10)//2), (cell_size + 10)//2)
                screen.blit(glow_surf, (seg_rect.x - 5, seg_rect.y - 5))
                
                # Head
                pygame.draw.rect(screen, self.theme['snake_head'], seg_rect, border_radius=8)
                
                # Eyes
                eye_size = 4
                eye_offset = 5
                pygame.draw.circle(screen, WHITE, (seg_rect.centerx - eye_offset, seg_rect.centery - 3), eye_size)
                pygame.draw.circle(screen, WHITE, (seg_rect.centerx + eye_offset, seg_rect.centery - 3), eye_size)
                pygame.draw.circle(screen, BLACK, (seg_rect.centerx - eye_offset, seg_rect.centery - 3), 2)
                pygame.draw.circle(screen, BLACK, (seg_rect.centerx + eye_offset, seg_rect.centery - 3), 2)
            else:  # Body
                # Gradient body
                ratio = i / len(self.snake_body)
                color = tuple(int(self.theme['snake'][j] + (self.theme['trail'][j] - self.theme['snake'][j]) * ratio) for j in range(3))
                pygame.draw.rect(screen, color, seg_rect, border_radius=7)
                
                # Highlight
                highlight = pygame.Rect(seg_rect.x + 2, seg_rect.y + 2, cell_size - 4, cell_size - 4)
                pygame.draw.rect(screen, (*color, 50), highlight, border_radius=5)

    def update(self):
        # Update trail
        if len(self.snake_body) > 0:
            self.trail.insert(0, self.snake_body[-1].copy())
            if len(self.trail) > 8:
                self.trail.pop()
        
        new_head = self.snake_body[0] + self.direction
        new_head.x = new_head.x % number_of_cells
        new_head.y = new_head.y % number_of_cells
        
        self.snake_body.insert(0, new_head)
        if self.add_segment:
            self.add_segment = False
        else:
            self.snake_body = self.snake_body[:-1]
    
    def reset(self):
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.trail = []
    
    def check_collision_with_obstacles(self, obstacles):
        for obstacle in obstacles:
            if self.snake_body[0] == obstacle.position:
                return True
        return False


class Game:
    def __init__(self, player_name, level, theme_key):
        self.player_name = player_name
        self.level = level
        self.level_config = LEVELS[level]
        self.theme = COLOR_THEMES[theme_key]
        
        self.snake = Snake(self.theme)
        self.state = "RUNNING"
        self.score = 0
        self.particles = []
        
        # Generate obstacles based on level
        self.obstacles = self.generate_obstacles(self.level_config['obstacles'])
        self.obstacles_positions = [obs.position for obs in self.obstacles]
        
        self.food1 = Food(self.snake.snake_body, self.obstacles_positions, 'apple')
        self.food2 = Food(self.snake.snake_body, self.obstacles_positions, 'mushroom', [self.food1.position])

    def generate_obstacles(self, count):
        obstacles = []
        
        for _ in range(count):
            while True:
                x = random.randint(0, number_of_cells - 1)
                y = random.randint(0, number_of_cells - 1)
                position = Vector2(x, y)
                
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
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

    def update(self):
        if self.state == "RUNNING":
            self.snake.update()
            self.check_collision_with_food()
            self.check_collision_with_tail()
            if self.snake.check_collision_with_obstacles(self.obstacles):
                self.game_over()
        
        # Update particles
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if len(p.particles) > 0]
    
    def check_collision_with_food(self):
        head_pos = self.snake.snake_body[0]
        
        if head_pos == self.food1.position:
            # Create particle effect
            x = OFFSET + head_pos.x * cell_size + cell_size // 2
            y = OFFSET + head_pos.y * cell_size + cell_size // 2
            self.particles.append(ParticleEffect(x, y, RED))
            
            self.food1.position = self.food1.generate_random_pos(self.snake.snake_body)
            self.snake.add_segment = True
            self.score += self.food1.get_points()
            if self.snake.eat_sound:
                self.snake.eat_sound.play()
        
        if head_pos == self.food2.position:
            # Create particle effect
            x = OFFSET + head_pos.x * cell_size + cell_size // 2
            y = OFFSET + head_pos.y * cell_size + cell_size // 2
            self.particles.append(ParticleEffect(x, y, ORANGE))
            
            self.food2.position = self.food2.generate_random_pos(self.snake.snake_body)
            self.snake.add_segment = True
            self.score += self.food2.get_points()
            if self.snake.eat_sound:
                self.snake.eat_sound.play()

    def game_over(self):
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
        overlay = pygame.Surface((cell_size * number_of_cells, cell_size * number_of_cells), pygame.SRCALPHA)
        overlay.fill((*BLACK, 200))
        screen.blit(overlay, (OFFSET, OFFSET))
        
        font = pygame.font.Font(None, 80)
        text = font.render('GAME OVER', True, RED)
        text_rect = text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                         OFFSET + number_of_cells * cell_size // 2 - 80))
        
        # Shadow
        shadow = font.render('GAME OVER', True, BLACK)
        shadow_rect = shadow.get_rect(center=(text_rect.centerx + 3, text_rect.centery + 3))
        screen.blit(shadow, shadow_rect)
        screen.blit(text, text_rect)
        
        # Info
        name_font = pygame.font.Font(None, 40)
        name_text = name_font.render(f'Player: {self.player_name}', True, WHITE)
        name_rect = name_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                               OFFSET + number_of_cells * cell_size // 2 - 20))
        screen.blit(name_text, name_rect)
        
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render('Press Any Key to Continue', True, GOLD)
        restart_rect = restart_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                                     OFFSET + number_of_cells * cell_size // 2 + 80))
        screen.blit(restart_text, restart_rect)


def select_theme():
    """Beautiful theme selection screen"""
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("🎨 Choose Your Snake Color")
    
    clock = pygame.time.Clock()
    selected = 0
    themes_list = list(COLOR_THEMES.keys())
    
    while True:
        # Animated background based on selected theme
        theme = COLOR_THEMES[themes_list[selected]]
        for y in range(600):
            ratio = y / 600
            color = tuple(int(theme['bg_start'][i] + (theme['bg_end'][i] - theme['bg_start'][i]) * ratio) for i in range(3))
            pygame.draw.line(screen, color, (0, y), (900, y))
        
        # Title
        title_font = pygame.font.Font(None, 70)
        title = title_font.render("Choose Your Snake Style", True, WHITE)
        title_rect = title.get_rect(center=(450, 60))
        
        # Shadow
        shadow = title_font.render("Choose Your Snake Style", True, BLACK)
        shadow_rect = shadow.get_rect(center=(452, 62))
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
        
        # Theme options
        y_start = 150
        spacing = 70
        
        for i, (key, theme_data) in enumerate(COLOR_THEMES.items()):
            y = y_start + i * spacing
            
            # Selection highlight
            if i == selected:
                highlight_rect = pygame.Rect(50, y - 5, 800, 60)
                pygame.draw.rect(screen, (*theme_data['accent'], 100), highlight_rect, border_radius=10)
                pygame.draw.rect(screen, theme_data['accent'], highlight_rect, 3, border_radius=10)
            
            # Color preview
            preview_rect = pygame.Rect(70, y + 5, 40, 40)
            pygame.draw.rect(screen, theme_data['snake'], preview_rect, border_radius=8)
            pygame.draw.rect(screen, theme_data['snake_head'], preview_rect, 3, border_radius=8)
            
            # Name
            name_font = pygame.font.Font(None, 48)
            name_text = name_font.render(theme_data['name'], True, WHITE)
            screen.blit(name_text, (130, y + 10))
            
            # Arrow for selected
            if i == selected:
                arrow_font = pygame.font.Font(None, 60)
                arrow = arrow_font.render("→", True, theme_data['accent'])
                screen.blit(arrow, (750, y + 5))
        
        # Instructions
        inst_font = pygame.font.Font(None, 32)
        inst = inst_font.render("↑↓ Select  |  ENTER Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(450, 550))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(themes_list)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(themes_list)
                elif event.key == pygame.K_RETURN:
                    return themes_list[selected]
        
        clock.tick(60)


def select_level():
    """Beautiful level selection screen"""
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("🎯 Choose Difficulty Level")
    
    clock = pygame.time.Clock()
    selected = 1
    
    while True:
        # Dynamic background
        level_color = LEVELS[selected]['color']
        for y in range(600):
            ratio = y / 600
            r = int(20 + (level_color[0] - 20) * ratio * 0.3)
            g = int(20 + (level_color[1] - 20) * ratio * 0.3)
            b = int(40 + (level_color[2] - 40) * ratio * 0.3)
            pygame.draw.line(screen, (r, g, b), (0, y), (900, y))
        
        # Title
        title_font = pygame.font.Font(None, 70)
        title = title_font.render("Select Difficulty", True, WHITE)
        title_rect = title.get_rect(center=(450, 60))
        shadow = title_font.render("Select Difficulty", True, BLACK)
        shadow_rect = shadow.get_rect(center=(452, 62))
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
        
        # Level cards
        card_width = 250
        card_height = 300
        x_start = (900 - (card_width * 3 + 60)) // 2
        y_pos = 180
        
        for level_num in [1, 2, 3]:
            x = x_start + (level_num - 1) * (card_width + 30)
            
            # Card
            card_rect = pygame.Rect(x, y_pos, card_width, card_height)
            
            if level_num == selected:
                # Selected glow
                glow_rect = pygame.Rect(x - 5, y_pos - 5, card_width + 10, card_height + 10)
                pygame.draw.rect(screen, LEVELS[level_num]['color'], glow_rect, border_radius=20)
                pygame.draw.rect(screen, (*LEVELS[level_num]['color'], 150), card_rect, border_radius=15)
            else:
                pygame.draw.rect(screen, (40, 40, 60), card_rect, border_radius=15)
            
            pygame.draw.rect(screen, LEVELS[level_num]['color'], card_rect, 3, border_radius=15)
            
            # Level number
            num_font = pygame.font.Font(None, 100)
            num_text = num_font.render(str(level_num), True, LEVELS[level_num]['color'])
            num_rect = num_text.get_rect(center=(x + card_width // 2, y_pos + 60))
            screen.blit(num_text, num_rect)
            
            # Level name
            name_font = pygame.font.Font(None, 40)
            name = name_font.render(LEVELS[level_num]['name'], True, WHITE)
            name_rect = name.get_rect(center=(x + card_width // 2, y_pos + 130))
            screen.blit(name, name_rect)
            
            # Description
            desc_font = pygame.font.Font(None, 24)
            desc = desc_font.render(LEVELS[level_num]['description'], True, (200, 200, 200))
            desc_rect = desc.get_rect(center=(x + card_width // 2, y_pos + 170))
            screen.blit(desc, desc_rect)
            
            # Stats
            stats_font = pygame.font.Font(None, 26)
            speed_text = f"Vitesse: {200 - LEVELS[level_num]['speed']}%"
            obstacles_text = f"Murs: {LEVELS[level_num]['obstacles']}"
            
            speed = stats_font.render(speed_text, True, WHITE)
            obstacles = stats_font.render(obstacles_text, True, WHITE)
            
            screen.blit(speed, (x + 20, y_pos + 210))
            screen.blit(obstacles, (x + 20, y_pos + 245))
        
        # Instructions
        inst_font = pygame.font.Font(None, 32)
        inst = inst_font.render("←→ Select  |  ENTER Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(450, 550))
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


def get_player_name():
    """Modern player name input"""
    screen = pygame.display.set_mode((700, 400))
    pygame.display.set_caption("Enter Your Name")
    
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 32)
    
    player_name = ""
    clock = pygame.time.Clock()
    
    while True:
        # Gradient background
        for y in range(400):
            ratio = y / 400
            r = int(30 + (60 - 30) * ratio)
            g = int(30 + (80 - 30) * ratio)
            b = int(60 + (120 - 60) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (700, y))
        
        # Title
        title = font.render("Enter Your Name", True, WHITE)
        title_rect = title.get_rect(center=(350, 80))
        screen.blit(title, title_rect)
        
        # Input box
        input_rect = pygame.Rect(100, 180, 500, 60)
        pygame.draw.rect(screen, (40, 40, 80), input_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 150, 255), input_rect, 3, border_radius=10)
        
        # Text
        text_surface = small_font.render(player_name, True, WHITE)
        screen.blit(text_surface, (120, 195))
        
        # Cursor blink
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = 120 + text_surface.get_width() + 5
            pygame.draw.line(screen, WHITE, (cursor_x, 190), (cursor_x, 230), 2)
        
        # Instruction
        inst = small_font.render("Press ENTER to continue", True, (200, 200, 200))
        inst_rect = inst.get_rect(center=(350, 320))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    return player_name
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 15 and event.unicode.isprintable():
                    player_name += event.unicode
        
        clock.tick(60)


# Game flow
player_name = get_player_name()
theme_key = select_theme()
level = select_level()

# Create game window
screen = pygame.display.set_mode((2*OFFSET + cell_size * number_of_cells, 
                                  2*OFFSET + cell_size * number_of_cells))
pygame.display.set_caption(f"Snake Game - {LEVELS[level]['name']}")

game = Game(player_name, level, theme_key)
clock = pygame.time.Clock()
running = True

SNAKE_MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SNAKE_MOVE_EVENT, LEVELS[level]['speed'])

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

    # Dynamic background based on theme
    theme = game.theme
    for y in range(2*OFFSET + cell_size * number_of_cells):
        ratio = y / (2*OFFSET + cell_size * number_of_cells)
        color = tuple(int(theme['bg_start'][i] + (theme['bg_end'][i] - theme['bg_start'][i]) * ratio) for i in range(3))
        pygame.draw.line(screen, color, (0, y), (2*OFFSET + cell_size * number_of_cells, y))
    
    # Game border with glow
    border_color = game.theme['accent']
    glow_rect = pygame.Rect(OFFSET-8, OFFSET-8, cell_size*number_of_cells+16, cell_size*number_of_cells+16)
    pygame.draw.rect(screen, (*border_color, 50), glow_rect, border_radius=12)
    
    border_rect = pygame.Rect(OFFSET-5, OFFSET-5, cell_size*number_of_cells+10, cell_size*number_of_cells+10)
    pygame.draw.rect(screen, border_color, border_rect, 3, border_radius=10)
    
    game.draw(screen)

    if game.state == "STOPPED":
        game.draw_game_over(screen)

    # UI
    title_font = pygame.font.Font(None, 60)
    score_font = pygame.font.Font(None, 50)
    
    title = title_font.render(f"Level {level}: {LEVELS[level]['name']}", True, WHITE)
    shadow_title = title_font.render(f"Level {level}: {LEVELS[level]['name']}", True, BLACK)
    screen.blit(shadow_title, (OFFSET-3, 18))
    screen.blit(title, (OFFSET-5, 15))
    
    # Score with background
    score_bg = pygame.Rect(OFFSET-10, OFFSET + cell_size*number_of_cells+10, 250, 55)
    pygame.draw.rect(screen, (*game.theme['accent'], 150), score_bg, border_radius=10)
    pygame.draw.rect(screen, game.theme['accent'], score_bg, 2, border_radius=10)
    
    score_text = score_font.render(f"Score: {game.score}", True, WHITE)
    screen.blit(score_text, (OFFSET, OFFSET + cell_size*number_of_cells+20))
    
    # Player name
    name_font = pygame.font.Font(None, 35)
    name = name_font.render(f"Player: {player_name}", True, WHITE)
    screen.blit(name, (OFFSET + 270, OFFSET + cell_size*number_of_cells+25))

    pygame.display.update()
    clock.tick(60)