import pygame as pg
from random import randrange
from time import perf_counter, sleep
import os

# Initialize
pg.init()
# Surfaces and vars
SAVE_PATH = "__persistent_stats/score.txt"
PIC_PATH = ''
bg = pg.image.load(f'{PIC_PATH}background.jpg')
pipe_img = pg.transform.scale(pg.image.load(f'{PIC_PATH}pipe.png'), (55, 345))
end = pg.transform.scale(pg.image.load(f'{PIC_PATH}end.png'), (55, 21))
player_img = pg.image.load(f'{PIC_PATH}bird.png')


# Classes
class Poop(pg.sprite.Sprite):
    def __init__(self, x, y, group):
        self.x = x
        self.y = y
        self.rect = poop_img.get_rect(topleft=(self.x, self.y))
        super().__init__(group)

    def draw(self, surf):
        surf.blit(poop_img, (self.x, self.y))

    def update(self, speed):
        self.y += speed
        if self.y >= 617:
            self.kill()
        self.rect = poop_img.get_rect(topleft=(self.x, self.y))


class Pipe(pg.sprite.Sprite):
    def __init__(self, x, y, orientation, group):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.group = group
        self.rect = pg.Rect(self.x, self.y - 21, 55, 657 - self.y) if self.orientation == 'top' else pg.Rect(self.x, 0, 55, self.y + 21)
        self.behind = False
        pg.sprite.Sprite.__init__(self, group)

    def draw(self, surf):
        if self.orientation == 'top':
            new_img = pg.transform.scale(pipe_img, (55, 636 - self.y))
            surf.blit(new_img, (self.x, self.y))
            surf.blit(end, (self.x, self.y - 21))
        else:
            '''
            Takes in x, y as the bottomleft coordinates of the pipe
            '''
            new_img = pg.transform.rotate(pg.transform.scale(pipe_img, (55, self.y)), 180)
            surf.blit(new_img, (self.x, 0))
            surf.blit(pg.transform.rotate(end, 180), (self.x, self.y))

    def update(self, speed):
        self.x -= speed
        if self.x < - 56:
            self.kill()
        self.rect = pg.Rect(self.x, self.y - 21, 55, 657 - self.y) if self.orientation == 'top' else pg.Rect(self.x, 0, 55, self.y + 21)


font = pg.font.SysFont("agencyfb", 50)
small_font = pg.font.SysFont("agencyfb", 25)


def show_text(text: str, surf, place, large=True):
    if large:
        img = font.render(text, True, (255, 255, 255))
    else:
        img = small_font.render(text, True, (255, 255, 255))
        surf.blit(img, place)
    surf.blit(img, place)


# main function
def main(hi_score):
    global car_img
    Ai_Cooldown = 0.05
    AI_start = perf_counter()
    # Variables used for the whole function
    running = True
    screen = pg.display.set_mode((500, 750))
    pipe_group = pg.sprite.Group()
    speed = 2
    poops = pg.sprite.Group()
    # Creation of first 6 pipes
    for x in range(500, 1176, 225):
        y = randrange(201, 614, 1)
        Pipe(x, y, 'top', pipe_group)
        Pipe(x, y - 200, 'bottom', pipe_group)
    # Variables related to the player
    playerX = 160
    playerY = 375
    playerY_change = 0
    playerRect = player_img.get_rect(topleft=(playerX, playerY))
    playerDead = False
    score = 0
    # Related to the car
    carX = pipe_group.sprites()[-2].x + randrange(26, 112)
    carY = 600
    carRect = car_img.get_rect(topleft=(carX, carY))
    carDead = False
    # Other
    gravity = 1
    fall_rate = 0.3
    pg.display.set_caption("Crappy Bird")
    while running:
        start = perf_counter()
        # Background
        screen.fill((0, 0, 0))
        screen.blit(bg, (0, 0))
        # AI
        AI_End = perf_counter()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                with open(SAVE_PATH, "w") as file:
                    file.write(str(max_score))
                pg.quit()
                quit(0)
            if AI_End - AI_start > Ai_Cooldown:
                # Magic Part
                ImportantPipe = list(filter(lambda pipe: pipe.x > playerX, [i for i in pipe_group]))[0]
                if playerY < ImportantPipe.y:
                    playerY_change = 15 * gravity
                    Poop(playerX, playerY + 30, poops)

        # Loop for checking each pipe
        for pipe in pipe_group:
            if not playerDead:
                pipe.update(speed)
            if -56 < pipe.x < 500:
                pipe.draw(screen)
            if len(pipe_group) < 8:
                y = randrange(201, 614, 1)
                Pipe(pipe_group.sprites()[-1].x + 225, y, 'top', pipe_group)
                Pipe(pipe_group.sprites()[-1].x, y - 200, 'bottom', pipe_group)
            if playerX > pipe.x and not pipe.behind:
                score += 0.5
                pipe.behind = True
            if pipe.rect.colliderect(playerRect):
                playerDead = True
        # Related to the player
        screen.blit(player_img, (playerX, playerY))
        playerY -= playerY_change
        playerY_change -= fall_rate
        playerRect.topleft = (playerX, playerY)
        playerDead = not 0 < playerY < 615 if not playerDead else True
        if playerY > 615:
            car_img = pg.image.load(f'{PIC_PATH}car.png')
            return score
        playerY_change = min(playerY_change, 4)
        # Related to poop
        for poop in poops:
            poop.draw(screen)
            poop.update(8)
            if poop.rect.colliderect(carRect) and not carDead:
                score += 2
                carDead = True
                poop.kill()
                car_img = pg.image.load(f'{PIC_PATH}poop_car.png')
        # Related to the car
        screen.blit(car_img, (carX, carY))
        if not playerDead:
            carX -= speed
        if carX < -115:
            carX = pipe_group.sprites()[randrange(-2, 0, 1)].x + randrange(26, 112)
            carDead = False
            car_img = pg.image.load(f'{PIC_PATH}car.png')
        carRect = car_img.get_rect(topleft=(carX, carY))
        # Showing some text
        score = int(score)
        show_text(str(score), screen, (240, 25))
        show_text(str(hi_score), screen, (245, 75), False)
        # Updating the display every frame
        pg.display.update()
        # Assuring that the frame rate is 60fps
        if (dif := perf_counter() - start) < 0.016:
            sleep(0.016 - dif)
        else:
            print("Frame rate is slower than 60fps")
        # Difficulty changing
        speed += 0.0002


if __name__ == '__main__':
    if not os.path.exists(SAVE_PATH):
        f = open(SAVE_PATH, "x")
        f.close()
    with open(SAVE_PATH) as f:
        saved_score = f.read()
        max_score = int(saved_score if saved_score else 0)
    while True:
        max_score = max(main(max_score), max_score)
