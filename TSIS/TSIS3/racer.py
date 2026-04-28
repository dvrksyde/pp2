import pygame
import random
from persistence import save_score

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
LANE_WIDTH = SCREEN_WIDTH // 4
TRACK_GOAL = 2000

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 70, 70)
GREEN = (60, 220, 120)
BLUE = (50, 150, 255)
GRAY = (110, 110, 110)
YELLOW = (250, 220, 80)
ORANGE = (255, 150, 0)
PURPLE = (180, 90, 220)


def lane_center(lane):
    return lane * LANE_WIDTH + LANE_WIDTH // 2


def safe_lane(player_lane):
    candidates = [0, 1, 2, 3]
    if player_lane in candidates:
        candidates.remove(player_lane)
    return random.choice(candidates)


def make_entity(kind, player_rect, player_lane):
    lane = safe_lane(player_lane)
    if kind == "traffic":
        rect = pygame.Rect(0, 0, 42, 62)
        color = RED
    elif kind == "obstacle":
        rect = pygame.Rect(0, 0, 44, 26)
        color = ORANGE
    elif kind == "oil":
        rect = pygame.Rect(0, 0, 46, 20)
        color = BLACK
    elif kind == "bump":
        rect = pygame.Rect(0, 0, 50, 12)
        color = (130, 80, 40)
    elif kind == "coin":
        rect = pygame.Rect(0, 0, 20, 20)
        color = YELLOW
    elif kind == "powerup":
        rect = pygame.Rect(0, 0, 26, 26)
        color = PURPLE
    else:
        rect = pygame.Rect(0, 0, 34, 34)
        color = WHITE
    rect.centerx = lane_center(lane)
    rect.y = -rect.height - random.randint(10, 120)
    if abs(rect.y - player_rect.y) < 120:
        rect.y -= 140
    return {"kind": kind, "lane": lane, "rect": rect, "color": color}


def run_game(username, settings):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Verdana", 18)

    player = pygame.Rect(0, 0, 40, 60)
    player.center = (lane_center(1), 520)

    car_color = settings.get("car_color", "RED")
    car_rgb = RED if car_color == "RED" else (BLUE if car_color == "BLUE" else GREEN)
    difficulty = settings.get("difficulty", "Medium")
    base_speed = 3 if difficulty == "Easy" else 5 if difficulty == "Medium" else 7

    traffic = []
    hazards = []
    coins = []
    road_events = []
    powerups = []

    active_powerup = None
    powerup_end = 0
    shield_hits = 0
    distance = 0.0
    coins_collected = 0
    bonus_points = 0

    running = True
    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "MENU", 0, 0, 0

        # Player lane movement.
        keys = pygame.key.get_pressed()
        player_lane = max(0, min(3, player.centerx // LANE_WIDTH))
        if keys[pygame.K_LEFT] and player_lane > 0:
            player.centerx = lane_center(player_lane - 1)
        if keys[pygame.K_RIGHT] and player_lane < 3:
            player.centerx = lane_center(player_lane + 1)

        # Dynamic difficulty scaling.
        progress_scale = 1 + (distance / TRACK_GOAL) * 0.8
        speed = base_speed * progress_scale
        traffic_rate = 0.015 + (distance / TRACK_GOAL) * 0.02
        obstacle_rate = 0.01 + (distance / TRACK_GOAL) * 0.02

        if active_powerup == "Nitro" and now < powerup_end:
            speed += 4
        if active_powerup and now >= powerup_end and active_powerup != "Shield":
            active_powerup = None

        # Spawn traffic/obstacles/events/coins/powerups.
        current_lane = player.centerx // LANE_WIDTH
        if random.random() < traffic_rate:
            traffic.append(make_entity("traffic", player, current_lane))
        if random.random() < obstacle_rate:
            hazards.append(make_entity(random.choice(["obstacle", "oil"]), player, current_lane))
        if random.random() < 0.008:
            road_events.append(make_entity("bump", player, current_lane))
        if random.random() < 0.02:
            coin = make_entity("coin", player, current_lane)
            coin["weight"] = random.randint(1, 3)
            coins.append(coin)
        if not active_powerup and not powerups and random.random() < 0.005:
            p = make_entity("powerup", player, current_lane)
            p_type = random.choice(["Nitro", "Shield", "Repair"])
            p["power_type"] = p_type
            p["timeout"] = now + 6000
            if p_type == "Nitro":
                p["color"] = BLUE
            elif p_type == "Shield":
                p["color"] = GREEN
            else:
                p["color"] = PURPLE
            powerups.append(p)

        # Move entities downward.
        for group in (traffic, hazards, road_events, coins, powerups):
            for item in group:
                item["rect"].y += int(speed)

        # Remove off-screen and timed-out entities.
        traffic = [x for x in traffic if x["rect"].top < SCREEN_HEIGHT + 10]
        hazards = [x for x in hazards if x["rect"].top < SCREEN_HEIGHT + 10]
        road_events = [x for x in road_events if x["rect"].top < SCREEN_HEIGHT + 10]
        coins = [x for x in coins if x["rect"].top < SCREEN_HEIGHT + 10]
        powerups = [x for x in powerups if x["rect"].top < SCREEN_HEIGHT + 10 and now <= x["timeout"]]

        # Collisions.
        hit_traffic = any(player.colliderect(t["rect"]) for t in traffic)
        hit_hazard = [h for h in hazards if player.colliderect(h["rect"])]
        hit_bump = any(player.colliderect(b["rect"]) for b in road_events)
        collected = [c for c in coins if player.colliderect(c["rect"])]
        picked_power = [p for p in powerups if player.colliderect(p["rect"])]

        if hit_traffic:
            if active_powerup == "Shield" and shield_hits == 0:
                shield_hits = 1
                active_powerup = None
                traffic.clear()
            else:
                score = int(coins_collected * 20 + distance * 0.3 + bonus_points)
                save_score(username, score, int(distance), coins_collected)
                return "GAMEOVER", score, int(distance), coins_collected

        for hazard in hit_hazard:
            if hazard["kind"] == "oil":
                # Slow zone / oil spill effect.
                distance = max(0, distance - 3)
            else:
                if active_powerup == "Shield" and shield_hits == 0:
                    shield_hits = 1
                    active_powerup = None
                else:
                    score = int(coins_collected * 20 + distance * 0.3 + bonus_points)
                    save_score(username, score, int(distance), coins_collected)
                    return "GAMEOVER", score, int(distance), coins_collected
        hazards = [h for h in hazards if h not in hit_hazard]

        if hit_bump:
            distance = max(0, distance - 2)
            bonus_points += 5
            road_events = [b for b in road_events if not player.colliderect(b["rect"])]

        for c in collected:
            coins_collected += c["weight"]
            bonus_points += c["weight"] * 6
        coins = [c for c in coins if c not in collected]

        for p in picked_power:
            active_powerup = p["power_type"]
            if active_powerup == "Nitro":
                powerup_end = now + 4000
                bonus_points += 15
            elif active_powerup == "Shield":
                powerup_end = now + 120000
                shield_hits = 0
            elif active_powerup == "Repair":
                powerup_end = now
                active_powerup = None
                traffic = traffic[: max(0, len(traffic) - 1)]
                hazards = hazards[: max(0, len(hazards) - 1)]
                bonus_points += 10
        powerups = [p for p in powerups if p not in picked_power]

        distance += speed * 0.25
        if distance >= TRACK_GOAL:
            score = int(coins_collected * 20 + distance * 0.3 + bonus_points + 100)
            save_score(username, score, int(distance), coins_collected)
            return "FINISH", score, int(distance), coins_collected

        # Draw.
        screen.fill(GRAY)
        for lane in range(1, 4):
            pygame.draw.line(screen, WHITE, (lane * LANE_WIDTH, 0), (lane * LANE_WIDTH, SCREEN_HEIGHT), 2)
        pygame.draw.rect(screen, car_rgb, player)
        for group in (traffic, hazards, road_events, coins, powerups):
            for item in group:
                pygame.draw.rect(screen, item["color"], item["rect"])

        remaining = max(0, int(TRACK_GOAL - distance))
        score_live = int(coins_collected * 20 + distance * 0.3 + bonus_points)
        screen.blit(font.render(f"Score: {score_live}", True, BLACK), (10, 8))
        screen.blit(font.render(f"Coins: {coins_collected}", True, BLACK), (10, 32))
        screen.blit(font.render(f"Dist: {int(distance)}m", True, BLACK), (260, 8))
        screen.blit(font.render(f"To finish: {remaining}m", True, BLACK), (220, 32))

        if active_powerup:
            time_left = "hit" if active_powerup == "Shield" else f"{max(0, int((powerup_end - now) / 1000))}s"
            txt = font.render(f"Power: {active_powerup} ({time_left})", True, BLUE)
            screen.blit(txt, (10, 56))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    pass
