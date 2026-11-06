import pygame
import sys
import random
import math

try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.init()
except:
    pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("MAZE ESCAPE - Hasan & Akter's Eternal Love")

# Color Palette
PLAYER_COLOR = (46, 204, 113)
PLAYER_EYE = (255, 255, 255)
COIN_COLOR = (241, 196, 15)
KEY_COLOR = (52, 152, 219)
DOOR_COLOR = (155, 89, 182)
ENEMY_COLOR = (231, 76, 60)
BOSS_COLOR = (120, 0, 40)
SPIKE_COLOR = (149, 165, 166)
POTION_COLOR = (41, 128, 185)
TEXT_COLOR = (240, 244, 248)
UI_BG = (28, 37, 56)
BTN_COLOR = (41, 128, 185)
BTN_HOVER = (52, 152, 219)

clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("Arial", 20, bold=True)
title_font = pygame.font.SysFont("Arial", 32, bold=True)
big_font = pygame.font.SysFont("Arial", 44, bold=True)

GRID_SIZE = 48


def generate_sound(freq, duration=0.1, volume=0.25):
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(127 * volume * math.sin(2 * math.pi * freq * t)) + 128
            buf.append(val);
            buf.append(val)
        return pygame.mixer.Sound(buffer=bytes(buf))
    except:
        return None


coin_sound = generate_sound(950, 0.08)
key_sound = generate_sound(1300, 0.15)
hit_sound = generate_sound(150, 0.2)
win_sound = generate_sound(600, 0.3)


def generate_story_levels():
    level_blueprints = [
        {"name": "1. Whispering Forest", "size": 24, "coins": 14, "enemies": 2, "bg": (15, 35, 20),
         "wall": (40, 100, 50)},
        {"name": "2. Shadowy Pathway", "size": 26, "coins": 16, "enemies": 3, "bg": (20, 20, 35), "wall": (60, 60, 90)},
        {"name": "3. Echoing Cavern", "size": 28, "coins": 18, "enemies": 3, "bg": (30, 40, 55), "wall": (80, 90, 110)},
        {"name": "4. Ancient Ruins", "size": 30, "coins": 20, "enemies": 4, "bg": (65, 25, 25), "wall": (140, 50, 50)},
        {"name": "5. Dungeon of Despair", "size": 32, "coins": 22, "enemies": 4, "bg": (20, 25, 55),
         "wall": (45, 65, 120)},
        {"name": "6. Foggy Marshland", "size": 32, "coins": 24, "enemies": 4, "bg": (15, 45, 40),
         "wall": (35, 100, 85)},
        {"name": "7. Starless Night", "size": 34, "coins": 26, "enemies": 5, "bg": (15, 15, 45), "wall": (55, 55, 140)},
        {"name": "8. Temple of Trials", "size": 34, "coins": 28, "enemies": 5, "bg": (50, 35, 15),
         "wall": (120, 90, 40)},
        {"name": "9. Cursed Mine", "size": 36, "coins": 30, "enemies": 6, "bg": (40, 25, 15), "wall": (95, 65, 35)},
        {"name": "10. Burning Sands", "size": 36, "coins": 32, "enemies": 6, "bg": (65, 45, 15),
         "wall": (150, 110, 35)},
        {"name": "11. Jungle Thorns", "size": 38, "coins": 34, "enemies": 7, "bg": (10, 35, 15), "wall": (25, 90, 35)},
        {"name": "12. Clockwork Trap", "size": 38, "coins": 36, "enemies": 7, "bg": (40, 40, 40), "wall": (90, 90, 90)},
        {"name": "13. Frostbite Keep", "size": 40, "coins": 38, "enemies": 8, "bg": (15, 45, 65),
         "wall": (60, 130, 180)},
        {"name": "14. Sanctum of Doom", "size": 40, "coins": 40, "enemies": 8, "bg": (45, 15, 45),
         "wall": (120, 50, 120)},
        {"name": "15. The Final Citadel", "size": 44, "coins": 48, "enemies": 10, "bg": (15, 15, 15),
         "wall": (170, 40, 40)}
    ]

    levels = []
    for idx, bp in enumerate(level_blueprints):
        size = bp["size"]
        m = [[1 if (r == 0 or r == size - 1 or c == 0 or c == size - 1) else 0 for c in range(size)] for r in
             range(size)]

        random.seed((idx + 1) * 888)
        for r in range(2, size - 2, 2):
            for c in range(2, size - 2, 2):
                if random.random() < 0.33: m[r][c] = 1

        # Clear space around player start
        m[1][1] = 0;
        m[1][2] = 0;
        m[2][1] = 0

        # Guaranteed Key position and clear surroundings
        m[size - 2][1] = 'K'
        m[size - 3][1] = 0;
        m[size - 2][2] = 0

        # Guaranteed Exit Door position with guaranteed open surroundings
        door_positions = [
            (size - 2, size - 2), (size - 2, size // 2), (size // 2, size - 2),
            (size - 3, size - 3), (size - 2, 2), (2, size - 2)
        ]
        dx, dy = door_positions[idx % len(door_positions)]
        m[dy][dx] = 'D'
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)]:
            nr, nc = dy + dr, dx + dc
            if 0 < nr < size - 1 and 0 < nc < size - 1:
                m[nr][nc] = 0

        # Coins placement
        placed = 0
        while placed < bp["coins"]:
            rx, ry = random.randint(1, size - 2), random.randint(1, size - 2)
            if m[ry][rx] == 0 and not (rx == 1 and ry == 1):
                m[ry][rx] = 'C'
                placed += 1

        # Spikes
        for _ in range(5 + idx):
            sx, sy = random.randint(2, size - 3), random.randint(2, size - 3)
            if m[sy][sx] == 0 and not (sx == 1 and sy == 1): m[sy][sx] = 'S'

        # Speed Potion
        if idx >= 1:
            px, py = random.randint(2, size - 3), random.randint(2, size - 3)
            if m[py][px] == 0 and not (px == 1 and py == 1): m[py][px] = 'P'

        # Active Enemies & Scaling Boss
        level_enemies = []
        total_enemies = bp["enemies"] + (idx // 2)
        for e in range(total_enemies):
            ex, ey = random.randint(3, size - 4), random.randint(3, size - 4)
            if m[ey][ex] == 0:
                is_boss = (e == 0)
                boss_speed_boost = (idx * 0.007) if is_boss else (idx * 0.002)
                level_enemies.append({
                    "x": float(ex), "y": float(ey),
                    "speed": (0.04 + boss_speed_boost),
                    "is_boss": is_boss
                })

        levels.append({
            "name": bp["name"],
            "map": m,
            "size": size,
            "coins_needed": bp["coins"],
            "enemies": level_enemies,
            "bg_color": bp["bg"],
            "wall_color": bp["wall"],
            "time_limit": 110 + (idx * 6)
        })
    return levels


levels_data = generate_story_levels()

game_state = "LOADING"
loading_progress = 0
difficulty_multiplier = 0.8  # Default Medium
username = "Hasan"
score = 0
total_coins_bank = 0
high_score = 0
current_level_idx = 0
coins_collected = 0
coins_target = 0
has_key = False
player_health = 10
max_health = 10
hit_anim_timer = 0
speed_boost_timer = 0
level_timer = 0
anim_timer = 0

player_x, player_y = 0, 0
player_size = 30
base_speed = 4.5
maze_map, enemies = [], []
map_width, map_height = 0, 0
current_bg = (15, 35, 20)
current_wall = (40, 100, 50)
current_level_name = "1. Whispering Forest"

skins = [
    {"name": "Hasan (Hero)", "type": "human", "color": (46, 204, 113), "price": 0, "unlocked": True},
    {"name": "Alien X", "type": "alien", "color": (155, 89, 182), "price": 0, "unlocked": True},
    {"name": "Cyber Cat", "type": "cat", "color": (52, 152, 219), "price": 0, "unlocked": True},
    {"name": "Wild Horse", "type": "horse", "color": (230, 126, 34), "price": 150, "unlocked": False},
    {"name": "Mega Elephant", "type": "elephant", "color": (149, 165, 166), "price": 250, "unlocked": False}
]
selected_skin_idx = 0
control_mode = "On-Screen Buttons"

moving_up = False
moving_down = False
moving_left = False
moving_right = False

btn_left = pygame.Rect(0, 0, 0, 0)
btn_right = pygame.Rect(0, 0, 0, 0)
btn_up = pygame.Rect(0, 0, 0, 0)
btn_down = pygame.Rect(0, 0, 0, 0)
pause_btn_rect = pygame.Rect(0, 0, 0, 0)
menu_btn_rect = pygame.Rect(0, 0, 0, 0)
start_btn_rect = pygame.Rect(0, 0, 0, 0)
store_btn_rect = pygame.Rect(0, 0, 0, 0)
settings_btn_rect = pygame.Rect(0, 0, 0, 0)
quit_btn_rect = pygame.Rect(0, 0, 0, 0)
resume_btn_rect = pygame.Rect(0, 0, 0, 0)
restart_btn_rect = pygame.Rect(0, 0, 0, 0)
menu_btn_rect_end = pygame.Rect(0, 0, 0, 0)
next_lvl_btn = pygame.Rect(0, 0, 0, 0)
play_again_btn = pygame.Rect(0, 0, 0, 0)
story_next_btn = pygame.Rect(0, 0, 0, 0)
diff_easy_btn = pygame.Rect(0, 0, 0, 0)
diff_med_btn = pygame.Rect(0, 0, 0, 0)
diff_hard_btn = pygame.Rect(0, 0, 0, 0)


def load_level(idx):
    global current_level_idx, maze_map, player_x, player_y, has_key, coins_collected, coins_target, enemies, map_width, map_height, level_timer, speed_boost_timer, current_bg, current_wall, current_level_name
    current_level_idx = idx
    ld = levels_data[idx]
    maze_map = [row[:] for row in ld["map"]]
    player_x = 1 * GRID_SIZE + 8
    player_y = 1 * GRID_SIZE + 8
    has_key = False
    coins_collected = 0
    coins_target = ld["coins_needed"]
    speed_boost_timer = 0
    level_timer = ld["time_limit"]
    map_width = ld["size"] * GRID_SIZE
    map_height = ld["size"] * GRID_SIZE
    current_bg = ld["bg_color"]
    current_wall = ld["wall_color"]
    current_level_name = ld["name"]
    enemies = [e.copy() for e in ld["enemies"]]


def draw_button(text, x, y, w, h):
    rect = pygame.Rect(x, y, w, h)
    mouse_pos = pygame.mouse.get_pos()
    color = BTN_HOVER if rect.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=12)
    txt = font.render(text, True, TEXT_COLOR)
    screen.blit(txt, (x + (w - txt.get_width()) // 2, y + (h - txt.get_height()) // 2))
    return rect


def draw_player(px, py, skin_type, color):
    if skin_type == "human":
        pygame.draw.rect(screen, color, (px, py, player_size, player_size), border_radius=8)
        pygame.draw.circle(screen, PLAYER_EYE, (px + 9, py + 9), 4)
        pygame.draw.circle(screen, PLAYER_EYE, (px + 21, py + 9), 4)
    elif skin_type == "alien":
        pygame.draw.ellipse(screen, color, (px + 2, py, player_size - 4, player_size + 4))
        pygame.draw.circle(screen, (255, 255, 0), (px + 10, py + 12), 5)
        pygame.draw.circle(screen, (255, 255, 0), (px + 20, py + 12), 5)
    elif skin_type == "cat":
        pygame.draw.rect(screen, color, (px + 2, py + 6, player_size - 4, player_size - 6), border_radius=6)
        pygame.draw.polygon(screen, color, [(px + 4, py + 6), (px + 2, py - 2), (px + 10, py + 4)])
        pygame.draw.polygon(screen, color, [(px + 26, py + 6), (px + 28, py - 2), (px + 20, py + 4)])
    elif skin_type == "horse":
        pygame.draw.rect(screen, color, (px, py + 4, player_size, player_size - 4), border_radius=10)
        pygame.draw.rect(screen, color, (px + 20, py - 4, 10, 12))
    elif skin_type == "elephant":
        pygame.draw.rect(screen, color, (px - 2, py, player_size + 4, player_size), border_radius=12)
        pygame.draw.rect(screen, color, (px + 10, py + 15, 8, 16))


def draw_game():
    global btn_up, btn_down, btn_left, btn_right, pause_btn_rect, menu_btn_rect, anim_timer
    screen.fill(current_bg)
    cam_x = player_x - SCREEN_WIDTH // 2
    cam_y = player_y - (SCREEN_HEIGHT - 100) // 2

    anim_timer += 0.1
    pulse = int(4 * math.sin(anim_timer))

    for r_idx, row in enumerate(maze_map):
        for c_idx, cell in enumerate(row):
            x = c_idx * GRID_SIZE - cam_x
            y = r_idx * GRID_SIZE - cam_y
            if -GRID_SIZE <= x <= SCREEN_WIDTH and -GRID_SIZE <= y <= SCREEN_HEIGHT - 100:
                if cell == 1:
                    # Enhanced 3D Map Aesthetics
                    pygame.draw.rect(screen, current_wall, (x, y, GRID_SIZE, GRID_SIZE), border_radius=6)
                    h_col = (min(255, current_wall[0] + 40), min(255, current_wall[1] + 40),
                             min(255, current_wall[2] + 40))
                    pygame.draw.rect(screen, h_col, (x + 3, y + 3, GRID_SIZE - 6, GRID_SIZE - 6), 2, border_radius=4)
                    pygame.draw.rect(screen, (255, 255, 255), (x, y, GRID_SIZE, GRID_SIZE), 1, border_radius=6)
                elif cell == 'C':
                    pygame.draw.circle(screen, COIN_COLOR, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 9 + (pulse // 2))
                elif cell == 'K':
                    pygame.draw.rect(screen, KEY_COLOR, (x + 12 + pulse // 2, y + 12, 22, 22), border_radius=5)
                elif cell == 'S':
                    pygame.draw.polygon(screen, SPIKE_COLOR, [(x + 8, y + 38), (x + 24, y + 10), (x + 40, y + 38)])
                elif cell == 'P':
                    pygame.draw.circle(screen, POTION_COLOR, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 12)
                elif cell == 'D':
                    door_rect = pygame.Rect(x + 4, y + 4, GRID_SIZE - 8, GRID_SIZE - 4)
                    pygame.draw.rect(screen, DOOR_COLOR, door_rect, border_radius=8)
                    pygame.draw.rect(screen, (255, 255, 255), door_rect, 3, border_radius=8)
                    pygame.draw.circle(screen, COIN_COLOR, (x + GRID_SIZE - 12, y + GRID_SIZE // 2), 5)

    # Active Boss & Enemy Rendering
    for enemy in enemies:
        ex = enemy["x"] * GRID_SIZE - cam_x
        ey = enemy["y"] * GRID_SIZE - cam_y
        if -GRID_SIZE <= ex <= SCREEN_WIDTH and -GRID_SIZE <= ey <= SCREEN_HEIGHT:
            if enemy["is_boss"]:
                scale_growth = int(current_level_idx * 2.0)
                boss_size = 60 + scale_growth
                pygame.draw.rect(screen, BOSS_COLOR, (ex - 10, ey - 10, boss_size, boss_size), border_radius=14)
                pygame.draw.rect(screen, (255, 40, 40), (ex - 10, ey - 10, boss_size, boss_size), 3, border_radius=14)

                # Horns
                pygame.draw.polygon(screen, (180, 40, 40), [(ex - 10, ey - 10), (ex - 2, ey - 24), (ex + 10, ey - 10)])
                pygame.draw.polygon(screen, (180, 40, 40),
                                    [(ex + boss_size - 10, ey - 10), (ex + boss_size + 2, ey - 24),
                                     (ex + boss_size - 10, ey - 10)])

                # Glowing Eyes
                pygame.draw.circle(screen, (255, 0, 0), (ex + 14, ey + 18), 9)
                pygame.draw.circle(screen, (255, 0, 0), (ex + boss_size - 16, ey + 18), 9)
                pygame.draw.circle(screen, (255, 255, 255), (ex + 14, ey + 18), 3)
                pygame.draw.circle(screen, (255, 255, 255), (ex + boss_size - 16, ey + 18), 3)

                # Teeth
                for d_i in range(3):
                    pygame.draw.polygon(screen, (255, 255, 255), [
                        (ex + 14 + (d_i * 14), ey + boss_size - 20),
                        (ex + 20 + (d_i * 14), ey + boss_size - 8),
                        (ex + 26 + (d_i * 14), ey + boss_size - 20)
                    ])
            else:
                pygame.draw.rect(screen, ENEMY_COLOR, (ex + 4, ey + 4, 38, 38), border_radius=10)
                pygame.draw.circle(screen, (255, 255, 0), (ex + 14, ey + 16), 5)
                pygame.draw.circle(screen, (255, 255, 0), (ex + 30, ey + 16), 5)
                pygame.draw.circle(screen, (0, 0, 0), (ex + 14, ey + 16), 2)
                pygame.draw.circle(screen, (0, 0, 0), (ex + 30, ey + 16), 2)

    px = player_x - cam_x
    py = player_y - cam_y
    p_color = skins[selected_skin_idx]["color"]
    if hit_anim_timer > 0 and (hit_anim_timer // 4) % 2 == 0:
        p_color = (255, 255, 255)

    draw_player(px, py, skins[selected_skin_idx]["type"], p_color)

    # Top UI Panel
    pygame.draw.rect(screen, UI_BG, (0, 0, SCREEN_WIDTH, 60))
    pygame.draw.line(screen, (60, 75, 100), (0, 60), (SCREEN_WIDTH, 60), 2)

    hearts_str = "❤️ " * player_health + "🖤 " * (max_health - player_health)
    health_txt = font.render(f"HP: {hearts_str}", True, (231, 76, 60))
    user_txt = font.render(f"Hero: {username}", True, (52, 152, 219))
    coin_txt = font.render(f"Coins: {coins_collected}/{coins_target} (Bank: {total_coins_bank})", True, COIN_COLOR)
    lvl_txt = font.render(current_level_name, True, TEXT_COLOR)
    timer_txt = font.render(f"Time: {int(level_timer)}s", True, (255, 200, 100))

    screen.blit(health_txt, (20, 18))
    screen.blit(user_txt, (320, 18))
    screen.blit(coin_txt, (480, 18))
    screen.blit(lvl_txt, (750, 18))
    screen.blit(timer_txt, (1120, 18))

    if control_mode == "On-Screen Buttons":
        pygame.draw.rect(screen, UI_BG, (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        pygame.draw.line(screen, (60, 75, 100), (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 2)

        btn_left = draw_button("Left", 30, SCREEN_HEIGHT - 82, 85, 65)
        btn_right = draw_button("Right", 215, SCREEN_HEIGHT - 82, 85, 65)
        btn_up = draw_button("Up", 122, SCREEN_HEIGHT - 82, 85, 65)
        btn_down = draw_button("Down", 122, SCREEN_HEIGHT - 14, 85, 34)

    pause_btn_rect = draw_button("Pause", SCREEN_WIDTH - 220, SCREEN_HEIGHT - 72, 90, 50)
    menu_btn_rect = draw_button("Menu", SCREEN_WIDTH - 115, SCREEN_HEIGHT - 72, 95, 50)


def check_wall_collision(nx, ny):
    p_rect = pygame.Rect(nx, ny, player_size, player_size)
    for r_idx, row in enumerate(maze_map):
        for c_idx, cell in enumerate(row):
            if cell == 1:
                w_rect = pygame.Rect(c_idx * GRID_SIZE, r_idx * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if p_rect.colliderect(w_rect): return True
    return False


def update_game():
    global player_x, player_y, score, total_coins_bank, coins_collected, has_key, speed_boost_timer, game_state, current_level_idx, player_health, hit_anim_timer, level_timer, high_score

    if hit_anim_timer > 0:
        hit_anim_timer -= 1

    level_timer -= 1 / 60.0
    if level_timer <= 0:
        game_state = "GAME_OVER"
        return

    if speed_boost_timer > 0: speed_boost_timer -= 1
    current_speed = base_speed * 1.5 if speed_boost_timer > 0 else base_speed

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0

    if control_mode == "Keyboard Only":
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += current_speed
    else:
        if keys[pygame.K_LEFT] or keys[pygame.K_a] or moving_left: dx -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] or moving_right: dx += current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w] or moving_up: dy -= current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s] or moving_down: dy += current_speed

    if dx != 0 and not check_wall_collision(player_x + dx, player_y): player_x += dx
    if dy != 0 and not check_wall_collision(player_x, player_y + dy): player_y += dy

    p_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for r_idx, row in enumerate(maze_map):
        for c_idx, cell in enumerate(row):
            c_rect = pygame.Rect(c_idx * GRID_SIZE, r_idx * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if p_rect.colliderect(c_rect):
                if cell == 'C':
                    coins_collected += 1
                    score += 20
                    total_coins_bank += 20
                    if coin_sound: coin_sound.play()
                    maze_map[r_idx][c_idx] = 0
                elif cell == 'K':
                    has_key = True
                    if key_sound: key_sound.play()
                    maze_map[r_idx][c_idx] = 0
                elif cell == 'P':
                    speed_boost_timer = 300
                    maze_map[r_idx][c_idx] = 0
                elif cell == 'S':
                    if hit_anim_timer == 0:
                        player_health -= 1
                        hit_anim_timer = 40
                        if hit_sound: hit_sound.play()
                        maze_map[r_idx][c_idx] = 0
                        if player_health <= 0: game_state = "GAME_OVER"
                elif cell == 'D':
                    if coins_collected >= coins_target and has_key:
                        if win_sound: win_sound.play()
                        game_state = "LEVEL_COMPLETE"

    # Difficulty-based Enemy tracking speed
    for enemy in enemies:
        ex = enemy["x"] * GRID_SIZE
        ey = enemy["y"] * GRID_SIZE
        angle = math.atan2(player_y - ey, player_x - ex)
        speed = enemy["speed"] * difficulty_multiplier * 1.2
        nx = enemy["x"] + math.cos(angle) * speed
        ny = enemy["y"] + math.sin(angle) * speed

        ld = levels_data[current_level_idx]
        e_gx, e_gy = int(nx + 0.5), int(enemy["y"] + 0.5)
        if 0 <= e_gx < ld["size"] and 0 <= int(enemy["y"]) < ld["size"] and maze_map[int(enemy["y"])][e_gx] != 1:
            enemy["x"] = nx
        if 0 <= int(enemy["x"]) < ld["size"] and 0 <= int(ny + 0.5) < ld["size"] and maze_map[int(ny + 0.5)][
            int(enemy["x"])] != 1:
            enemy["y"] = ny

        hit_box_size = (60 + int(current_level_idx * 2.0)) if enemy["is_boss"] else 38
        e_rect = pygame.Rect(enemy["x"] * GRID_SIZE, enemy["y"] * GRID_SIZE, hit_box_size, hit_box_size)
        if p_rect.colliderect(e_rect) and hit_anim_timer == 0:
            player_health -= 1
            hit_anim_timer = 40
            if hit_sound: hit_sound.play()
            player_x = 1 * GRID_SIZE + 8
            player_y = 1 * GRID_SIZE + 8
            if player_health <= 0: game_state = "GAME_OVER"


# Main Game Loop
running = True
while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "STORY_INTRO":
                if story_next_btn.collidepoint(mouse_pos):
                    game_state = "MENU"
            elif game_state == "MENU":
                if start_btn_rect.collidepoint(mouse_pos):
                    game_state = "DIFFICULTY_SELECT"  # Go to difficulty selection screen
                elif store_btn_rect.collidepoint(mouse_pos):
                    game_state = "STORE"
                elif settings_btn_rect.collidepoint(mouse_pos):
                    game_state = "SETTINGS"
                elif quit_btn_rect.collidepoint(mouse_pos):
                    running = False
            elif game_state == "DIFFICULTY_SELECT":
                if diff_easy_btn.collidepoint(mouse_pos):
                    difficulty_multiplier = 0.5  # Easy
                    score, player_health = 0, max_health
                    load_level(0)
                    game_state = "PLAYING"
                elif diff_med_btn.collidepoint(mouse_pos):
                    difficulty_multiplier = 0.8  # Medium
                    score, player_health = 0, max_health
                    load_level(0)
                    game_state = "PLAYING"
                elif diff_hard_btn.collidepoint(mouse_pos):
                    difficulty_multiplier = 1.25  # Hard
                    score, player_health = 0, max_health
                    load_level(0)
                    game_state = "PLAYING"
            elif game_state == "STORE":
                for idx, skin in enumerate(skins):
                    btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, 180 + (idx * 75), 320, 60)
                    if btn_rect.collidepoint(mouse_pos):
                        if skin["unlocked"]:
                            selected_skin_idx = idx
                        elif total_coins_bank >= skin["price"]:
                            total_coins_bank -= skin["price"]
                            skin["unlocked"] = True
                            selected_skin_idx = idx
                back_store_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, 580, 200, 50)
                if back_store_btn.collidepoint(mouse_pos):
                    game_state = "MENU"
            elif game_state == "SETTINGS":
                ctrl_btn = pygame.Rect(SCREEN_WIDTH // 2 - 150, 260, 300, 60)
                if ctrl_btn.collidepoint(mouse_pos):
                    if control_mode == "On-Screen Buttons":
                        control_mode = "Keyboard Only"
                    else:
                        control_mode = "On-Screen Buttons"
                back_set_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)
                if back_set_btn.collidepoint(mouse_pos):
                    game_state = "MENU"
            elif game_state == "PLAYING":
                if pause_btn_rect.collidepoint(mouse_pos):
                    game_state = "PAUSED"
                elif menu_btn_rect.collidepoint(mouse_pos):
                    game_state = "MENU"
            elif game_state == "PAUSED":
                if resume_btn_rect.collidepoint(mouse_pos):
                    game_state = "PLAYING"
                elif menu_btn_rect.collidepoint(mouse_pos):
                    game_state = "MENU"
            elif game_state == "LEVEL_COMPLETE":
                if next_lvl_btn.collidepoint(mouse_pos):
                    if current_level_idx + 1 < len(levels_data):
                        load_level(current_level_idx + 1)
                        game_state = "PLAYING"
                    else:
                        if score > high_score: high_score = score
                        game_state = "VICTORY_ANIMATION"
                elif play_again_btn.collidepoint(mouse_pos):
                    load_level(current_level_idx)
                    game_state = "PLAYING"
            elif game_state == "GAME_OVER":
                if restart_btn_rect.collidepoint(mouse_pos):
                    player_health = max_health
                    load_level(0)
                    game_state = "PLAYING"
                elif menu_btn_rect_end.collidepoint(mouse_pos):
                    game_state = "MENU"
            elif game_state == "VICTORY_ANIMATION":
                if restart_btn_rect.collidepoint(mouse_pos):
                    score, player_health = 0, max_health
                    load_level(0)
                    game_state = "STORY_INTRO"
                elif menu_btn_rect_end.collidepoint(mouse_pos):
                    game_state = "MENU"

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING":
                    game_state = "PAUSED"
                elif game_state == "PAUSED":
                    game_state = "PLAYING"

    if game_state == "PLAYING":
        moving_left = btn_left.collidepoint(mouse_pos) and mouse_buttons[0]
        moving_right = btn_right.collidepoint(mouse_pos) and mouse_buttons[0]
        moving_up = btn_up.collidepoint(mouse_pos) and mouse_buttons[0]
        moving_down = btn_down.collidepoint(mouse_pos) and mouse_buttons[0]

    # Screen Render States
    if game_state == "LOADING":
        screen.fill((10, 15, 25))
        loading_progress += 0.6  # Slower and smoother loading speed

        # HA Logo Animation
        logo_font = pygame.font.SysFont("Arial", 72, bold=True)
        logo_surf = logo_font.render("HA", True, (241, 196, 15))
        screen.blit(logo_surf, (SCREEN_WIDTH // 2 - logo_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 90))

        sub_font = pygame.font.SysFont("Arial", 22, bold=True)
        sub_surf = sub_font.render("Hasan & Akter Studio", True, (150, 160, 180))
        screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 10))

        # Loading Bar
        bar_w, bar_h = 420, 22
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y = SCREEN_HEIGHT // 2 + 60
        pygame.draw.rect(screen, (40, 50, 70), (bar_x, bar_y, bar_w, bar_h), border_radius=11)
        filled_w = int((loading_progress / 100.0) * bar_w)
        if filled_w > bar_w: filled_w = bar_w
        pygame.draw.rect(screen, (46, 204, 113), (bar_x, bar_y, filled_w, bar_h), border_radius=11)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=11)

        pct_surf = font.render(f"Loading Game Assets... {int(loading_progress)}%", True, TEXT_COLOR)
        screen.blit(pct_surf, (SCREEN_WIDTH // 2 - pct_surf.get_width() // 2, bar_y + 35))

        if loading_progress >= 100:
            game_state = "STORY_INTRO"

    elif game_state == "STORY_INTRO":
        screen.fill((20, 15, 35))

        header_rect = pygame.Rect(SCREEN_WIDTH // 2 - 500, 40, 1000, 75)
        pygame.draw.rect(screen, (45, 25, 70), header_rect, border_radius=16)
        pygame.draw.rect(screen, COIN_COLOR, header_rect, 3, border_radius=16)
        st_title = title_font.render("💖 THE ETERNAL TALE OF HASAN & AKTER 💖", True, COIN_COLOR)
        screen.blit(st_title, (SCREEN_WIDTH // 2 - st_title.get_width() // 2, header_rect.y + 20))

        story_box = pygame.Rect(SCREEN_WIDTH // 2 - 560, 135, 1120, 370)
        pygame.draw.rect(screen, (30, 40, 60), story_box, border_radius=16)
        pygame.draw.rect(screen, KEY_COLOR, story_box, 2, border_radius=16)

        unified_story_paragraph = [
            "Once upon a time in a peaceful valley, Hasan and Akter shared a pure and unbreakable love,",
            "dreaming of a wonderful future together. But their happiness was shattered when a dark evil",
            "force and a terrifying Boss monster kidnapped Akter, dragging her deep into the labyrinth",
            "of 15 dangerous mazes. Determined and fearless, Hasan vowed to fight through every deadly",
            "trap and vicious beast to save her. With every single maze you successfully conquer, Hasan",
            "and Akter will take a step closer to each other until they are united forever. Stand by",
            "Hasan, defeat the darkness, and witness true love conquer all!"
        ]

        for idx, line in enumerate(unified_story_paragraph):
            t_surf = font.render(line, True, TEXT_COLOR)
            screen.blit(t_surf, (story_box.x + 35, story_box.y + 25 + (idx * 46)))

        story_next_btn = draw_button("BEGIN EPIC JOURNEY ➔", SCREEN_WIDTH // 2 - 160, 545, 320, 60)

    elif game_state == "MENU":
        screen.fill((15, 35, 20))
        title = title_font.render(f"WELCOME, {username.upper()}!", True, COIN_COLOR)
        sub = font.render("Hasan & Akter Love Adventure", True, TEXT_COLOR)
        hs_txt = font.render(f"High Score: {high_score} | Bank Coins: {total_coins_bank}", True, KEY_COLOR)

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 160))
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 210))
        screen.blit(hs_txt, (SCREEN_WIDTH // 2 - hs_txt.get_width() // 2, 255))

        start_btn_rect = draw_button("START JOURNEY", SCREEN_WIDTH // 2 - 130, 330, 260, 50)
        store_btn_rect = draw_button("STORE (Characters)", SCREEN_WIDTH // 2 - 130, 395, 260, 50)
        settings_btn_rect = draw_button("SETTINGS", SCREEN_WIDTH // 2 - 130, 460, 260, 50)
        quit_btn_rect = draw_button("EXIT GAME", SCREEN_WIDTH // 2 - 130, 525, 260, 50)

    elif game_state == "DIFFICULTY_SELECT":
        screen.fill((20, 25, 40))
        diff_title = title_font.render("SELECT DIFFICULTY LEVEL", True, COIN_COLOR)
        diff_sub = font.render("Choose how challenging you want your journey to be!", True, TEXT_COLOR)

        screen.blit(diff_title, (SCREEN_WIDTH // 2 - diff_title.get_width() // 2, 160))
        screen.blit(diff_sub, (SCREEN_WIDTH // 2 - diff_sub.get_width() // 2, 220))

        diff_easy_btn = draw_button("🟢 EASY (Relaxed & Slow Enemies)", SCREEN_WIDTH // 2 - 200, 310, 400, 60)
        diff_med_btn = draw_button("🟡 MEDIUM (Balanced Challenge)", SCREEN_WIDTH // 2 - 200, 390, 400, 60)
        diff_hard_btn = draw_button("🔴 HARD (Intense & Fast Enemies)", SCREEN_WIDTH // 2 - 200, 470, 400, 60)

    elif game_state == "STORE":
        screen.fill((20, 25, 40))
        st_title = title_font.render("CHARACTER STORE (First 3 Free!)", True, COIN_COLOR)
        st_sub = font.render(f"Bank Coins: {total_coins_bank}", True, KEY_COLOR)
        screen.blit(st_title, (SCREEN_WIDTH // 2 - st_title.get_width() // 2, 70))
        screen.blit(st_sub, (SCREEN_WIDTH // 2 - st_sub.get_width() // 2, 120))

        for idx, skin in enumerate(skins):
            btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, 180 + (idx * 75), 320, 60)
            status = "Selected" if selected_skin_idx == idx else (
                "Unlocked (Free)" if skin["unlocked"] and skin["price"] == 0 else (
                    "Unlocked" if skin["unlocked"] else f"Buy: {skin['price']} Coins"))

            pygame.draw.rect(screen, (40, 55, 75), btn_rect, border_radius=10)
            txt = font.render(f"{skin['name']} - {status}", True, TEXT_COLOR)
            screen.blit(txt, (btn_rect.x + 20, btn_rect.y + 18))

        back_store_btn = draw_button("BACK TO MENU", SCREEN_WIDTH // 2 - 100, 580, 200, 50)

    elif game_state == "SETTINGS":
        screen.fill((20, 25, 40))
        set_title = title_font.render("GAME SETTINGS", True, COIN_COLOR)
        screen.blit(set_title, (SCREEN_WIDTH // 2 - set_title.get_width() // 2, 120))

        ctrl_btn = draw_button(f"Control: {control_mode}", SCREEN_WIDTH // 2 - 150, 260, 300, 60)
        back_set_btn = draw_button("BACK TO MENU", SCREEN_WIDTH // 2 - 100, 450, 200, 50)

    elif game_state == "PLAYING":
        update_game()
        draw_game()

    elif game_state == "PAUSED":
        draw_game()
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT));
        s.set_alpha(170);
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))
        ptxt = title_font.render("GAME PAUSED", True, TEXT_COLOR)
        screen.blit(ptxt, (SCREEN_WIDTH // 2 - ptxt.get_width() // 2, 260))
        resume_btn_rect = draw_button("RESUME", SCREEN_WIDTH // 2 - 120, 340, 240, 50)
        menu_btn_rect = draw_button("MAIN MENU", SCREEN_WIDTH // 2 - 120, 410, 240, 50)

    elif game_state == "LEVEL_COMPLETE":
        screen.fill((15, 25, 35))

        c_txt = big_font.render(f"🎉 CONGRATULATIONS! LEVEL {current_level_idx + 1} CLEARED! 💖", True, COIN_COLOR)
        sub_txt = font.render(f"Hasan and Akter took another step closer to each other... 💕", True, (255, 220, 150))

        screen.blit(c_txt, (SCREEN_WIDTH // 2 - c_txt.get_width() // 2, 70))
        screen.blit(sub_txt, (SCREEN_WIDTH // 2 - sub_txt.get_width() // 2, 135))

        # Character Closeness Progress Visual
        progress_ratio = (current_level_idx + 1) / 15.0
        hasan_x = int(320 + (progress_ratio * 250))
        akter_x = int(910 - (progress_ratio * 250))

        # Hasan (Boy)
        pygame.draw.rect(screen, PLAYER_COLOR, (hasan_x, 260, 50, 65), border_radius=10)
        pygame.draw.circle(screen, (245, 222, 179), (hasan_x + 25, 230), 18)
        h_label = font.render(username, True, (255, 255, 255))
        screen.blit(h_label, (hasan_x - 10, 335))

        # Akter (Girl)
        pygame.draw.rect(screen, (236, 72, 153), (akter_x, 260, 50, 65), border_radius=10)
        pygame.draw.circle(screen, (245, 222, 179), (akter_x + 25, 230), 18)
        a_label = font.render("Akter", True, (255, 255, 255))
        screen.blit(a_label, (akter_x + 5, 335))

        pygame.draw.line(screen, (100, 100, 120), (370, 295), (910, 295), 4)
        pygame.draw.circle(screen, (239, 68, 68), ((hasan_x + akter_x + 50) // 2, 295), 12)

        score_txt = font.render(f"Current Score: {score} | Bank Coins: {total_coins_bank}", True, KEY_COLOR)
        screen.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, 400))

        # Two Options: Next Level and Play Again This Level
        next_lvl_btn = draw_button("NEXT LEVEL ➔", SCREEN_WIDTH // 2 - 270, 470, 240, 55)
        play_again_btn = draw_button("PLAY AGAIN THIS LEVEL", SCREEN_WIDTH // 2 + 30, 470, 260, 55)

    elif game_state == "GAME_OVER":
        screen.fill((150, 20, 20))

        sk_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        pygame.draw.circle(screen, (240, 240, 240), sk_center, 45)
        pygame.draw.circle(screen, (20, 20, 20), (sk_center[0] - 15, sk_center[1] - 5), 10)
        pygame.draw.circle(screen, (20, 20, 20), (sk_center[0] + 15, sk_center[1] - 5), 10)
        pygame.draw.rect(screen, (20, 20, 20), (sk_center[0] - 8, sk_center[1] + 15, 16, 12))

        gotxt = big_font.render("DEAD - ALL HP GONE!", True, (255, 255, 255))
        gosub = title_font.render(f"Restarting from Level 1, {username}...", True, (255, 220, 220))
        screen.blit(gotxt, (SCREEN_WIDTH // 2 - gotxt.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(gosub, (SCREEN_WIDTH // 2 - gosub.get_width() // 2, SCREEN_HEIGHT // 2 + 85))

        restart_btn_rect = draw_button("RESTART FROM LEVEL 1", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 150, 300,
                                       55)
        menu_btn_rect_end = draw_button("MAIN MENU", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 215, 300, 50)

    elif game_state == "VICTORY_ANIMATION":
        screen.fill((20, 15, 30))
        v_title = big_font.render("💖 LOVE CONQUERED ALL! THEY ARE UNITED! 💖", True, COIN_COLOR)
        v_sub = title_font.render(f"Final Score: {score} | Total Bank Coins: {total_coins_bank}", True, TEXT_COLOR)
        screen.blit(v_title, (SCREEN_WIDTH // 2 - v_title.get_width() // 2, 80))
        screen.blit(v_sub, (SCREEN_WIDTH // 2 - v_sub.get_width() // 2, 130))

        pygame.draw.rect(screen, skins[selected_skin_idx]["color"], (590, 340, 50, 65), border_radius=10)
        pygame.draw.circle(screen, (245, 222, 179), (615, 310), 18)

        pygame.draw.rect(screen, (236, 72, 153), (635, 340, 50, 65), border_radius=10)
        pygame.draw.circle(screen, (245, 222, 179), (660, 310), 18)

        dialog_box = pygame.Rect(530, 200, 220, 60)
        pygame.draw.rect(screen, (255, 255, 255), dialog_box, border_radius=12)
        diag_txt = font.render(f"Forever Together, {username} & Akter", True, (15, 35, 20))
        screen.blit(diag_txt, (542, 218))

        heart_txt = big_font.render("💋 ❤️ 💖", True, (239, 68, 68))
        screen.blit(heart_txt, (595, 260))

        restart_btn_rect = draw_button("PLAY AGAIN", SCREEN_WIDTH // 2 - 130, 480, 260, 55)
        menu_btn_rect_end = draw_button("MAIN MENU", SCREEN_WIDTH // 2 - 130, 555, 260, 55)

    pygame.display.flip()

pygame.quit()
sys.exit()