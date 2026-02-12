# Ce fichier implémente une version multijoueur locale du jeu Snake avec:
# - 2 joueurs sur le même écran
# - Chaque joueur choisit la couleur de son serpent
# - Différents niveaux de difficulté (Easy, Medium, Hard)
# - Obstacles générés aléatoirement
# - Deux types de nourriture (pomme 10pts, champignon 15pts)
# - Contrôles indépendants: Joueur 1 (flèches), Joueur 2 (WASD)
# - Système de score individuel avec réinitialisation en cas de collision

# Module système : fournit des fonctions pour interagir avec l'interpréteur.
# Utilisé ici pour sys.exit() qui permet de quitter proprement le programme.
import sys

# Module random : génération de nombres aléatoires.
# Indispensable pour placer aléatoirement la nourriture, les obstacles, etc.
import random

# Bibliothèque Pygame : framework de développement de jeux 2D.
# Gère la fenêtre, les événements, le rendu graphique, le son, etc.
import pygame

# Importation de la classe Vector2 depuis le module math de Pygame.
# Représente un vecteur 2D (x, y) – utilisé pour les positions et directions.
from pygame.math import Vector2

# Module JSON (JavaScript Object Notation) – importé mais non utilisé dans ce fichier.
# Peut servir pour sauvegarder/charger des scores ou configurations (conservé par compatibilité).
import json

# Module os (operating system) – permet d'interagir avec le système de fichiers.
# Utilisé indirectement via pygame.image.load() pour vérifier l'existence des images.
import os

# Initialise tous les modules Pygame (affichage, mixeur audio, gestion des événements…).
# Doit être appelé avant toute autre fonction Pygame.
pygame.init()


# PALETTE DE COULEURS POUR LES DEUX SERPENTS
# Dictionnaire contenant 8 couleurs différentes pour personnaliser les serpents.
# Chaque serpent peut choisir indépendamment sa couleur parmi ces options.
# Structure : clé -> dictionnaire avec 'name' (nom affiché), 'body' (couleur RVB du corps),
#            'head' (couleur RVB de la tête, souvent plus claire).
SNAKE_COLORS = {
    # Teal : vert-bleu turquoise
    'teal': {'name': 'Teal', 'body': (22, 160, 133), 'head': (26, 188, 156)},
    # Blue : bleu classique
    'blue': {'name': 'Blue', 'body': (52, 152, 219), 'head': (41, 128, 185)},
    # Red : rouge vif
    'red': {'name': 'Red', 'body': (231, 76, 60), 'head': (255, 100, 100)},
    # Purple : violet
    'purple': {'name': 'Purple', 'body': (155, 89, 182), 'head': (187, 143, 206)},
    # Orange : orange
    'orange': {'name': 'Orange', 'body': (230, 126, 34), 'head': (255, 160, 70)},
    # Green : vert
    'green': {'name': 'Green', 'body': (46, 204, 113), 'head': (100, 255, 150)},
    # Pink : rose
    'pink': {'name': 'Pink', 'body': (255, 100, 150), 'head': (255, 150, 200)},
    # Yellow : jaune
    'yellow': {'name': 'Yellow', 'body': (241, 196, 15), 'head': (255, 230, 100)}
}

# COULEURS FIXES POUR L'INTERFACE ET LE DÉCOR
# Ces couleurs sont utilisées pour le fond, le texte, les bordures, etc.
# Elles sont définies en format RVB (Rouge, Vert, Bleu) de 0 à 255.
# Vert clair – couleur de départ du dégradé d'arrière-plan
BG_LIGHT = (46, 204, 113)
# Vert foncé – couleur de fin du dégradé d'arrière-plan
BG_DARK = (39, 174, 96)
# Rouge – utilisé pour la pomme (nourriture de base)
RED = (231, 76, 60)
# Orange – utilisé pour le champignon (nourriture bonus)
ORANGE = (230, 126, 34)
# Blanc – utilisé pour le texte, les bordures et les reflets
WHITE = (236, 240, 241)
# Noir – utilisé pour les ombres du texte et les contours
BLACK = (44, 62, 80)
# Or – utilisé pour les effets de surbrillance (sélection)
GOLD = (241, 196, 15)
# Texte foncé – non utilisé directement dans ce code (conservé pour homogénéité)
TEXT_DARK = (44, 62, 80)
# Fond des éléments d'interface (ex: zones de score) – gris bleuté
UI_BG = (52, 73, 94)

# POLICES DE CARACTÈRES
# pygame.font.Font(None, taille) utilise la police par défaut du système.
title_font = pygame.font.Font(None, 60)   # Police pour les gros titres (60px)
score_font = pygame.font.Font(None, 40)   # Police pour l'affichage des scores (40px)
info_font = pygame.font.Font(None, 28)    # Police pour les informations secondaires (28px)

# PARAMÈTRES DE LA GRILLE DE JEU
# Le terrain est divisé en cellules carrées de taille fixe.
# Taille en pixels d'une cellule (carré de 20x20 pixels)
cell_size = 20
# Nombre de cellules dans chaque dimension (largeur et hauteur)
# La grille fait donc 20 x 20 = 400 cellules
number_of_cells = 20
# Décalage en pixels depuis le bord de la fenêtre pour le terrain de jeu.
# Cette marge permet d'afficher le titre, les scores et les bordures sans chevaucher le jeu.
OFFSET = 75

# NIVEAUX DE DIFFICULTÉ (version simplifiée pour deux joueurs)
# Dictionnaire définissant 3 niveaux avec leurs paramètres.
LEVELS = {
    1: {'name': 'Easy', 'speed': 200, 'obstacles': 5},   # Niveau 1 : facile, vitesse lente, 5 obstacles
    2: {'name': 'Medium', 'speed': 150, 'obstacles': 8}, # Niveau 2 : moyen, vitesse moyenne, 8 obstacles
    3: {'name': 'Hard', 'speed': 100, 'obstacles': 12}   # Niveau 3 : difficile, vitesse rapide, 12 obstacles
}

# TYPES DE NOURRITURE
# Dictionnaire définissant les caractéristiques des aliments disponibles.
FOOD_TYPES = {
    # Pomme : rapporte 10 points, fichier image 'snake_food.png'
    'apple': {'image': 'snake_food.png', 'points': 10},
    # Champignon : rapporte 15 points, fichier image 'snake_game2.png'
    'mushroom': {'image': 'snake_game2.png', 'points': 15}
}


# CLASSE Food
# Représente la nourriture que les serpents peuvent manger.
# Gère le chargement de l'image, le placement aléatoire sur la grille,
# et l'affichage.
class Food:
    def __init__(self, snake_bodies, obstacles_positions=None, food_type=None, existing_food_positions=None):
        """
        Constructeur de la nourriture.
        
        Args:
            snake_bodies (list): Liste contenant les listes de positions (Vector2) des corps des deux serpents.
                                 Utilisé pour éviter de placer la nourriture sur un serpent.
            obstacles_positions (list, optional): Liste des positions (Vector2) des obstacles.
                                                  Si None, initialisé à liste vide.
            food_type (str, optional): Type de nourriture ('apple' ou 'mushroom').
                                       Si None, un type est choisi aléatoirement.
            existing_food_positions (list, optional): Liste des positions des autres nourritures déjà placées.
                                                      Permet d'éviter les chevauchements.
        """
        # Initialise la liste des positions d'obstacles (liste vide par défaut)
        self.obstacles_positions = obstacles_positions or []
        # Initialise la liste des positions des autres nourritures (liste vide par défaut)
        self.existing_food_positions = existing_food_positions or []
        # Stocke les corps des deux serpents pour les vérifications de collision
        self.snake_bodies = snake_bodies
        # Détermine le type de nourriture : soit celui passé, soit choisi aléatoirement
        self.food_type = food_type if food_type else random.choice(list(FOOD_TYPES.keys()))
        # Génère une position aléatoire valide pour cette nourriture
        self.position = self.generate_random_pos()
        # Charge l'image correspondant au type de nourriture
        self.load_image()

    def load_image(self):
        """
        Charge l'image de la nourriture depuis le fichier et la redimensionne.
        Si le fichier est introuvable, crée une surface avec un cercle de couleur de secours.
        """
        try:
            # Récupère le chemin du fichier image depuis le dictionnaire FOOD_TYPES
            image_path = FOOD_TYPES[self.food_type]['image']
            # Charge l'image dans une Surface Pygame
            self.surface = pygame.image.load(image_path)
            # Redimensionne l'image pour qu'elle corresponde exactement à la taille d'une cellule
            self.surface = pygame.transform.scale(self.surface, (cell_size, cell_size))
        except:
            # En cas d'échec (fichier manquant, format non supporté, etc.)
            # Crée une surface transparente (pygame.SRCALPHA active le canal alpha)
            self.surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            # Choisit la couleur de secours : rouge pour pomme, orange pour champignon
            color = RED if self.food_type == 'apple' else ORANGE
            # Dessine un cercle au centre de la surface comme image de remplacement
            pygame.draw.circle(self.surface, color, (cell_size//2, cell_size//2), cell_size//2)

    def draw(self, screen):
        """
        Dessine la nourriture à l'écran à sa position actuelle.
        
        Args:
            screen (pygame.Surface): Surface de la fenêtre où dessiner.
        """
        # Convertit les coordonnées de la grille (self.position) en coordonnées pixels
        # OFFSET décale le terrain pour laisser la place à l'interface
        food_rec = pygame.Rect(
            OFFSET + self.position.x * cell_size,
            OFFSET + self.position.y * cell_size,
            cell_size, cell_size
        )
        # Copie (blit) la surface de l'image sur l'écran à la position du rectangle
        screen.blit(self.surface, food_rec)

    def generate_random_cell(self):
        """
        Génère une cellule aléatoire sur la grille.
        
        Returns:
            Vector2: Coordonnées (x, y) de la cellule, avec x et y entre 0 et number_of_cells-1.
        """
        x = random.randint(0, number_of_cells - 1)
        y = random.randint(0, number_of_cells - 1)
        return Vector2(x, y)

    def generate_random_pos(self):
        """
        Génère une position aléatoire valide pour la nourriture.
        Une position est valide si elle n'est pas occupée par :
            - un obstacle,
            - le corps d'un des deux serpents,
            - une autre nourriture déjà placée.
        
        Returns:
            Vector2: Position valide.
        """
        position = self.generate_random_cell()
        # Tant que la position est occupée, on en génère une nouvelle
        while self.is_position_occupied(position):
            position = self.generate_random_cell()
        return position

    def is_position_occupied(self, position):
        """
        Vérifie si une position donnée est déjà occupée.
        
        Args:
            position (Vector2): Position à tester.
        
        Returns:
            bool: True si la position est occupée, False sinon.
        """
        # Vérification avec les obstacles
        if position in self.obstacles_positions:
            return True
        # Vérification avec les corps des serpents
        for snake_body in self.snake_bodies:
            if position in snake_body:
                return True
        # Vérification avec les autres nourritures
        if position in self.existing_food_positions:
            return True
        return False

    def get_points(self):
        """
        Retourne le nombre de points rapporté par cette nourriture.
        
        Returns:
            int: Points (10 pour pomme, 15 pour champignon).
        """
        return FOOD_TYPES[self.food_type]['points']


# CLASSE Obstacle
# Représente un mur sur la grille.
# Le serpent meurt instantanément s'il entre en collision avec un obstacle.
class Obstacle:
    def __init__(self, position):
        """
        Constructeur de l'obstacle.
        
        Args:
            position (Vector2): Position de l'obstacle sur la grille.
        """
        self.position = position
        try:
            # Tentative de chargement de l'image de brique (fichier 'barier.png' – probablement 'barrier')
            self.brick_image = pygame.image.load('barier.png')
            # Redimensionne l'image à la taille d'une cellule
            self.brick_image = pygame.transform.scale(self.brick_image, (cell_size, cell_size))
        except:
            # Si l'image est introuvable, on dessinera un motif de briques manuellement
            self.brick_image = None

    def draw(self, screen):
        """
        Dessine l'obstacle à l'écran.
        
        Args:
            screen (pygame.Surface): Surface de la fenêtre.
        """
        # Conversion des coordonnées grille → pixels
        x = OFFSET + self.position.x * cell_size
        y = OFFSET + self.position.y * cell_size

        if self.brick_image:
            # Si l'image est chargée, on l'affiche simplement
            screen.blit(self.brick_image, (x, y))
        else:
            # Sinon, on dessine un motif de briques réaliste avec des rectangles
            # Couleurs pour simuler une brique
            BRICK_RED = (192, 57, 43)    # Rouge brique
            BRICK_DARK = (169, 50, 38)   # Rouge foncé pour les ombres
            BRICK_LIGHT = (205, 97, 85)  # Rouge clair pour les reflets

            # Rectangle principal de la brique
            obstacle_rect = pygame.Rect(x, y, cell_size, cell_size)
            # Fond de la brique avec coins arrondis
            pygame.draw.rect(screen, BRICK_RED, obstacle_rect, border_radius=4)

            # Hauteur d'une rangée de briques (3 rangées dans une cellule)
            brick_height = cell_size // 3
            # Largeur d'une brique (2 briques par rangée)
            brick_width = cell_size // 2

            # Rangée du haut : deux briques sombres (effet d'ombre)
            pygame.draw.rect(screen, BRICK_DARK, (x, y, brick_width - 1, brick_height - 1))
            pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y, brick_width - 1, brick_height - 1))
            # Rangée du milieu : une brique claire sur toute la largeur
            pygame.draw.rect(screen, BRICK_LIGHT, (x, y + brick_height, cell_size, brick_height - 1))
            # Rangée du bas : deux briques sombres
            pygame.draw.rect(screen, BRICK_DARK, (x, y + 2 * brick_height, brick_width - 1, brick_height))
            pygame.draw.rect(screen, BRICK_DARK, (x + brick_width, y + 2 * brick_height, brick_width - 1, brick_height))

            # Bordure sombre autour de l'obstacle (largeur 2 pixels)
            pygame.draw.rect(screen, BRICK_DARK, obstacle_rect, 2, border_radius=4)


# CLASSE Snake
# Représente un serpent contrôlé par un joueur.
# Gère le mouvement, la croissance, l'affichage et les collisions.
class Snake:
    def __init__(self, start_pos, color_key, player_name):
        """
        Constructeur du serpent.
        
        Args:
            start_pos (list): [x, y] position de la tête au départ.
            color_key (str): Clé du dictionnaire SNAKE_COLORS pour choisir les couleurs.
            player_name (str): Nom du joueur contrôlant ce serpent (affiché dans l'interface).
        """
        # Corps initial : 3 segments alignés horizontalement vers la droite
        self.snake_body = [
            Vector2(start_pos[0], start_pos[1]),          # Tête
            Vector2(start_pos[0] - 1, start_pos[1]),      # Segment 1
            Vector2(start_pos[0] - 2, start_pos[1])       # Segment 2 (queue)
        ]
        # Direction initiale : vers la droite (1, 0)
        self.direction = Vector2(1, 0)
        # Drapeau : si True, un segment sera ajouté lors du prochain update (après avoir mangé)
        self.add_segment = False
        # Couleur du corps et de la tête définies par le thème choisi
        self.color = SNAKE_COLORS[color_key]['body']
        self.head_color = SNAKE_COLORS[color_key]['head']
        # Nom du joueur
        self.player_name = player_name
        # État de vie – dans cette version, le serpent est toujours considéré vivant
        # (il est réinitialisé immédiatement après une collision)
        self.alive = True

        # Chargement des effets sonores (optionnel)
        try:
            # Son joué quand le serpent mange de la nourriture
            self.eat_sound = pygame.mixer.Sound("snake_eat.wav")
            # Son joué lors d'une collision (mur, obstacle, autre serpent)
            self.wall_hit_sound = pygame.mixer.Sound("snake_collision.wav")
        except:
            # Si les fichiers audio sont absents, on désactive les sons
            self.eat_sound = None
            self.wall_hit_sound = None

    def draw(self, screen):
        """
        Dessine le serpent à l'écran.
        
        Args:
            screen (pygame.Surface): Surface de la fenêtre.
        """
        if not self.alive:
            return

        # Parcours de tous les segments du corps
        for i, seg in enumerate(self.snake_body):
            # Conversion grille → pixels
            seg_rect = pygame.Rect(
                OFFSET + seg.x * cell_size,
                OFFSET + seg.y * cell_size,
                cell_size, cell_size
            )
            # Tête : couleur spéciale, corps : couleur normale
            color = self.head_color if i == 0 else self.color
            # Dessine un rectangle aux coins arrondis (border_radius)
            pygame.draw.rect(screen, color, seg_rect, border_radius=7)

            # Petit reflet blanc sur la tête pour un effet brillant
            if i == 0:
                shine_rect = pygame.Rect(seg_rect.x + 4, seg_rect.y + 4, 6, 6)
                pygame.draw.rect(screen, WHITE, shine_rect, border_radius=3)

    def update(self):
        """
        Met à jour la position du serpent.
        La nouvelle tête est ajoutée dans la direction actuelle.
        Si add_segment est False, le dernier segment (queue) est supprimé.
        Le passage des bordures est géré par modulo (effet de wrap‑around).
        """
        if not self.alive:
            return

        # Calcule la nouvelle position de la tête = ancienne tête + direction
        new_head = self.snake_body[0] + self.direction
        # Effet de rebondissement : si le serpent sort par la droite (x = 20),
        # il réapparaît à gauche (x = 0) grâce au modulo
        new_head.x = new_head.x % number_of_cells
        new_head.y = new_head.y % number_of_cells

        # Insère la nouvelle tête au début de la liste
        self.snake_body.insert(0, new_head)

        if self.add_segment:
            # Si le serpent a mangé, on conserve le dernier segment → le serpent grandit
            self.add_segment = False
        else:
            # Sinon, on supprime le dernier segment → déplacement sans changement de longueur
            self.snake_body = self.snake_body[:-1]

    def reset(self, start_pos):
        """
        Réinitialise le serpent à sa position et direction de départ.
        Utilisé après une collision.
        
        Args:
            start_pos (list): [x, y] position de la tête au départ.
        """
        self.snake_body = [
            Vector2(start_pos[0], start_pos[1]),
            Vector2(start_pos[0] - 1, start_pos[1]),
            Vector2(start_pos[0] - 2, start_pos[1])
        ]
        self.direction = Vector2(1, 0)
        self.alive = True

    def check_collision_with_obstacles(self, obstacles):
        """
        Vérifie si la tête du serpent touche un obstacle.
        
        Args:
            obstacles (list): Liste d'objets Obstacle.
        
        Returns:
            bool: True si collision, False sinon.
        """
        if not self.alive:
            return False
        for obstacle in obstacles:
            if self.snake_body[0] == obstacle.position:
                return True
        return False

    def check_collision_with_tail(self):
        """
        Vérifie si la tête du serpent touche une partie de son propre corps.
        
        Returns:
            bool: True si la tête est dans le corps (sauf elle-même), False sinon.
        """
        if not self.alive:
            return False
        headless_body = self.snake_body[1:]  # Corps sans la tête
        return self.snake_body[0] in headless_body

    def check_collision_with_other_snake(self, other_snake):
        """
        Vérifie si la tête de ce serpent touche le corps de l'autre serpent.
        
        Args:
            other_snake (Snake): L'autre serpent.
        
        Returns:
            bool: True si collision, False sinon.
        """
        if not self.alive or not other_snake.alive:
            return False
        return self.snake_body[0] in other_snake.snake_body


# CLASSE TwoPlayerGame
# Classe principale qui gère toute la logique du jeu pour deux joueurs.
# Coordonne les serpents, la nourriture, les obstacles, les scores.
class TwoPlayerGame:
    def __init__(self, player1_name, player2_name, p1_color, p2_color, level):
        """
        Constructeur du jeu à deux joueurs.
        
        Args:
            player1_name (str): Nom du joueur 1.
            player2_name (str): Nom du joueur 2.
            p1_color (str): Clé de couleur choisie pour le serpent du joueur 1.
            p2_color (str): Clé de couleur choisie pour le serpent du joueur 2.
            level (int): Niveau de difficulté (1, 2 ou 3).
        """
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.level = level

        # Création des deux serpents avec des positions de départ distinctes
        # Joueur 1 : départ à (6,9) – orientation droite
        self.snake1 = Snake([6, 9], p1_color, player1_name)
        # Joueur 2 : départ à (14,9) – orientation droite
        self.snake2 = Snake([14, 9], p2_color, player2_name)

        # Génération des obstacles selon le nombre défini dans le niveau
        num_obstacles = LEVELS[level]['obstacles']
        self.obstacles = self.generate_obstacles(num_obstacles)
        # Liste des positions des obstacles (utile pour la nourriture)
        obstacle_positions = [obs.position for obs in self.obstacles]

        # Création de deux nourritures :
        #   food1 : pomme (10 points)
        self.food1 = Food(
            [self.snake1.snake_body, self.snake2.snake_body],
            obstacle_positions,
            'apple'
        )
        #   food2 : champignon (15 points)
        #   On passe la position de food1 pour éviter qu'elles se superposent
        self.food2 = Food(
            [self.snake1.snake_body, self.snake2.snake_body],
            obstacle_positions,
            'mushroom',
            [self.food1.position]
        )

        # Scores des deux joueurs
        self.score1 = 0
        self.score2 = 0
        # État du jeu (toujours RUNNING, pas de pause générale)
        self.state = "RUNNING"

    def generate_obstacles(self, count):
        """
        Génère un nombre donné d'obstacles à des positions aléatoires,
        en évitant les positions de départ des deux serpents.
        
        Args:
            count (int): Nombre d'obstacles à générer.
        
        Returns:
            list: Liste d'objets Obstacle.
        """
        obstacles = []
        # Positions interdites : les 3 cellules de départ de chaque serpent
        forbidden_positions = [
            Vector2(6, 9), Vector2(5, 9), Vector2(4, 9),   # Joueur 1
            Vector2(14, 9), Vector2(15, 9), Vector2(16, 9) # Joueur 2
        ]

        for _ in range(count):
            max_attempts = 50  # Limite pour éviter une boucle infinie si la grille est saturée
            for _ in range(max_attempts):
                pos = Vector2(
                    random.randint(0, number_of_cells - 1),
                    random.randint(0, number_of_cells - 1)
                )
                # Vérifie que la position n'est ni interdite ni déjà occupée par un autre obstacle
                if pos not in forbidden_positions and pos not in [o.position for o in obstacles]:
                    obstacles.append(Obstacle(pos))
                    break  # Sort de la boucle interne, passe à l'obstacle suivant
        return obstacles

    def draw(self, screen):
        """
        Dessine tous les éléments du jeu : obstacles, nourritures, serpents.
        
        Args:
            screen (pygame.Surface): Surface de la fenêtre.
        """
        # Dessin des obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        # Dessin des nourritures
        self.food1.draw(screen)
        self.food2.draw(screen)
        # Dessin des serpents
        self.snake1.draw(screen)
        self.snake2.draw(screen)

    def update(self):
        """
        Met à jour la logique du jeu : déplacement des serpents et collisions.
        """
        if self.state == "RUNNING":
            self.snake1.update()
            self.snake2.update()
            self.check_collisions()

    def check_collisions(self):
        """
        Vérifie et traite toutes les collisions :
            - Serpent mange la nourriture (points, croissance, repositionnement)
            - Collision avec obstacles, propre queue, ou autre serpent (game over individuel)
        """
        # --- Joueur 1 mange food1 (pomme) ---
        if self.snake1.snake_body[0] == self.food1.position:
            # Repositionne la nourriture à un endroit valide
            self.food1.position = self.food1.generate_random_pos()
            # Active la croissance du serpent
            self.snake1.add_segment = True
            # Ajoute les points au score du joueur 1
            self.score1 += self.food1.get_points()
            # Joue le son de "manger" si disponible
            if self.snake1.eat_sound:
                self.snake1.eat_sound.play()

        # --- Joueur 1 mange food2 (champignon) ---
        if self.snake1.snake_body[0] == self.food2.position:
            self.food2.position = self.food2.generate_random_pos()
            self.snake1.add_segment = True
            self.score1 += self.food2.get_points()
            if self.snake1.eat_sound:
                self.snake1.eat_sound.play()

        # --- Joueur 2 mange food1 ---
        if self.snake2.snake_body[0] == self.food1.position:
            self.food1.position = self.food1.generate_random_pos()
            self.snake2.add_segment = True
            self.score2 += self.food1.get_points()
            if self.snake2.eat_sound:
                self.snake2.eat_sound.play()

        # --- Joueur 2 mange food2 ---
        if self.snake2.snake_body[0] == self.food2.position:
            self.food2.position = self.food2.generate_random_pos()
            self.snake2.add_segment = True
            self.score2 += self.food2.get_points()
            if self.snake2.eat_sound:
                self.snake2.eat_sound.play()

        # --- Collisions du Joueur 1 ---
        if (self.snake1.check_collision_with_obstacles(self.obstacles) or
            self.snake1.check_collision_with_tail() or
            self.snake1.check_collision_with_other_snake(self.snake2)):
            self.game_over_player(1)

        # --- Collisions du Joueur 2 ---
        if (self.snake2.check_collision_with_obstacles(self.obstacles) or
            self.snake2.check_collision_with_tail() or
            self.snake2.check_collision_with_other_snake(self.snake1)):
            self.game_over_player(2)

    def game_over_player(self, player_num):
        """
        Gère la mort d'un joueur : réinitialise son serpent et son score à zéro,
        et joue un son de collision.
        
        Args:
            player_num (int): 1 pour le joueur 1, 2 pour le joueur 2.
        """
        if player_num == 1:
            # Réinitialise le serpent du joueur 1 à sa position de départ
            self.snake1.reset([6, 9])
            if self.snake1.wall_hit_sound:
                self.snake1.wall_hit_sound.play()
            self.score1 = 0
            # Affichage dans la console pour le debug
            print(f"{self.player1_name} died! Score reset.")
        else:
            # Réinitialise le serpent du joueur 2
            self.snake2.reset([14, 9])
            if self.snake2.wall_hit_sound:
                self.snake2.wall_hit_sound.play()
            self.score2 = 0
            print(f"{self.player2_name} died! Score reset.")


# FONCTION select_level()
# Écran de sélection du niveau de difficulté.
# Affiche trois cartes interactives (Easy, Medium, Hard).
# Retourne le niveau choisi (1, 2 ou 3).
def select_level():
    """Écran de sélection du niveau."""
    # Crée une fenêtre de 800x600 pixels pour cette interface
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Select Level")

    selected = 1  # Niveau par défaut : Easy
    clock = pygame.time.Clock()

    while True:
        # --- Arrière-plan dégradé vertical ---
        for y in range(600):
            ratio = y / 600
            # Dégradé allant du bleu-gris au bleu plus foncé
            r = int(30 + (50 - 30) * ratio)
            g = int(40 + (70 - 40) * ratio)
            b = int(60 + (100 - 60) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (800, y))

        # --- Titre ---
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("SELECT LEVEL", True, WHITE)
        title_rect = title.get_rect(center=(400, 80))
        screen.blit(title, title_rect)

        # --- Paramètres des cartes ---
        card_width = 220
        card_height = 280
        # Calcule la position X de départ pour centrer les 3 cartes
        x_start = (800 - (card_width * 3 + 60)) // 2
        y_pos = 180

        # Affiche les trois niveaux
        for level_num in [1, 2, 3]:
            x = x_start + (level_num - 1) * (card_width + 30)
            card_rect = pygame.Rect(x, y_pos, card_width, card_height)

            # Si ce niveau est sélectionné, ajoute un effet de lueur dorée
            if level_num == selected:
                glow_rect = pygame.Rect(x - 5, y_pos - 5, card_width + 10, card_height + 10)
                pygame.draw.rect(screen, GOLD, glow_rect, border_radius=15)

            # Fond de la carte (gris foncé)
            pygame.draw.rect(screen, (40, 40, 60), card_rect, border_radius=12)
            # Bordure : blanche si sélectionné, grise sinon
            border_color = WHITE if level_num == selected else (100, 100, 120)
            pygame.draw.rect(screen, border_color, card_rect, 3, border_radius=12)

            # --- Numéro du niveau (grand) ---
            num_font = pygame.font.Font(None, 90)
            num_color = GOLD if level_num == selected else WHITE
            num_text = num_font.render(str(level_num), True, num_color)
            num_rect = num_text.get_rect(center=(x + card_width // 2, y_pos + 60))
            screen.blit(num_text, num_rect)

            # --- Nom du niveau ---
            name_font = pygame.font.Font(None, 42)
            name = name_font.render(LEVELS[level_num]['name'], True, WHITE)
            name_rect = name.get_rect(center=(x + card_width // 2, y_pos + 130))
            screen.blit(name, name_rect)

            # --- Statistiques : vitesse et nombre d'obstacles ---
            stats_font = pygame.font.Font(None, 28)
            speed_text = f"Speed: {LEVELS[level_num]['speed']}ms"
            obstacles_text = f"Obstacles: {LEVELS[level_num]['obstacles']}"
            speed = stats_font.render(speed_text, True, (200, 200, 200))
            obstacles = stats_font.render(obstacles_text, True, (200, 200, 200))
            speed_rect = speed.get_rect(center=(x + card_width // 2, y_pos + 190))
            obstacles_rect = obstacles.get_rect(center=(x + card_width // 2, y_pos + 230))
            screen.blit(speed, speed_rect)
            screen.blit(obstacles, obstacles_rect)

        # --- Instructions pour l'utilisateur ---
        inst_font = pygame.font.Font(None, 32)
        inst = inst_font.render("Use Arrow Keys | Press ENTER to Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(400, 520))
        screen.blit(inst, inst_rect)

        # Rafraîchit l'affichage
        pygame.display.flip()

        # --- Gestion des événements ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = max(1, selected - 1)   # Ne peut pas descendre en dessous de 1
                elif event.key == pygame.K_RIGHT:
                    selected = min(3, selected + 1)   # Ne peut pas dépasser 3
                elif event.key == pygame.K_RETURN:
                    return selected   # Valide le choix et retourne le niveau

        clock.tick(60)  # Limite à 60 images par seconde

# FONCTION select_colors()
# Écran de sélection des couleurs pour les deux serpents.
# Permet à chaque joueur de choisir indépendamment sa couleur.
# Navigation : flèches pour se déplacer, TAB pour changer de joueur,
# ENTER pour valider les deux choix.
# Retourne un tuple (clé_couleur_j1, clé_couleur_j2).
def select_colors():
    """Écran de sélection des couleurs pour les deux joueurs."""
    # Fenêtre de 900x700 pixels
    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Select Colors")

    # Liste des clés de couleurs disponibles
    color_keys = list(SNAKE_COLORS.keys())
    # Index des couleurs sélectionnées par défaut
    p1_selected = 0   # Joueur 1 : teal (indice 0)
    p2_selected = 1   # Joueur 2 : blue (indice 1)
    active_player = 1 # Joueur actif (1 ou 2)

    clock = pygame.time.Clock()

    while True:
        # --- Arrière-plan dégradé ---
        for y in range(700):
            ratio = y / 700
            r = int(30 + (50 - 30) * ratio)
            g = int(40 + (70 - 40) * ratio)
            b = int(60 + (100 - 60) * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (900, y))

        # --- Titre ---
        font_large = pygame.font.Font(None, 72)
        title = font_large.render("SELECT COLORS", True, WHITE)
        title_rect = title.get_rect(center=(450, 60))
        screen.blit(title, title_rect)

        # --- Section Joueur 1 ---
        font_medium = pygame.font.Font(None, 48)
        # Le titre du joueur est blanc s'il est actif, gris sinon
        p1_title_color = WHITE if active_player == 1 else (150, 150, 150)
        p1_title = font_medium.render("Player 1", True, p1_title_color)
        screen.blit(p1_title, (100, 140))

        # Grille de couleurs pour le joueur 1 (4 colonnes x 2 lignes)
        start_x = 100
        start_y = 200
        box_size = 80
        spacing = 100

        for i, key in enumerate(color_keys):
            x = start_x + (i % 4) * spacing
            y = start_y + (i // 4) * spacing
            color = SNAKE_COLORS[key]['body']

            # Dessine le carré de couleur
            box_rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(screen, color, box_rect, border_radius=10)

            # Si cette couleur est sélectionnée pour le joueur 1, ajoute une coche blanche
            if i == p1_selected:
                pygame.draw.rect(screen, WHITE, box_rect, 4, border_radius=10)
                font_check = pygame.font.Font(None, 60)
                check = font_check.render("✓", True, WHITE)
                check_rect = check.get_rect(center=box_rect.center)
                screen.blit(check, check_rect)

        # --- Section Joueur 2 ---
        p2_title_color = WHITE if active_player == 2 else (150, 150, 150)
        p2_title = font_medium.render("Player 2", True, p2_title_color)
        screen.blit(p2_title, (100, 420))

        start_y2 = 480
        for i, key in enumerate(color_keys):
            x = start_x + (i % 4) * spacing
            y = start_y2 + (i // 4) * spacing
            color = SNAKE_COLORS[key]['body']

            box_rect = pygame.Rect(x, y, box_size, box_size)
            pygame.draw.rect(screen, color, box_rect, border_radius=10)

            if i == p2_selected:
                pygame.draw.rect(screen, WHITE, box_rect, 4, border_radius=10)
                font_check = pygame.font.Font(None, 60)
                check = font_check.render("✓", True, WHITE)
                check_rect = check.get_rect(center=box_rect.center)
                screen.blit(check, check_rect)

        # --- Instructions ---
        inst_font = pygame.font.Font(None, 28)
        inst = inst_font.render("Arrow Keys: Navigate | TAB: Switch Player | ENTER: Confirm", True, WHITE)
        inst_rect = inst.get_rect(center=(450, 650))
        screen.blit(inst, inst_rect)

        pygame.display.flip()

        # --- Gestion des événements ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Alterne le joueur actif
                    active_player = 2 if active_player == 1 else 1

                # Navigation pour le joueur actif
                if event.key == pygame.K_LEFT:
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
                    # Monter de 4 cases (colonne)
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
                    # Valide et retourne les clés des couleurs choisies
                    return color_keys[p1_selected], color_keys[p2_selected]

        clock.tick(60)


# FONCTION get_player_names()
# Écran de saisie des noms des deux joueurs.
# Affiche deux champs de texte avec curseur clignotant.
# Navigation : TAB ou clic souris pour changer de champ, ENTER pour valider.
# Retourne un tuple (nom_joueur1, nom_joueur2).
def get_player_names():
    """Écran de saisie des noms des deux joueurs."""
    # Fenêtre de 700x450 pixels
    screen_temp = pygame.display.set_mode((700, 450))
    pygame.display.set_caption("Enter Names")

    font = pygame.font.Font(None, 48)      # Police pour le titre
    small_font = pygame.font.Font(None, 32) # Police pour les champs de saisie

    player1_name = ""
    player2_name = ""
    active_field = "player1"   # Champ actuellement sélectionné

    clock = pygame.time.Clock()

    while True:
        # --- Arrière-plan dégradé ---
        for y in range(450):
            ratio = y / 450
            # Dégradé vert
            r = int(39 + (52 - 39) * ratio)
            g = int(174 + (73 - 174) * ratio)
            b = int(96 + (94 - 96) * ratio)
            pygame.draw.line(screen_temp, (r, g, b), (0, y), (700, y))

        # --- Titre principal ---
        title = font.render("LOCAL MULTIPLAYER", True, WHITE)
        title_rect = title.get_rect(center=(350, 50))
        screen_temp.blit(title, title_rect)

        # --- Sous-titre ---
        subtitle = small_font.render("Enter Player Names", True, (189, 195, 199))
        subtitle_rect = subtitle.get_rect(center=(350, 100))
        screen_temp.blit(subtitle, subtitle_rect)

        # --- Champ de saisie Joueur 1 ---
        p1_label = small_font.render("Player 1 (Arrow Keys):", True, WHITE)
        screen_temp.blit(p1_label, (100, 160))

        # Couleur de la bordure : blanc si actif, gris sinon
        p1_color = WHITE if active_field == "player1" else (149, 165, 166)
        pygame.draw.rect(screen_temp, UI_BG, (100, 195, 500, 50), border_radius=8)
        pygame.draw.rect(screen_temp, p1_color, (100, 195, 500, 50), 3, border_radius=8)
        p1_text = small_font.render(player1_name, True, WHITE)
        screen_temp.blit(p1_text, (115, 210))

        # --- Champ de saisie Joueur 2 ---
        p2_label = small_font.render("Player 2 (WASD):", True, WHITE)
        screen_temp.blit(p2_label, (100, 270))

        p2_color = WHITE if active_field == "player2" else (149, 165, 166)
        pygame.draw.rect(screen_temp, UI_BG, (100, 305, 500, 50), border_radius=8)
        pygame.draw.rect(screen_temp, p2_color, (100, 305, 500, 50), 3, border_radius=8)
        p2_text = small_font.render(player2_name, True, WHITE)
        screen_temp.blit(p2_text, (115, 320))

        # --- Instructions ---
        instruction_font = pygame.font.Font(None, 26)
        start_text = instruction_font.render("Press ENTER to Start | TAB to switch fields", True, (189, 195, 199))
        screen_temp.blit(start_text, (130, 390))

        pygame.display.update()

        # --- Gestion des événements ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Permet de sélectionner un champ avec la souris
                mouse_pos = pygame.mouse.get_pos()
                if 100 <= mouse_pos[0] <= 600:
                    if 195 <= mouse_pos[1] <= 245:
                        active_field = "player1"
                    elif 305 <= mouse_pos[1] <= 355:
                        active_field = "player2"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Les deux noms doivent être non vides pour démarrer
                    if player1_name and player2_name:
                        return player1_name, player2_name
                elif event.key == pygame.K_TAB:
                    # Alterne les champs
                    active_field = "player2" if active_field == "player1" else "player1"
                elif event.key == pygame.K_BACKSPACE:
                    # Supprime le dernier caractère du champ actif
                    if active_field == "player1":
                        player1_name = player1_name[:-1]
                    else:
                        player2_name = player2_name[:-1]
                else:
                    # Ajoute le caractère saisi (limité à 15 caractères)
                    if active_field == "player1" and len(player1_name) < 15:
                        player1_name += event.unicode
                    elif active_field == "player2" and len(player2_name) < 15:
                        player2_name += event.unicode

        clock.tick(30)  # 30 FPS pour cette interface


# DÉROULEMENT PRINCIPAL DU JEU

# Étape 1 : Saisie des noms des deux joueurs
player1_name, player2_name = get_player_names()

# Étape 2 : Sélection des couleurs des serpents
p1_color, p2_color = select_colors()

# Étape 3 : Sélection du niveau de difficulté
level = select_level()

# Étape 4 : Création de la fenêtre de jeu principale
# La taille est calculée à partir des paramètres de la grille et des marges
screen = pygame.display.set_mode((
    2 * OFFSET + cell_size * number_of_cells,
    2 * OFFSET + cell_size * number_of_cells
))
pygame.display.set_caption(f"Snake Game - Local Multiplayer - {LEVELS[level]['name']}")

# Étape 5 : Initialisation de l'instance du jeu avec tous les paramètres
game = TwoPlayerGame(player1_name, player2_name, p1_color, p2_color, level)

# Horloge pour limiter le nombre d'images par seconde
clock = pygame.time.Clock()
running = True  # Flag de la boucle principale

# --- Configuration de l'événement de mouvement ---
# Crée un type d'événement personnalisé (pygame.USEREVENT + 1)
SNAKE_MOVE_EVENT = pygame.USEREVENT + 1
# Programme un timer qui envoie cet événement toutes les X millisecondes
# La vitesse est définie par le niveau choisi
pygame.time.set_timer(SNAKE_MOVE_EVENT, LEVELS[level]['speed'])

# BOUCLE PRINCIPALE
while running:
    # --- Gestion des événements ---
    for event in pygame.event.get():
        # Événement de mouvement : déclenché par le timer
        if event.type == SNAKE_MOVE_EVENT:
            game.update()   # Met à jour la position des serpents et les collisions

        # Événements clavier
        if event.type == pygame.KEYDOWN:
            # --- Contrôles Joueur 1 (flèches) ---
            # Chaque direction est modifiée seulement si le serpent ne va pas déjà dans la direction opposée
            if event.key == pygame.K_UP and game.snake1.direction != Vector2(0, 1):
                game.snake1.direction = Vector2(0, -1)   # Haut
            if event.key == pygame.K_DOWN and game.snake1.direction != Vector2(0, -1):
                game.snake1.direction = Vector2(0, 1)    # Bas
            if event.key == pygame.K_LEFT and game.snake1.direction != Vector2(1, 0):
                game.snake1.direction = Vector2(-1, 0)   # Gauche
            if event.key == pygame.K_RIGHT and game.snake1.direction != Vector2(-1, 0):
                game.snake1.direction = Vector2(1, 0)    # Droite

            # --- Contrôles Joueur 2 (WASD) ---
            if event.key == pygame.K_w and game.snake2.direction != Vector2(0, 1):
                game.snake2.direction = Vector2(0, -1)   # Haut
            if event.key == pygame.K_s and game.snake2.direction != Vector2(0, -1):
                game.snake2.direction = Vector2(0, 1)    # Bas
            if event.key == pygame.K_a and game.snake2.direction != Vector2(1, 0):
                game.snake2.direction = Vector2(-1, 0)   # Gauche
            if event.key == pygame.K_d and game.snake2.direction != Vector2(-1, 0):
                game.snake2.direction = Vector2(1, 0)    # Droite

        # Fermeture de la fenêtre
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- Rendu graphique ---

    # Arrière-plan dégradé (vert)
    for y in range(2 * OFFSET + cell_size * number_of_cells):
        ratio = y / (2 * OFFSET + cell_size * number_of_cells)
        # Interpolation linéaire entre BG_LIGHT et BG_DARK
        r = int(46 + (39 - 46) * ratio)
        g = int(204 + (174 - 204) * ratio)
        b = int(113 + (96 - 113) * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (2 * OFFSET + cell_size * number_of_cells, y))

    # Bordure noire autour du terrain (effet de cadre)
    pygame.draw.rect(screen, BLACK,
                     (OFFSET - 7, OFFSET - 7,
                      cell_size * number_of_cells + 14,
                      cell_size * number_of_cells + 14),
                     border_radius=10)
    # Bordure décorative intérieure (vert foncé, épaisseur 5)
    pygame.draw.rect(screen, BG_DARK,
                     (OFFSET - 5, OFFSET - 5,
                      cell_size * number_of_cells + 10,
                      cell_size * number_of_cells + 10),
                     5, border_radius=8)

    # Dessin des éléments du jeu (obstacles, nourritures, serpents)
    game.draw(screen)

    # --- Interface utilisateur ---
    # Titre : niveau de difficulté
    title_shadow = title_font.render(f"{LEVELS[level]['name'].upper()} MODE", True, BLACK)
    title_surface = title_font.render(f"{LEVELS[level]['name'].upper()} MODE", True, WHITE)
    screen.blit(title_shadow, (OFFSET - 3, 18))
    screen.blit(title_surface, (OFFSET - 5, 15))

    # Score du Joueur 1 (affiché à gauche)
    p1_bg_rect = pygame.Rect(OFFSET - 10, OFFSET + cell_size * number_of_cells + 5, 190, 50)
    pygame.draw.rect(screen, UI_BG, p1_bg_rect, border_radius=8)
    p1_score_text = f"{player1_name}: {game.score1}"
    p1_score_surface = score_font.render(p1_score_text, True, game.snake1.head_color)
    screen.blit(p1_score_surface, (OFFSET, OFFSET + cell_size * number_of_cells + 15))

    # Score du Joueur 2 (affiché à droite)
    p2_score_text = f"{player2_name}: {game.score2}"
    p2_score_surface = score_font.render(p2_score_text, True, game.snake2.head_color)
    p2_width = p2_score_surface.get_width()   # Largeur du texte pour positionner le fond
    p2_bg_rect = pygame.Rect(
        OFFSET + cell_size * number_of_cells - p2_width - 5,
        OFFSET + cell_size * number_of_cells + 5,
        p2_width + 15, 50
    )
    pygame.draw.rect(screen, UI_BG, p2_bg_rect, border_radius=8)
    screen.blit(p2_score_surface,
                (OFFSET + cell_size * number_of_cells - p2_width,
                 OFFSET + cell_size * number_of_cells + 15))

    # Mise à jour de l'affichage
    pygame.display.update()
    # Limite le taux de rafraîchissement à 60 images par seconde
    clock.tick(60)