import pygame
import sys
import json
import os
from db import init_db, get_top_scores
from game import Game
from config import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 20)

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"snake_color": [0, 255, 0], "grid": True, "sound": True}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f: return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f: json.dump(s, f)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def main_menu():
    username = ""
    settings = load_settings()
    db_ready = init_db()
    
    while True:
        screen.fill((30, 30, 30))
        draw_text("SNAKE MASTER", font, (0, 255, 0), 200, 50)
        if not db_ready:
            draw_text("DB offline: leaderboard save/load disabled", small_font, (255, 120, 120), 140, 75)
        draw_text("Enter username and press Enter:", small_font, (200, 200, 200), 180, 100)
        input_box = pygame.Rect(190, 125, 220, 35)
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (120, 120, 120), input_box, 2)
        draw_text(username or "Player", small_font, (20, 20, 20), 200, 133)
        
        play_btn = pygame.Rect(200, 200, 200, 50)
        lead_btn = pygame.Rect(200, 270, 200, 50)
        sett_btn = pygame.Rect(200, 340, 200, 50)
        quit_btn = pygame.Rect(200, 410, 200, 50)
        
        for btn, txt in [(play_btn, "PLAY"), (lead_btn, "LEADERBOARD"), (sett_btn, "SETTINGS"), (quit_btn, "QUIT")]:
            pygame.draw.rect(screen, (60, 60, 60), btn)
            draw_text(txt, small_font, (255, 255, 255), btn.x + 40, btn.y + 15)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    username = username.strip() or "Player"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isprintable() and len(username) < 18:
                    username += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    active_username = username.strip() or "Player"
                    while True:
                        game = Game(active_username, settings)
                        res = game.run(screen)
                        if res != "GAMEOVER":
                            break
                        action = game_over_screen(game.score, game.level, game.personal_best)
                        if action != "RETRY":
                            break
                elif lead_btn.collidepoint(event.pos): leaderboard_screen()
                elif sett_btn.collidepoint(event.pos): settings_screen(settings)
                elif quit_btn.collidepoint(event.pos): sys.exit()
        
        pygame.display.flip()

def leaderboard_screen():
    while True:
        screen.fill((20, 20, 20))
        draw_text("TOP 10 PLAYERS", font, (255, 255, 0), 180, 50)
        scores = get_top_scores()
        y = 120
        for i, s in enumerate(scores):
            date_str = s[3].strftime("%Y-%m-%d") if hasattr(s[3], "strftime") else str(s[3])[:10]
            row = f"{i+1:>2}. {s[0]:<10} score:{s[1]:<4} lvl:{s[2]}  {date_str}"
            draw_text(row, small_font, (255, 255, 255), 40, y)
            y += 30
            
        back = pygame.Rect(250, 520, 100, 40)
        pygame.draw.rect(screen, (100, 0, 0), back)
        draw_text("BACK", small_font, (255, 255, 255), 275, 530)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(event.pos): return
        pygame.display.flip()

def settings_screen(s):
    while True:
        screen.fill((40, 40, 40))
        draw_text("SETTINGS", font, (255, 255, 255), 230, 50)
        draw_text(f"Grid: {'ON' if s['grid'] else 'OFF'}", small_font, (200, 200, 200), 200, 150)
        draw_text(f"Sound: {'ON' if s['sound'] else 'OFF'}", small_font, (200, 200, 200), 200, 200)
        draw_text(f"Snake color: {tuple(s['snake_color'])}", small_font, (200, 200, 200), 200, 250)
        
        save = pygame.Rect(250, 450, 100, 40)
        pygame.draw.rect(screen, (0, 100, 0), save)
        draw_text("SAVE & BACK", small_font, (255, 255, 255), 245, 460)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 200 < event.pos[0] < 300:
                    if 140 < event.pos[1] < 170: s['grid'] = not s['grid']
                    elif 190 < event.pos[1] < 220: s['sound'] = not s['sound']
                    elif 240 < event.pos[1] < 270:
                        palette = [[0, 255, 0], [0, 180, 255], [255, 200, 0], [255, 80, 80]]
                        current = s.get('snake_color', [0, 255, 0])
                        idx = palette.index(current) if current in palette else 0
                        s['snake_color'] = palette[(idx + 1) % len(palette)]
                if save.collidepoint(event.pos):
                    save_settings(s)
                    return
        pygame.display.flip()

def game_over_screen(score, level, best):
    while True:
        screen.fill((0, 0, 0))
        draw_text("GAME OVER", font, (255, 0, 0), 220, 150)
        draw_text(f"Score: {score}  Level: {level}", small_font, (255, 255, 255), 220, 220)
        draw_text(f"Personal Best: {best}", small_font, (255, 255, 0), 230, 250)

        retry = pygame.Rect(150, 350, 120, 50)
        menu = pygame.Rect(300, 350, 160, 50)
        pygame.draw.rect(screen, (70, 70, 70), retry)
        pygame.draw.rect(screen, (50, 50, 50), menu)
        draw_text("RETRY", small_font, (255, 255, 255), 180, 365)
        draw_text("MAIN MENU", small_font, (255, 255, 255), 325, 365)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry.collidepoint(event.pos):
                    return "RETRY"
                if menu.collidepoint(event.pos):
                    return "MENU"
        pygame.display.flip()

if __name__ == "__main__":
    main_menu()
