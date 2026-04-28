import pygame

def draw_text(surface, text, font, color, x, y):
    img = font.render(text, True, color)
    surface.blit(img, (x, y))

def draw_button(surface, rect, text, font, color=(100, 100, 100), text_color=(255, 255, 255)):
    pygame.draw.rect(surface, color, rect)
    txt_surf = font.render(text, True, text_color)
    text_rect = txt_surf.get_rect(center=rect.center)
    surface.blit(txt_surf, text_rect)
