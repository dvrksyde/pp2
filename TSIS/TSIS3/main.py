import pygame
import sys
from persistence import load_settings, save_settings, load_leaderboard
from racer import run_game
from ui import draw_text, draw_button

pygame.init()
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont("Verdana", 25)
small_font = pygame.font.SysFont("Verdana", 18)

def main_menu():
    username = ""
    settings = load_settings()
    
    while True:
        screen.fill((200, 200, 200))
        draw_text(screen, "RACER GAME", font, (0, 0, 0), 100, 50)
        draw_text(screen, "Enter username and press Enter:", small_font, (50, 50, 50), 65, 115)
        input_box = pygame.Rect(90, 145, 220, 35)
        pygame.draw.rect(screen, (255, 255, 255), input_box)
        pygame.draw.rect(screen, (80, 80, 80), input_box, 2)
        draw_text(screen, username or "Player1", small_font, (30, 30, 30), 100, 153)
        
        play_rect = pygame.Rect(100, 200, 200, 50)
        lead_rect = pygame.Rect(100, 270, 200, 50)
        sett_rect = pygame.Rect(100, 340, 200, 50)
        quit_rect = pygame.Rect(100, 410, 200, 50)
        
        draw_button(screen, play_rect, "PLAY", small_font)
        draw_button(screen, lead_rect, "LEADERBOARD", small_font)
        draw_button(screen, sett_rect, "SETTINGS", small_font)
        draw_button(screen, quit_rect, "QUIT", small_font)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    username = username.strip() or "Player1"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isprintable() and len(username) < 18:
                    username += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_pos = event.pos
                if play_rect.collidepoint(m_pos):
                    active_username = username.strip() or "Player1"
                    while True:
                        state, score, dist, coins = run_game(active_username, settings)
                        if state not in ("GAMEOVER", "FINISH"):
                            break
                        action = game_over_screen(score, dist, coins, finished=(state == "FINISH"))
                        if action != "RETRY":
                            break
                elif lead_rect.collidepoint(m_pos):
                    leaderboard_screen()
                elif sett_rect.collidepoint(m_pos):
                    settings_screen(settings)
                elif quit_rect.collidepoint(m_pos):
                    pygame.quit()
                    sys.exit()
                    
        pygame.display.update()

def leaderboard_screen():
    while True:
        screen.fill((255, 255, 255))
        draw_text(screen, "TOP 10 SCORES", font, (0, 0, 0), 80, 40)
        
        scores = load_leaderboard()
        y = 100
        for i, s in enumerate(scores):
            row = f"{i+1:>2}. {s['name']:<10} score:{s['score']:<4} dist:{s['distance']}m coins:{s.get('coins', 0)}"
            draw_text(screen, row, small_font, (0, 0, 0), 15, y)
            y += 30
            
        back_rect = pygame.Rect(150, 520, 100, 40)
        draw_button(screen, back_rect, "BACK", small_font)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos): return
        
        pygame.display.update()

def settings_screen(settings):
    while True:
        screen.fill((240, 240, 240))
        draw_text(screen, "SETTINGS", font, (0, 0, 0), 130, 50)
        
        draw_text(screen, f"Sound: {'ON' if settings['sound'] else 'OFF'}", small_font, (0,0,0), 50, 150)
        draw_text(screen, f"Color: {settings['car_color']}", small_font, (0,0,0), 50, 200)
        draw_text(screen, f"Difficulty: {settings['difficulty']}", small_font, (0,0,0), 50, 250)
        
        save_rect = pygame.Rect(150, 500, 100, 40)
        draw_button(screen, save_rect, "SAVE", small_font, color=(0, 150, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 50 < event.pos[0] < 200:
                    if 140 < event.pos[1] < 170: settings['sound'] = not settings['sound']
                    elif 190 < event.pos[1] < 220: 
                        settings['car_color'] = "BLUE" if settings['car_color'] == "RED" else ("GREEN" if settings['car_color'] == "BLUE" else "RED")
                    elif 240 < event.pos[1] < 270:
                        settings['difficulty'] = "Hard" if settings['difficulty'] == "Medium" else ("Easy" if settings['difficulty'] == "Hard" else "Medium")
                if save_rect.collidepoint(event.pos):
                    save_settings(settings)
                    return
        
        pygame.display.update()

def game_over_screen(score, dist, coins, finished=False):
    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, "RACE FINISHED" if finished else "GAME OVER", font, (255, 0, 0), 90, 150)
        draw_text(screen, f"Score: {score}", small_font, (255, 255, 255), 150, 220)
        draw_text(screen, f"Distance: {dist}m", small_font, (255, 255, 255), 135, 250)
        draw_text(screen, f"Coins: {coins}", small_font, (255, 255, 255), 150, 280)

        retry_rect = pygame.Rect(70, 360, 120, 50)
        back_rect = pygame.Rect(210, 360, 140, 50)
        draw_button(screen, retry_rect, "RETRY", small_font)
        draw_button(screen, back_rect, "MAIN MENU", small_font)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos):
                    return "RETRY"
                if back_rect.collidepoint(event.pos):
                    return "MENU"
        
        pygame.display.update()

if __name__ == "__main__":
    main_menu()
