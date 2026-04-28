import pygame
import random
from config import *
from db import save_game_result, get_personal_best

class Snake:
    def __init__(self, color=(0, 255, 0)):
        self.body = [[100, 100], [80, 100], [60, 100]]
        self.direction = "RIGHT"
        self.color = color
        self.shielded = False

    def move(self):
        head = list(self.body[0])
        if self.direction == "UP": head[1] -= BLOCK_SIZE
        elif self.direction == "DOWN": head[1] += BLOCK_SIZE
        elif self.direction == "LEFT": head[0] -= BLOCK_SIZE
        elif self.direction == "RIGHT": head[0] += BLOCK_SIZE
        self.body.insert(0, head)
        return head

class Game:
    def __init__(self, username, settings):
        self.username = username
        self.settings = settings
        self.snake = Snake(settings.get('snake_color', (0, 255, 0)))
        self.obstacles = []
        self.powerup = None
        self.food = self.spawn_food()
        self.poison = self.spawn_food() if random.random() < 0.3 else None
        self.powerup_timer = 0
        self.score = 0
        self.level = 1
        self.speed = FPS
        self.personal_best = get_personal_best(username)
        self.active_powerup = None
        self.powerup_end = 0

    def spawn_food(self):
        while True:
            pos = [random.randrange(1, SCREEN_WIDTH//BLOCK_SIZE) * BLOCK_SIZE,
                   random.randrange(1, SCREEN_HEIGHT//BLOCK_SIZE) * BLOCK_SIZE]
            if pos not in self.snake.body and pos not in self.obstacles and (not self.powerup or pos != self.powerup.get("pos")):
                return pos

    def has_escape_route(self, head):
        neighbors = [
            [head[0] + BLOCK_SIZE, head[1]],
            [head[0] - BLOCK_SIZE, head[1]],
            [head[0], head[1] + BLOCK_SIZE],
            [head[0], head[1] - BLOCK_SIZE],
        ]
        for n in neighbors:
            if 0 <= n[0] < SCREEN_WIDTH and 0 <= n[1] < SCREEN_HEIGHT:
                if n not in self.obstacles and n not in self.snake.body:
                    return True
        return False

    def check_level_up(self):
        if self.score >= self.level * 50:
            self.level += 1
            self.speed += 2
            if self.level >= 3:
                self.spawn_obstacles()

    def spawn_obstacles(self):
        self.obstacles = []
        head = self.snake.body[0]
        no_spawn_zone = {
            tuple(head),
            (head[0] + BLOCK_SIZE, head[1]),
            (head[0] - BLOCK_SIZE, head[1]),
            (head[0], head[1] + BLOCK_SIZE),
            (head[0], head[1] - BLOCK_SIZE),
        }
        for _ in range(self.level * 2):
            attempts = 0
            while True:
                attempts += 1
                pos = [random.randrange(1, SCREEN_WIDTH//BLOCK_SIZE) * BLOCK_SIZE,
                       random.randrange(1, SCREEN_HEIGHT//BLOCK_SIZE) * BLOCK_SIZE]
                pos_key = (pos[0], pos[1])
                # Avoid trapping snake and avoid invalid overlaps.
                if pos not in self.snake.body and pos != self.food and pos != self.poison and pos_key not in no_spawn_zone and pos not in self.obstacles:
                    self.obstacles.append(pos)
                    if not self.has_escape_route(head):
                        self.obstacles.pop()
                        if attempts > 20:
                            break
                        continue
                    break
                if attempts > 40:
                    break

    def run(self, screen):
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 20)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.snake.direction != "DOWN": self.snake.direction = "UP"
                    elif event.key == pygame.K_DOWN and self.snake.direction != "UP": self.snake.direction = "DOWN"
                    elif event.key == pygame.K_LEFT and self.snake.direction != "RIGHT": self.snake.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.snake.direction != "LEFT": self.snake.direction = "RIGHT"

            # Move snake
            head = self.snake.move()

            # Collisions
            collision = False
            if head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT: collision = True
            if head in self.snake.body[1:]: collision = True
            if head in self.obstacles: collision = True

            if collision:
                if self.snake.shielded:
                    self.snake.shielded = False
                    self.active_powerup = None
                    self.snake.body[0] = list(self.snake.body[1])
                else:
                    save_game_result(self.username, self.score, self.level)
                    return "GAMEOVER"

            # Eating Food
            if head == self.food:
                self.score += 10
                self.food = self.spawn_food()
                self.check_level_up()
                if random.random() < 0.2: self.poison = self.spawn_food()
            else:
                self.snake.body.pop()

            # Eating Poison
            if self.poison and head == self.poison:
                if len(self.snake.body) <= 3:
                    save_game_result(self.username, self.score, self.level)
                    return "GAMEOVER"
                self.snake.body = self.snake.body[:-2]
                self.poison = None

            # Powerups
            if not self.powerup and random.random() < 0.05:
                self.powerup = {
                    "pos": self.spawn_food(),
                    "type": random.choice(["SPEED_BOOST", "SLOW_MOTION", "SHIELD"]),
                    "expiry": pygame.time.get_ticks() + 8000
                }
            
            if self.powerup and pygame.time.get_ticks() > self.powerup['expiry']:
                self.powerup = None

            if self.powerup and head == self.powerup['pos']:
                self.active_powerup = self.powerup['type']
                self.powerup_end = pygame.time.get_ticks() + 5000
                if self.active_powerup == "SHIELD":
                    self.snake.shielded = True
                    self.powerup_end = pygame.time.get_ticks() + 1000000
                self.powerup = None

            # Update speed for powerups
            current_fps = self.speed
            if self.active_powerup == "SPEED_BOOST" and pygame.time.get_ticks() < self.powerup_end:
                current_fps += 10
            elif self.active_powerup == "SLOW_MOTION" and pygame.time.get_ticks() < self.powerup_end:
                current_fps = max(5, current_fps - 5)
            elif self.active_powerup and pygame.time.get_ticks() > self.powerup_end and self.active_powerup != "SHIELD":
                self.active_powerup = None

            # Drawing
            screen.fill((0, 0, 0))
            if self.settings.get('grid', True):
                for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                    pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
                for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
                    pygame.draw.line(screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))

            for segment in self.snake.body:
                pygame.draw.rect(screen, self.snake.color, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))
            
            pygame.draw.rect(screen, (255, 0, 0), (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))
            if self.poison:
                pygame.draw.rect(screen, (139, 0, 0), (self.poison[0], self.poison[1], BLOCK_SIZE, BLOCK_SIZE))
            if self.powerup:
                color = (0, 0, 255) if self.powerup['type'] == "SPEED_BOOST" else ((255, 255, 0) if self.powerup['type'] == "SLOW_MOTION" else (255, 0, 255))
                pygame.draw.rect(screen, color, (self.powerup['pos'][0], self.powerup['pos'][1], BLOCK_SIZE, BLOCK_SIZE))
            
            for obs in self.obstacles:
                pygame.draw.rect(screen, (100, 100, 100), (obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE))

            # HUD
            hud = font.render(f"Score: {self.score}  Level: {self.level}  Best: {self.personal_best}", True, (255, 255, 255))
            screen.blit(hud, (10, 10))
            if self.active_powerup:
                if self.active_powerup == "SHIELD":
                    suffix = "(until hit)"
                else:
                    left = max(0, int((self.powerup_end - pygame.time.get_ticks()) / 1000))
                    suffix = f"({left}s)"
                p_text = font.render(f"BUFF: {self.active_powerup} {suffix}", True, (0, 255, 255))
                screen.blit(p_text, (10, 35))

            pygame.display.flip()
            clock.tick(current_fps)
