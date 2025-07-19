import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import sys
import random
import time
import threading
import math

# --------- DREAM DATA "ASSETS" ---------
DREAM_COLORS = [
    (42, 6, 69),   # deep purple
    (60, 80, 160), # dark blue
    (212, 155, 47),# gold
    (160, 220, 224),# vaporwave cyan
    (140, 255, 166),# sickly green
    (222, 92, 125), # b3313 pink
]

MARIO_COLOR = (220, 60, 40)
PLATFORM_COLOR = (90, 60, 120)
EXIT_COLOR = (255, 240, 70)

# --------- TKINTER LAUNCHER ---------
class DreamLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SMM64_Dream.z64 (Wa Wa Dream Launcher)")
        self.geometry("480x380")
        self.configure(bg="#222244")
        tk.Label(self, text="SMM64 Dream ROM Emulator", font=("Arial", 18, "bold"), bg="#222244", fg="#f6f6f6").pack(pady=14)
        self.selected_dream = tk.StringVar(value="Random Dream")

        dreams = [
            "Haunted Hallway (B3313-Style)",
            "Shifting Color Plains",
            "Lost Daisy World",
            "Mario's Recurring Room",
            "Beta Skybox Maze",
            "Infinite Fuzzy Platforms"
        ]
        tk.Label(self, text="Select Dream Level:", bg="#222244", fg="#d3d3ff").pack()
        self.dream_combo = ttk.Combobox(self, values=dreams, state="readonly", textvariable=self.selected_dream)
        self.dream_combo.pack(pady=8)
        self.dream_combo.set("Random Dream")

        tk.Label(self, text="FMRI Seed (Randomizes Colors):", bg="#222244", fg="#bfffee").pack(pady=(16, 0))
        self.seed_entry = tk.Entry(self)
        self.seed_entry.insert(0, str(int(time.time())))
        self.seed_entry.pack(pady=4)

        self.ram_label = tk.Label(self, text="Allocated Dream RAM: 64 MB", bg="#222244", fg="#ffffbb")
        self.ram_label.pack(pady=5)
        self.ram_slider = tk.Scale(self, from_=32, to=512, orient="horizontal", bg="#333366", fg="#fff", highlightbackground="#222244", length=200, command=self.update_ram)
        self.ram_slider.set(64)
        self.ram_slider.pack()

        self.play_btn = tk.Button(self, text="Enter Dream", font=("Arial", 14, "bold"),
                                 bg="#4e3ecc", fg="#fff", bd=0, padx=10, pady=7, command=self.start_dream)
        self.play_btn.pack(pady=16)

        tk.Label(self, text="AI/ROM built from sleep data.\nB3313 but even more cursed.\nMeme-powered since Y2K38.", 
                 bg="#222244", fg="#ccc", font=("Arial", 9, "italic")).pack(pady=(18,0))
        
        self.mainloop_thread = None

    def update_ram(self, val):
        self.ram_label.config(text=f"Allocated Dream RAM: {val} MB")

    def start_dream(self):
        dream = self.selected_dream.get()
        try:
            seed = int(self.seed_entry.get())
        except:
            seed = int(time.time())
        if dream == "Random Dream":
            dream = random.choice([
                "Haunted Hallway (B3313-Style)",
                "Shifting Color Plains",
                "Lost Daisy World",
                "Mario's Recurring Room",
                "Beta Skybox Maze",
                "Infinite Fuzzy Platforms"
            ])
        self.withdraw()
        threading.Thread(target=run_pygame_dream, args=(dream, seed, int(self.ram_slider.get()), self)).start()

def run_pygame_dream(dream_name, seed, ram, parent):
    pygame.init()
    W, H = 768, 432
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption(f"SMM64_Dream.z64 - {dream_name}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 26, bold=True)
    random.seed(seed)

    # Colors/backgrounds cycle every dream
    palette = random.sample(DREAM_COLORS, k=len(DREAM_COLORS))
    bg_color = random.choice(palette)
    color_shift = 0

    # Mario placeholder: circle
    mario_x = W // 3
    mario_y = H - 80
    mario_vy = 0
    on_ground = False

    # Platforms (list of [x, y, w, h])
    platforms = []
    for i in range(8):
        px = random.randint(60, W-160)
        py = H - 50 - i*random.randint(32, 70)
        pw = random.randint(100, 180)
        platforms.append([px, py, pw, 18])
    # "Exit" platform
    exit_rect = pygame.Rect(platforms[-1][0]+platforms[-1][2]-60, platforms[-1][1]-22, 48, 18)
    
    # "Daisy is missing" always
    daisy_missing = True

    running = True
    msg_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            mario_x -= 4
        if keys[pygame.K_RIGHT]:
            mario_x += 4
        if keys[pygame.K_UP] and on_ground:
            mario_vy = -11
            on_ground = False

        # Gravity
        mario_vy += 0.55
        mario_y += mario_vy

        # Collisions
        on_ground = False
        mario_rect = pygame.Rect(mario_x-18, mario_y-24, 36, 44)
        for plat in platforms:
            plat_rect = pygame.Rect(plat[0], plat[1], plat[2], plat[3])
            if mario_rect.colliderect(plat_rect) and mario_vy >= 0:
                mario_y = plat[1]-44
                mario_vy = 0
                on_ground = True

        # Exiting dream
        if mario_rect.colliderect(exit_rect):
            running = False

        # Color-shifting background (dream/fMRI meme)
        color_shift = (color_shift + 1) % 360
        hue = int(120 + 120 * math.sin(color_shift / 57))
        bg = (abs((bg_color[0]+hue)%255), abs((bg_color[1]+hue*2)%255), abs((bg_color[2]+hue*3)%255))
        screen.fill(bg)

        # Draw platforms
        for plat in platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, plat)
        # Exit
        pygame.draw.rect(screen, EXIT_COLOR, exit_rect)
        screen.blit(font.render("EXIT", True, (30,30,30)), (exit_rect.x+2, exit_rect.y-8))

        # Mario
        pygame.draw.ellipse(screen, MARIO_COLOR, (mario_x-18, mario_y-24, 36, 44))
        screen.blit(font.render("M", True, (255,255,255)), (mario_x-10, mario_y-10))

        # Daisy meme (always missing)
        if daisy_missing and random.randint(0,120)==0:
            screen.blit(font.render("Daisy is missing...", True, (255,215,255)), (random.randint(0,W-180), random.randint(0,H-30)))

        # Dream info
        screen.blit(font.render(dream_name, True, (245,245,255)), (16, 16))
        screen.blit(font.render("Press [ESC] to exit dream", True, (130,180,255)), (16, H-40))

        pygame.display.flip()
        clock.tick(60)
        # Escape
        if keys[pygame.K_ESCAPE]:
            running = False

    pygame.quit()
    parent.deiconify()

# ---- RUN THE LAUNCHER ----
if __name__ == "__main__":
    DreamLauncher()
