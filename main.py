import pygame
import sys
from src.constants import *
from src.ui import CircuitVisualizer, DraggableBlock, RunButton, draw_solution_zone, draw_timer
from src.backend import validate_sequence

# Game States
STATE_WAITING = 0
STATE_DEMO = 1
STATE_GAMEPLAY = 2
STATE_WIN = 3
STATE_FAIL = 4

def main():
    pygame.init()
    
    # 1. Detectare Sigură a Rezoluției
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h
    
    # Fallback: Dacă nu poate detecta rezoluția (ex: returnează 0 sau -1), folosim standard
    if W <= 0 or H <= 0:
        W, H = 1024, 768
        print("WARN: Nu s-a putut detecta rezoluția. Se folosește 1024x768.")
    else:
        print(f"INFO: Rezoluție detectată: {W} x {H}")

    # Setăm modul ecran complet
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    pygame.display.set_caption("LED Morse Challenge")
    clock = pygame.time.Clock()

    # 2. Configurare Fonturi (Adaptabile)
    # Ne asigurăm că fontul este cel puțin 14px
    ui_font_size = max(20, int(H / 35))
    big_font_size = max(40, int(H / 15))
    
    font_ui = pygame.font.SysFont("arial", ui_font_size)
    font_big = pygame.font.SysFont("arial", big_font_size, bold=True)

    # --- CALCULARE LAYOUT ---
    
    # 1. Top Half: Circuit
    half_height = H // 2
    
    circuit_h = int(half_height * 0.7) # 70% din jumătatea de sus
    circuit_x = (W // 2) - 100 
    circuit_y = (half_height - circuit_h) // 2 
    
    circuit = CircuitVisualizer(x=circuit_x, y=circuit_y, max_height=circuit_h)

    # 2. Bottom Half: Split Left (Tools) and Right (Zone)
    col_width = W // 2
    
    # --- Stânga: Blocurile de cod ---
    block_width = int(col_width * 0.8)
    block_height = int(H * 0.08) # 8% din înălțimea ecranului
    
    start_x = (col_width - block_width) // 2
    start_y = half_height + 20
    
    blocks = []
    # Recreăm blocurile cu noile dimensiuni calculate
    for data in AVAILABLE_BLOCKS_DATA:
        b = DraggableBlock(start_x, start_y, block_width, block_height, data)
        blocks.append(b)
        start_y += block_height + 10 # Spațiu între blocuri

    # --- Dreapta: Zona Soluție ---
    zone_w = int(col_width * 0.9)
    zone_h = int(half_height * 0.65)
    
    zone_x = col_width + (col_width - zone_w) // 2
    zone_y = half_height + 20
    
    solution_rect = pygame.Rect(zone_x, zone_y, zone_w, zone_h)

    # --- BUTONUL DE COMPILARE ---
    btn_w = int(zone_w * 0.6) # Butonul e 60% din lățimea zonei
    btn_h = int(H * 0.08)     # Destul de înalt să fie apăsat ușor
    
    btn_x = zone_x + (zone_w - btn_w) // 2
    # Îl punem exact sub zona de soluție
    btn_y = zone_y + zone_h + 15
    
    print(f"DEBUG: Buton poziționat la X={btn_x}, Y={btn_y}, W={btn_w}, H={btn_h}")
    
    run_btn = RunButton(btn_x, btn_y, btn_w, btn_h, font_ui)

    # --- LOGICA JOCULUI ---
    current_state = STATE_WAITING
    init_time = pygame.time.get_ticks()
    game_start_time = 0
    rem_time = GAME_DURATION_SEC
    end_state_start_time = 0
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # --- EVENIMENTE ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Ieșire rapidă cu ESC (util pentru fullscreen)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if current_state == STATE_GAMEPLAY:
                # 1. Verificăm Butonul
                if run_btn.is_clicked(event):
                    print("Buton apăsat!")
                    in_zone = [b for b in blocks if solution_rect.collidepoint(b.rect.center)]
                    in_zone.sort(key=lambda b: b.rect.y)
                    
                    if validate_sequence(in_zone):
                        current_state = STATE_WIN
                    else:
                        current_state = STATE_FAIL

                # 2. Verificăm Drag & Drop
                # Procesăm inversa listei pentru a prinde blocurile de "deasupra"
                block_clicked = None
                for b in reversed(blocks):
                    # handle_event returnează True dacă s-a interacționat cu blocul
                    if b.handle_event(event):
                        block_clicked = b
                        break # Oprim propagarea la primul bloc găsit
                
                # Aducem blocul în față dacă a fost atins
                if block_clicked and event.type == pygame.MOUSEBUTTONDOWN:
                    blocks.remove(block_clicked)
                    blocks.append(block_clicked)

        # --- UPDATE STARE ---
        if current_state == STATE_WAITING:
            if current_time - init_time > DEMO_START_DELAY_MS:
                current_state = STATE_DEMO
                circuit.start_demo()

        elif current_state == STATE_DEMO:
            circuit.update(current_time)
            if not circuit.demo_active:
                current_state = STATE_GAMEPLAY
                game_start_time = current_time

        elif current_state == STATE_GAMEPLAY:
            elapsed = (current_time - game_start_time) // 1000
            rem_time = GAME_DURATION_SEC - elapsed 
            if rem_time <= 0:
                current_state = STATE_FAIL
        
        # --- DESENARE (Ordinea contează!) ---
        screen.fill(COLOR_BG)

        # 1. Separatoare
        pygame.draw.line(screen, COLOR_BG, (0, half_height), (W, half_height), 4)
        pygame.draw.line(screen, COLOR_BG, (col_width, half_height), (col_width, H), 4)
    
        # 2. Circuit
        circuit.draw(screen)
        
        # 3. Zona Soluție
        draw_solution_zone(screen, font_ui, solution_rect)
        
        # 4. Butonul (Îl desenăm înainte de blocuri sau după, dar sigur trebuie desenat)
        run_btn.draw(screen)
        
        # 5. Blocurile (Desenate ultimele ca să fie "peste" tot)
        for b in blocks:
            b.draw(screen)

        # 6. Overlay-uri (Mesaje)
        if current_state == STATE_WAITING:
            msg = font_big.render("Privește LED-ul!", True, COLOR_TEXT_BLACK)
            # Centrat în partea de sus
            screen.blit(msg, (W//2 - msg.get_width()//2, half_height//2 + 100))
            
        elif current_state == STATE_DEMO:
            msg = font_big.render("Memorează!", True, COLOR_BLOCK)
            screen.blit(msg, (W//2 - msg.get_width()//2, half_height//2 + 100))
            
        elif current_state == STATE_GAMEPLAY:
            draw_timer(screen, rem_time, font_big)
            
        elif current_state == STATE_WIN:
            s = pygame.Surface((W, H))
            s.set_alpha(200)
            s.fill(COLOR_SUCCESS)
            screen.blit(s, (0,0))
            msg = font_big.render("FELICITĂRI!", True, COLOR_TEXT_WHITE)
            screen.blit(msg, (W//2 - msg.get_width()//2, H//2))
            
        elif current_state == STATE_FAIL:
            s = pygame.Surface((W, H))
            s.set_alpha(200)
            s.fill(COLOR_FAIL)
            screen.blit(s, (0,0))
            msg = font_big.render("GREȘIT / TIMP EXPIRAT", True, COLOR_TEXT_WHITE)
            screen.blit(msg, (W//2 - msg.get_width()//2, H//2))
        
        if current_state in [STATE_WIN, STATE_FAIL]:
            # Pornim cronometrul dacă nu a fost pornit deja
            if end_state_start_time == 0:
                end_state_start_time = pygame.time.get_ticks()
            
            # Verificăm dacă au trecut 8 secunde (8000 ms)
            if current_time - end_state_start_time > 8000:
                print("Sistem: Închidere automată după 8 secunde.")
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()