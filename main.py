import pygame as pg
pg.init()

W, H = 1000, 600
screen = pg.display.set_mode((W, H))
clock = pg.time.Clock()
pg.display.set_caption("MyGame")

with open("level1.txt", "r", encoding="utf-8") as f:
    level = f.read()
    level = level.split("\n")
background_images = [pg.transform.scale(pg.image.load(rf"image\oak_woods_v1.0\background\background_layer_{i}.png"), (W, H)).convert_alpha() for i in range(1, 4)]


class GameSprite(pg.sprite.Sprite):
    def __init__(self, image:str, x:int, y:int, w:int, h:int) -> None:
        super().__init__()
        self.image = pg.transform.scale(pg.image.load(f'image\{image}'), (w, h)).convert_alpha()
        self.rect = self.image.get_rect(centerx=W//2, bottom=H)
        # self.rect = pg.Rect()
 
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, image, x, y, w, h) -> None:
        super().__init__(image, x, y, w, h)
        self.speed = 5
        self.points = 0 # очки для второй игры

        self.lose = False # если враг дотронулся до игрока то lose равен True
        # типо куда смотрит
        self.side = 'right'
        self.time_mouse = 0 # чтобы нельзя была слишком быстро стрелять
        self.mouse = False # Знать нажата ли была кнопка
        self.JUMP_POWER = 12
        self.GRAVITY = 0.35 # Сила, которая будет тянуть нас вниз
        self.yvel = 0 # скорость вертикального перемещения
        self.xvel = 0
        self.onGround = False # На земле ли я?
        self.MOVE_SPEED = 7

        # Animations, image
        self.frame_animation = 0
        
        # типо стоять, я хз как на инглишь бцдет стоять
        self.stating_image_right = self.image
        self.stating_image_left = pg.transform.flip(self.stating_image_right, True, False)
        
        self.run_images_right = [pg.transform.scale(pg.image.load(fr"image\hero\run_{i}.png"), (w, h)) for i in range(1, 8)]
        self.run_images_left = [pg.transform.flip(i, True, False) for i in self.run_images_right]
        
    def update(self, platforms, HP=False):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]: # LEFT
            self.xvel = -self.MOVE_SPEED
            if self.frame_animation % 3 == 0:
                self.image = self.run_images_left[0]
            if self.frame_animation % 5 == 0:
                self.image = self.run_images_left[1]
            if self.frame_animation % 7 == 0:
                self.image = self.run_images_left[2]
            if self.frame_animation % 10 == 0:
                self.image = self.run_images_left[3]
            if self.frame_animation % 12 == 0:
                self.image = self.run_images_left[4]
            if self.frame_animation % 15 == 0:
                self.image = self.run_images_left[5]
            if self.frame_animation % 17 == 0:
                self.image = self.run_images_left[6]
            self.frame_animation += 0.5
            self.side = 'left'
        if keys[pg.K_RIGHT] or keys[pg.K_d]: # RIGHT
            self.xvel = self.MOVE_SPEED
            if self.frame_animation % 3 == 0:
                self.image = self.run_images_right[0]
            if self.frame_animation % 5 == 0:
                self.image = self.run_images_right[1]
            if self.frame_animation % 7 == 0:
                self.image = self.run_images_right[2]
            if self.frame_animation % 10 == 0:
                self.image = self.run_images_right[3]
            if self.frame_animation % 12 == 0:
                self.image = self.run_images_right[4]
            if self.frame_animation % 15 == 0:
                self.image = self.run_images_right[5]
            if self.frame_animation % 17 == 0:
                self.image = self.run_images_right[6]
            self.frame_animation += 0.5
            self.side = 'right'
        if keys[pg.K_UP] or keys[pg.K_w] or keys[pg.K_SPACE]: # прыгаем, только когда можем оттолкнуться от земли
            if self.onGround:
                self.yvel = -self.JUMP_POWER
        if not(keys[pg.K_LEFT] or keys[pg.K_RIGHT] or keys[pg.K_a] or keys[pg.K_d]): # стоим, когда нет указаний идти   
            self.xvel = 0
            self.frame_animation = 0
            if self.side == "right":
                self.image = self.stating_image_right
            else:
                self.image = self.stating_image_left
        if not self.onGround: # гравитация
            self.yvel += self.GRAVITY
        self.onGround = False;
        self.rect.y += self.yvel 
        self.collide(0, self.yvel,platforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self,xvel, yvel, pfs):
        for p in pfs:
            if pg.sprite.collide_rect(self, p):
                if xvel > 0:                      # если движется вправо
                    self.rect.right = p.rect.left # то не движется вправо
                if xvel < 0:                      # если движется влево
                    self.rect.left = p.rect.right # то не движется влево

                if yvel > 0:                      # если падает вниз
                    self.rect.bottom = p.rect.top # то не падает вниз
                    self.onGround = True          # и становится на что-то твердое
                    self.yvel = 0                 # и энергия падения пропадает

                if yvel < 0:                      # если движется вверх
                    self.rect.top = p.rect.bottom # то не движется вверх
                    self.yvel = 0                 # и энергия прыжка пропадает

class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, COLOR, image=False):
        pg.sprite.Sprite.__init__(self)
        if image:
            self.image = pg.transform.scale(pg.image.load(image), (PLATFORM_WIDTH, PLATFORM_HEIGHT))
            self.rect = self.rect = pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
        if not image:
            self.image = pg.Surface((PLATFORM_WIDTH, PLATFORM_HEIGHT))  
            self.image.fill(pg.Color(COLOR))
            self.rect = pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

# Camera
class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = pg.Rect(0, 0, width, height)
	
    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
def camera_configure(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l+W / 2, -t+H / 2

    l = min(0, l)                  # Не движемся дальше левой границы
    l = max(-(camera.width-W), l)  # Не движемся дальше правой границы
    t = max(-(camera.height-H), t) # Не движемся дальше нижней границы
    t = min(0, t)                  # Не движемся дальше верхней границы

    return pg.Rect(l, t, w, h)  
total_level_w = len(level[0])*30
total_level_h = len(level)*30

camera = Camera(camera_configure, total_level_w, total_level_h)

sprites = pg.sprite.Group()
player = Player('hero/1.png', 90, 120, 25, 50)
sprites.add(player)


platforms = []
PLATFORM_WIDTH = PLATFORM_HEIGHT = 30
x=y=0 # координаты
for row in level: # вся строка
    for col in row: # каждый символ
        if col == "-":
            #создаем блок, заливаем его цветом и рисеум его
            pf = Platform(x, y, "#036a96", "image/ground/block_up.png")
            sprites.add(pf)
            platforms.append(pf)
        if col == 'r':
            pf = Platform(x, y, "#036a96", "image/ground/block_up_right.png")
            sprites.add(pf)
            platforms.append(pf)    
        if col == "l":
            pf = Platform(x, y, "asdasd", "image/ground/block_up_left.png")        
            sprites.add(pf)
            platforms.append(pf)    
        if col == '1':
            pf = Platform(x, y, "asdasd", "image/ground/block_right.png")        
            sprites.add(pf)
            platforms.append(pf)    
        if col == '2':
            pf = Platform(x, y, "asdasd", "image/ground/block_left.png")        
            sprites.add(pf)
            platforms.append(pf)    
        x += PLATFORM_WIDTH #блоки платформы ставятся на ширине блоков
    y += PLATFORM_HEIGHT    #то же самое и с высотой
    x = 0                   #на каждой новой строчке начинаем с нуля

while True:
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            pg.quit()
        if ev.type == pg.MOUSEBUTTONDOWN:
            mouse = pg.mouse.get_pos()
            print(mouse)

    # draw background
    for i in background_images:
        screen.blit(i, (0, 0))
    
    player.update(platforms)
    camera.update(player)
    # draw sprites
    for e in sprites:
        screen.blit(e.image, camera.apply(e))

    pg.display.update()
    clock.tick(60)