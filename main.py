import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fireboy & Watergirl - Temple Style")
clock = pygame.time.Clock()


try:
    full_sprite_sheet = pygame.image.load("ppl.png").convert_alpha()
    
    sheet_width = full_sprite_sheet.get_width()
    sheet_height = full_sprite_sheet.get_height()
    
    fireboy_img = full_sprite_sheet.subsurface(pygame.Rect(0, 0, sheet_width // 2, sheet_height))
    watergirl_img = full_sprite_sheet.subsurface(pygame.Rect(sheet_width // 2, 0, sheet_width // 2, sheet_height))
    
    fireboy_img = pygame.transform.scale(fireboy_img, (40, 50))
    watergirl_img = pygame.transform.scale(watergirl_img, (40, 50))

except Exception as e:
    print(f"Error loading images: {e}")
    # Fallback to colored surfaces if image is missing
    fireboy_img = pygame.Surface((40, 50)); fireboy_img.fill((255, 60, 0))
    watergirl_img = pygame.Surface((40, 50)); watergirl_img.fill((0, 180, 255))

# Load background (keeping your original brick logic)
try:
    background = pygame.image.load("brick.webp")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((40, 40, 20))

# Colors
BLACK = (0, 0, 0)
SAND = (194, 178, 128)
DARK_SAND = (140, 120, 80)
RED = (255, 60, 0)
BLUE = (0, 180, 255)
GREEN = (0, 255, 100)
GOLD = (255, 215, 0)

class Player:
    def __init__(self, x, y, image, controls, kind):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.image = image
        self.vel_y = 0
        self.on_ground = False
        self.controls = controls
        self.kind = kind
        self.facing_right = True if kind == "fire" else False

    def move(self, keys):
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
        for platform in platforms + moving_platforms:
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

    def draw(self):
        # Flip image based on direction
        img = self.image
        if not self.facing_right:
            img = pygame.transform.flip(self.image, True, False)
        screen.blit(img, (self.rect.x, self.rect.y))

# --- Game Objects Setup ---
platforms = [
    pygame.Rect(0, 600, 900, 50),
    pygame.Rect(100, 520, 300, 20),
    pygame.Rect(500, 480, 300, 20),
    pygame.Rect(200, 400, 250, 20),
    pygame.Rect(500, 350, 250, 20),
]

moving_platforms = [pygame.Rect(350, 550, 120, 20)]
mp_dir = 1

fire_pool = pygame.Rect(200, 600, 120, 20)
water_pool = pygame.Rect(500, 600, 120, 20)
acid_pool = pygame.Rect(350, 580, 100, 20)

gems = [
    ("fire", pygame.Rect(150, 480, 15, 15)),
    ("water", pygame.Rect(700, 450, 15, 15)),
    ("fire", pygame.Rect(300, 350, 15, 15)),
    ("water", pygame.Rect(600, 300, 15, 15)),
]

button = pygame.Rect(120, 580, 40, 10)
gate = pygame.Rect(300, 550, 20, 50)
gate_open = False

# Initialize players with images instead of colors
fireboy = Player(50, 550, fireboy_img, {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}, "fire")
watergirl = Player(820, 550, watergirl_img, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}, "water")

fire_door = pygame.Rect(750, 200, 40, 60)
water_door = pygame.Rect(800, 200, 40, 60)

font = pygame.font.SysFont(None, 40)
running = True
win = False

while running:
    screen.blit(background, (0, 0))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not win:
        moving_platforms[0].x += 2 * mp_dir
        if moving_platforms[0].x > 700 or moving_platforms[0].x < 300:
            mp_dir *= -1

        fireboy.move(keys)
        watergirl.move(keys)

        gate_open = fireboy.rect.colliderect(button) or watergirl.rect.colliderect(button)

        for p in platforms:
            pygame.draw.rect(screen, SAND, p)
            pygame.draw.rect(screen, DARK_SAND, p, 3)

        for mp in moving_platforms:
            pygame.draw.rect(screen, DARK_SAND, mp)

        pygame.draw.rect(screen, RED, fire_pool)
        pygame.draw.rect(screen, BLUE, water_pool)
        pygame.draw.rect(screen, GREEN, acid_pool)

        for kind, gem in gems:
            color = RED if kind == "fire" else BLUE
            pygame.draw.polygon(screen, color, [(gem.centerx, gem.top), (gem.right, gem.centery), (gem.centerx, gem.bottom), (gem.left, gem.centery)])

        if not gate_open:
            pygame.draw.rect(screen, DARK_SAND, gate)
        pygame.draw.rect(screen, GOLD, button)
        pygame.draw.rect(screen, RED, fire_door)
        pygame.draw.rect(screen, BLUE, water_door)

        # Draw the character sprites!
        fireboy.draw()
        watergirl.draw()

        if fireboy.rect.colliderect(water_pool) or fireboy.rect.colliderect(acid_pool): running = False
        if watergirl.rect.colliderect(fire_pool) or watergirl.rect.colliderect(acid_pool): running = False

        if fireboy.rect.colliderect(fire_door) and watergirl.rect.colliderect(water_door):
            win = True
    else:
        text = font.render("You Win!", True, GOLD)
        screen.blit(text, (WIDTH//2 - 80, HEIGHT//2))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()