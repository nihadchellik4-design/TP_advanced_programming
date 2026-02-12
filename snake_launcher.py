# snake_launcher.py
import sys
import pygame
import subprocess
import os

# Initialize Pygame
pygame.init()

# Colors - Modern palette
DARK_BG = (20, 25, 35)
ACCENT_BLUE = (52, 152, 219)
ACCENT_HOVER = (41, 128, 185)
TEXT_COLOR = (236, 240, 241)
SUBTITLE_COLOR = (149, 165, 166)
SUCCESS_GREEN = (46, 204, 113)
WARNING_RED = (231, 76, 60)
GOLD = (255, 215, 0)
PURPLE = (155, 89, 182)
PURPLE_HOVER = (142, 68, 173)

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700  # Increased for more buttons


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False

    def draw(self, screen, font):
        # Draw button with rounded corners
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, TEXT_COLOR, self.rect, 2, border_radius=10)

        # Draw text
        text_surface = font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.action()
                return True
        return False


class MainMenu:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game - Main Menu")

        self.clock = pygame.time.Clock()
        self.running = True

        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 28)

        # Create buttons - AJOUT DU BOUTON SINGLE PLAYER
        button_width = 450
        button_height = 70
        button_x = (SCREEN_WIDTH - button_width) // 2
        start_y = 150
        spacing = 80

        self.buttons = [
            Button(button_x, start_y, button_width, button_height,
                   "Single Player", ACCENT_BLUE, ACCENT_HOVER,
                   self.launch_single_player),

            Button(button_x, start_y + spacing, button_width, button_height,
                   "Premium (Levels + Themes)", GOLD, (230, 180, 0),
                   self.launch_premium),

            Button(button_x, start_y + spacing * 2, button_width, button_height,
                   "Local Multiplayer (2 Players)", PURPLE, PURPLE_HOVER,
                   self.launch_2players_local),

            Button(button_x, start_y + spacing * 3, button_width, button_height,
                   "Multiplayer Host (Server)", SUCCESS_GREEN, (39, 174, 96),
                   self.launch_multiplayer_server),

            Button(button_x, start_y + spacing * 4, button_width, button_height,
                   "Multiplayer Join (Client)", WARNING_RED, (192, 57, 43),
                   self.launch_multiplayer_client),

            Button(button_x, start_y + spacing * 5, button_width, button_height,
                   "Exit", (100, 100, 100), (70, 70, 70),
                   self.quit_game),
        ]

    def launch_single_player(self):
        """Launch single player mode"""
        print("Launching Single Player Mode...")
        self.running = False
        try:
            subprocess.run([sys.executable, "snake_game.py"])
        except FileNotFoundError:
            print("Error: snake_game.py not found!")
            self.running = True

    def launch_premium(self):
        """Launch premium version with levels and color themes"""
        print("Launching Premium Version...")
        self.running = False
        try:
            subprocess.run([sys.executable, "snake_server.py"])
        except FileNotFoundError:
            print("Error: snake_server.py not found!")
            self.running = True

    def launch_2players_local(self):
        """Launch 2 players local mode"""
        print("Launching Local Multiplayer Mode...")
        self.running = False
        try:
            subprocess.run([sys.executable, "snake_2players_local.py"])
        except FileNotFoundError:
            print("Error: snake_2players_local.py not found!")
            self.running = True

    def launch_multiplayer_server(self):
        """Lancer le serveur de jeu multijoueur"""
        print("Launching Multiplayer Server...")
        self.running = False
        try:
            subprocess.run([sys.executable, "hamachi_server.py"])  # Utiliser hamachi_server.py
        except FileNotFoundError:
            print("Error: hamachi_server.py not found!")
            self.running = True

    def launch_multiplayer_client(self):
        """Launch multiplayer client only"""
        print("Launching Multiplayer Client...")
        self.running = False
        try:
            subprocess.run([sys.executable, "snake_client.py"])
        except FileNotFoundError:
            print("Error: snake_client.py not found!")
            self.running = True

    def quit_game(self):
        """Exit the game"""
        print("Goodbye!")
        self.running = False
        pygame.quit()
        sys.exit()

    def draw_gradient_background(self):
        """Draw a gradient background"""
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(20 + (30 - 20) * ratio)
            g = int(25 + (35 - 25) * ratio)
            b = int(35 + (50 - 35) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_snake_decoration(self):
        """Draw decorative snake graphics"""
        # Draw a stylized snake in the background
        snake_segments = [
            (100, 100), (130, 100), (160, 100), (190, 110), (210, 130),
            (220, 160), (210, 190), (180, 200), (150, 190)
        ]

        for i, pos in enumerate(snake_segments):
            size = 25 - i
            color = (46 + i * 10, 204 - i * 10, 113 - i * 5)
            pygame.draw.circle(self.screen, color, pos, size)

        # Mirror on right side
        for i, pos in enumerate(snake_segments):
            size = 25 - i
            color = (46 + i * 10, 204 - i * 10, 113 - i * 5)
            mirrored_x = SCREEN_WIDTH - pos[0]
            pygame.draw.circle(self.screen, color, (mirrored_x, pos[1]), size)

    def draw_instructions(self):
        """Draw instructions at the bottom"""
        instructions = [
            "🐍 SNAKE GAME - 3 MODES AVAILABLE",
            "Single Player: Classic snake game with score saving",
            "Local Multiplayer: 2 players on same PC (Arrows vs WASD)",
            "Network Multiplayer: Play with friends over Hamachi",
            "Server IP for Hamachi: 25.40.67.39"
        ]

        y_pos = SCREEN_HEIGHT - 150
        for i, instruction in enumerate(instructions):
            color = (100, 255, 150) if i == 0 else SUBTITLE_COLOR
            font = self.button_font if i == 0 else self.small_font
            text = font.render(instruction, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos + i * 25))
            self.screen.blit(text, text_rect)

    def run(self):
        """Main menu loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                # Let buttons handle events
                for button in self.buttons:
                    button.handle_event(event)

            # Draw everything
            self.draw_gradient_background()
            self.draw_snake_decoration()

            # Draw title
            title_surface = self.title_font.render("SNAKE GAME", True, SUCCESS_GREEN)
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))

            # Draw title shadow
            shadow_surface = self.title_font.render("SNAKE GAME", True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(SCREEN_WIDTH // 2 + 3, 83))
            self.screen.blit(shadow_surface, shadow_rect)
            self.screen.blit(title_surface, title_rect)

            # Draw subtitle
            subtitle_surface = self.subtitle_font.render("Choose Your Game Mode", True, SUBTITLE_COLOR)
            subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))
            self.screen.blit(subtitle_surface, subtitle_rect)

            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen, self.button_font)

            # Draw instructions
            self.draw_instructions()

            pygame.display.flip()
            self.clock.tick(60)


def main():
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()