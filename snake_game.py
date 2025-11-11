import sys
import random
import pygame
from pygame.math import Vector2

pygame.init()

GREEN = (173, 204, 97)
DARK_GREEN = (0, 128, 0)

cell_size = 30
number_of_cells = 20


class Food:
    def __init__(self):
        self.position = self.generate_random_pos()

    def draw(self):
        food_rec = pygame.Rect(self.position.x * cell_size, self.position.y * cell_size, cell_size, cell_size)
        screen.blit(food_surface, food_rec)

    def generate_random_pos(self):
        x = random.randint(0, number_of_cells - 1)
        y = random.randint(0, number_of_cells - 1)
        position = Vector2(x, y)
        return position


class Snake:
    def __init__(self):
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        self.direction = Vector2(1, 0)

    def draw(self):
        for seg in self.snake_body:
            seg_rect = pygame.Rect(seg.x * cell_size, seg.y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, DARK_GREEN, seg_rect, 0, 7)

    def move(self):
        body_copy = self.snake_body[:-1]
        body_copy.insert(0, self.snake_body[0] + self.direction)
        self.snake_body = body_copy
class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
    def draw(self):
        self.snake.draw()
        self.food.draw()
    def update(self):
        self.snake.move()
game = Game()


screen = pygame.display.set_mode((cell_size * number_of_cells, cell_size * number_of_cells))
pygame.display.set_caption("Snake Game")



try:
    food_surface = pygame.image.load("snake_food.png")
    food_surface = pygame.transform.scale(food_surface, (cell_size, cell_size))
except:
    food_surface = pygame.Surface((cell_size, cell_size))
    food_surface.fill((255, 0, 0))
    print("Image non trouvée - utilisation placeholder")

clock = pygame.time.Clock()
running = True

SNAKE_MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SNAKE_MOVE_EVENT, 200)

while running:
    for event in pygame.event.get():
        if event.type == SNAKE_MOVE_EVENT:
            game.update()

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
    game.draw()
    pygame.display.update()
    clock.tick(60)




