#Create your own shooter
#import kniznice pygame

from pygame import *
from random import randint
from time import time as timer


#vytvorime hlavne okno 700x500
win_width = 1024
win_height = 768
FPS = 30
lost = 0
score = 0
goal = 10 
max_lost = 3
life = 3
num_fire = 0
rel_time = False # cas, kedy sa nabyja



window = display.set_mode((win_width,win_height))
display.set_caption("Shooter")

#vytvorime pozadie
background = transform.scale(image.load("galaxy.jpg"), (win_width, win_height))


#hudba na pozadi
mixer.init()
mixer.music.load("space.ogg")
#mixer.music.play()

# zvuk strely
fire_sound = mixer.Sound("fire.ogg")
fire_sound.set_volume(0.1)


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, x, y, size_x, size_y, speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x,size_y))
        self.rect = self.image.get_rect()
        #print(self.rect)
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def render(self):
        window.blit(self.image, self.rect)

class Player(GameSprite):
    def __init__(self, player_image, x, y, size_x, size_y, speed):
        super().__init__(player_image, x, y, size_x, size_y, speed)
    
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x = self.rect.x - self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 105:
            self.rect.x = self.rect.x + self.speed

    # metoda fire - prida objekt Bullet do skupiny bullets
    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx - 10, self.rect.top, 20, 20, -15)
        bullets.add(bullet)


class Enemy(GameSprite):
    # inicializujeme triedu Enemy
    def __init__(self, enemy_image, x, y, size_x, size_y, speed):
        # inicializujeme triedu GameSprite (rodica)
        super().__init__(enemy_image, x, y, size_x, size_y, speed) 
    
    # aktualizuje polohu 
    def update(self):
        global lost
        self.rect.y = self.rect.y + self.speed
        if self.rect.y > win_height:
            self.rect.y = 0
            self.rect.x = randint(80, win_width - 80)
            lost = lost + 1

class Bullet(GameSprite):
    def __init__(self, player_image, x, y, size_x, size_y, speed):
        super().__init__(player_image, x, y, size_x, size_y, speed)

    def update(self):
        self.rect.y = self.rect.y + self.speed
        if self.rect.y < 0:
            self.kill()

# vytvarame objekty z tried (inštancia objektov)
ship = Player("rocket.png",win_width / 2, win_height - 55, 50, 50, 10)

# vytvorime skupinu nepriatelov
enemys = sprite.Group()
# vytvorime skupinu striel
bullets = sprite.Group() 

# vytvorime skupinu asteroidy
asteroids = sprite.Group()
# naplnili sme skupinu 
for i in range(3):
    asteroid = Enemy("asteroid.png", randint(80, win_width - 80), 0, 50, 50, randint(1,3))
    asteroids.add(asteroid)



for i in range(6):
    enemys.add(Enemy("ufo.png", randint(80, win_width - 80), 0, 50, 50, randint(1,3)))

font.init()
font2 = font.Font(None, 36)

font1 = font.Font(None, 80)

win = font1.render("VICTORY", True, (255,255,255)) #RGB
lose = font1.render("GAME OVER", True, (180,0,0)) 


#vytvorime hernu slucku
clock = time.Clock()
finish = False
run = True

while run:

    #kontrola stlacenia close
    for e in event.get():
        if e.type == QUIT:
            run = False
        #je stlaceny klaves
        elif e.type == KEYDOWN:
            # medzernik
            if e.key == K_SPACE:
                #ak pocet striel je menej ako 5 a nenabija sa
                if num_fire < 5 and rel_time == False:
                    num_fire = num_fire + 1
                    # zavola sa metoda fire()
                    ship.fire()
                    fire_sound.play()
                #ak pocet striel je viac ako 5 a nenabija sa
                if num_fire >= 5 and rel_time == False:
                    last_time = timer()
                    rel_time = True



    if not finish:

        # aktivujeme pozadie
        window.blit(background, (0,0))
        # aktivujeme playera
        ship.render()
        ship.update()

        # aktivujeme a nakreslime nepriatelov
        
        enemys.update()
        enemys.draw(window)

        # aktivujeme a vykreslime strely
        bullets.update()
        bullets.draw(window)


        asteroids.update()
        asteroids.draw(window)

        #nabijanie
        if rel_time == True:
            now_time = timer()

            if now_time - last_time < 2:
                reload = font2.render("Wait, reload...",1,(150,0,0))
                window.blit(reload, (win_width / 2 - 50, win_height - 100 ))
            else:
                num_fire = 0
                rel_time = False

        #kolizia medzi strelami a nepriatelmi
        collides = sprite.groupcollide(enemys, bullets, True, True)
        for c in collides:
            score = score + 1
            enemy = Enemy("ufo.png", randint(80, win_width - 80), 0, 50, 50, randint(1,3))    
            enemys.add(enemy)

        #kolizia medzi playerom a nepritelmi a asteroidmi
        if sprite.spritecollide(ship, enemys, False) or sprite.spritecollide(ship, asteroids, False):
            
            sprite.spritecollide(ship, enemys, True)
            sprite.spritecollide(ship, asteroids, True)
            life = life - 1
            
        if life == 0 or lost >= max_lost:
            finish = True
            window.blit(lose, (int(win_width / 2) - int(lose.get_width() / 2),win_height / 2))

        #vyhra
        if score >= goal:
            finish = True
            window.blit(win, (int(win_width / 2) - int(win.get_width() / 2),win_height / 2))

        text_lose = font2.render("Missed: " + str(lost), 1, (255,255,255))
        window.blit(text_lose, (10,50))

        text_score = font2.render("Score: " + str(score), 1, (255,255,255))
        window.blit(text_score, (10, 20))

        text_life = font2.render("Life: " + str(life), 1, (255,255,255))
        window.blit(text_life, (win_width - 100, 20))

        # aktualizujeme hlavne okno
    else:
        finish = False
        score = 0
        lost = 0
        life = 3
        num_fire = 0
        for b in bullets:
            b.kill()
        
        for e in enemys:
            e.kill()

        for e in asteroids:
            e.kill()    
        
        time.delay(3000)

        for i in range(6):
            enemy = Enemy("ufo.png", randint(80, win_width - 80), 0, 50, 50, randint(1,3))
            enemys.add(enemy)

        for i in range(3):
            asteroid = Enemy("asteroid.png", randint(80, win_width - 80), 0, 50, 50, randint(1,3))
            asteroids.add(asteroid)

    display.update()

    clock.tick(FPS)


quit()


