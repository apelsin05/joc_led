import pygame
import os
from .constants import *

class CircuitVisualizer:
    def __init__(self, x, y, max_height=250):
        self.pos = (x, y)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        assets_path = os.path.join(project_root, "assets")
        
        try:
            img_on_raw = pygame.image.load(os.path.join(assets_path, "circuit_on.png")).convert_alpha()
            img_off_raw = pygame.image.load(os.path.join(assets_path, "circuit_off.png")).convert_alpha()
            
            # Dynamic scaling based on max_height
            aspect_ratio = img_on_raw.get_width() / img_on_raw.get_height()
            target_width = int(max_height * aspect_ratio)
            
            self.img_on = pygame.transform.smoothscale(img_on_raw, (target_width, max_height))
            self.img_off = pygame.transform.smoothscale(img_off_raw, (target_width, max_height))
            
        except Exception as e:
            print(f"Error loading circuit images: {e}")
            # Fallback surfaces
            self.img_on = pygame.Surface((200, max_height))
            self.img_on.fill((255, 255, 0))
            self.img_off = pygame.Surface((200, max_height))
            self.img_off.fill((50, 50, 50))

        self.is_lit = False
        self.demo_active = False
        self.demo_start_time = 0

    def start_demo(self):
        self.demo_active = True
        self.demo_start_time = pygame.time.get_ticks()
        self.is_lit = False

    def update(self, current_time):
        if not self.demo_active:
            return

        elapsed = current_time - self.demo_start_time
        pattern_time = 0
        found_state = False

        for state, duration, _, _ in TARGET_PATTERN:
            pattern_time += duration
            if elapsed < pattern_time:
                self.is_lit = state
                found_state = True
                break
        
        if not found_state:
            self.is_lit = False
            self.demo_active = False

    def draw(self, surface):
        if self.is_lit:
            surface.blit(self.img_on, self.pos)
        else:
            surface.blit(self.img_off, self.pos)

class RunButton:
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = "COMPILEAZĂ"  # Textul cerut
        
        # Culori stil "Arduino IDE"
        self.base_color = (0, 151, 157)    # Turcoaz închis
        self.hover_color = (0, 180, 185)   # Turcoaz deschis
        self.text_color = (255, 255, 255)  # Alb

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        # Schimbă culoarea când mouse-ul este deasupra (feedback vizual)
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        
        # Desenăm corpul butonului
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)

        # Desenăm textul centrat
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Această funcție returnează True DOAR când se apasă click stânga pe buton"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Click stânga
                if self.rect.collidepoint(event.pos):
                    return True
        return False

class DraggableBlock:
    def __init__(self, x, y, width, height, data):
        self.rect = pygame.Rect(x, y, width, height)
        self.data = data
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        # --- ADAPTIVE FONT SCALING ---
        # Start with a base size relative to height
        base_font_size = int(height * 0.4) 
        self.font = pygame.font.SysFont("arial", base_font_size, bold=True)
        
        # Render text to check width
        self.text_lines = data[2].split('\n')
        self.rendered_lines = []
        
        for line in self.text_lines:
            s = self.font.render(line, True, (255, 255, 255))
            # If text is too wide, scale it down
            if s.get_width() > width - 10:
                scale_factor = (width - 10) / s.get_width()
                new_w = int(s.get_width() * scale_factor)
                new_h = int(s.get_height() * scale_factor)
                s = pygame.transform.smoothscale(s, (new_w, new_h))
            self.rendered_lines.append(s)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                mx, my = event.pos
                self.offset_x = self.rect.x - mx
                self.offset_y = self.rect.y - my
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                mx, my = event.pos
                self.rect.x = mx + self.offset_x
                self.rect.y = my + self.offset_y
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 120, 215), self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)
        
        total_h = sum([img.get_height() for img in self.rendered_lines])
        start_y = self.rect.centery - (total_h / 2)
        
        for img in self.rendered_lines:
            r = img.get_rect(centerx=self.rect.centerx, top=start_y)
            surface.blit(img, r)
            start_y += img.get_height() + 2

# UPDATED: Now accepts 'rect' argument to support dynamic layouts
def draw_solution_zone(surface, font, rect):
    pygame.draw.rect(surface, (230, 230, 230), rect, border_radius=10)
    pygame.draw.rect(surface, (150, 150, 150), rect, 3, border_radius=10)
    
    lbl = font.render("ZONA SOLUȚIE", True, (100, 100, 100))
    # Draw text centered horizontally in the rect, slightly down from top
    surface.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.y + 10))

def draw_timer(surface, seconds, font):
    col = COLOR_TEXT_BLACK if seconds > 10 else COLOR_FAIL
    txt = font.render(f"Timp: {seconds}s", True, col)
    surface.blit(txt, (20, 20))