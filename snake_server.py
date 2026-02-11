# ====================================================================
# Ce fichier implémente une version premium du jeu Snake avec:
# - Plusieurs thèmes de couleurs
# - Différents niveaux de difficulté
# - Effets de particules
# - Animations avancées
# - Sauvegarde des scores
# ====================================================================
# Module système pour gérer la sortie du programme (sys.exit())
import sys
# Module pour générer des nombres aléatoires (positions de la nourriture, obstacles, etc.)
import random
# Bibliothèque principale pour créer des jeux 2D en Python
# Gère l'affichage graphique, les événements, les sons, etc.
import pygame
# Importation de la classe Vector2 pour représenter des vecteurs 2D
# Utilisée pour les positions (x, y) et les directions du serpent
from pygame.math import Vector2
# Module pour manipuler les données JSON
# Utilisé pour sauvegarder/charger les scores des joueurs

import json
# Module pour interagir avec le système d'exploitation
# Utilisé pour vérifier l'existence de fichiers

import os
# Initialise tous les modules de pygame
# DOIT être appelé avant d'utiliser toute fonctionnalité pygame

pygame.init()

# Dictionnaire contenant 6 thèmes de couleurs différents
# Chaque thème a un nom et des couleurs pour différents éléments
COLOR_THEMES = {
    'neon': {
        # Thème "Neon Cyber" - Couleurs cyberpunk néon
        'name': 'Neon Cyber',
        'bg_start': (10, 10, 30),      # Couleur de début du dégradé d'arrière-plan (RGB)
        'bg_end': (30, 10, 50),        # Couleur de fin du dégradé d'arrière-plan
        'snake': (0, 255, 200),        # Couleur du corps du serpent (cyan néon)
        'snake_head': (100, 255, 255), # Couleur de la tête du serpent (cyan clair)
        'trail': (0, 200, 150),        # Couleur de la traînée/queue
        'accent': (255, 0, 200)        # Couleur d'accentuation (rose néon)
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

# Blanc pur - utilisé pour le texte et les bordures
WHITE = (255, 255, 255)
# Noir pur - utilisé pour les ombres du texte
BLACK = (0, 0, 0)
# Rouge - utilisé pour la nourriture (pomme)
RED = (255, 70, 70)
# Orange - utilisé pour la nourriture spéciale (champignon)
ORANGE = (255, 150, 50)
# Or - utilisé pour mettre en évidence certains éléments
GOLD = (255, 215, 0)

# Taille en pixels de chaque cellule de la grille
# Le terrain de jeu est divisé en cellules carrées de 20x20 pixels
cell_size = 20

# Nombre de cellules dans chaque direction (largeur et hauteur)
# Le terrain est donc une grille de 20x20 = 400 cellules
number_of_cells = 20

# Décalage en pixels depuis le bord de la fenêtre
# Crée une marge autour du terrain de jeu pour afficher le titre et le score
OFFSET = 75

# Dictionnaire définissant 3 niveaux de difficulté
# Chaque niveau a des paramètres différents
LEVELS = {
    1: {
        'name': 'Débutant',
        'speed': 200,  # Vitesse en millisecondes entre chaque mouvement (plus lent)
        'obstacles': 3,  # Nombre d'obstacles générés sur le terrain
        'color': (100, 255, 100),  # Couleur verte pour le niveau facile
        'description': 'Facile - Vitesse normale'  # Description affichée
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
# Dictionnaire définissant les différents types de nourriture disponibles
    'apple': {
        'image': 'snake_food.png',  # Fichier image de la pomme
        'points': 10  # Points gagnés en mangeant une pomme
    },
    'mushroom': {
        'image': 'snake_game2.png',  # Fichier image du champignon
        'points': 15  # Points gagnés en mangeant un champignon (plus de points)
    }
}


class ParticleEffect:

    """
    Classe pour créer de beaux effets de particules lorsque le serpent mange
    Les particules s'envolent dans toutes les directions avec de la physique
    """
    def __init__(self, x, y, color):
        """
        Constructeur de l'effet de particules
        Args:
            x: Position X du centre de l'effet
            y: Position Y du centre de l'effet
            color: Couleur des particules
        """
        self.particles = []
        # Liste pour stocker toutes les particules individuelles
         # Crée 15 particules

        for _ in range(15):
            # Angle aléatoire en degrés (0-360) pour la direction de la particule
            angle = random.uniform(0, 360)
            # Vitesse aléatoire entre 2 et 6 pixels par frame
            speed = random.uniform(2, 6)
            self.particles.append({
                # Ajoute une particule avec ses propriétés
                'x': x,  # Position X initiale
                'y': y,  # Position Y initiale
                'vx': speed * pygame.math.Vector2(1, 0).rotate(angle).x,
                # Vitesse horizontale calculée avec trigonométrie
                # Vector2(1, 0) est un vecteur unitaire horizontal
                # rotate(angle) le fait tourner
                # .x récupère la composante X
                
                'vy': speed * pygame.math.Vector2(1, 0).rotate(angle).y,
                # Vitesse verticale (même calcul pour Y)
                
                'life': 30,  # Durée de vie en frames (30 frames ≈ 0.5 seconde à 60 FPS)
                'color': color  # Couleur de la particule
            })
    
    def update(self):
        """
        Met à jour toutes les particules à chaque frame
        Applique le mouvement et la gravité
        """
        for p in self.particles:
            # Pour chaque particule
            
            p['x'] += p['vx']
            # Déplace la particule horizontalement selon sa vitesse
            
            p['y'] += p['vy']
            # Déplace la particule verticalement selon sa vitesse
            
            p['life'] -= 1
            # Réduit la durée de vie (la particule va disparaître)
            
            p['vy'] += 0.2  # Gravité
            # Ajoute une accélération vers le bas (effet de gravité)
            # Fait tomber les particules progressivement
        
        self.particles = [p for p in self.particles if p['life'] > 0]
        # Filtre la liste: garde seulement les particules encore vivantes
        # Supprime les particules dont life <= 0
    
    def draw(self, screen):
        """
        Dessine toutes les particules à l'écran
        Args:
            screen: Surface pygame où dessiner
        """
        for p in self.particles:
            # Pour chaque particule vivante
            
            alpha = int(255 * (p['life'] / 30))
            # Calcule la transparence basée sur la durée de vie restante
            # Plus la particule est proche de mourir, plus elle est transparente
            # 255 = opaque, 0 = invisible
            
            size = int(4 * (p['life'] / 30))
            # Calcule la taille basée sur la durée de vie
            # Les particules rétrécissent en mourant
            
            if size > 0:
                # Ne dessine que si la taille est visible
                
                color = (*p['color'][:3], alpha) if len(p['color']) > 3 else p['color']
                # Ajoute la transparence à la couleur si nécessaire
                # (*p['color'][:3], alpha) = (R, G, B, alpha)
                
                pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), size)
                # Dessine un cercle pour représenter la particule



class Food:
    """
    Classe représentant la nourriture que le serpent doit manger
    Gère l'affichage, la position et l'animation de la nourriture
    """
    def __init__(self, snake_body, obstacles_positions=None, food_type=None, existing_food_positions=None):
        """
        Constructeur de la nourriture
        Args:
            snake_body: Liste des positions du corps du serpent (pour éviter de placer la nourriture dessus)
            obstacles_positions: Liste des positions des obstacles
            food_type: Type de nourriture ('apple' ou 'mushroom'), aléatoire si None
            existing_food_positions: Positions d'autres nourritures déjà présentes
        """
        self.obstacles_positions = obstacles_positions or []
        # Initialise la liste des obstacles (liste vide si None)
        
        self.existing_food_positions = existing_food_positions or []
        # Initialise la liste des autres nourritures
        
        self.food_type = food_type if food_type else random.choice(list(FOOD_TYPES.keys()))
        # Choisit un type de nourriture: utilise celui fourni ou en choisit un aléatoirement
        # list(FOOD_TYPES.keys()) = ['apple', 'mushroom']
        # random.choice() en choisit un au hasard
        
        self.position = self.generate_random_pos(snake_body)
        # Génère une position aléatoire valide pour la nourriture
        
        self.load_image()
        # Charge l'image correspondant au type de nourriture
        
        self.pulse = 0  # Animation
        # Variable pour l'animation de pulsation (breathing effect)
  
    def load_image(self):
        """
        Charge l'image de la nourriture depuis un fichier
        Crée une image de secours si le fichier n'existe pas
        """
        try:
            # Tente de charger l'image
            
            image_path = FOOD_TYPES[self.food_type]['image']
            # Récupère le chemin du fichier image depuis le dictionnaire FOOD_TYPES
            
            self.surface = pygame.image.load(image_path)
            # Charge l'image dans une Surface pygame
            
            self.surface = pygame.transform.scale(self.surface, (cell_size, cell_size))
            # Redimensionne l'image pour qu'elle corresponde exactement à la taille d'une cellule
            
        except:
            # Si le chargement échoue (fichier manquant, corrompu, etc.)
            
            self.surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            # Crée une surface vide transparente de la bonne taille
            # pygame.SRCALPHA permet la transparence
            
            color = RED if self.food_type == 'apple' else ORANGE
            # Choisit la couleur: rouge pour pomme, orange pour champignon
            
            pygame.draw.circle(self.surface, color, (cell_size//2, cell_size//2), cell_size//2)
            # Dessine un cercle simple comme image de secours
            # Centre: (cell_size//2, cell_size//2) = centre de la cellule
            # Rayon: cell_size//2 = le cercle remplit la cellule

    def draw(self, screen):
        """
        Dessine la nourriture à l'écran avec une animation de pulsation
        Args:
            screen: Surface pygame où dessiner
        """
        # === ANIMATION DE PULSATION ===
        self.pulse = (self.pulse + 0.1) % (2 * 3.14159)
        # Incrémente la variable pulse (0.1 par frame)
        # % (2 * π) fait une boucle de 0 à 2π (un cycle complet)
        # Utilisé pour créer une animation cyclique
        
        scale = 1 + 0.1 * abs(pygame.math.Vector2(0, 1).rotate(self.pulse * 50).y)
        # Calcule le facteur d'échelle pour l'animation
        # 1 = taille normale
        # +/- 0.1 = variation de 10%
        # abs(...) assure que l'échelle est toujours positive
        # rotate(self.pulse * 50) crée une oscillation sinusoïdale
        
        size = int(cell_size * scale)
        # Calcule la taille actuelle en pixels (varie entre 90% et 110% de cell_size)
        
        offset_adjust = (cell_size - size) // 2
        # Calcule le décalage pour centrer l'image redimensionnée
        # Si size < cell_size, on doit décaler pour recentrer
        
        scaled_surface = pygame.transform.scale(self.surface, (size, size))
        # Redimensionne l'image à la taille actuelle de l'animation
        
        food_rec = pygame.Rect(
            OFFSET + self.position.x * cell_size + offset_adjust,
            OFFSET + self.position.y * cell_size + offset_adjust,
            size, size
        )
        # Crée un rectangle définissant la position et la taille de la nourriture
        # OFFSET + position * cell_size = conversion grille → pixels
        # + offset_adjust = centrage
        
        # === EFFET DE LUEUR (GLOW) ===
        glow_size = size + 6
        # La lueur est légèrement plus grande que la nourriture
        
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        # Crée une surface transparente pour la lueur
        
        glow_color = (255, 255, 100, 50) if self.food_type == 'apple' else (255, 150, 50, 50)
        # Couleur de la lueur avec transparence (dernière valeur = alpha)
        # Jaune pour pomme, orange pour champignon
        # 50 = assez transparent
        
        pygame.draw.circle(glow_surf, glow_color, (glow_size//2, glow_size//2), glow_size//2)
        # Dessine un cercle flou pour la lueur
        
        screen.blit(glow_surf, (food_rec.x - 3, food_rec.y - 3))
        # Dessine la lueur légèrement décalée derrière la nourriture
        # -3 pour centrer la lueur (puisqu'elle est +6 pixels plus grande)
        
        screen.blit(scaled_surface, food_rec)
        # Dessine l'image de la nourriture par-dessus la lueur

    def generate_random_cell(self):
        """
        Génère une position aléatoire sur la grille
        Returns:
            Vector2: Position (x, y) dans la grille
        """
        x = random.randint(0, number_of_cells - 1)
        # X aléatoire entre 0 et 19
        
        y = random.randint(0, number_of_cells - 1)
        # Y aléatoire entre 0 et 19
        
        return Vector2(x, y)
        # Retourne un vecteur 2D représentant la position

    def generate_random_pos(self, snake_body):
        """
        Génère une position aléatoire VALIDE pour la nourriture
        (ne doit pas être sur le serpent, les obstacles ou d'autres nourritures)
        Args:
            snake_body: Liste des positions du serpent
        Returns:
            Vector2: Position valide
        """
        position = self.generate_random_cell()
        # Génère une première position aléatoire
        
        while (position in snake_body or 
               position in self.obstacles_positions or 
               position in self.existing_food_positions):
            # Tant que la position est invalide (sur un obstacle/serpent/autre nourriture)
            
            position = self.generate_random_cell()
            # Génère une nouvelle position aléatoire
        
        return position
        # Retourne la position valide trouvée
    
    def get_points(self):
        """
        Retourne le nombre de points que cette nourriture rapporte
        Returns:
            int: Nombre de points (10 pour pomme, 15 pour champignon)
        """
        return FOOD_TYPES[self.food_type]['points']
        # Accède au dictionnaire FOOD_TYPES pour obtenir les points

class Obstacle:
    """
    Classe représentant un obstacle (mur) sur le terrain
    Le serpent meurt s'il touche un obstacle
    """
    
    def __init__(self, position):
        """
        Constructeur de l'obstacle
        Args:
            position: Vector2 représentant la position (x, y) dans la grille
        """
        self.position = position
        # Stocke la position de l'obstacle
        
        try:
            # Tente de charger l'image de brique
            
            self.brick_image = pygame.image.load('barier.png')
            # Charge l'image du fichier
            
            self.brick_image = pygame.transform.scale(self.brick_image, (cell_size, cell_size))
            # Redimensionne l'image à la taille d'une cellule
            
        except:
            # Si le chargement échoue
            
            self.brick_image = None
            # Pas d'image (on dessinera un rectangle simple)
    
    def draw(self, screen):
        """
        Dessine l'obstacle à l'écran
        Args:
            screen: Surface pygame où dessiner
        """
        x = OFFSET + self.position.x * cell_size
        # Calcule la position X en pixels
        
        y = OFFSET + self.position.y * cell_size
        # Calcule la position Y en pixels
        
        if self.brick_image:
            # Si l'image a été chargée avec succès
            
            screen.blit(self.brick_image, (x, y))
            # Dessine l'image de brique
            
        else:
            # Si pas d'image de brique chargée, dessine un rectangle avec texture de briques
            BRICK_RED = (192, 57, 43) # Couleur rouge brique
            BRICK_DARK = (169, 50, 38) # Couleur foncée pour les ombres
            BRICK_LIGHT = (205, 97, 85)  # Couleur claire pour les reflets
            
            # Crée un rectangle pour l'obstacle
            obstacle_rect = pygame.Rect(x, y, cell_size, cell_size)
            # Dessine le fond de la brique avec coins arrondis
            pygame.draw.rect(screen, BRICK_RED, obstacle_rect, border_radius=4)
            # Hauteur d'une rangée de briques (cellule divisée en 3 horizontalement)
            brick_height = cell_size // 3
            # Largeur d'une brique (cellule divisée en 2 verticalement)
            brick_width = cell_size // 2
            # Dessine le motif de briques (3 rangées)
            # Brique supérieure gauche
            pygame.draw.rect(screen, BRICK_DARK, (x, y, brick_width - 1, brick_height - 1))
            # Brique supérieure droite
            pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y, brick_width - 1, brick_height - 1))
            # Rangée du milieu (couleur claire) - brique entière
            pygame.draw.rect(screen, BRICK_LIGHT, (x, y + brick_height, cell_size, brick_height - 1))
            # Brique inférieure gauche
            pygame.draw.rect(screen, BRICK_DARK, (x, y + 2 * brick_height, brick_width - 1, brick_height))
            # Brique inférieure droite
            pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y + 2 * brick_height, brick_width - 1, brick_height))
            # Dessine une bordure autour de l'obstacle (largeur 2 pixels)
            pygame.draw.rect(screen, BRICK_DARK, obstacle_rect, 2, border_radius=4)


class Snake:
    """
    Classe représentant le serpent du joueur
    Gère le mouvement, l'affichage et les collisions du serpent
    """
    def __init__(self, theme):
        """
        Constructeur du serpent
        Args:
            theme: Dictionnaire de couleurs pour le thème visuel
        """
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        # Corps initial du serpent: 3 segments
        # Position [0] = tête (6, 9)
        # Positions [1] et [2] = corps (5, 9) et (4, 9)
        # Le serpent démarre orienté vers la droite
        
        self.direction = Vector2(1, 0)
        # Direction initiale: (1, 0) = vers la droite
        # (0, -1) = haut, (0, 1) = bas, (-1, 0) = gauche
        
        self.add_segment = False
        # Flag booléen: True = ajouter un segment au prochain update
        # Devient True quand le serpent mange de la nourriture
        
        self.theme = theme
        # Stocke le thème de couleurs pour l'affichage
        
        self.trail = []  # Trail effect
        # Liste pour stocker les positions de la traînée visuelle
        # Crée un effet de "queue fantôme" derrière le serpent
        
        try:
            # Tente de charger les effets sonores
            
            self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
            # Son joué quand le serpent mange
            
            self.wall_hit_sound = pygame.mixer.Sound("snake_collision.wav")
            # Son joué lors d'une collision (game over)
            
        except:
            # Si les fichiers son n'existent pas
            
            self.eat_sound = None
            self.wall_hit_sound = None
            # Pas de son (le jeu continue sans audio)
   
    def draw(self, screen):
        """
        Dessine le serpent à l'écran avec tous les effets visuels
        Args:
            screen: Surface pygame où dessiner
        """
        
        # === DESSINER L'EFFET DE TRAÎNÉE ===
        for i, pos in enumerate(self.trail):
            # Pour chaque position dans la traînée
            # i = index (0 = plus récente, len-1 = plus ancienne)
            # pos = position Vector2
            
            alpha = int(100 * (1 - i / len(self.trail)))
            # Calcule la transparence: 100 pour la plus récente, 0 pour la plus ancienne
            # Crée un effet de fondu progressif
            
            trail_surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            # Crée une surface transparente pour dessiner la traînée
            
            color = (*self.theme['trail'], alpha)
            # Ajoute la transparence à la couleur du thème
            # (*color, alpha) = (R, G, B, A)
            
            pygame.draw.circle(trail_surf, color, (cell_size//2, cell_size//2), cell_size//3)
            # Dessine un cercle pour la traînée (plus petit que la tête)
            
            screen.blit(trail_surf, (OFFSET + pos.x * cell_size, OFFSET + pos.y * cell_size))
            # Affiche la traînée à la position calculée
        
        # === DESSINER LE CORPS DU SERPENT ===
        for i, seg in enumerate(self.snake_body):
            # Pour chaque segment du corps
            # i = 0 pour la tête, i > 0 pour le corps
            
            seg_rect = pygame.Rect(OFFSET + seg.x * cell_size,
                                   OFFSET + seg.y * cell_size, 
                                   cell_size, cell_size)
            # Crée un rectangle pour ce segment
            # Convertit position grille → pixels
            
            if i == 0:  # HEAD (TÊTE)
                # === EFFET DE LUEUR AUTOUR DE LA TÊTE ===
                glow_surf = pygame.Surface((cell_size + 10, cell_size + 10), pygame.SRCALPHA)
                # Surface plus grande pour la lueur (10 pixels de plus)
                
                pygame.draw.circle(glow_surf, (*self.theme['snake_head'], 80), 
                                 ((cell_size + 10)//2, (cell_size + 10)//2), (cell_size + 10)//2)
                # Dessine un cercle semi-transparent pour la lueur
                # 80 = alpha (assez transparent)
                
                screen.blit(glow_surf, (seg_rect.x - 5, seg_rect.y - 5))
                # Affiche la lueur centrée sur la tête
                
                # === DESSINER LA TÊTE ===
                pygame.draw.rect(screen, self.theme['snake_head'], seg_rect, border_radius=8)
                # Rectangle avec coins arrondis pour la tête
                
                # === DESSINER LES YEUX ===
                eye_size = 4
                # Rayon des yeux en pixels
                
                eye_offset = 5
                # Distance entre les yeux et le centre
                
                # Yeux blancs (sclère)
                pygame.draw.circle(screen, WHITE, (seg_rect.centerx - eye_offset, seg_rect.centery - 3), eye_size)
                # Œil gauche
                
                pygame.draw.circle(screen, WHITE, (seg_rect.centerx + eye_offset, seg_rect.centery - 3), eye_size)
                # Œil droit
                
                # Pupilles noires
                pygame.draw.circle(screen, BLACK, (seg_rect.centerx - eye_offset, seg_rect.centery - 3), 2)
                # Pupille gauche
                
                pygame.draw.circle(screen, BLACK, (seg_rect.centerx + eye_offset, seg_rect.centery - 3), 2)
                # Pupille droite
                
            else:  # BODY (CORPS)
                # === DÉGRADÉ DE COULEUR SUR LE CORPS ===
                ratio = i / len(self.snake_body)
                # Calcule le ratio de position: 0 (proche de la tête) à 1 (bout de la queue)
                
                color = tuple(int(self.theme['snake'][j] + (self.theme['trail'][j] - self.theme['snake'][j]) * ratio) for j in range(3))
                # Interpolation linéaire entre la couleur du serpent et la couleur de la traînée
                # Crée un dégradé progressif du corps vers la queue
                # Pour chaque composante RGB (j in range(3))
                
                pygame.draw.rect(screen, color, seg_rect, border_radius=7)
                # Dessine le segment du corps avec la couleur calculée
                
                # === EFFET DE BRILLANCE (HIGHLIGHT) ===
                highlight = pygame.Rect(seg_rect.x + 2, seg_rect.y + 2, cell_size - 4, cell_size - 4)
                # Rectangle plus petit à l'intérieur du segment
                
                pygame.draw.rect(screen, (*color, 50), highlight, border_radius=5)
                # Dessine un rectangle semi-transparent pour simuler une brillance
                # 50 = alpha (très transparent)


    def update(self):
        """
        Met à jour la position du serpent (appelé à chaque frame de jeu)
        Gère le mouvement et la croissance
        """
        
        # === METTRE À JOUR LA TRAÎNÉE ===
        if len(self.snake_body) > 0:
            # Si le serpent existe
            
            self.trail.insert(0, self.snake_body[-1].copy())
            # Ajoute la position du dernier segment (queue) au début de la traînée
            # copy() crée une copie pour éviter les références
            
            if len(self.trail) > 8:
                # Si la traînée est trop longue
                
                self.trail.pop()
                # Supprime l'élément le plus ancien (à la fin de la liste)
        
        # === CALCULER LA NOUVELLE POSITION DE LA TÊTE ===
        new_head = self.snake_body[0] + self.direction
        # Position actuelle de la tête + vecteur de direction
        # Ex: (6, 9) + (1, 0) = (7, 9) si on va à droite
        
        new_head.x = new_head.x % number_of_cells
        # Modulo pour créer un effet de "wraparound" horizontal
        # Si x = 20, alors x % 20 = 0 (réapparaît de l'autre côté)
        
        new_head.y = new_head.y % number_of_cells
        # Modulo pour créer un effet de "wraparound" vertical
        
        # === AJOUTER LA NOUVELLE TÊTE ===
        self.snake_body.insert(0, new_head)
        # Insère la nouvelle position au début de la liste
        # L'ancien segment [0] devient [1], etc.
        
        # === GÉRER LA CROISSANCE ===
        if self.add_segment:
            # Si le serpent a mangé (flag activé)
            
            self.add_segment = False
            # Réinitialise le flag
            # On ne supprime PAS le dernier segment → le serpent grandit
            
        else:
            # Si le serpent n'a pas mangé
            
            self.snake_body = self.snake_body[:-1]
            # Supprime le dernier segment
            # Maintient la longueur constante (mouvement normal)
 
    def reset(self):
        """
        Réinitialise le serpent à son état initial (appelé au game over)
        """
        self.snake_body = [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]
        # Repositionne le serpent à sa position de départ (3 segments)
        
        self.direction = Vector2(1, 0)
        # Réinitialise la direction vers la droite
        
        self.trail = []
        # Efface la traînée

    def check_collision_with_obstacles(self, obstacles):
        """
        Vérifie si la tête du serpent touche un obstacle
        Args:
            obstacles: Liste d'objets Obstacle
        Returns:
            bool: True si collision, False sinon
        """
        for obstacle in obstacles:
            # Pour chaque obstacle sur le terrain
            
            if self.snake_body[0] == obstacle.position:
                # Si la position de la tête == position de l'obstacle
                
                return True
                # Collision détectée!
        
        return False
        # Aucune collision


class Game:
    """
    Classe principale qui gère toute la logique du jeu
    Coordonne le serpent, la nourriture, les obstacles et le score
    """
    
    def __init__(self, player_name, level, theme_key):
        """
        Constructeur du jeu
        Args:
            player_name: Nom du joueur
            level: Numéro du niveau (1, 2 ou 3)
            theme_key: Clé du thème de couleurs ('neon', 'sunset', etc.)
        """
        self.player_name = player_name
        # Stocke le nom du joueur pour l'affichage et la sauvegarde des scores
        
        self.level = level
        # Stocke le numéro du niveau choisi
        
        self.level_config = LEVELS[level]
        # Récupère la configuration du niveau (vitesse, obstacles, etc.)
        # Ex: LEVELS[2] = {'name': 'Intermédiaire', 'speed': 150, ...}
        
        self.theme = COLOR_THEMES[theme_key]
        # Récupère le thème de couleurs choisi
        # Ex: COLOR_THEMES['neon'] = {'name': 'Neon Cyber', 'bg_start': ...}
        
        self.snake = Snake(self.theme)
        # Crée l'objet serpent avec le thème
        
        self.state = "RUNNING"
        # État du jeu: "RUNNING" (en cours) ou "STOPPED" (game over)
        
        self.score = 0
        # Score initial à 0
        
        self.particles = []
        # Liste pour stocker les effets de particules actifs
        
        # === GÉNÉRATION DES OBSTACLES ===
        self.obstacles = self.generate_obstacles(self.level_config['obstacles'])
        # Génère les obstacles selon le niveau (3, 6 ou 10)
        
        self.obstacles_positions = [obs.position for obs in self.obstacles]
        # Crée une liste de toutes les positions d'obstacles
        # Utilisé pour vérifier rapidement les collisions
        
        # === CRÉATION DE LA NOURRITURE ===
        self.food1 = Food(self.snake.snake_body, self.obstacles_positions, 'apple')
        # Crée une pomme (10 points)
        # Évite les positions du serpent et des obstacles
        
        self.food2 = Food(self.snake.snake_body, self.obstacles_positions, 'mushroom', [self.food1.position])
        # Crée un champignon (15 points)
        # Évite également la position de food1

    def generate_obstacles(self, count):
        """
        Génère un nombre spécifique d'obstacles à des positions aléatoires
        Args:
            count: Nombre d'obstacles à générer
        Returns:
            list: Liste d'objets Obstacle
        """
        obstacles = []
        # Liste vide pour stocker les obstacles
        
        for _ in range(count):
            # Répète 'count' fois (3, 6 ou 10 selon le niveau)
            
            while True:
                # Boucle infinie jusqu'à trouver une position valide
                
                x = random.randint(0, number_of_cells - 1)
                # X aléatoire entre 0 et 19
                
                y = random.randint(0, number_of_cells - 1)
                # Y aléatoire entre 0 et 19
                
                position = Vector2(x, y)
                # Crée un vecteur pour la position
                
                # === VÉRIFICATIONS DE VALIDITÉ ===
                if position not in [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)]:
                    # Vérifie que l'obstacle n'est PAS sur la position initiale du serpent
                    # [Vector2(6, 9), Vector2(5, 9), Vector2(4, 9)] = corps initial du serpent
                    
                    if all(obs.position != position for obs in obstacles):
                        # Vérifie qu'aucun obstacle existant n'est déjà à cette position
                        # all() retourne True si tous les obstacles sont différents
                        
                        obstacles.append(Obstacle(position))
                        # Position valide trouvée! Crée et ajoute l'obstacle
                        
                        break
                        # Sort de la boucle while pour passer à l'obstacle suivant
        
        return obstacles
        # Retourne la liste complète des obstacles générés

    def draw(self, screen):
        """
        Dessine tous les éléments du jeu à l'écran
        Args:
            screen: Surface pygame où dessiner
        """
        self.snake.draw(screen)
        # Dessine le serpent (corps, tête, yeux, traînée)
        
        self.food1.draw(screen)
        # Dessine la première nourriture (pomme)
        
        self.food2.draw(screen)
        # Dessine la deuxième nourriture (champignon)
        
        for obstacle in self.obstacles:
            # Pour chaque obstacle
            obstacle.draw(screen)
            # Dessine l'obstacle
        
        # === DESSINER LES EFFETS DE PARTICULES ===
        for particle in self.particles:
            # Pour chaque effet de particules actif
            particle.draw(screen)
            # Dessine l'effet

    def update(self):
        """
        Met à jour la logique du jeu (appelé à chaque frame)
        Gère le mouvement, les collisions et l'état du jeu
        """
        if self.state == "RUNNING":
            # Si le jeu est en cours (pas en game over)
            
            self.snake.update()
            # Met à jour la position du serpent
            
            self.check_collision_with_food()
            # Vérifie si le serpent a mangé de la nourriture
            
            self.check_collision_with_tail()
            # Vérifie si le serpent s'est mordu la queue
            
            if self.snake.check_collision_with_obstacles(self.obstacles):
                # Vérifie si le serpent a touché un obstacle
                
                self.game_over()
                # Déclenche le game over
        
        # === METTRE À JOUR LES PARTICULES ===
        for particle in self.particles:
            # Pour chaque effet de particules
            
            particle.update()
            # Met à jour l'animation (mouvement, gravité, vie)
        
        self.particles = [p for p in self.particles if len(p.particles) > 0]
        # Filtre: garde seulement les effets qui ont encore des particules vivantes
        # Supprime les effets terminés

    def check_collision_with_food(self):
        """
        Vérifie si le serpent a mangé de la nourriture
        Gère les points, la croissance et les effets
        """
        head_pos = self.snake.snake_body[0]
        # Position de la tête du serpent
        
        # === VÉRIFIER COLLISION AVEC FOOD1 (POMME) ===
        if head_pos == self.food1.position:
            # Si la tête est sur la pomme
            
            # === CRÉER L'EFFET DE PARTICULES ===
            x = OFFSET + head_pos.x * cell_size + cell_size // 2
            # Position X du centre de la cellule (en pixels)
            
            y = OFFSET + head_pos.y * cell_size + cell_size // 2
            # Position Y du centre de la cellule (en pixels)
            
            self.particles.append(ParticleEffect(x, y, RED))
            # Crée un effet de particules rouges
            
            # === REPOSITIONNER LA NOURRITURE ===
            self.food1.position = self.food1.generate_random_pos(self.snake.snake_body)
            # Génère une nouvelle position aléatoire valide
            
            self.snake.add_segment = True
            # Active le flag pour faire grandir le serpent
            
            self.score += self.food1.get_points()
            # Ajoute les points au score (10 pour une pomme)
            
            if self.snake.eat_sound:
                # Si le son existe
                
                self.snake.eat_sound.play()
                # Joue le son de manger
        
        # === VÉRIFIER COLLISION AVEC FOOD2 (CHAMPIGNON) ===
        if head_pos == self.food2.position:
            # Même logique pour le champignon
            
            x = OFFSET + head_pos.x * cell_size + cell_size // 2
            y = OFFSET + head_pos.y * cell_size + cell_size // 2
            self.particles.append(ParticleEffect(x, y, ORANGE))
            # Particules oranges pour le champignon
            
            self.food2.position = self.food2.generate_random_pos(self.snake.snake_body)
            self.snake.add_segment = True
            self.score += self.food2.get_points()
            # 15 points pour un champignon
            
            if self.snake.eat_sound:
                self.snake.eat_sound.play()

    def game_over(self):
        """
        Gère la logique du game over
        Réinitialise le jeu et joue le son de collision
        """
        self.snake.reset()
        # Réinitialise le serpent à sa position de départ
        
        self.food1.position = self.food1.generate_random_pos(self.snake.snake_body)
        # Repositionne food1
        
        self.food2.position = self.food2.generate_random_pos(self.snake.snake_body)
        # Repositionne food2
        
        self.state = "STOPPED"
        # Change l'état du jeu en "arrêté"
        
        self.score = 0
        # Réinitialise le score à 0
        
        if self.snake.wall_hit_sound:
            # Si le son de collision existe
            
            self.snake.wall_hit_sound.play()
            # Joue le son

    def check_collision_with_tail(self):
        """
        Vérifie si la tête du serpent touche son propre corps
        """
        headless_body = self.snake.snake_body[1:]
        # Corps sans la tête (segments de index 1 à la fin)
        # [1:] = slice Python qui exclut le premier élément
        
        if self.snake.snake_body[0] in headless_body:
            # Si la position de la tête est dans le reste du corps
            
            self.game_over()
            # Le serpent s'est mordu → game over
   
    def draw_game_over(self, screen):
        """
        Affiche l'écran de Game Over par-dessus le jeu
        Args:
            screen: Surface pygame où dessiner
        """
        
        # === CRÉER UN OVERLAY SEMI-TRANSPARENT ===
        overlay = pygame.Surface((cell_size * number_of_cells, cell_size * number_of_cells), pygame.SRCALPHA)
        # Crée une surface de la taille du terrain de jeu avec support de transparence
        # SRCALPHA permet d'avoir un canal alpha (transparence)
        
        overlay.fill((*BLACK, 200))
        # Remplit avec du noir semi-transparent
        # (*BLACK, 200) = (0, 0, 0, 200) où 200 = opacité (sur 255)
        # Assombrit le jeu sans le cacher complètement
        
        screen.blit(overlay, (OFFSET, OFFSET))
        # Affiche l'overlay à la position du terrain de jeu
        
        # === TEXTE "GAME OVER" ===
        font = pygame.font.Font(None, 80)
        # Police grande taille (80 pixels)
        
        text = font.render('GAME OVER', True, RED)
        # Rend le texte en rouge
        
        text_rect = text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                         OFFSET + number_of_cells * cell_size // 2 - 80))
        # Centre le texte au milieu du terrain, décalé de 80 pixels vers le haut
        # center= définit la position du centre du texte
        
        # === OMBRE PORTÉE POUR LE TEXTE ===
        shadow = font.render('GAME OVER', True, BLACK)
        # Même texte en noir pour l'ombre
        
        shadow_rect = shadow.get_rect(center=(text_rect.centerx + 3, text_rect.centery + 3))
        # Positionne l'ombre légèrement décalée (+3, +3) par rapport au texte
        
        screen.blit(shadow, shadow_rect)
        # Dessine d'abord l'ombre
        
        screen.blit(text, text_rect)
        # Puis le texte par-dessus
        
        # === AFFICHAGE DU NOM DU JOUEUR ===
        name_font = pygame.font.Font(None, 40)
        # Police moyenne (40 pixels)
        
        name_text = name_font.render(f'Player: {self.player_name}', True, WHITE)
        # Affiche le nom du joueur en blanc
        
        name_rect = name_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                               OFFSET + number_of_cells * cell_size // 2 - 20))
        # Centre en dessous du "GAME OVER"
        
        screen.blit(name_text, name_rect)
        # Affiche le nom
        
        # === INSTRUCTION DE REDÉMARRAGE ===
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render('Press Any Key to Continue', True, GOLD)
        # Texte en or pour attirer l'attention
        
        restart_rect = restart_text.get_rect(center=(OFFSET + number_of_cells * cell_size // 2, 
                                                     OFFSET + number_of_cells * cell_size // 2 + 80))
        # Centre en dessous du nom du joueur
        
        screen.blit(restart_text, restart_rect)
        # Affiche l'instruction

def select_theme():
    """
    Écran de sélection du thème de couleurs
    Permet au joueur de choisir parmi les 6 thèmes disponibles
    Returns:
        str: Clé du thème sélectionné ('neon', 'sunset', etc.)
    """
    screen = pygame.display.set_mode((900, 600))
    # Crée une fenêtre de 900x600 pixels pour la sélection
    
    pygame.display.set_caption("🎨 Choose Your Snake Color")
    # Définit le titre de la fenêtre
    
    clock = pygame.time.Clock()
    # Horloge pour contrôler le FPS
    
    selected = 0
    # Index du thème actuellement sélectionné (0-5)
    
    themes_list = list(COLOR_THEMES.keys())
    # Crée une liste des clés: ['neon', 'sunset', 'ocean', 'forest', 'fire', 'galaxy']
    
    while True:
        # Boucle infinie jusqu'à ce que le joueur confirme son choix
        
        # === ARRIÈRE-PLAN ANIMÉ BASÉ SUR LE THÈME SÉLECTIONNÉ ===
        theme = COLOR_THEMES[themes_list[selected]]
        # Récupère le thème actuellement sélectionné
        
        for y in range(600):
            # Pour chaque ligne horizontale de pixels
            
            ratio = y / 600
            # Ratio de 0 (haut) à 1 (bas)
            
            color = tuple(int(theme['bg_start'][i] + (theme['bg_end'][i] - theme['bg_start'][i]) * ratio) for i in range(3))
            # Interpolation linéaire entre bg_start et bg_end
            # Crée un dégradé vertical
            # Pour chaque composante RGB (i in range(3))
            
            pygame.draw.line(screen, color, (0, y), (900, y))
            # Dessine une ligne horizontale avec cette couleur
        
        # === TITRE ===
        title_font = pygame.font.Font(None, 70)
        title = title_font.render("Choose Your Snake Style", True, WHITE)
        title_rect = title.get_rect(center=(450, 60))
        # Centre le titre à 60 pixels du haut
        
        # Ombre du titre
        shadow = title_font.render("Choose Your Snake Style", True, BLACK)
        shadow_rect = shadow.get_rect(center=(452, 62))
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
        
        # === OPTIONS DE THÈME ===
        y_start = 150
        # Position Y du premier thème
        
        spacing = 70
        # Espacement vertical entre chaque thème
        
        for i, (key, theme_data) in enumerate(COLOR_THEMES.items()):
            # Pour chaque thème (i = index, key = 'neon', theme_data = dictionnaire)
            
            y = y_start + i * spacing
            # Calcule la position Y de ce thème
            
            # === SURBRILLANCE SI SÉLECTIONNÉ ===
            if i == selected:
                # Si c'est le thème actuellement sélectionné
                
                highlight_rect = pygame.Rect(50, y - 5, 800, 60)
                # Rectangle pour la surbrillance
                
                pygame.draw.rect(screen, (*theme_data['accent'], 100), highlight_rect, border_radius=10)
                # Fond semi-transparent de la couleur d'accent du thème
                
                pygame.draw.rect(screen, theme_data['accent'], highlight_rect, 3, border_radius=10)
                # Bordure de 3 pixels de la couleur d'accent
            
            # === APERÇU DE LA COULEUR ===
            preview_rect = pygame.Rect(70, y + 5, 40, 40)
            # Petit carré pour l'aperçu
            
            pygame.draw.rect(screen, theme_data['snake'], preview_rect, border_radius=8)
            # Remplit avec la couleur du serpent
            
            pygame.draw.rect(screen, theme_data['snake_head'], preview_rect, 3, border_radius=8)
            # Bordure avec la couleur de la tête
            
            # === NOM DU THÈME ===
            name_font = pygame.font.Font(None, 48)
            name_text = name_font.render(theme_data['name'], True, WHITE)
            # Ex: "Neon Cyber", "Sunset Vibes", etc.
            
            screen.blit(name_text, (130, y + 10))
            # Affiche à côté de l'aperçu
            
            # === FLÈCHE POUR LE THÈME SÉLECTIONNÉ ===
            if i == selected:
                arrow_font = pygame.font.Font(None, 60)
                arrow = arrow_font.render("→", True, theme_data['accent'])
                # Flèche de la couleur d'accent
                
                screen.blit(arrow, (750, y + 5))
                # Affiche à droite
        
        # === INSTRUCTIONS ===
        inst_font = pygame.font.Font(None, 32)
        inst = inst_font.render("↑↓ Select  |  ENTER Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(450, 550))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        # Met à jour l'affichage
        
        # === GESTION DES ÉVÉNEMENTS ===
        for event in pygame.event.get():
            # Pour chaque événement
            
            if event.type == pygame.QUIT:
                # Si le joueur ferme la fenêtre
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Si une touche est pressée
                
                if event.key == pygame.K_UP:
                    # Flèche haut
                    selected = (selected - 1) % len(themes_list)
                    # Décrémente avec wraparound (5 → 0 → 5)
                    
                elif event.key == pygame.K_DOWN:
                    # Flèche bas
                    selected = (selected + 1) % len(themes_list)
                    # Incrémente avec wraparound (0 → 5 → 0)
                    
                elif event.key == pygame.K_RETURN:
                    # Touche Entrée
                    return themes_list[selected]
                    # Retourne la clé du thème sélectionné et quitte la fonction
        
        clock.tick(60)
        # Limite à 60 FPS


def select_level():
    """
    Écran de sélection du niveau de difficulté
    Affiche 3 cartes pour les niveaux Débutant, Intermédiaire et Expert
    Returns:
        int: Numéro du niveau sélectionné (1, 2 ou 3)
    """
    screen = pygame.display.set_mode((900, 600))
    # Fenêtre 900x600
    
    pygame.display.set_caption("🎯 Choose Difficulty Level")
    # Titre de la fenêtre
    
    clock = pygame.time.Clock()
    selected = 1
    # Niveau initial sélectionné = 1 (Débutant)
    
    while True:
        # === ARRIÈRE-PLAN DYNAMIQUE ===
        level_color = LEVELS[selected]['color']
        # Couleur du niveau sélectionné
        
        for y in range(600):
            # Pour chaque ligne
            
            ratio = y / 600
            # Ratio vertical
            
            # Calcul de dégradé basé sur la couleur du niveau
            r = int(20 + (level_color[0] - 20) * ratio * 0.3)
            g = int(20 + (level_color[1] - 20) * ratio * 0.3)
            b = int(40 + (level_color[2] - 40) * ratio * 0.3)
            # Dégradé subtil (facteur 0.3) pour ne pas être trop intense
            
            pygame.draw.line(screen, (r, g, b), (0, y), (900, y))
            # Dessine la ligne
        
        # === TITRE ===
        title_font = pygame.font.Font(None, 70)
        title = title_font.render("Select Difficulty", True, WHITE)
        title_rect = title.get_rect(center=(450, 60))
        
        shadow = title_font.render("Select Difficulty", True, BLACK)
        shadow_rect = shadow.get_rect(center=(452, 62))
        screen.blit(shadow, shadow_rect)
        screen.blit(title, title_rect)
        
        # === CARTES DE NIVEAU ===
        card_width = 250
        # Largeur de chaque carte
        
        card_height = 300
        # Hauteur de chaque carte
        
        x_start = (900 - (card_width * 3 + 60)) // 2
        # Calcule la position X de départ pour centrer les 3 cartes
        # 60 = espacement entre les cartes (30 pixels * 2)
        
        y_pos = 180
        # Position Y des cartes
        
        for level_num in [1, 2, 3]:
            # Pour chaque niveau
            
            x = x_start + (level_num - 1) * (card_width + 30)
            # Calcule la position X de cette carte
            # level 1: x_start + 0
            # level 2: x_start + 280
            # level 3: x_start + 560
            
            # === RECTANGLE DE LA CARTE ===
            card_rect = pygame.Rect(x, y_pos, card_width, card_height)
            
            if level_num == selected:
                # Si c'est le niveau sélectionné
                
                # === EFFET DE LUEUR ===
                glow_rect = pygame.Rect(x - 5, y_pos - 5, card_width + 10, card_height + 10)
                # Rectangle légèrement plus grand
                
                pygame.draw.rect(screen, LEVELS[level_num]['color'], glow_rect, border_radius=20)
                # Dessine la lueur avec la couleur du niveau
                
                pygame.draw.rect(screen, (*LEVELS[level_num]['color'], 150), card_rect, border_radius=15)
                # Fond semi-transparent de la carte
                
            else:
                # Si ce n'est pas le niveau sélectionné
                
                pygame.draw.rect(screen, (40, 40, 60), card_rect, border_radius=15)
                # Fond gris foncé
            
            pygame.draw.rect(screen, LEVELS[level_num]['color'], card_rect, 3, border_radius=15)
            # Bordure de 3 pixels avec la couleur du niveau
            
            # === NUMÉRO DU NIVEAU ===
            num_font = pygame.font.Font(None, 100)
            # Grande police pour le numéro
            
            num_text = num_font.render(str(level_num), True, LEVELS[level_num]['color'])
            # Affiche "1", "2" ou "3" avec la couleur du niveau
            
            num_rect = num_text.get_rect(center=(x + card_width // 2, y_pos + 60))
            # Centre le numéro dans le haut de la carte
            
            screen.blit(num_text, num_rect)
            
            # === NOM DU NIVEAU ===
            name_font = pygame.font.Font(None, 40)
            name = name_font.render(LEVELS[level_num]['name'], True, WHITE)
            # "Débutant", "Intermédiaire" ou "Expert"
            
            name_rect = name.get_rect(center=(x + card_width // 2, y_pos + 130))
            screen.blit(name, name_rect)
            
            # === DESCRIPTION ===
            desc_font = pygame.font.Font(None, 24)
            desc = desc_font.render(LEVELS[level_num]['description'], True, (200, 200, 200))
            # "Facile - Vitesse normale", etc.
            
            desc_rect = desc.get_rect(center=(x + card_width // 2, y_pos + 170))
            screen.blit(desc, desc_rect)
            
            # === STATISTIQUES ===
            stats_font = pygame.font.Font(None, 26)
            
            speed_text = f"Vitesse: {200 - LEVELS[level_num]['speed']}%"
            # Calcule un pourcentage de vitesse
            # Level 1: 200-200 = 0% (référence)
            # Level 2: 200-150 = 50% (plus rapide)
            # Level 3: 200-100 = 100% (très rapide)
            
            obstacles_text = f"Murs: {LEVELS[level_num]['obstacles']}"
            # "Murs: 3", "Murs: 6" ou "Murs: 10"
            
            speed = stats_font.render(speed_text, True, WHITE)
            obstacles = stats_font.render(obstacles_text, True, WHITE)
            
            screen.blit(speed, (x + 20, y_pos + 210))
            # Affiche la vitesse
            
            screen.blit(obstacles, (x + 20, y_pos + 245))
            # Affiche le nombre de murs
        
        # === INSTRUCTIONS ===
        inst_font = pygame.font.Font(None, 32)
        inst = inst_font.render("←→ Select  |  ENTER Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(450, 550))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        # === GESTION DES ÉVÉNEMENTS ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # Flèche gauche
                    selected = max(1, selected - 1)
                    # Décrémente mais pas en dessous de 1
                    
                elif event.key == pygame.K_RIGHT:
                    # Flèche droite
                    selected = min(3, selected + 1)
                    # Incrémente mais pas au-dessus de 3
                    
                elif event.key == pygame.K_RETURN:
                    # Entrée
                    return selected
                    # Retourne le niveau sélectionné
        
        clock.tick(60)


def get_player_name():
    """
    Écran de saisie du nom du joueur
    Interface moderne avec curseur clignotant
    Returns:
        str: Nom du joueur saisi
    """
    screen = pygame.display.set_mode((700, 400))
    # Fenêtre 700x400
    
    pygame.display.set_caption("Enter Your Name")
    
    font = pygame.font.Font(None, 48)
    # Police pour le titre
    
    small_font = pygame.font.Font(None, 32)
    # Police pour le texte saisi
    
    player_name = ""
    # Chaîne vide pour stocker le nom
    
    clock = pygame.time.Clock()
    
    while True:
        # === ARRIÈRE-PLAN DÉGRADÉ ===
        for y in range(400):
            ratio = y / 400
            r = int(30 + (60 - 30) * ratio)
            g = int(30 + (80 - 30) * ratio)
            b = int(60 + (120 - 60) * ratio)
            # Dégradé bleu/violet
            
            pygame.draw.line(screen, (r, g, b), (0, y), (700, y))
        
        # === TITRE ===
        title = font.render("Enter Your Name", True, WHITE)
        title_rect = title.get_rect(center=(350, 80))
        screen.blit(title, title_rect)
        
        # === BOÎTE DE SAISIE ===
        input_rect = pygame.Rect(100, 180, 500, 60)
        # Rectangle de 500x60 pixels
        
        pygame.draw.rect(screen, (40, 40, 80), input_rect, border_radius=10)
        # Fond bleu foncé avec coins arrondis
        
        pygame.draw.rect(screen, (100, 150, 255), input_rect, 3, border_radius=10)
        # Bordure bleue de 3 pixels
        
        # === TEXTE SAISI ===
        text_surface = small_font.render(player_name, True, WHITE)
        # Rend le texte saisi
        
        screen.blit(text_surface, (120, 195))
        # Affiche avec un petit décalage depuis le bord
        
        # === CURSEUR CLIGNOTANT ===
        if pygame.time.get_ticks() % 1000 < 500:
            # Si le nombre de millisecondes depuis le démarrage modulo 1000 < 500
            # Crée un effet de clignotement: visible 500ms, invisible 500ms
            
            cursor_x = 120 + text_surface.get_width() + 5
            # Position X du curseur = après le texte + 5 pixels
            
            pygame.draw.line(screen, WHITE, (cursor_x, 190), (cursor_x, 230), 2)
            # Dessine une ligne verticale de 2 pixels d'épaisseur
        
        # === INSTRUCTION ===
        inst = small_font.render("Press ENTER to continue", True, (200, 200, 200))
        inst_rect = inst.get_rect(center=(350, 320))
        screen.blit(inst, inst_rect)
        
        pygame.display.flip()
        
        # === GESTION DES ÉVÉNEMENTS ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                # Si une touche est pressée
                
                if event.key == pygame.K_RETURN and player_name:
                    # Si Entrée ET le nom n'est pas vide
                    return player_name
                    # Retourne le nom et quitte
                    
                elif event.key == pygame.K_BACKSPACE:
                    # Si Backspace
                    player_name = player_name[:-1]
                    # Supprime le dernier caractère
                    # "Hello" → "Hell"
                    
                elif len(player_name) < 15 and event.unicode.isprintable():
                    # Si le nom a moins de 15 caractères ET
                    # le caractère est imprimable (pas une touche spéciale)
                    
                    player_name += event.unicode
                    # Ajoute le caractère au nom
        
        clock.tick(60)


# === APPEL DES FONCTIONS DE SÉLECTION ===
player_name = get_player_name()
# Obtient le nom du joueur

theme_key = select_theme()
# Obtient le thème choisi ('neon', 'sunset', etc.)

level = select_level()
# Obtient le niveau choisi (1, 2 ou 3)

# === CRÉATION DE LA FENÊTRE DE JEU ===
screen = pygame.display.set_mode((2*OFFSET + cell_size * number_of_cells, 
                                  2*OFFSET + cell_size * number_of_cells))
# Taille de la fenêtre:
# 2*OFFSET = marges haut et bas (2 * 75 = 150)
# cell_size * number_of_cells = terrain (20 * 20 = 400)
# Total: 550x550 pixels

pygame.display.set_caption(f"Snake Game - {LEVELS[level]['name']}")
# Titre de la fenêtre: "Snake Game - Débutant" par exemple

# === CRÉATION DE L'OBJET JEU ===
game = Game(player_name, level, theme_key)
# Crée une instance du jeu avec les paramètres choisis

clock = pygame.time.Clock()
# Horloge pour contrôler le FPS

running = True
# Flag pour la boucle principale

# === CONFIGURATION DE L'ÉVÉNEMENT DE MOUVEMENT ===
SNAKE_MOVE_EVENT = pygame.USEREVENT + 1
# Crée un type d'événement personnalisé
# pygame.USEREVENT est le premier ID d'événement personnalisé
# +1 pour éviter les conflits

pygame.time.set_timer(SNAKE_MOVE_EVENT, LEVELS[level]['speed'])
# Crée un timer qui génère SNAKE_MOVE_EVENT toutes les X millisecondes
# X = vitesse du niveau (200, 150 ou 100 ms)
# Plus le nombre est petit, plus le serpent va vite


# ===== LIGNES 719-740: BOUCLE PRINCIPALE - GESTION DES ÉVÉNEMENTS =====

while running:
    # Boucle principale du jeu
    
    for event in pygame.event.get():
        # Pour chaque événement dans la file d'événements
        
        # === ÉVÉNEMENT DE MOUVEMENT DU SERPENT ===
        if event.type == SNAKE_MOVE_EVENT:
            # Si c'est notre timer personnalisé
            
            game.update()
            # Met à jour la logique du jeu (mouvement, collisions, etc.)

        # === REDÉMARRAGE APRÈS GAME OVER ===
        if event.type == pygame.KEYDOWN:
            # Si une touche est pressée
            
            if game.state == "STOPPED":
                # Si le jeu est en état game over
                
                game.state = "RUNNING"
                # Redémarre le jeu
                # (le serpent a déjà été réinitialisé par game_over())

        # === CONTRÔLES DU SERPENT ===
        if event.type == pygame.KEYDOWN:
            # Si une touche est pressée
            
            if event.key == pygame.K_UP and game.snake.direction != Vector2(0, 1):
                # Flèche HAUT ET le serpent ne va PAS vers le bas
                # (empêche de faire demi-tour à 180°)
                
                game.snake.direction = Vector2(0, -1)
                # Change la direction vers le haut
                # Y négatif = vers le haut (système de coordonnées pygame)
                
            if event.key == pygame.K_DOWN and game.snake.direction != Vector2(0, -1):
                # Flèche BAS ET le serpent ne va PAS vers le haut
                
                game.snake.direction = Vector2(0, 1)
                # Change la direction vers le bas
                
            if event.key == pygame.K_LEFT and game.snake.direction != Vector2(1, 0):
                # Flèche GAUCHE ET le serpent ne va PAS vers la droite
                
                game.snake.direction = Vector2(-1, 0)
                # Change la direction vers la gauche
                
            if event.key == pygame.K_RIGHT and game.snake.direction != Vector2(-1, 0):
                # Flèche DROITE ET le serpent ne va PAS vers la gauche
                
                game.snake.direction = Vector2(1, 0)
                # Change la direction vers la droite

        # === FERMETURE DE LA FENÊTRE ===
        if event.type == pygame.QUIT:
            # Si le joueur clique sur X
            
            pygame.quit()
            # Ferme pygame
            
            sys.exit()
            # Quitte le programme


# ===== LIGNES 742-756: BOUCLE PRINCIPALE - RENDU GRAPHIQUE =====

    # === ARRIÈRE-PLAN DÉGRADÉ ===
    theme = game.theme
    # Récupère le thème du jeu
    
    for y in range(2*OFFSET + cell_size * number_of_cells):
        # Pour chaque ligne de la fenêtre (550 lignes)
        
        ratio = y / (2*OFFSET + cell_size * number_of_cells)
        # Ratio de 0 (haut) à 1 (bas)
        
        color = tuple(int(theme['bg_start'][i] + (theme['bg_end'][i] - theme['bg_start'][i]) * ratio) for i in range(3))
        # Interpolation linéaire pour créer un dégradé
        # Pour chaque composante RGB
        
        pygame.draw.line(screen, color, (0, y), (2*OFFSET + cell_size * number_of_cells, y))
        # Dessine une ligne horizontale avec cette couleur
    
    # === BORDURE DU TERRAIN AVEC EFFET DE LUEUR ===
    border_color = game.theme['accent']
    # Couleur d'accent du thème
    
    glow_rect = pygame.Rect(OFFSET-8, OFFSET-8, cell_size*number_of_cells+16, cell_size*number_of_cells+16)
    # Rectangle légèrement plus grand que le terrain (8 pixels de chaque côté)
    
    pygame.draw.rect(screen, (*border_color, 50), glow_rect, border_radius=12)
    # Dessine la lueur (semi-transparente, alpha=50)
    
    border_rect = pygame.Rect(OFFSET-5, OFFSET-5, cell_size*number_of_cells+10, cell_size*number_of_cells+10)
    # Rectangle pour la bordure principale
    
    pygame.draw.rect(screen, border_color, border_rect, 3, border_radius=10)
    # Dessine la bordure de 3 pixels


# ===== LIGNES 757-782: BOUCLE PRINCIPALE - AFFICHAGE DU JEU ET UI =====

    game.draw(screen)
    # Dessine tous les éléments du jeu (serpent, nourriture, obstacles, particules)

    if game.state == "STOPPED":
        # Si le jeu est en game over
        
        game.draw_game_over(screen)
        # Affiche l'écran de game over par-dessus

    # === INTERFACE UTILISATEUR ===
    # TITRE
    title_font = pygame.font.Font(None, 60)
    score_font = pygame.font.Font(None, 50)
    
    title = title_font.render(f"Level {level}: {LEVELS[level]['name']}", True, WHITE)
    # Ex: "Level 2: Intermédiaire"
    
    shadow_title = title_font.render(f"Level {level}: {LEVELS[level]['name']}", True, BLACK)
    # Ombre noire
    
    screen.blit(shadow_title, (OFFSET-3, 18))
    # Dessine l'ombre légèrement décalée
    
    screen.blit(title, (OFFSET-5, 15))
    # Dessine le titre
    
    # === SCORE AVEC FOND ===
    score_bg = pygame.Rect(OFFSET-10, OFFSET + cell_size*number_of_cells+10, 250, 55)
    # Rectangle pour le fond du score
    
    pygame.draw.rect(screen, (*game.theme['accent'], 150), score_bg, border_radius=10)
    # Fond semi-transparent de la couleur d'accent
    
    pygame.draw.rect(screen, game.theme['accent'], score_bg, 2, border_radius=10)
    # Bordure de 2 pixels
    
    score_text = score_font.render(f"Score: {game.score}", True, WHITE)
    # Texte du score
    
    screen.blit(score_text, (OFFSET, OFFSET + cell_size*number_of_cells+20))
    # Affiche le score
    
    # === NOM DU JOUEUR ===
    name_font = pygame.font.Font(None, 35)
    name = name_font.render(f"Player: {player_name}", True, WHITE)
    screen.blit(name, (OFFSET + 270, OFFSET + cell_size*number_of_cells+25))
    # Affiche le nom à droite du score

    pygame.display.update()
    # Met à jour l'affichage (affiche tout ce qui a été dessiné)
    
    clock.tick(60)
    # Limite le jeu à 60 FPS
    # Si la boucle s'exécute plus vite, attend pour maintenir 60 FPS



# ====================================================================
#
# RÉSUMÉ DU FONCTIONNEMENT:
# 
# 1. INITIALISATION:
#    - Import des modules nécessaires
#    - Définition des thèmes de couleurs et niveaux
#    - pygame.init() pour initialiser pygame
#
# 2. CLASSES:
#    - ParticleEffect: Effets visuels de particules
#    - Food: Gestion de la nourriture (position, affichage, animation)
#    - Obstacle: Murs sur le terrain
#    - Snake: Le serpent (mouvement, affichage, collisions)
#    - Game: Logique principale (score, état, mise à jour)
#
# 3. INTERFACES DE SÉLECTION:
#    - get_player_name(): Saisie du nom
#    - select_theme(): Choix du thème de couleurs
#    - select_level(): Choix du niveau de difficulté
#
# 4. BOUCLE PRINCIPALE:
#    - Gestion des événements (clavier, timer, fermeture)
#    - Mise à jour de la logique (game.update())
#    - Rendu graphique (arrière-plan, bordures, jeu, UI)
#    - Contrôle du FPS (60 images par seconde)
#
# Le jeu utilise un système d'événements avec un timer pour contrôler
# la vitesse du serpent selon le niveau choisi. Les graphismes sont
# rendus avec des dégradés, des effets de lueur et des animations
# pour créer une expérience visuelle moderne et attractive.
# ====================================================================