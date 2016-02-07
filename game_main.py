import pygame, pyani, pylevel, json
from pylevel import *
from pyani import *

pygame.init()

class TileSizer:
    def __init__(self, width, height):
        self.tile_width = width
        self.tile_height = height


background = pygame.image.load("res/imgs/background.png")
game = Game(1080, 720, TileSizer(32,32), 100, 100, background)
game.tilemanager.loadTiles(pygame.image.load("res/imgs/blocks.png"), 5, 1, "blocks")
game.tilemanager.loadTiles(pygame.image.load("res/imgs/turrets.png"), 4, 1, "turrets")
game.tilemanager.loadTiles(pygame.image.load("res/imgs/background_tiles.png"), 4, 1, "background")
game.tilemanager.loadTiles(pygame.image.load("res/imgs/doors.png"), 4, 2, "doors")
game.tilemanager.loadTiles(pygame.image.load("res/imgs/buttons.png"), 10, 8, "buttons")
game.entmanager.loadTiles(pygame.image.load("res/imgs/player.png"), 7, 2, "player")
game.entmanager.loadImage(pygame.image.load("res/imgs/spikes.png"), "spikes")
game.entmanager.loadTiles(pygame.image.load("res/imgs/bullet.png"), 3, 1, "bullet")
game.entmanager.loadTiles(pygame.image.load("res/imgs/player_skull.png"), 2, 1, "player_skull")
game.entmanager.loadTiles(pygame.image.load("res/imgs/laser_saw.png"), 5, 1, "saw")
game.entmanager.loadTiles(pygame.image.load("res/imgs/locks.png"), 10, 1, "locks")
game.entmanager.loadTiles(pygame.image.load("res/imgs/flags.png"), 2, 1, "flags")
game.addAnimationSet("player", AnimationSet(game.entmanager, ["walk_left:player,0,200;player,1,200;player,2,200;player,1,200",
                                                              "walk_right:player,11,200;player,10,200;player,9,200;player,10,200",
                                                              "stand_left:player,3,500;player,4,500",
                                                              "stand_right:player,7,500;player,8,500",
                                                              "jump_left:player,0,100",
                                                              "jump_right:player,11,100",
                                                              "hang_left:player,5,500;player,6,500",
                                                              "hang_right:player,12,500;player,13,500"]))
game.addAnimationSet("player_skull", AnimationSet(game.entmanager, ["left:player_skull,0,100",
                                                                    "right:player_skull,1,100"]))
game.addAnimationSet("black_block", AnimationSet(game.tilemanager, ["on:blocks,0,100"]))
game.addAnimationSet("red_block", AnimationSet(game.tilemanager, ["on:blocks,1,100",
                                                                  "off:blocks,2,100"]))
game.addAnimationSet("green_block", AnimationSet(game.tilemanager, ["on:blocks,3,100",
                                                                    "off:blocks,4,100"]))
game.addAnimationSet("spike", AnimationSet(game.entmanager, ["on:spikes,0,100"]))
game.addAnimationSet("turret", AnimationSet(game.tilemanager, ["t0:turrets,0,100",
                                                               "t1:turrets,1,100",
                                                               "t2:turrets,2,100",
                                                               "t3:turrets,3,100"]))
game.addAnimationSet("bullet", AnimationSet(game.entmanager, ["moving:bullet,0,100;bullet,1,100;bullet,2,100"]))
game.addAnimationSet("background", AnimationSet(game.tilemanager, ["0:background,0,100",
                                                                   "1:background,1,100",
                                                                   "2:background,2,100",
                                                                   "3:background,3,100"]))
game.addAnimationSet("saw", AnimationSet(game.entmanager, ["spin:saw,0,100;saw,1,100;saw,2,100;saw,3,100;saw,4,100"]))
game.addAnimationSet("door", AnimationSet(game.tilemanager, ["closed_0:doors,4,100",
                                                             "open_0:doors,5,100",
                                                             "closed_1:doors,3,100",
                                                             "open_1:doors,2,100",
                                                             "closed_2:doors,7,100",
                                                             "open_2:doors,6,100",
                                                             "closed_3:doors,0,100",
                                                             "open_3:doors,1,100"]))
game.addAnimationSet("lock", AnimationSet(game.entmanager, ["0:locks,0,100", "1:locks,1,100", "2:locks,2,100", "3:locks,3,100", "4:locks,4,100",
                                                             "5:locks,5,100", "6:locks,6,100", "7:locks,7,100", "8:locks,8,100", "9:locks,9,100"]))
game.addAnimationSet("checkpoint", AnimationSet(game.entmanager, ["on:flags,0,100"]))
game.addAnimationSet("finishline", AnimationSet(game.entmanager, ["on:flags,1,100"]))

button_anisets = []
for direction in range(4):
    row = 0
    if direction == 1:
        row = 4
    elif direction == 2:
        row = 2
    elif direction == 3:
        row = 6
    for doorid in range(10):
        imgid = (row * 10) + doorid * 2
        button_anisets.append("up_"+str(direction)+"_"+str(doorid)+":buttons,"+str( (row * 10) + (doorid * 2) )+",100")
        button_anisets.append("down_"+str(direction)+"_"+str(doorid)+":buttons,"+str( (row * 10) + (doorid * 2) + 1 )+",100")
game.addAnimationSet("button", AnimationSet(game.tilemanager, button_anisets))
                                                               

#game.loadLevel(pygame.image.load("map.png"), Level.IMAGE_LOAD)
def run(mapname, levelname = None, worldname = None):
    mapname = "res/levels/" + mapname
    game.reloadScreen()
    game.loadLevel(levelname, worldname, json.load(open(mapname)), Level.JSON_LOAD)

    fps_timer = pygame.time.get_ticks()
    cur_frames = 0
    last_tick = pygame.time.get_ticks()
    running = True
    while running and not game.finished:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game.level.state = game.level.state+1
                    if game.level.state > 2:
                        game.level.state = 1
                elif event.key == pygame.K_r:
                    game.level.killPlayer()
                
            game.call(event)
                
        elapsed = pygame.time.get_ticks() - last_tick
        last_tick = pygame.time.get_ticks()
        game.tick(elapsed/1000)
        cur_frames+=1

        if pygame.time.get_ticks() - fps_timer >= 1000:
            pygame.display.set_caption(str(cur_frames))
            fps_timer = pygame.time.get_ticks()
            cur_frames = 0
