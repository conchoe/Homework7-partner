import pygame
import sys
import json
import os

# --- Constants ---
WIDTH, HEIGHT = 900, 650
FPS = 60
SAND, DARK_SAND = (194, 178, 128), (140, 120, 80)
RED, BLUE, GREEN, GOLD = (255, 60, 0), (0, 180, 255), (0, 255, 100), (255, 215, 0)

class Player:
    def __init__(self, x, y, image, controls, kind):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.image = image
        self.vel_y = 0
        self.on_ground = False
        self.controls = controls
        self.kind = kind
        self.facing_right = True if kind == "fire" else False

        # Death Animation State
        self.is_dying = False
        self.death_timer = 0
        self.death_duration = 30 # Frames (0.5 seconds at 60fps)
    
    def die(self):
        if not self.is_dying:
            self.is_dying = True
            self.death_timer = self.death_duration

    def move(self, keys, current_platforms):
        dx = 0
        if keys[self.controls['left']]: 
            dx -= 5
            self.facing_right = False
        if keys[self.controls['right']]: 
            dx += 5
            self.facing_right = True
            
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = -12

        self.vel_y += 0.6
        dy = self.vel_y
        self.on_ground = False

        # Collision logic
        for platform in current_platforms:
            if platform.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            if platform.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y > 0:
                    dy = platform.top - self.rect.bottom
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    dy = platform.bottom - self.rect.top
                    self.vel_y = 0
        
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, screen):
        if self.is_dying and self.death_timer > 0:
            # Calculate shrink and rotation
            # Scale goes from 1.0 down to 0.0
            scale = self.death_timer / self.death_duration
            angle = (self.death_duration - self.death_timer) * 15 # Spins faster as it goes
            
            # Create the dying effect
            img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            dying_img = pygame.transform.rotozoom(img, angle, scale)
            
            # Center the shrinking image on the original rect
            new_rect = dying_img.get_rect(center=self.rect.center)
            screen.blit(dying_img, new_rect)
            
            self.death_timer -= 1
        elif not self.is_dying:
            img = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
            screen.blit(img, (self.rect.x, self.rect.y))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fireboy & Watergirl - Temple Style")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 50)
        
        self.load_assets()
        self.current_level = 1
        self.game_state = "PLAYING" # States: "PLAYING", "GAMEOVER", "WIN"
        
        # Load the first level
        self.load_level(f"level{self.current_level}.json")
        self.reset_game()

    def load_assets(self):
        try:
            sheet = pygame.image.load("ppl.png").convert_alpha()
            sw = sheet.get_width() // 2
            self.fb_img = pygame.transform.scale(sheet.subsurface(0, 0, sw, sheet.get_height()), (40, 50))
            self.wg_img = pygame.transform.scale(sheet.subsurface(sw, 0, sw, sheet.get_height()), (40, 50))
            self.bg = pygame.transform.scale(pygame.image.load("brick.webp"), (WIDTH, HEIGHT))
        except:
            self.fb_img = pygame.Surface((40, 50)); self.fb_img.fill(RED)
            self.wg_img = pygame.Surface((40, 50)); self.wg_img.fill(BLUE)
            self.bg = pygame.Surface((WIDTH, HEIGHT)); self.bg.fill((40, 40, 20))

    def load_level(self, filename):
        """Loads data from JSON. Does not handle logic, just data."""
        with open(filename, "r") as f:
            data = json.load(f)
        
        self.platforms = [pygame.Rect(p) for p in data["platforms"]]
        self.moving_platforms = [pygame.Rect(mp) for mp in data["moving_platforms"]]
        self.fire_pool = pygame.Rect(data["fire_pool"])
        self.water_pool = pygame.Rect(data["water_pool"])
        self.acid_pool = pygame.Rect(data["acid_pool"])
        self.fire_door = pygame.Rect(data["fire_door"])
        self.water_door = pygame.Rect(data["water_door"])
        self.spawn_fb = data["spawn_fb"]
        self.spawn_wg = data["spawn_wg"]

    def reset_game(self):
        """Resets players and basic states."""
        self.fireboy = Player(self.spawn_fb[0], self.spawn_fb[1], self.fb_img, 
                             {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}, "fire")
        self.watergirl = Player(self.spawn_wg[0], self.spawn_wg[1], self.wg_img, 
                               {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}, "water")
        self.mp_dir = 1
        self.game_state = "PLAYING"

    def next_level(self):
        """Handles transition. If level file missing, triggers WIN state."""
        next_num = self.current_level + 1
        filename = f"level{next_num}.json"
        
        if os.path.exists(filename):
            self.current_level = next_num
            self.load_level(filename)
            self.reset_game()
        else:
            self.game_state = "WIN"
            # Move characters away to avoid double triggers
            self.fireboy.rect.x, self.watergirl.rect.x = -100, -100

    def draw_end_screen(self, message, color):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        self.screen.blit(overlay, (0,0))

        msg_text = self.font.render(message, True, color)
        sub_text = "Press 'R' to restart the Temple" if self.game_state == "WIN" else "Press 'R' to Retry"
        retry_text = self.font.render(sub_text, True, (255, 255, 255))
        
        self.screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, HEIGHT//2 - 50))
        self.screen.blit(retry_text, (WIDTH//2 - retry_text.get_width()//2, HEIGHT//2 + 20))

    def run(self):
        while True:
            # 1. Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    # Restart Logic
                    if self.game_state != "PLAYING" and event.key == pygame.K_r:
                        if self.game_state == "WIN":
                            self.current_level = 1
                            self.load_level("level1.json")
                        self.reset_game()
                    
                    # Cheat Hotkey
                    if event.key == pygame.K_n:
                        self.next_level()

            # 2. Logic
            if self.game_state == "PLAYING":
                keys = pygame.key.get_pressed()
                
                # Moving Platforms
                if self.moving_platforms:
                    self.moving_platforms[0].x += 2 * self.mp_dir
                    if self.moving_platforms[0].x > 700 or self.moving_platforms[0].x < 300:
                        self.mp_dir *= -1

                # Player Movement
                self.fireboy.move(keys, self.platforms + self.moving_platforms)
                self.watergirl.move(keys, self.platforms + self.moving_platforms)

                # Hazard Checks
                if self.fireboy.rect.colliderect(self.water_pool) or self.fireboy.rect.colliderect(self.acid_pool):
                    self.fireboy.die()
                if self.watergirl.rect.colliderect(self.fire_pool) or self.watergirl.rect.colliderect(self.acid_pool):
                    self.watergirl.die()

                # If either is dying, check if the animation is finished
                if self.fireboy.is_dying or self.watergirl.is_dying:
                    if self.fireboy.death_timer == 0 and self.watergirl.death_timer == 0:
                        # Character disappeared, NOW show the Game Over screen
                        self.game_state = "GAMEOVER"
                
                # Win Condition
                if not self.fireboy.is_dying and not self.watergirl.is_dying:
                    if self.fireboy.rect.colliderect(self.fire_door) and self.watergirl.rect.colliderect(self.water_door):
                        self.next_level()

            # 3. Drawing
            self.screen.blit(self.bg, (0, 0))
            
            for p in self.platforms: pygame.draw.rect(self.screen, SAND, p)
            for mp in self.moving_platforms: pygame.draw.rect(self.screen, DARK_SAND, mp)
            
            pygame.draw.rect(self.screen, RED, self.fire_pool)
            pygame.draw.rect(self.screen, BLUE, self.water_pool)
            pygame.draw.rect(self.screen, GREEN, self.acid_pool)
            pygame.draw.rect(self.screen, RED, self.fire_door)
            pygame.draw.rect(self.screen, BLUE, self.water_door)

            self.fireboy.draw(self.screen)
            self.watergirl.draw(self.screen)

            if self.game_state == "GAMEOVER":
                self.draw_end_screen("GAME OVER", RED)
            elif self.game_state == "WIN":
                self.draw_end_screen("TEMPLE CONQUERED!", GOLD)

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()