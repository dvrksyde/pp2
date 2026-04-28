import pygame
import math

def draw_shape(surface, tool, start, end, color, thickness):
    if not start or not end: return
    
    x1, y1 = start
    x2, y2 = end
    width = x2 - x1
    height = y2 - y1
    
    if tool == "line":
        pygame.draw.line(surface, color, start, end, thickness)
    elif tool == "rect":
        pygame.draw.rect(surface, color, (min(x1, x2), min(y1, y2), abs(width), abs(height)), thickness)
    elif tool == "circle":
        radius = int(math.hypot(width, height))
        pygame.draw.circle(surface, color, start, radius, thickness)
    elif tool == "square":
        side = max(abs(width), abs(height))
        pygame.draw.rect(surface, color, (min(x1, x2), min(y1, y2), side, side), thickness)
    elif tool == "r_tri":
        pygame.draw.polygon(surface, color, [(x1, y1), (x1, y2), (x2, y2)], thickness)
    elif tool == "e_tri":
        side = abs(width)
        h = side * math.sqrt(3) / 2
        pygame.draw.polygon(surface, color, [(x1, y1), (x1 + side, y1), (x1 + side/2, y1 - h)], thickness)
    elif tool == "rhombus":
        pygame.draw.polygon(surface, color, [(x1 + width/2, y1), (x1 + width, y1 + height/2), (x1 + width/2, y1 + height), (x1, y1 + height/2)], thickness)
