import pygame
import random
from config import *
from db import save_game_result, get_personal_best

# Wall border color: distinct from gray obstacles so the player can clearly see boundaries
WALL_COLOR = (180, 100, 40)


class Snake:
    """Player-controlled snake.

    The body is stored as a list of [x, y] grid positions (multiples of BLOCK_SIZE).
    body[0] is the head; body[-1] is the tail.
    """

    def __init__(self, color=(0, 255, 0)):
        # Start with a 3-segment snake pointing right, well inside the wall border
        self.body = [[100, 100], [80, 100], [60, 100]]
        self.direction = "RIGHT"
        self.color = color
        self.shielded = False  # True while a Shield powerup is active

    def move(self):
        """Advance the snake one step in the current direction.

        Inserts a new head and returns it. The caller is responsible for
        removing the tail when the snake did NOT eat food this frame.
        """
        head = list(self.body[0])
        if self.direction == "UP":    head[1] -= BLOCK_SIZE
        elif self.direction == "DOWN":  head[1] += BLOCK_SIZE
        elif self.direction == "LEFT":  head[0] -= BLOCK_SIZE
        elif self.direction == "RIGHT": head[0] += BLOCK_SIZE
        self.body.insert(0, head)
        return head


class Game:
    """Manages all game state, the main loop, and rendering for one play session."""

    def __init__(self, username, settings):
        self.username = username
        self.settings = settings
        self.snake = Snake(settings.get('snake_color', (0, 255, 0)))
        self.obstacles = []
        self.powerup = None
        self.food = self.spawn_food()
        # Poison spawns with 30% probability at the start of each game
        self.poison = self.spawn_food() if random.random() < 0.3 else None
        self.powerup_timer = 0
        self.score = 0
        self.level = 1
        self.speed = FPS      # current game speed in frames per second
        self.personal_best = get_personal_best(username)
        self.active_powerup = None
        self.powerup_end = 0

    def spawn_food(self):
        """Return a random interior grid position that avoids walls, snake, obstacles, and powerups.

        Positions are kept one cell inside the screen edges so food never
        appears on the wall border that surrounds the playing area.
        """
        while True:
            # randrange(1, N-1) excludes both the first cell (wall) and the last cell (wall)
            pos = [
                random.randrange(1, (SCREEN_WIDTH  // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                random.randrange(1, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE,
            ]
            if (pos not in self.snake.body
                    and pos not in self.obstacles
                    and (not self.powerup or pos != self.powerup.get("pos"))):
                return pos

    def has_escape_route(self, head):
        """Return True if the snake head has at least one free neighboring cell.

        Used during obstacle placement to ensure the snake is never fully boxed in.
        A 'free' cell must be inside the wall border and unoccupied.
        """
        neighbors = [
            [head[0] + BLOCK_SIZE, head[1]],
            [head[0] - BLOCK_SIZE, head[1]],
            [head[0], head[1] + BLOCK_SIZE],
            [head[0], head[1] - BLOCK_SIZE],
        ]
        for n in neighbors:
            # Cell must be in the interior (not on the wall border)
            if (BLOCK_SIZE <= n[0] < SCREEN_WIDTH - BLOCK_SIZE
                    and BLOCK_SIZE <= n[1] < SCREEN_HEIGHT - BLOCK_SIZE):
                if n not in self.obstacles and n not in self.snake.body:
                    return True
        return False

    def check_level_up(self):
        """Advance to the next level when the score threshold is reached.

        Threshold formula: level * 50 points.
        Each level-up increases movement speed by 2 FPS.
        Obstacles start appearing from level 3 onward.
        """
        if self.score >= self.level * 50:
            self.level += 1
            self.speed += 2  # make the snake move faster every level
            if self.level >= 3:
                self.spawn_obstacles()

    def spawn_obstacles(self):
        """Regenerate the obstacle set sized for the current level.

        Obstacle count = level * 2. Each obstacle is placed in the interior
        with safety checks to guarantee the snake always has an escape route.
        """
        self.obstacles = []
        head = self.snake.body[0]
        # Cells directly adjacent to the head are reserved — no obstacles here
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
                # Only spawn in the interior to avoid overlapping wall cells
                pos = [
                    random.randrange(1, (SCREEN_WIDTH  // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                    random.randrange(1, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE,
                ]
                pos_key = (pos[0], pos[1])
                if (pos not in self.snake.body
                        and pos != self.food
                        and pos != self.poison
                        and pos_key not in no_spawn_zone
                        and pos not in self.obstacles):
                    self.obstacles.append(pos)
                    # Roll back if this placement traps the snake
                    if not self.has_escape_route(head):
                        self.obstacles.pop()
                        if attempts > 20:
                            break
                        continue
                    break
                if attempts > 40:
                    break

    def _draw_walls(self, screen):
        """Draw the one-cell-wide border of wall tiles around the screen perimeter.

        The snake dies on contact with any of these cells.
        """
        # Top and bottom rows span the full width
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.rect(screen, WALL_COLOR, (x, 0, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, WALL_COLOR, (x, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        # Left and right columns, skipping corners already covered above
        for y in range(BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE):
            pygame.draw.rect(screen, WALL_COLOR, (0, y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, WALL_COLOR, (SCREEN_WIDTH - BLOCK_SIZE, y, BLOCK_SIZE, BLOCK_SIZE))

    def run(self, screen):
        """Run the game loop until the player quits or the game ends.

        Returns 'QUIT' (window closed) or 'GAMEOVER' (snake collision).
        """
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("Arial", 20)

        while True:
            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    # Prevent 180-degree reversals
                    if event.key == pygame.K_UP    and self.snake.direction != "DOWN":  self.snake.direction = "UP"
                    elif event.key == pygame.K_DOWN  and self.snake.direction != "UP":   self.snake.direction = "DOWN"
                    elif event.key == pygame.K_LEFT  and self.snake.direction != "RIGHT": self.snake.direction = "LEFT"
                    elif event.key == pygame.K_RIGHT and self.snake.direction != "LEFT":  self.snake.direction = "RIGHT"

            # --- Move snake ---
            head = self.snake.move()

            # --- Collision detection ---
            collision = False

            # Wall (border) collision: the outer ring of cells are wall tiles —
            # the snake is leaving the playing area when it enters these cells
            if (head[0] < BLOCK_SIZE or head[0] > SCREEN_WIDTH - 2 * BLOCK_SIZE
                    or head[1] < BLOCK_SIZE or head[1] > SCREEN_HEIGHT - 2 * BLOCK_SIZE):
                collision = True

            # Self-collision: head overlaps any body segment behind it
            if head in self.snake.body[1:]:
                collision = True

            # Obstacle collision
            if head in self.obstacles:
                collision = True

            if collision:
                if self.snake.shielded:
                    # Shield absorbs one collision — snap the head back to the second segment
                    self.snake.shielded = False
                    self.active_powerup = None
                    self.snake.body[0] = list(self.snake.body[1])
                else:
                    save_game_result(self.username, self.score, self.level)
                    return "GAMEOVER"

            # --- Eating food ---
            if head == self.food:
                self.score += 10
                self.food = self.spawn_food()
                self.check_level_up()  # check if score crossed the next level threshold
                if random.random() < 0.2:
                    self.poison = self.spawn_food()  # occasionally place a poison pellet
            else:
                # No food eaten — pop the tail to keep the snake length constant
                self.snake.body.pop()

            # --- Eating poison ---
            if self.poison and head == self.poison:
                if len(self.snake.body) <= 3:
                    # Snake is too short to survive losing two segments
                    save_game_result(self.username, self.score, self.level)
                    return "GAMEOVER"
                self.snake.body = self.snake.body[:-2]  # shorten by 2 segments
                self.poison = None

            # --- Powerup spawning ---
            if not self.powerup and random.random() < 0.05:
                self.powerup = {
                    "pos": self.spawn_food(),
                    "type": random.choice(["SPEED_BOOST", "SLOW_MOTION", "SHIELD"]),
                    "expiry": pygame.time.get_ticks() + 8000  # disappears after 8 seconds
                }

            # Remove powerup if it expired without being collected
            if self.powerup and pygame.time.get_ticks() > self.powerup['expiry']:
                self.powerup = None

            # --- Picking up a powerup ---
            if self.powerup and head == self.powerup['pos']:
                self.active_powerup = self.powerup['type']
                self.powerup_end = pygame.time.get_ticks() + 5000
                if self.active_powerup == "SHIELD":
                    self.snake.shielded = True
                    self.powerup_end = pygame.time.get_ticks() + 1000000  # lasts until hit
                self.powerup = None

            # --- Speed modifiers from active powerup ---
            current_fps = self.speed
            if self.active_powerup == "SPEED_BOOST" and pygame.time.get_ticks() < self.powerup_end:
                current_fps += 10
            elif self.active_powerup == "SLOW_MOTION" and pygame.time.get_ticks() < self.powerup_end:
                current_fps = max(5, current_fps - 5)
            elif self.active_powerup and pygame.time.get_ticks() > self.powerup_end and self.active_powerup != "SHIELD":
                self.active_powerup = None

            # --- Drawing ---
            screen.fill((0, 0, 0))

            # Optional grid overlay (cosmetic — shows cell boundaries)
            if self.settings.get('grid', True):
                for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                    pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
                for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
                    pygame.draw.line(screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))

            # Draw the border walls — snake dies on contact with these
            self._draw_walls(screen)

            # Draw snake body segments
            for segment in self.snake.body:
                pygame.draw.rect(screen, self.snake.color, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

            # Draw food (red), poison (dark red), and powerup (color-coded by type)
            pygame.draw.rect(screen, (255, 0, 0), (self.food[0], self.food[1], BLOCK_SIZE, BLOCK_SIZE))
            if self.poison:
                pygame.draw.rect(screen, (139, 0, 0), (self.poison[0], self.poison[1], BLOCK_SIZE, BLOCK_SIZE))
            if self.powerup:
                color = ((0, 0, 255) if self.powerup['type'] == "SPEED_BOOST"
                         else (255, 255, 0) if self.powerup['type'] == "SLOW_MOTION"
                         else (255, 0, 255))
                pygame.draw.rect(screen, color, (self.powerup['pos'][0], self.powerup['pos'][1], BLOCK_SIZE, BLOCK_SIZE))

            # Draw obstacles (gray blocks, present from level 3 onward)
            for obs in self.obstacles:
                pygame.draw.rect(screen, (100, 100, 100), (obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE))

            # --- HUD: score counter, level counter, personal best ---
            hud = font.render(f"Score: {self.score}  Level: {self.level}  Best: {self.personal_best}", True, (255, 255, 255))
            screen.blit(hud, (10, 10))
            if self.active_powerup:
                suffix = ("(until hit)" if self.active_powerup == "SHIELD"
                          else f"({max(0, int((self.powerup_end - pygame.time.get_ticks()) / 1000))}s)")
                p_text = font.render(f"BUFF: {self.active_powerup} {suffix}", True, (0, 255, 255))
                screen.blit(p_text, (10, 35))

            pygame.display.flip()
            clock.tick(current_fps)
