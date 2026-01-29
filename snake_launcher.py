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

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

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
        pygame.display.set_caption("🐍 Snake Game - Main Menu")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 28)
        
        # Create buttons
        button_width = 400
        button_height = 70
        button_x = (SCREEN_WIDTH - button_width) // 2
        start_y = 220
        spacing = 90
        
        self.buttons = [
            Button(button_x, start_y, button_width, button_height,
                   "🎮 Single Player", ACCENT_BLUE, ACCENT_HOVER,
                   self.launch_single_player),
            Button(button_x, start_y + spacing, button_width, button_height,
                   "👥 Multiplayer (Host Server)", SUCCESS_GREEN, (39, 174, 96),
                   self.launch_multiplayer_server),
            Button(button_x, start_y + spacing * 2, button_width, button_height,
                   "🌐 Multiplayer (Join Game)", SUCCESS_GREEN, (39, 174, 96),
                   self.launch_multiplayer_client),
            Button(button_x, start_y + spacing * 3, button_width, button_height,
                   "❌ Exit", WARNING_RED, (192, 57, 43),
                   self.quit_game)
        ]
        
    def launch_single_player(self):
        """Launch single player mode"""
        print("🎮 Launching Single Player Mode...")
        self.running = False
        try:
            subprocess.run([sys.executable, "snake_game_modern.py"])
        except FileNotFoundError:
            print("❌ Error: snake_game_modern.py not found!")
    
    def launch_multiplayer_server(self):
        """Launch multiplayer server"""
        print("🖥️ Launching Multiplayer Server...")
        self.running = False
        try:
            # Start server in a separate process
            server_process = subprocess.Popen([sys.executable, "snake_server.py"])
            # Give server time to start
            import time
            time.sleep(1)
            # Start client
            subprocess.run([sys.executable, "snake_client_modern.py"])
            # Cleanup
            server_process.terminate()
        except FileNotFoundError:
            print("❌ Error: Multiplayer files not found!")
    
    def launch_multiplayer_client(self):
        """Launch multiplayer client only"""
        print("🌐 Launching Multiplayer Client...")
        self.running = False
        try:
            subprocess.run([sys.executable, "snake_client_modern.py"])
        except FileNotFoundError:
            print("❌ Error: snake_client_modern.py not found!")
    
    def quit_game(self):
        """Exit the game"""
        print("👋 Goodbye!")
        self.running = False
        pygame.quit()
        sys.exit()
    
    def draw_gradient_background(self):
        """Draw a gradient background"""
        for y in range(SCREEN_HEIGHT):
            # Calculate color gradient from dark to slightly lighter
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
            alpha = 50 + i * 5
            size = 25 - i
            color = (46 + i * 10, 204 - i * 10, 113 - i * 5)
            pygame.draw.circle(self.screen, color, pos, size)
        
        # Mirror on right side
        for i, pos in enumerate(snake_segments):
            alpha = 50 + i * 5
            size = 25 - i
            color = (46 + i * 10, 204 - i * 10, 113 - i * 5)
            mirrored_x = SCREEN_WIDTH - pos[0]
            pygame.draw.circle(self.screen, color, (mirrored_x, pos[1]), size)
    
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
            subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(subtitle_surface, subtitle_rect)
            
            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen, self.button_font)
            
            # Draw footer
            footer_text = self.small_font.render("Use arrow keys to control the snake | Eat food to grow", True, SUBTITLE_COLOR)
            footer_rect = footer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(footer_text, footer_rect)
            
            pygame.display.flip()
            self.clock.tick(60)

def main():
    menu = MainMenu()
    menu.run()

if __name__ == "__main__":
    main()
