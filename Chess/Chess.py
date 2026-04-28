import pygame
import random

# --- Инициализация ---
pygame.init()
WIDTH, HEIGHT = 640, 640
wind = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess & Checkers Ultimate')
clock = pygame.time.Clock()

COLORS = {
    'bg': (49, 46, 43),
    'board_light': (235, 236, 208),
    'board_dark': (119, 149, 86),
    'button': (129, 182, 76),
    'button_hover': (149, 202, 96),
    'highlight': (247, 247, 105, 160),
    'dot': (0, 0, 0, 40),
    'crown': (255, 215, 0),
    'win_overlay': (129, 182, 76, 180),
    'lose_overlay': (200, 50, 50, 180)
}

FONT_SM = pygame.font.SysFont('Segoe UI', 25, bold=True)
FONT_LG = pygame.font.SysFont('Segoe UI', 70, bold=True)

# --- Глобальные переменные ---
GAME_TYPE = "CHESS"
DIFFICULTY = "ЛЕГКО"
Board = []
PIECE_VALUES = {'P': 10, 'H': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900, 'C': 10, 'D': 50}

AttackDict = {
    'R': [[0,1],[0,-1],[1,0],[-1,0], 7],
    'B': [[1,1],[-1,-1],[1,-1],[-1,1], 7],
    'Q': [[1,1],[-1,-1],[1,-1],[-1,1],[0,1],[0,-1],[1,0],[-1,0], 7],
    'H': [[1,2],[2,1],[-1,-2],[-2,-1],[-1,2],[-2,1],[1,-2],[2,-1], 1],
    'K': [[1,1],[-1,-1],[1,-1],[-1,1],[0,1],[0,-1],[1,0],[-1,0], 1]
}

def init_board(mode):
    global Board
    if mode == "CHESS":
        Board = [
            ['R1', 'H1', 'B1', 'Q1', 'K1', 'B1', 'H1', 'R1'],
            ['p1', 'p1', 'p1', 'p1', 'p1', 'p1', 'p1', 'p1'],
            ['.']*8, ['.']*8, ['.']*8, ['.']*8,
            ['P0', 'P0', 'P0', 'P0', 'P0', 'P0', 'P0', 'P0'],
            ['R0', 'H0', 'B0', 'Q0', 'K0', 'B0', 'H0', 'R0']
        ]
    else:
        Board = [['.']*8 for _ in range(8)]
        for y in range(8):
            for x in range(8):
                if (x + y) % 2 != 0:
                    if y < 3: Board[y][x] = 'c1'
                    if y > 4: Board[y][x] = 'C0'

def get_checkers_jumps(x, y, color, current_board):
    jumps = []
    dirs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for dx, dy in dirs:
        nx, ny, mx, my = x + dx*2, y + dy*2, x + dx, y + dy
        if 0 <= nx <= 7 and 0 <= ny <= 7:
            target = current_board[my][mx]
            if target != '.' and target[1] != color and current_board[ny][nx] == '.':
                temp_board = [row[:] for row in current_board]
                temp_board[my][mx] = '.'
                temp_board[ny][nx] = temp_board[y][x]
                temp_board[y][x] = '.'
                sub = get_checkers_jumps(nx, ny, color, temp_board)
                if sub:
                    for s in sub: jumps.append([[nx, ny]] + s)
                else: jumps.append([[nx, ny]])
    return jumps

def get_variants(x, y):
    variants = []
    piece = Board[y][x]
    if piece == '.': return []
    p_type, p_color = piece[0], piece[1]
    
    if GAME_TYPE == "CHESS":
        if p_type.upper() == 'P':
            d = -1 if p_color == '0' else 1
            if 0 <= y+d <= 7 and Board[y+d][x] == '.':
                variants.append([x, y+d])
                if (p_color=='0' and y==6) or (p_color=='1' and y==1):
                    if Board[y+2*d][x] == '.': variants.append([x, y+2*d])
            for dx in [-1, 1]:
                if 0 <= x+dx <= 7 and 0 <= y+d <= 7:
                    target = Board[y+d][x+dx]
                    if target != '.' and target[1] != p_color: variants.append([x+dx, y+d])
        elif p_type.upper() in AttackDict:
            for move in AttackDict[p_type.upper()][0:-1]:
                for i in range(1, AttackDict[p_type.upper()][-1] + 1):
                    nx, ny = x + move[0]*i, y + move[1]*i
                    if 0 <= nx <= 7 and 0 <= ny <= 7:
                        if Board[ny][nx] == '.': variants.append([nx, ny])
                        elif Board[ny][nx][1] != p_color: variants.append([nx, ny]); break
                        else: break
                    else: break
    else:
        jumps = get_checkers_jumps(x, y, p_color, [row[:] for row in Board])
        if jumps: return jumps
        m_dirs = [(-1,-1),(1,-1)] if p_color=='0' else [(-1,1),(1,1)]
        if p_type.upper() == 'D' or p_type.upper() == 'C': m_dirs = [(-1,-1),(1,-1),(-1,1),(1,1)]
        for dx, dy in m_dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= 7 and 0 <= ny <= 7 and Board[ny][nx] == '.': variants.append([[nx, ny]])
    return variants

def make_move(start, chain):
    sx, sy = start
    curr_x, curr_y = sx, sy
    p_data = Board[sy][sx]
    for step in chain:
        ex, ey = step
        if abs(ex - curr_x) == 2: Board[(ey+curr_y)//2][(ex+curr_x)//2] = '.'
        Board[ey][ex] = p_data
        Board[curr_y][curr_x] = '.'
        curr_x, curr_y = ex, ey
    if curr_y == (0 if p_data[1]=='0' else 7):
        if GAME_TYPE == "CHESS" and p_data[0].upper() == 'P': Board[curr_y][curr_x] = 'Q' + p_data[1]
        if GAME_TYPE == "CHECKERS": Board[curr_y][curr_x] = 'D' + p_data[1]

def check_end_game():
    pieces_0, pieces_1 = 0, 0
    has_k0, has_k1 = False, False
    for row in Board:
        for p in row:
            if p != '.':
                if p[1] == '0': 
                    pieces_0 += 1
                    if p[0] == 'K': has_k0 = True
                else: 
                    pieces_1 += 1
                    if p[0] == 'K': has_k1 = True
    
    if GAME_TYPE == "CHESS":
        if not has_k1: return "win"
        if not has_k0: return "lose"
    else:
        if pieces_1 == 0: return "win"
        if pieces_0 == 0: return "lose"
    return None

def show_end_screen(result):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    color = COLORS['win_overlay'] if result == "win" else COLORS['lose_overlay']
    text = "ПОБЕДА!" if result == "win" else "ПОРАЖЕНИЕ"
    
    for alpha in range(0, color[3], 4):
        overlay.fill((color[0], color[1], color[2], alpha))
        draw_all(None, [])
        wind.blit(overlay, (0, 0))
        t_surf = FONT_LG.render(text, True, (255, 255, 255))
        wind.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, HEIGHT//2 - t_surf.get_height()//2))
        pygame.display.flip()
        pygame.time.delay(20)
    pygame.time.delay(2000)

def bot_move():
    all_moves = []
    for y in range(8):
        for x in range(8):
            if Board[y][x] != '.' and Board[y][x][1] == '1':
                v_list = get_variants(x, y)
                for v in v_list:
                    target = v[-1] if isinstance(v[0], list) else v
                    score = 0
                    if Board[target[1]][target[0]] != '.':
                        score = PIECE_VALUES.get(Board[target[1]][target[0]][0].upper(), 0)
                    all_moves.append({'start': [x, y], 'chain': v if isinstance(v[0], list) else [v], 'score': score})
    if all_moves:
        if DIFFICULTY == "СЛОЖНО":
            all_moves.sort(key=lambda m: m['score'], reverse=True)
            max_s = all_moves[0]['score']
            best = [m for m in all_moves if m['score'] == max_s]
            move = random.choice(best)
        else: move = random.choice(all_moves)
        make_move(move['start'], move['chain'])

def draw_all(selected, vars):
    wind.fill(COLORS['bg'])
    for y in range(8):
        for x in range(8):
            c = COLORS['board_light'] if (x+y)%2==0 else COLORS['board_dark']
            pygame.draw.rect(wind, c, (x*80, y*80, 80, 80))
            if selected == [x, y]: pygame.draw.rect(wind, COLORS['highlight'], (x*80, y*80, 80, 80))
            p = Board[y][x]
            if p != '.':
                if GAME_TYPE == "CHECKERS":
                    p_c = (240,240,240) if p[1]=='0' else (30,30,30)
                    pygame.draw.circle(wind, p_c, (x*80+40, y*80+40), 30)
                    if p[0].upper() == 'D': pygame.draw.circle(wind, COLORS['crown'], (x*80+40, y*80+40), 12)
                else:
                    try:
                        img = pygame.image.load(f"{p}.png")
                        wind.blit(pygame.transform.smoothscale(img, (70, 70)), (x*80+5, y*80+5))
                    except:
                        txt_c = (255,255,255) if p[1]=='0' else (20,20,20)
                        txt = FONT_SM.render(p[0].upper(), True, txt_c)
                        wind.blit(txt, (x*80+32, y*80+25))
    for v in vars:
        target = v[-1] if isinstance(v[0], list) else v
        s = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(s, COLORS['dot'], (40, 40), 12)
        wind.blit(s, (target[0]*80, target[1]*80))

def main():
    global GAME_TYPE, DIFFICULTY
    while True: # Цикл для возврата в меню после игры
        menu = True
        while menu:
            wind.fill(COLORS['bg'])
            m_pos = pygame.mouse.get_pos()
            btns = {'chess': pygame.Rect(220, 180, 200, 50), 'check': pygame.Rect(220, 250, 200, 50),
                    'diff': pygame.Rect(220, 320, 200, 50), 'start': pygame.Rect(220, 420, 200, 60)}
            for k, b in btns.items():
                c = COLORS['button'] if (k=='chess' and GAME_TYPE=='CHESS') or (k=='check' and GAME_TYPE=='CHECKERS') or k=='start' else (80,80,80)
                if b.collidepoint(m_pos): c = COLORS['button_hover']
                pygame.draw.rect(wind, c, b, border_radius=10)
            wind.blit(FONT_SM.render("ШАХМАТЫ", True, (255,255,255)), (265, 190))
            wind.blit(FONT_SM.render("ШАШКИ", True, (255,255,255)), (275, 260))
            wind.blit(FONT_SM.render(f"БОТ: {DIFFICULTY}", True, (255,255,255)), (245, 330))
            wind.blit(FONT_SM.render("ИГРАТЬ", True, (255,255,255)), (275, 435))
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); return
                if e.type == pygame.MOUSEBUTTONDOWN:
                    if btns['chess'].collidepoint(e.pos): GAME_TYPE = "CHESS"
                    if btns['check'].collidepoint(e.pos): GAME_TYPE = "CHECKERS"
                    if btns['diff'].collidepoint(e.pos): DIFFICULTY = "СЛОЖНО" if DIFFICULTY == "ЛЕГКО" else "ЛЕГКО"
                    if btns['start'].collidepoint(e.pos): menu = False
            pygame.display.flip()

        init_board(GAME_TYPE)
        selected, vars, turn, game_active = None, [], '0', True
        while game_active:
            draw_all(selected, vars)
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); return
                if e.type == pygame.MOUSEBUTTONDOWN and turn == '0':
                    x, y = e.pos[0]//80, e.pos[1]//80
                    target_chain = next((v for v in vars if (v[-1] if isinstance(v[0], list) else v) == [x, y]), None)
                    if target_chain:
                        make_move(selected, target_chain if isinstance(target_chain[0], list) else [target_chain])
                        selected, vars = None, []
                        res = check_end_game()
                        if res: show_end_screen(res); game_active = False; break
                        draw_all(None, []); pygame.display.flip()
                        pygame.time.delay(500); bot_move()
                        res = check_end_game()
                        if res: show_end_screen(res); game_active = False; break
                    elif 0 <= x <= 7 and 0 <= y <= 7 and Board[y][x] != '.' and Board[y][x][1] == '0':
                        selected, vars = [x, y], get_variants(x, y)
                    else: selected, vars = None, []
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__": main()