import pygame
import datetime
import math
from tools import draw_shape

# Base colors (kept for backward compatibility)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Color palette shown in the toolbar — user clicks a swatch to change drawing color
PALETTE = [
    (0,   0,   0),       # Black
    (255, 255, 255),     # White
    (255,   0,   0),     # Red
    (0,   200,   0),     # Green
    (0,     0, 255),     # Blue
    (255, 255,   0),     # Yellow
    (255, 165,   0),     # Orange
    (150,   0, 200),     # Purple
    (0,   200, 200),     # Cyan
    (139,  69,  19),     # Brown
    (255, 100, 150),     # Pink
    (128, 128, 128),     # Gray
]

PALETTE_NAMES = [
    "Black", "White", "Red", "Green", "Blue", "Yellow",
    "Orange", "Purple", "Cyan", "Brown", "Pink", "Gray",
]


class PaintApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("TSIS 2: Paint Application")
        self.clock = pygame.time.Clock()

        self.canvas = pygame.Surface((1000, 600))
        self.canvas.fill(WHITE)

        self.tool = "pencil"  # active tool: pencil, line, rect, circle, square, r_tri, e_tri, rhombus, eraser, fill, text
        self.color = BLACK    # current drawing color
        self.thickness = 2

        self.drawing = False
        self.start_pos = None
        self.last_pos = None

        # Text tool state
        self.text_pos = None
        self.text_content = ""
        self.font = pygame.font.SysFont("Arial", 20)

        # Palette swatch rects built each frame in draw_toolbar; used for click detection
        self.palette_rects = []

        self.running = True

    def get_brush_size(self):
        return self.thickness

    def get_color_name(self):
        """Return the name of the current color if it matches a palette entry, else its RGB value."""
        for i, clr in enumerate(PALETTE):
            if clr == self.color:
                return PALETTE_NAMES[i]
        return str(self.color)

    def draw_toolbar(self):
        """Draw the bottom toolbar with tool info, clickable color palette, and keyboard hints."""
        pygame.draw.rect(self.screen, (200, 200, 200), (0, 600, 1000, 100))

        # Row 1 — current tool, brush size, and selected color name
        info_text = f"Tool: {self.tool} | Size: {self.thickness}px | Color: {self.get_color_name()}"
        self.screen.blit(self.font.render(info_text, True, BLACK), (10, 607))

        # Row 2 — color palette: label, then one 24×24 swatch per palette entry
        self.screen.blit(self.font.render("Color:", True, BLACK), (10, 637))
        self.palette_rects = []
        for i, clr in enumerate(PALETTE):
            rx = 90 + i * 26   # 26px step = 24px swatch + 2px gap
            ry = 634
            rect = pygame.Rect(rx, ry, 24, 24)
            pygame.draw.rect(self.screen, clr, rect)
            if clr == self.color:
                # Highlight the selected swatch with a white inner border
                pygame.draw.rect(self.screen, WHITE, rect.inflate(-4, -4), 2)
                pygame.draw.rect(self.screen, BLACK, rect, 2)
            else:
                pygame.draw.rect(self.screen, (80, 80, 80), rect, 1)
            self.palette_rects.append((rect, clr))

        # Row 3 — keyboard shortcut reference
        controls = ("Keys: 1-3(Size)  P(Pencil)  L(Line)  R(Rect)  C(Circle)  "
                    "S(Square)  T(Tri)  E(EqTri)  M(Rhombus)  F(Fill)  X(Text)  Z(Eraser)  Ctrl+S(Save)")
        self.screen.blit(self.font.render(controls, True, BLACK), (10, 670))

    def flood_fill(self, x, y, new_color):
        """Iterative flood-fill: replaces the contiguous region of the clicked color with new_color."""
        target_color = self.canvas.get_at((x, y))
        if target_color == new_color:
            return

        pixels = [(x, y)]
        width, height = self.canvas.get_size()

        while pixels:
            curr_x, curr_y = pixels.pop()
            if self.canvas.get_at((curr_x, curr_y)) == target_color:
                self.canvas.set_at((curr_x, curr_y), new_color)
                if curr_x > 0:           pixels.append((curr_x - 1, curr_y))
                if curr_x < width - 1:   pixels.append((curr_x + 1, curr_y))
                if curr_y > 0:           pixels.append((curr_x, curr_y - 1))
                if curr_y < height - 1:  pixels.append((curr_x, curr_y + 1))

    def run(self):
        while self.running:
            self.screen.fill(WHITE)
            self.screen.blit(self.canvas, (0, 0))

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    # Brush size shortcuts
                    if event.key == pygame.K_1:   self.thickness = 2
                    elif event.key == pygame.K_2: self.thickness = 5
                    elif event.key == pygame.K_3: self.thickness = 10
                    # Tool shortcuts
                    elif event.key == pygame.K_p: self.tool = "pencil"
                    elif event.key == pygame.K_l: self.tool = "line"
                    elif event.key == pygame.K_r: self.tool = "rect"
                    elif event.key == pygame.K_c: self.tool = "circle"
                    elif event.key == pygame.K_s: self.tool = "square"
                    elif event.key == pygame.K_t: self.tool = "r_tri"
                    elif event.key == pygame.K_e: self.tool = "e_tri"
                    elif event.key == pygame.K_m: self.tool = "rhombus"
                    elif event.key == pygame.K_f: self.tool = "fill"
                    elif event.key == pygame.K_x: self.tool = "text"
                    elif event.key == pygame.K_z: self.tool = "eraser"

                    # Ctrl+S — save canvas as PNG with a timestamp filename
                    if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        fname = f"paint_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        pygame.image.save(self.canvas, fname)
                        print(f"Saved as {fname}")

                    # Text tool — handle character input while a text position is set
                    if self.tool == "text" and self.text_pos:
                        if event.key == pygame.K_RETURN:
                            txt_surf = self.font.render(self.text_content, True, self.color)
                            self.canvas.blit(txt_surf, self.text_pos)
                            self.text_pos = None
                            self.text_content = ""
                        elif event.key == pygame.K_ESCAPE:
                            self.text_pos = None
                            self.text_content = ""
                        elif event.key == pygame.K_BACKSPACE:
                            self.text_content = self.text_content[:-1]
                        else:
                            self.text_content += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mouse_pos[1] >= 600:
                        # Click inside the toolbar — check if a color swatch was clicked
                        for rect, clr in self.palette_rects:
                            if rect.collidepoint(mouse_pos):
                                self.color = clr  # change the active drawing color
                                break
                    else:
                        # Click on the canvas
                        if self.tool == "fill":
                            self.flood_fill(mouse_pos[0], mouse_pos[1], self.color)
                        elif self.tool == "text":
                            self.text_pos = mouse_pos
                            self.text_content = ""
                        else:
                            self.drawing = True
                            self.start_pos = mouse_pos
                            self.last_pos = mouse_pos

                if event.type == pygame.MOUSEBUTTONUP:
                    if self.drawing:
                        if self.tool != "pencil":
                            # Commit the final shape to the canvas on mouse release
                            draw_shape(self.canvas, self.tool, self.start_pos, mouse_pos, self.color, self.thickness)
                        self.drawing = False

            if self.drawing:
                if self.tool == "pencil":
                    # Pencil draws continuously as the mouse moves
                    pygame.draw.line(self.canvas, self.color, self.last_pos, mouse_pos, self.thickness)
                    self.last_pos = mouse_pos
                elif self.tool == "eraser":
                    # Eraser always uses the canvas background color (white) regardless of selected color
                    pygame.draw.circle(self.canvas, WHITE, mouse_pos, self.thickness * 2)
                else:
                    # Live preview: draw the shape on the screen surface (not the canvas)
                    # so the preview disappears when the mouse moves
                    draw_shape(self.screen, self.tool, self.start_pos, mouse_pos, self.color, self.thickness)

            # Show text cursor preview while typing
            if self.tool == "text" and self.text_pos:
                txt_surf = self.font.render(self.text_content + "|", True, self.color)
                self.screen.blit(txt_surf, self.text_pos)

            self.draw_toolbar()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    PaintApp().run()
