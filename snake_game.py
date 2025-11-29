import sys
import random
import pygame
from pygame.math import Vector2
import json
import os

pygame.init()

title_font = pygame.font.Font(None,60)
score_font = pygame.font.Font(None,40)

GREEN = (173, 204, 96)
DARK_GREEN = (43, 51, 24)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
BRICK_RED = (180, 70, 50)
BRICK_DARK = (140, 50, 35)
BRICK_LIGHT = (200, 90, 60)

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
        # NEW: Added obstacles and existing food positions
        self.obstacles_positions = obstacles_positions or []
        self.existing_food_positions = existing_food_positions or []
        self.food_type = food_type if food_type else random.choice(list(FOOD_TYPES.keys()))
        self.position = self.generate_random_pos(snake_body)
        self.load_image()
    
    # NEW: Load image based on food type
    def load_image(self):
        try:
            image_path = FOOD_TYPES[self.food_type]['image']
            self.surface = pygame.image.load(image_path)
            self.surface = pygame.transform.scale(self.surface, (cell_size, cell_size))
        except:
            self.surface = pygame.Surface((cell_size, cell_size))
            self.surface.fill((255, 0, 0))
            print(f"Image {FOOD_TYPES[self.food_type]['image']} not found - using placeholder")

    def draw(self):
        food_rec = pygame.Rect(OFFSET+ self.position.x * cell_size, OFFSET+ self.position.y * cell_size, cell_size, cell_size)
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
    
    def draw(self):
        x = OFFSET + self.position.x * cell_size
        y = OFFSET + self.position.y * cell_size
        
        obstacle_rect = pygame.Rect(x, y, cell_size, cell_size)
        pygame.draw.rect(screen, BRICK_RED, obstacle_rect)
        
        brick_height = cell_size // 3
        brick_width = cell_size // 2
        
        pygame.draw.rect(screen, BRICK_DARK, (x, y, brick_width - 1, brick_height - 1))
        pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y, brick_width - 1, brick_height - 1))
        pygame.draw.rect(screen, BRICK_LIGHT, (x, y + brick_height, cell_size, brick_height - 1))
        pygame.draw.rect(screen, BRICK_DARK, (x, y + 2 * brick_height, brick_width - 1, brick_height))
        pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y + 2 * brick_height, brick_width - 1, brick_height))
        
        pygame.draw.line(screen, (100, 100, 100), (x, y + brick_height), (x + cell_size, y + brick_height), 2)
        pygame.draw.line(screen, (100, 100, 100), (x, y + 2 * brick_height), (x + cell_size, y + 2 * brick_height), 2)
        pygame.draw.line(screen, (100, 100, 100), (x + brick_width, y), (x + brick_width, y + brick_height), 2)
        pygame.draw.line(screen, (100, 100, 100), (x + brick_width, y + 2 * brick_height), (x + brick_width, y + cell_size), 2)
        
        pygame.draw.rect(screen, (80, 40, 30), obstacle_rect, 2)


class Snake:
    def __init__(self):
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)
        self.add_segment = False
        self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
        self.wall_hit_sound = pygame.mixer.Sound("snake_collision.wav")
    def draw(self):
        for seg in self.snake_body:
            seg_rect = pygame.Rect(OFFSET+ seg.x * cell_size,OFFSET+ seg.y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, DARK_GREEN, seg_rect, 0, 7)

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
        self.snake_body =  [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
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
                
                if position not in [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]:
                    if all(obs.position != position for obs in obstacles):
                        obstacles.append(Obstacle(position))
                        break
        
        return obstacles

    def draw(self):
        self.snake.draw()
        self.food1.draw()
        self.food2.draw()
        for obstacle in self.obstacles:
            obstacle.draw()

    def update(self):
      if self.state == "RUNNING":
         self.snake.update()
         self.check_collision_with_food()
         self.check_collision_with_tail()
         # NEW: Check collision with obstacles
         if self.snake.check_collision_with_obstacles(self.obstacles):
             self.game_over()

    def check_collision_with_food(self):
        # Check collision with food1 (apple)
        if self.snake.snake_body[0] == self.food1.position:
          self.food1.position = self.food1.generate_random_pos(self.snake.snake_body) 
          self.snake.add_segment = True
          self.score += self.food1.get_points()
          self.snake.eat_sound.play()
        
       
        if self.snake.snake_body[0] == self.food2.position:
          self.food2.position = self.food2.generate_random_pos(self.snake.snake_body)
          self.snake.add_segment = True
          self.score += self.food2.get_points()
          self.snake.eat_sound.play()

    
    def check_collision_with_edges(self):
        if self.snake.snake_body[0].x == number_of_cells or self.snake.snake_body[0].x == -1:
            self.game_over()  
        if self.snake.snake_body[0].y == number_of_cells or self.snake.snake_body[0].y == -1:  
              self.game_over()

    def game_over(self):
    
       self.player_manager.save_score(self.player_id, self.player_name, self.score)
       
       self.snake.reset()
       self.food1.position = self.food1.generate_random_pos(self.snake.snake_body)
       self.food2.position = self.food2.generate_random_pos(self.snake.snake_body)
       self.state = "STOPPED"
       self.score = 0
       self.snake.wall_hit_sound.play()

    def check_collision_with_tail(self):
        headless_body = self.snake.snake_body[1:]        
        if self.snake.snake_body[0] in headless_body:
            self.game_over()
    
    def draw_game_over(self):
        overlay = pygame.Surface((cell_size * number_of_cells, cell_size * number_of_cells))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (OFFSET, OFFSET))
        
        font = pygame.font.Font(None, 72)
        text = font.render('GAME OVER', True, RED)
        text_rect = text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                         OFFSET + number_of_cells * cell_size // 2 - 80))
        screen.blit(text, text_rect)
        
        name_font = pygame.font.Font(None, 36)
        name_text = name_font.render(f'Player: {self.player_name}', True, WHITE)
        name_rect = name_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                               OFFSET + number_of_cells * cell_size // 2 - 20))
        screen.blit(name_text, name_rect)
        
        player_high_score = self.player_manager.get_player_high_score(self.player_id, self.player_name)
        if player_high_score:
            hs_font = pygame.font.Font(None, 36)
            hs_text = hs_font.render(f'Your Best: {player_high_score} pts', True, GOLD)
            hs_rect = hs_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                              OFFSET + number_of_cells * cell_size // 2 + 30))
            screen.blit(hs_text, hs_rect)
        
        restart_font = pygame.font.Font(None, 32)
        restart_text = restart_font.render('Press Any Key to Continue', True, WHITE)
        restart_rect = restart_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                                     OFFSET + number_of_cells * cell_size // 2 + 80))
        screen.blit(restart_text, restart_rect)


def get_player_info():
    screen_temp = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Snake Game - Player Info")
    
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 28)
    
    player_id = ""
    player_name = ""
    active_field = "id"
    
    clock = pygame.time.Clock()
    
    while True:
        screen_temp.fill(GREEN)
        
        title = font.render("Enter Your Information", True, BLACK)
        screen_temp.blit(title, (150, 50))
        
        id_label = small_font.render("Player ID:", True, BLACK)
        screen_temp.blit(id_label, (100, 120))
        
        id_color = BLACK if active_field == "id" else (128, 128, 128)
        pygame.draw.rect(screen_temp, WHITE, (100, 150, 400, 40))
        pygame.draw.rect(screen_temp, id_color, (100, 150, 400, 40), 2)
        id_text = small_font.render(player_id, True, BLACK)
        screen_temp.blit(id_text, (110, 160))
        
        name_label = small_font.render("Player Name:", True, BLACK)
        screen_temp.blit(name_label, (100, 220))
        
        name_color = BLACK if active_field == "name" else (128, 128, 128)
        pygame.draw.rect(screen_temp, WHITE, (100, 250, 400, 40))
        pygame.draw.rect(screen_temp, name_color, (100, 250, 400, 40), 2)
        name_text = small_font.render(player_name, True, BLACK)
        screen_temp.blit(name_text, (110, 260))
        
        start_text = small_font.render("Press ENTER to Start", True, BLACK)
        screen_temp.blit(start_text, (180, 330))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 100 <= mouse_pos[0] <= 500:
                    if 150 <= mouse_pos[1] <= 190:
                        active_field = "id"
                    elif 250 <= mouse_pos[1] <= 290:
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


# NEW: Get player info first
player_id, player_name = get_player_info()

# Original code from here
screen = pygame.display.set_mode((2*OFFSET + cell_size * number_of_cells, 2*OFFSET + cell_size * number_of_cells))
pygame.display.set_caption("Snake Game")

try:
    food_surface = pygame.image.load("snake_food.png")
    food_surface = pygame.transform.scale(food_surface, (cell_size, cell_size))
except:
    food_surface = pygame.Surface((cell_size, cell_size))
    food_surface.fill((255, 0, 0))
    print("Image non trouvée - utilisation placeholder")

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
                game.state ="RUNNING"

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

    screen.fill(GREEN)
    pygame.draw.rect(screen, DARK_GREEN, (OFFSET-5, OFFSET-5, cell_size*number_of_cells+10,cell_size*number_of_cells+10) , 5 )
    game.draw()

   
    if game.state == "STOPPED":
        game.draw_game_over()

    title_surface = title_font.render("Snake Game", True , DARK_GREEN)
    score_surface = score_font.render(str(game.score), True, DARK_GREEN)
    screen.blit(title_surface,(OFFSET-5, 20))
    screen.blit(score_surface, (OFFSET-5, OFFSET +cell_size*number_of_cells+10 ))

    pygame.display.update()
  