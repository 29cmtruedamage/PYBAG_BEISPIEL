# src/main.py
import pygame
import asyncio
import random
import sys
import os
from random import randint

# ---------------------------
# Hilfsfunktion (resource_path) - gleiche Logik wie in utils.py
# ---------------------------
def resource_path(relative_path: str) -> str:
    """
    Gibt den richtigen Pfad zurück, egal ob:
    - lokal in Python
    - PyInstaller
    - pygbag / Emscripten
    """
    # PyInstaller
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    # pygbag / Emscripten
    if getattr(sys, "platform", "") == "emscripten":
        return relative_path  # direkt im src-Ordner nutzen

    # lokales Python
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ---------------------------
# JumpAndRun-Logik (Player, Obstacle, Utility-Funktionen)
# ---------------------------
colourGreen = (0, 139, 69)
colourBeige = (255, 222, 173)

generalSpeed = 1

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_x = 150
        self.player_y = 512
        coordinate_Player = (self.player_x, self.player_y)
        playerScale = 0.2

        # Lade Animationen/Bilder
        playerRun1 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/characters/RunAnimation/PlayerRun1.png')), 0, playerScale).convert_alpha()
        playerRun2 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/characters/RunAnimation/PlayerRun2.png')), 0, playerScale).convert_alpha()
        playerRun3 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/characters/RunAnimation/PlayerRun3.png')), 0, playerScale).convert_alpha()
        playerRun4 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/characters/RunAnimation/PlayerRun4.png')), 0, playerScale).convert_alpha()
        playerRun5 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/characters/RunAnimation/PlayerRun5.png')), 0, playerScale).convert_alpha()
        player_rec = playerRun1.get_rect(midbottom = coordinate_Player)
        playerStanding = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/characters/PlayerStanding.png')), 0, playerScale).convert_alpha()
        playerJump = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/characters/PlayerJump.png')), 0, playerScale).convert_alpha()

        self.animationList = [playerRun1, playerRun2, playerRun3, playerRun4, playerRun5]
        self.playerJump = playerJump
        self.playerStanding = playerStanding
        self.index = 0
        self.image = self.animationList[self.index]
        self.rect = player_rec
        self.hitbox = self.rect.inflate(-120, -50)

        # Sound
        try:
            self.jumpSound = pygame.mixer.Sound(resource_path('environment/audios/jumpSound.ogg'))
            self.jumpSound.set_volume(0.5)
        except Exception:
            self.jumpSound = None

        self.gravity = 0
        self.jumpHeight = -12
        self.playerSpeed = 0.1
        self.gravitySpeed = 0.33

    def playerInput(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 500:
            self.gravity = self.jumpHeight
            if self.jumpSound:
                try:
                    self.jumpSound.play()
                except Exception:
                    pass

    def playerJumpHandling(self):
        self.gravity += self.gravitySpeed
        self.rect.y += self.gravity
        if self.rect.bottom >= self.player_y:
            self.rect.bottom = self.player_y

    def playerAnimation(self):
        if self.rect.bottom != self.player_y:
            self.image = self.playerJump
        else:
            self.index += self.playerSpeed
            self.index = self.index % len(self.animationList)
            helperIndex = self.index
            self.image = self.animationList[int(helperIndex)]

    def playerReset(self):
        self.rect.bottom = self.player_y
        self.gravity = 0
        self.playerSpeed = 0.1
        self.gravitySpeed = 0.33

    def playerSpeedUp(self):
        self.playerSpeed = 0.3
        self.gravitySpeed = 0.5

    def update(self):
        self.playerInput()
        self.playerJumpHandling()
        self.playerAnimation()
        self.hitbox.center = self.rect.center

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        y_pos_trees = 500
        treeScale = 0.35
        birdScale = 0.1
        mushroomScale = 0.5
        if type == 'bird':
            bird1_def = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/obstacles/Bird/Vogel1.png')).convert_alpha(), 0, birdScale)
            bird1 = pygame.transform.flip(bird1_def, True, False)
            bird2_def = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/obstacles/Bird/Vogel2.png')).convert_alpha(), 0, birdScale)
            bird2 = pygame.transform.flip(bird2_def, True, False)
            bird3_def = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/obstacles/Bird/Vogel3.png')).convert_alpha(), 0, birdScale)
            bird3 = pygame.transform.flip(bird3_def, True, False)
            self.frames = [bird1, bird2, bird3]
            y_pos = 350
        if type == 'tree1':
            tree1 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/obstacles/Tree_1.png')).convert_alpha(), 0, treeScale)
            self.frames = [tree1]
            y_pos = y_pos_trees
        if type == 'tree2':
            tree2 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/obstacles/Tree_2.png')).convert_alpha(), 0, treeScale)
            self.frames = [tree2]
            y_pos = y_pos_trees
        if type == 'tree3':
            tree3 = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/obstacles/Tree_3.png')).convert_alpha(), 0, treeScale)
            self.frames = [tree3]
            y_pos = y_pos_trees
        if type == 'mushroom':
            mushroom = pygame.transform.rotozoom(pygame.image.load(resource_path('environment/obstacles/Mushroom_2.png')).convert_alpha(), 0, mushroomScale)
            self.frames = [mushroom]
            y_pos = y_pos_trees

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(1100, 1300), y_pos))
        self.obstacleSpeed = 4

    def animation_state(self):
        self.animation_index += 0.1
        self.animation_index = self.animation_index % len(self.frames)
        self.image = self.frames[int(self.animation_index)]

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

    def obstacleSpeedUp(self):
        self.obstacleSpeed = 12

    def obstacleReset(self):
        self.obstacleSpeed = 4

    def update(self):
        self.animation_state()
        self.rect.x -= self.obstacleSpeed
        self.destroy()

def obstacle_SpeedUp(obstacle_group):
    for obstacle in obstacle_group:
        obstacle.obstacleSpeedUp()

def obstacle_Reset(obstacle_group):
    for obstacle in obstacle_group:
        obstacle.obstacleReset()

def drawScore(screen, startTime, highScore):
    score_font = pygame.font.Font(resource_path('environment/textStyles/textStyle1.ttf'), 55)
    highScore_font = pygame.font.Font(resource_path('environment/textStyles/textStyle1.ttf'), 40)
    currentScore = int((pygame.time.get_ticks() - startTime) / 100)
    score_text = score_font.render(f" Your Score: {currentScore} ", True, 'Black')
    highScore_text = highScore_font.render(f" HIGHSCORE: {highScore} ", False, 'Black')

    score_rect_Score = score_text.get_rect(center = (500, 150))
    score_rect_HighScore = highScore_text.get_rect(center = (500, 50))

    screen.blit(score_text, score_rect_Score)
    screen.blit(highScore_text, score_rect_HighScore)

    return currentScore

def checkHighscore(highScore, currentScore):
    if highScore >= currentScore:
        return highScore
    else:
        return currentScore

def environmentReset(rectList):
    rectList[0].center = (500, 300)
    rectList[1].center = (1500, 300)
    rectList[2].midtop = (500, 500)
    rectList[3].midtop = (1500, 500)

def drawEnvironment(screen, b_image, u_image, rectList):
    screen.blit(b_image, rectList[0])
    screen.blit(b_image, rectList[1])
    screen.blit(u_image, rectList[2])
    screen.blit(u_image, rectList[3])

def manageEnvironment(rectList, backgroundSpeed, undergroundSpeed):
    rectList[0].x -= backgroundSpeed
    rectList[1].x -= backgroundSpeed

    rectList[2].x -= undergroundSpeed
    rectList[3].x -= undergroundSpeed

    for rect in rectList:
        if rect.right <= 12:
            rect.left = 1000

def collisionCheck(player, obstacle_group, gameOverSound):
    for obstacle_rect in obstacle_group:
        if player.sprite.hitbox.colliderect(obstacle_rect.rect):
            if gameOverSound:
                try:
                    gameOverSound.play()
                except Exception:
                    pass
            return False, True
    return True, False

def gameOverScreen(screen, score):
    gameOverScreen_font = pygame.font.Font(resource_path('environment/textStyles/textStyle1.ttf'), 200)
    gameOverPressEnter_font = pygame.font.Font(resource_path('environment/textStyles/textStyle1.ttf'), 50)
    gameOverCenter = (500, 200)
    gameOverPressEnterCenter = (500, 400)
    returnBackMenuCenter = (500, 460)
    showScore_center = (500, 340)

    gameOverScreen_text = gameOverScreen_font.render("GAME OVER", False, colourBeige)
    gameOverScreen_rect = gameOverScreen_text.get_rect(center = gameOverCenter)

    gameOverPressEnter_text = gameOverPressEnter_font.render("PRESS ENTER TO RESTART", True, colourBeige)
    gameOverPressEnter_rect = gameOverPressEnter_text.get_rect(center = gameOverPressEnterCenter)

    returnBackMenu_text = gameOverPressEnter_font.render("PRESS ESC TO RETURN TO MENU", True, colourBeige)
    returnBackMenu_rect = returnBackMenu_text.get_rect(center = returnBackMenuCenter)

    showScore_text = gameOverPressEnter_font.render(f"You got {score} points", True, colourBeige)
    showScore_rect = showScore_text.get_rect(center = showScore_center)
    screen.fill(colourGreen)

    screen.blit(showScore_text, showScore_rect)
    screen.blit(gameOverScreen_text, gameOverScreen_rect)
    screen.blit(gameOverPressEnter_text, gameOverPressEnter_rect)
    screen.blit(returnBackMenu_text, returnBackMenu_rect)

# ---------------------------
# main (vereinigt mit deiner ursprünglichen main.py)
# ---------------------------
# init pygame (muss vor Font/Sound-Ladeoperationen passieren)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # keine besonderen Flags
pygame.display.set_caption("JumpAndRun - Web (pygbag)")
clock = pygame.time.Clock()

# Game state (vereinfachte Variante für nur JumpAndRun)
class GameState:
    def __init__(self):
        self.menu = False
        self.game_on = True
        self.game_over = False
        self.start_screen = False

async def safe_sleep_zero():
    # convenience: immer await asyncio.sleep(0) für pygbag compatibility
    await asyncio.sleep(0)

async def main():
    # -------------------------
    # Lade assets (Background, Underground, Sounds)
    # -------------------------
    try:
        bg_path = resource_path('environment/graphics/BG.png')
        background_image = pygame.transform.scale(pygame.image.load(bg_path), (WIDTH, HEIGHT)).convert()
    except Exception as e:
        print("Fehler beim Laden des Backgrounds:", e)
        # Fallback: einfarbige Oberfläche
        background_image = pygame.Surface((WIDTH, HEIGHT)).convert()
        background_image.fill((204, 235, 255))

    background_rect1 = background_image.get_rect(center=(500, 300))
    background_rect2 = background_image.get_rect(center=(1500, 300))

    try:
        underground_image = pygame.transform.scale(pygame.image.load(resource_path('environment/graphics/Untergrund.png')), (1050, 250)).convert_alpha()
    except Exception:
        underground_image = pygame.Surface((1050, 250), pygame.SRCALPHA)
        underground_image.fill((0,0,0,0))
    underground_rect1 = underground_image.get_rect(midtop=(500, 500))
    underground_rect2 = underground_image.get_rect(midtop=(1500, 500))

    environmentRectList = [background_rect1, background_rect2, underground_rect1, underground_rect2]

    # Sounds (robustes Laden)
    def try_load_sound(path):
        try:
            s = pygame.mixer.Sound(resource_path(path))
            s.set_volume(0.5)
            return s
        except Exception:
            return None

    gameOverSound = try_load_sound('environment/audios/GameOverSound.ogg')
    gameStartSound = try_load_sound('environment/audios/GameStartSound.ogg')
    jarMusik = try_load_sound('environment/audios/JumpAndRunBM.ogg')
    menuMusik = try_load_sound('environment/audios/MenuBackgroundMusik.ogg')

    if jarMusik:
        jarMusik.set_volume(0.5)
    if menuMusik:
        menuMusik.set_volume(0.5)
    if gameOverSound:
        gameOverSound.set_volume(0.5)
    if gameStartSound:
        gameStartSound.set_volume(0.5)

    # time/event timers (verwenden pygame event timer)
    obstacleSpawnTimer = pygame.USEREVENT + 1
    pygame.time.set_timer(obstacleSpawnTimer, 2000)

    obstacleSpawnTimer_speedUp = pygame.USEREVENT + 2
    pygame.time.set_timer(obstacleSpawnTimer_speedUp, 770)

    # state + helper vars
    state = GameState()
    state.game_on = True
    speedUp = False
    firstLevel = 100
    secondLevel = 150

    backgroundSpeed = 1
    undergroundSpeed = 4

    # Sprites
    player_group = pygame.sprite.GroupSingle()
    player_group.add(Player())

    obstacle_group = pygame.sprite.Group()

    # score/time
    startTime = pygame.time.get_ticks()
    highScore = 0
    score = 0

    def reset_game():
        nonlocal backgroundSpeed, undergroundSpeed, speedUp, score
        environmentReset(environmentRectList)
        backgroundSpeed = 1
        undergroundSpeed = 4
        player_group.sprite.playerReset()
        speedUp = False
        score = 0
        obstacle_group.empty()
        if jarMusik:
            try:
                jarMusik.stop()
            except Exception:
                pass

    running = True
    # Hauptschleife (async)
    while running:
        # Event-Handling
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            # QUIT: in Browser soll kein abruptes Exit erfolgen -> nur stoppe loop
            if event.type == pygame.QUIT:
                running = False

            # Timer Events: Obstacle Spawning
            if event.type == obstacleSpawnTimer and state.game_on and not speedUp:
                if score < firstLevel:
                    obstacle_group.add(Obstacle(random.choice(['bird','tree1','tree2','bird','tree1','tree2','tree3','mushroom'])))
            if event.type == obstacleSpawnTimer_speedUp and state.game_on and speedUp:
                obstacle_group.add(Obstacle(random.choice(['bird','tree1','tree2','bird','tree1','tree2','tree3','mushroom'])))
                obstacle_SpeedUp(obstacle_group)

            # MOUSE handling: Start screen or restart
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start the music / game if on start screen
                if not state.game_on and not state.game_over:
                    state.game_on = True
                    startTime = pygame.time.get_ticks()
                    if gameStartSound:
                        try:
                            gameStartSound.play()
                        except Exception:
                            pass
                    if jarMusik:
                        try:
                            jarMusik.play(loops=-1)
                        except Exception:
                            pass
                # If game over, click can restart
                if state.game_over:
                    # reset and start
                    state.game_over = False
                    state.game_on = True
                    reset_game()
                    startTime = pygame.time.get_ticks()
                    if jarMusik:
                        try:
                            jarMusik.play(loops=-1)
                        except Exception:
                            pass

            # KEY handling: ESC should not quit the browser; wir behandeln Esc als Pause/reset
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # toggle pause
                    if state.game_on:
                        state.game_on = False
                    elif state.game_over:
                        # return to menu state (not implemented). For now just reset to start.
                        state.game_over = False
                        reset_game()
                        state.game_on = True

        # --- Game update & draw (nur wenn game_on) ---
        screen.fill((204, 235, 255))  # background clear

        if state.game_on:
            # Draw + update environment
            drawEnvironment(screen, background_image, underground_image, environmentRectList)
            manageEnvironment(environmentRectList, backgroundSpeed, undergroundSpeed)
            score = drawScore(screen, startTime, highScore=highScore)
            highScore = checkHighscore(highScore, score)

            # sprites
            player_group.draw(screen)
            player_group.update()
            obstacle_group.draw(screen)
            obstacle_group.update()

            # collision
            state.game_on, state.game_over = collisionCheck(player_group, obstacle_group, gameOverSound)
            # speedup logic
            if not speedUp and score > secondLevel:
                speedUp = True
                player_group.sprite.playerSpeedUp()
                backgroundSpeed = 3
                undergroundSpeed = 12

        elif state.game_over:
            gameOverScreen(screen, score)
        else:
            # start screen (simple)
            try:
                font_big = pygame.font.Font(resource_path('environment/textStyles/textStyle1.ttf'), 80)
            except Exception:
                font_big = pygame.font.SysFont(None, 80)
            txt = font_big.render("Click to Start JumpAndRun", True, 'Black')
            r = txt.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(txt, r)
            # optionally play menu music
            if menuMusik and not pygame.mixer.get_busy():
                try:
                    menuMusik.play(loops=-1)
                except Exception:
                    pass

        # essentials
        await asyncio.sleep(0)   # zwingend für pygbag-kompatibilität in jeder Loop
        clock.tick(80)
        pygame.display.update()

    # Ende - aufräumen
    pygame.quit()

if __name__ == "__main__":
    # Wichtig: asyncio.run ist nötig, damit pygbag das async main korrekt startet
    try:
        asyncio.run(main())
    except Exception as e:
        print("Fehler beim Starten des Spiels:", e)
        pygame.quit()
        # nicht sys.exit() in Browser!
