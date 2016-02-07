import math, pygame, pycol, pyani, random, json
from pycol import *
from pyani import *


class Hook:
    def call(self, event):
        return

class Tile(Block):
    def __init__(self, world, x, y, aniset, tilemanager, tileid = 0):
        self.tx = x
        self.ty = y
        self.tm = tilemanager
        self.aniset = aniset
        self.tileid = tileid
        Block.__init__(self, world, x * self.tm.tile_width, y * self.tm.tile_height, self.tm.tile_width, self.tm.tile_height, world.nextID())
        self.updateChunks()

    def get_type(self):
        return "tile"

    def updateSize(self):
        self.x = self.tx * self.tm.tilewidth
        self.y = self.ty * self.tm.tileheight
        self.width = self.tm.tilewidth
        self.height = self.tm.tileheight
        self.updateChunks()

    def draw(self, target, offset):
        rx = self.x - offset.x
        ry = self.y - offset.y
        target.blit(self.aniset.get(), [rx, ry])
        
class Entity(Block):
    def __init__(self, world, x, y, width, height, aniset, entmanager):
        Block.__init__(self, world, x, y, width, height, world.nextID())
        self.aniset = aniset
        self.em = entmanager

        self.vel = Vector(0,0)
        self.acc = Vector(0,0)
        self.updateChunks()

    def update(self, elapsed):
        self.vel = self.vel.addVec(self.acc)
        self.move(self.vel.x, self.vel.y)

    def draw(self, target, offset):
        rx = self.x - offset.x
        ry = self.y - offset.y
        target.blit(self.aniset.get(), [rx,ry])

class Checkpoint(Block):
    def __init__(self, world, x, y, width, height, aniset, entmanager):
        Block.__init__(self, world, x, y, width, height, world.nextID())
        self.aniset = aniset.loop("on")
        self.em = entmanager

        self.solid = False
        self.updateChunks()

    def get_type(self):
        return "checkpoint"

    def get_priority(self):
        return 3

    def update(self, elapsed):
        if self.world.checkArea(self.x, self.y, self.width, self.height, [], True, ["player"]):
            self.world.setSpawn(self)

    def draw(self, target, offset):
        rx = self.x - offset.x
        ry = self.y - offset.y
        target.blit(self.aniset.get(), [rx,ry])

class FinishLine(Checkpoint):
    def __init__(self, world, x, y, width, height, aniset, entmanager):
        Checkpoint.__init__(self, world, x, y, width, height, aniset, entmanager)

    def update(self, elapsed):
        if self.world.checkArea(self.x, self.y, self.width, self.height, [], True, ["player"]):
            self.world.finish()

class Trap(Block):
    def __init__(self, world, x, y, width, height, aniset, entmanager, damage = 1):
        Block.__init__(self, world, x, y, width, height, world.nextID())
        self.aniset = aniset
        self.em = entmanager

        self.solid = False
        self.damage = 1
        self.updateChunks()

    def get_priority(self):
        return 2

    def get_type(self):
        return "trap"

    def draw(self, target, offset):
        rx = self.x - offset.x
        ry = self.y - offset.y
        target.blit(self.aniset.get(), [rx,ry])

class CircleTrap(CircleBlock):
    def __init__(self, world, x, y, radius, aniset, entmanager, damage = 1):
        CircleBlock.__init__(self, world, x, y, radius, world.nextID())
        self.aniset = aniset
        self.em = entmanager

        self.solid = False
        self.damage = 1
        self.updateChunks()

    def get_priority(self):
        return 2

    def get_type(self):
        return "trap"

    def draw(self, target, offset):
        rx = self.x - offset.x
        ry = self.y - offset.y
        target.blit(self.aniset.get(), [rx,ry])

class Saw(CircleTrap):
    def __init__(self, world, pos_list, speed, radius, aniset, entmanager):
        CircleTrap.__init__(self, world, pos_list[0][0], pos_list[0][1], radius, aniset, entmanager)
        self.speed = speed
        self.pos_list = pos_list
        self.aniset.loop("spin")
        self.solid = False
        
        if len(self.pos_list) > 1:
            self.arg_list = []
            self.dist_list = []
            for i in range(len(pos_list)):
                j = (i + 1) % len(pos_list)
                vec = Vector(pos_list[j][0] - pos_list[i][0], pos_list[j][1] - pos_list[i][1])
                #print(vec.getArg(),":",vec)
                self.arg_list.append(vec.getArg())
                self.dist_list.append(vec.getMod())

            self.step = -1
            self.curdist = 0
            self.nextStep()

    def updatePosList(self):
        if len(self.pos_list) > 1:
            self.arg_list = []
            self.dist_list = []
            for i in range(len(pos_list)):
                j = (i + 1) % len(pos_list)
                vec = Vector(pos_list[j][0] - pos_list[i][0], pos_list[j][1] - pos_list[i][1])
                self.arg_list.append(vec.getArg())
                self.dist_list.append(vec.getMod())

    def nextStep(self):
        self.step+=1
        if self.step >= len(self.arg_list):
            self.step = 0
        
        self.centre_x = self.pos_list[self.step][0]
        self.centre_y = self.pos_list[self.step][1]
        self.curdist = 0
        
        self.vel = Vector(0,0)
        self.vel.setMod(self.speed)
        self.vel.setArg(self.arg_list[self.step])

        #print(self.vel.getArg(),":",self.vel.getMod())
        #print(self.vel)
        #print("-----------------")
        

    def update(self, elapsed):
        if len(self.pos_list) > 1:
            move_vec = self.vel.mult(elapsed)
            self.simple_move(move_vec.x, move_vec.y)
            #print("HI:",self.vel,":",self.x)
            self.curdist += move_vec.getMod()
            if self.curdist >= self.dist_list[self.step]:
                self.nextStep()

class Wall(Tile):
    def __init__(self, world, x, y, aniset, tilemanager, tileid = 0):
        Tile.__init__(self, world, x, y, aniset, tilemanager, tileid)
        self.aniset = aniset.loop("on")
        self.last_state = world.state

        self.typename = "wall"
        if tileid == 1 or tileid == 2:
            self.typename = "toggle_wall"

    def get_priority(self):
        return 1

    def get_type(self):
        return self.typename

    def update(self, elapsed):
        if self.world.state != self.last_state and self.tileid != 0:
            if self.world.state == self.tileid or self.tileid == 0:
                self.aniset.loop("on")
                self.solid = True
                if self.world.player != None:
                    if self.collides(self.world.player):
                        self.world.killPlayer()
                        return True
            else:
                self.aniset.loop("off")
                self.solid = False
            self.last_state = self.world.state
    
    def draw(self, target, offset):
        
        rx = self.x - offset.x
        ry = self.y - offset.y
        target.blit(self.aniset.get(), [rx, ry])

class Button(Block):
    def __init__(self, world, x, y, aniset, tilemanager, direction, doorid = 0, button_lock = False):
        bounds = [0, tilemanager.tile_height - 3, tilemanager.tile_width, 3]
        self.press_bounds = [ (x*tilemanager.tile_width), (y*tilemanager.tile_height) + tilemanager.tile_height - 6, tilemanager.tile_width, 6]
        if direction == 1:
            bounds = [0, 0, 3, tilemanager.tile_height]
            self.press_bounds = [(x*tilemanager.tile_width), (y*tilemanager.tile_height), 6, tilemanager.tile_height]
        elif direction == 2:
            bounds = [0, 0, tilemanager.tile_width, 3]
            self.press_bounds = [(x*tilemanager.tile_width), (y*tilemanager.tile_height), tilemanager.tile_width, 6]
        elif direction == 3:
            bounds = [tilemanager.tile_width - 3, 0, 3, tilemanager.tile_height]
            self.press_bounds = [(x*tilemanager.tile_width) + tilemanager.tile_width - 6, (y*tilemanager.tile_height), 6, tilemanager.tile_height]
        Block.__init__(self, world, (x*tilemanager.tile_width) + bounds[0], (y*tilemanager.tile_height) + bounds[1], bounds[2], bounds[3], world.nextID())

        self.direction = direction
        self.pressed = False
        self.button_lock = button_lock
        self.tx = x
        self.ty = y
        self.tm = tilemanager
        self.aniset = aniset.loop("up_"+str(direction)+"_"+str(doorid))
        self.doorid = doorid
        self.solid = False
        self.updateChunks()

    def pressButton(self):
        self.pressed = True
        self.aniset.loop("down_"+str(self.direction)+"_"+str(self.doorid))
        self.world.openDoors(self.doorid)

    def unpressButton(self):
        self.pressed = False
        self.aniset.loop("up_"+str(self.direction)+"_"+str(self.doorid))
        self.world.closeDoors(self.doorid)

    def get_priority(self):
        return 1

    def get_type(self):
        return "button"

    def update(self, elapsed):
        if not self.pressed or not self.button_lock:
            if self.world.checkArea(self.press_bounds[0], self.press_bounds[1], self.press_bounds[2], self.press_bounds[3], [], True, ["player", "skull"], True):
                self.pressButton()
            else:
                self.unpressButton()

    def draw(self, target, offset):
        rx = (self.tx*self.tm.tile_width) - offset.x
        ry = (self.ty*self.tm.tile_height) - offset.y
        target.blit(self.aniset.get(), [rx, ry])

class Door(Block):
    def __init__(self, world, x, y, aniset, aniset_lock, tilemanager, direction, doorid = 0): #default = up, 1 = right, 2 = down, 3 = left
        bounds = [0, 0, tilemanager.tile_width, 12]
        if direction == 1:
            bounds = [tilemanager.tile_width - 12, 0, 12, tilemanager.tile_height]
        elif direction == 2:
            bounds = [0, tilemanager.tile_height - 12, tilemanager.tile_width, 12]
        elif direction == 3:
            bounds = [0, 0, 12, tilemanager.tile_height]
        Block.__init__(self, world, (x*tilemanager.tile_width) + bounds[0], (y*tilemanager.tile_height) + bounds[1], bounds[2], bounds[3], world.nextID())

        self.direction = direction
        self.open = False
        self.tx = x
        self.ty = y
        self.tm = tilemanager
        self.aniset = aniset.loop("closed_"+str(direction))
        self.aniset_lock = aniset_lock.loop(str(doorid))
        self.lock_offset = [0, 0]
        if direction == 1 or direction == 3:
            self.lock_offset = [bounds[0] + 3, bounds[1] + 11]
        else:
            self.lock_offset = [bounds[0] + 13, bounds[1] + 1]
        self.doorid = doorid
        self.updateChunks()

    def closeDoor(self):
        self.open = False
        self.aniset = self.aniset.loop("closed_"+str(self.direction))
        self.solid = True

    def openDoor(self):
        self.open = True
        self.aniset = self.aniset.loop("open_"+str(self.direction))
        self.solid = False

    def get_priority(self):
        return 1

    def get_type(self):
        return "door"

    def draw(self, target, offset):
        rx = (self.tx*self.tm.tile_width) - offset.x
        ry = (self.ty*self.tm.tile_height) - offset.y
        target.blit(self.aniset.get(), [rx, ry])
        if not self.open:
            target.blit(self.aniset_lock.get(), [rx+self.lock_offset[0], ry+self.lock_offset[1]])

class BackgroundTile(Block):
    def __init__(self, world, x, y, aniset, tilemanager, settype = -1):
        Block.__init__(self, world, -100, -100, 0, 0, world.nextID())
        self.real_x = x * tilemanager.tile_width
        self.real_y = y * tilemanager.tile_height
        if settype == -1:
            settype = random.randint(0, 3)
        self.aniset = aniset.loop(str(settype))
        self.updateChunks()
        self.solid = False

    def get_type(self):
        return "background"

    def draw(self, target, offset):
        rx = self.real_x - offset.x
        ry = self.real_y - offset.y
        target.blit(self.aniset.get(), [rx, ry])

        
class Skull(Block):
    def __init__(self, world, x, y, width, height, aniset, vel, facing_left = True):
        Block.__init__(self, world, x, y, width, height, world.nextID())
        self.facing_left = facing_left
        self.aniset = aniset
        self.solid = False
        self.vel = vel
        self.acc = Vector(-vel.x, 980)
        self.terminal_vel = Vector(450, 300)
        self.terminal_vel_fall = Vector(450, 700)
        self.updateChunks()
        self.cds = Cooldowns().create("bounce_x", 200).start().create("bounce_y", 400).start()
        self.airborne = True

        if facing_left:
            self.aniset.loop("left")
        else:
            self.aniset.loop("right")

    def get_type(self):
        return "skull"

    def get_priority(self):
        return 4

    def updateVelX(self):
        self.acc.x = -self.vel.x
        if self.vel.x > 0:
            self.facing_left = False
            self.aniset.loop("right")
        else:
            self.facing_left = True
            self.aniset.loop("left")

    def update(self, elapsed):
        if self.world.checkArea(self.x+1, self.y, self.width-2, self.height+1, [self], True, None, False, ["player", "toggle_wall"]):
            if self.airborne and self.cds.check("bounce_y"):
                self.vel.y = -self.vel.y * 0.5
                self.cds.start()
            else:
                self.vel.y = 0
            self.airborne = False
        else:
            self.airborne = True
        if self.world.checkArea(self.x-1, self.y+1, self.width+2, self.height-2, [self], True, None, False, ["player", "toggle_wall"]):
            if math.fabs(self.vel.x) < 10:
                self.vel.x = 0
            elif self.cds.check("bounce_x"):
                self.vel.x = -self.vel.x * 0.5
                self.updateVelX()
                self.cds.start()
                #print("hi, ", self.vel.x)
        if self.facing_left and self.vel.x >= 0:
            self.acc.x = 0
            self.vel.x = 0
        elif not self.facing_left and self.vel.x <= 0:
            self.acc.x = 0
            self.vel.x = 0
        players = self.world.checkAndReturnArea(self.x-2, self.y-2, self.width+4, self.height+4, [self], True, ["player"])
        if len(players) > 0:
            vel_mod = Vector(0, 0)
            for player in players:
                vel_mod = vel_mod.addVec(player.vel.mult(0.35))
            self.vel = self.vel.addVec(vel_mod)
            self.updateVelX()
        self.vel = self.vel.addVec(self.acc.mult(elapsed))
        if self.vel.y > 0:
            self.vel = self.vel.capVector(self.terminal_vel_fall)
        else:
            self.vel = self.vel.capVector(self.terminal_vel)
        moveamt = self.vel.mult(elapsed)
        self.clever_move(moveamt.x, moveamt.y, False, True, True, ["player","toggle_wall"])

    def draw(self, target, offset):
        rx = self.x - offset.x
        ry = self.y - offset.y
        target.blit(self.aniset.get(), [rx, ry])


class Spike(Trap):
    def __init__(self, world, x, y, width, height, aniset, entmanager):
        Trap.__init__(self, world, x, y, width, height, aniset, entmanager, 1)
        self.aniset.loop("on")

class Bullet(Trap):
    def __init__(self, world, x, y, width, height, aniset, entmanager, vel):
        Trap.__init__(self, world, x, y, width, height, aniset, entmanager, 1)
        self.aniset.loop("moving")
        self.vel = vel
        self.dead = False

    def update(self, elapsed):
        if self.dead:
            self.destroy()
        else:
            moveamt = self.vel.mult(elapsed)
            result = self.clever_move(moveamt.x, moveamt.y, False, False, True)
            if not result[0] or not result[1]:
                self.dead = True

class Turret(Tile):
    def __init__(self, world, x, y, aniset, tilemanager, direction, cd_offset = 0):
        Tile.__init__(self, world, x, y, aniset, tilemanager, 10)
        self.aniset.loop("t"+str(direction))
        self.cds = Cooldowns().create("shoot", 750).start().offset(cd_offset)
        self.direction = direction
        self.bul_vel = Vector(0,0)
        self.bul_off = [0,0]
        if direction == 0: #up
            self.bul_vel = Vector(0, -100)
            self.bul_off = [int(self.tm.tile_width/2) - 5, -11]
        elif direction == 1: #right
            self.bul_vel = Vector(100, 0)
            self.bul_off = [self.width + 1, int(self.tm.tile_height/2) - 5]
        elif direction == 2: #down
            self.bul_vel = Vector(0, 100)
            self.bul_off = [int(self.tm.tile_width/2) - 5, self.height + 1]
        elif direction == 3: #left
            self.bul_vel = Vector(-100, 0)
            self.bul_off = [-11, int(self.tm.tile_height/2) - 5]


    def get_type(self):
        return "turret"

    def update(self, elapsed):
        if self.cds.check("shoot"):
            Bullet(self.world, self.x + self.bul_off[0], self.y + self.bul_off[1], 10, 10, self.world.game.getAniSet("bullet"), self.world.game.entmanager, self.bul_vel.copy())
            self.cds.start()

class Player(Entity, Hook):
    def __init__(self, world, x, y, width, height, aniset, entmanager):
        Entity.__init__(self, world, x, y, width, height, aniset, entmanager)
        self.terminal_vel = Vector(1500, 1500)
        self.terminal_air = Vector(200, 1500)
        self.acc.y = 980
        self.acc.x = 0
        self.max_jumps = 10
        self.jumps = self.max_jumps
        self.cds = Cooldowns()
        self.cds.create("jump", 100).start()
        self.cds.create("airmove", 200).start()
        self.aniset.loop("stand_left")

        self.jump_input = False
        self.health = 1
        self.was_grounded = False
        self.jumping = False
        self.facing_left = True

    def get_priority(self):
        return 5

    def get_type(self):
        return "player"

    def call(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.jump_input = True

    def update(self, elapsed):
        move_block = False
        acc_mod = 1
        press = pygame.key.get_pressed()
        grounded = self.world.checkArea(self.x+1, self.y, self.width-2, self.height+1, [self], True)
        if not grounded and self.was_grounded and not self.jumping and ( not ( press[pygame.K_d] or press[pygame.K_a] or press[pygame.K_LEFT] or press[pygame.K_RIGHT]) or press[pygame.K_s] or press[pygame.K_DOWN]):
            self.vel.x = 0
        if grounded and self.jumping:
            self.jumping = False
        
        if (press[pygame.K_a] or press[pygame.K_LEFT]):# and self.cds.check("airmove"):
            if grounded:
                self.vel.x = -200
            elif self.world.checkArea(self.x, self.y+1, self.width-1, self.height-2, [self], False) and self.cds.check("airmove"):
                #move_block = True
                if self.vel.y >= 0:
                    acc_mod = 0.1
                self.vel.x = 0
                #self.vel.y = 0
            else:
                self.acc.x = -600
        
        if (press[pygame.K_d] or press[pygame.K_RIGHT]):# and self.cds.check("airmove"):
            if grounded:
                self.vel.x = 200
            elif self.world.checkArea(self.x+1, self.y+1, self.width-1, self.height-2, [self], False) and self.cds.check("airmove"):
                #move_block = True
                if self.vel.y >= 0:
                    acc_mod = 0.1
                #self.vel.y = 0
                self.vel.x = 0
            else:
                self.acc.x = 600
        if not press[pygame.K_a] and not press[pygame.K_LEFT] and not press[pygame.K_d] and not press[pygame.K_RIGHT] or ( (press[pygame.K_a] or press[pygame.K_LEFT]) and (press[pygame.K_d] or press[pygame.K_RIGHT])):
            if grounded:
                self.vel.x = 0
            else:
                self.acc.x = 0
        if self.jump_input and self.jumps > 0 and self.cds.check("jump"):
            if grounded: #floor check
                self.vel.y = -370
                self.acc.x = 0
                self.jumps-=1
                self.cds.start()
                move_block = False
                self.jumping = True
            elif self.world.checkArea(self.x-1, self.y, self.width, self.height, [self]):
                self.vel.y = -320
                self.vel.x = 330
                self.acc.x = 0
                self.jumps-=1
                self.cds.start()
                self.cds.start("airmove")
                move_block = False
                self.jumping = True
            elif self.world.checkArea(self.x+1, self.y, self.width, self.height, [self]):
                self.vel.y = -320
                self.vel.x = -330
                self.acc.x = 0
                self.jumps-=1
                self.cds.start()
                self.cds.start("airmove")
                move_block = False
                self.jumping = True
                #print("JUMPING")

        if grounded:
            self.acc.x = 0
        self.vel = self.vel.addVec(self.acc.mult(elapsed*acc_mod))
        
        if grounded:
            self.vel = self.vel.capVector(self.terminal_vel)
        else:
            self.vel = self.vel.capVector(self.terminal_air)
        if self.vel.x > 0:
            self.facing_left = False
        elif self.vel.x < 0:
            self.facing_left = True
        #print(self.vel)
        diff = self.vel.mult(elapsed)
        results = self.clever_move(diff.x, diff.y)
        if results[1] == False:
            self.vel.y = 0
            self.jumps = self.max_jumps
        self.jump_input = False
        self.was_grounded = grounded

        traps = self.world.checkAndReturnArea(self.x, self.y, self.width, self.height, [self], False, ["trap"], True, True)
        #print(len(traps))
        for trap in traps:
            self.health-=trap.damage
        if self.health <= 0:
            self.world.killPlayer()
            return True
        if not grounded and self.facing_left and acc_mod < 1:
            self.aniset.loop("hang_right")
        elif not grounded and not self.facing_left and acc_mod < 1:
            self.aniset.loop("hang_left")  
        elif not grounded and self.facing_left:
            self.aniset.loop("jump_left")
        elif not grounded and not self.facing_left:
            self.aniset.loop("jump_right")
        elif self.vel.x == 0 and self.facing_left:
            self.aniset.loop("stand_left")
        elif self.vel.x == 0 and not self.facing_left:
            self.aniset.loop("stand_right")
        elif grounded and self.facing_left:
            self.aniset.loop("walk_left")
        elif grounded and not self.facing_left:
            self.aniset.loop("walk_right")
        #print(self.vel)
        #print(self.vel)
        #self.world.offset.x = max(0, min(self.world.map_width - self.world.game.screen.get_width(), int(self.x + (self.width/2) - (self.world.game.screen.get_width()/2))))
        #self.world.offset.y = max(0, min(int(self.world.map_height - (self.world.game.screen.get_height()/2)), int(self.y + (self.height/2) - (self.world.game.screen.get_height()/2))))
        #self.world.offset.x = self.x + (self.width/2) - (self.world.game.screen.get_width()/2)
        #self.world.offset.y = self.y + (self.height/2) - (self.world.game.screen.get_height()/2)

        

class Game:
    def __init__(self, width, height, tile_sizer, chunk_width, chunk_height, background):
        self.tilemanager = ImageManager(tile_sizer)
        self.entmanager = ImageManager()
        self.anisets = {}
        self.screen = pygame.display.set_mode((width, height))
        self.chunk_width = chunk_width
        self.chunk_height = chunk_height
        self.width = width
        self.height = height
        self.background = background
        self.level = None
        self.level_name = None
        self.world_name = None

        self.hooks = {}
        self.paused = False
        self.finished = False

        self.game_time = 0

    def reloadScreen(self):
        self.screen = pygame.display.set_mode((self.width, self.height))

    def addAnimationSet(self, name, aniset):
        self.anisets[name] = aniset

    def getAniSet(self, name):
        return self.anisets[name].copy()

    def loadLevel(self, level_name, world_name, load_dat, load_type, set_level = True):
        self.level_name = level_name
        self.world_name = world_name
        level = Level(self, load_dat, self.chunk_width, self.chunk_height, load_type)
        if set_level:
            self.setLevel(level)
        return level

    def setLevel(self, level):
        self.level = level
        self.level.display = self.screen

    def save(self, timer):
        timer = math.floor(timer * 1000)
        if self.level_name != None and self.world_name != None:
            savename = self.world_name + ":::" + self.level_name
            
            f = open('res/levels/save.jsv')
            data = json.load(f)
            f.close()
            override = True
            if savename in data.keys():
                if savename[data] < timer:
                    override = False
            if override:
                data[self.world_name + ":::" + self.level_name] = timer
                f = open('res/levels/save.jsv', 'w')
                json.dump(data, f)
                f.close()

    def getWidth(self):
        return self.screen.get_width()

    def getHeight(self):
        return self.screen.get_height()

    def tick(self, elapsed):
        self.screen.fill([255,255,255])
        #self.screen.blit(self.background, [0,0])
        self.level.tick(elapsed, self.paused)
        pygame.display.flip()

    def addHook(self, hook, eventtypes):
        if type(eventtypes) != list:
            eventtypes = [eventtypes]
        for eventtype in eventtypes:
            if not eventtype in self.hooks.keys():
                self.hooks[eventtype] = []
            self.hooks[eventtype].append(hook)

    def destroyHook(self, hook):
        for eventtype in self.hooks.keys():
            if hook in self.hooks[eventtype]:
                self.hooks[eventtype].remove(hook)

    def call(self, event):
        if event.type in self.hooks.keys():
            hook_list = self.hooks[event.type]
            for hook in hook_list:
                hook.call(event)

        
class Level(World):
    IMAGE_LOAD = 0
    JSON_LOAD = 1
    def __init__(self, game, load_dat, chunk_width, chunk_height, load_type = 0):
        World.__init__(self, chunk_width, chunk_height)
        self.load_dat = load_dat
        self.load_type = load_type
        self.game = game
        self.skulls = []
        self.skull_limit = 3
        self.level_timer = 0
        self.spawn = None
        self.spawn_tile = None
        self.restart()

    def killPlayer(self):
        if len(self.skulls) < self.skull_limit:
            self.skulls.append(Skull(self, self.player.x+5, self.player.y+1, 11, 12, self.game.getAniSet("player_skull"), self.player.vel, self.player.facing_left))
        else:
            new_skulls = [None] * self.skull_limit
            for i in range(1, self.skull_limit):
                j = len(self.skulls)-(i+1)
                new_skulls[j] = self.skulls[j + 1]
            new_skulls[self.skull_limit-1] = Skull(self, self.player.x+5, self.player.y+1, 11, 12, self.game.getAniSet("player_skull"), self.player.vel, self.player.facing_left)
            self.skulls = new_skulls
        self.restart()

    def finish(self):
        self.game.paused = True
        self.game.finished = True
        self.game.save(self.level_timer)

    def addDoor(self, door):
        if not door.doorid in self.doors:
            self.doors[door.doorid] = []
        self.doors[door.doorid].append(door)

    def openDoors(self, doorid):
        if str(doorid) in self.doors:
            #print("OPENING DOORS")
            for door in self.doors[str(doorid)]:
                door.openDoor()
        #else:
        #    print("NO SUCH DOORS EXISTS (",

    def closeDoors(self, doorid):
        if str(doorid) in self.doors:
            #print("OPENING DOORS")
            for door in self.doors[str(doorid)]:
                door.closeDoor()
        #else:
            #print("NO SUCH DOORS EXIST (", doorid, ")")

    def restart(self):
        self.reset()
        self.game.hooks = {}
        self.offset = Vector(0,0)
        self.state = 0
        self.player = None
        self.doors = {}
        if self.load_type == Level.IMAGE_LOAD:
            self.load_image(self.load_dat)
        elif self.load_type == Level.JSON_LOAD:
            self.load_JSON(self.load_dat)
        #world, x, y, aniset, aniset_lock, tilemanager, direction, doorid = 0
        #for i in range(4):
        #    for j in range(10):
        #        door = Door(self, 22+i, 1+j, self.game.getAniSet("door"), self.game.getAniSet("lock"), self.game.tilemanager, i, j)
                #door.openDoor()
        #door = Door(self, 3, 3, self.game.getAniSet("door"), self.game.getAniSet("lock"), self.game.tilemanager, 2, 0)
        #door.openDoor()
        #Button(self, 2, 3, self.game.getAniSet("button"), self.game.tilemanager, 0, 0)
        if self.player != None:
            self.game.addHook(self.player, [pygame.KEYDOWN])
        for skull in self.skulls:
            skull.updateChunks()
        self.state = 1
        self.respawn()

    def setSpawn(self, spawn_tile):
        if spawn_tile != self.spawn_tile:
            self.spawn = [self.player.x, self.player.y, self.player.vel, self.player.acc]
            self.spawn_tile = spawn_tile
    
    def respawn(self):
        if self.spawn != None:
            if self.player != None:
                self.game.destroyHook(player)
                self.player.destroy()
            self.player = Player(self, self.spawn[0], self.spawn[1], 22, 22, self.game.getAniSet("player"), self.game.entmanager)
            self.game.addHook(self.player, pygame.KEYDOWN)
            if len(self.spawn) > 2:
                self.player.vel = self.spawn[2]
                self.player.acc = self.spawn[3]
    
    def load_image(self, map_image):
        for x in range(map_image.get_width()):
            for y in range(map_image.get_height()):
                colour = map_image.get_at((x,y))
                if colour[0] == 0 and colour[1] == 0 and colour[2] == 0:
                    Wall(self, x, y, self.game.getAniSet("black_block"), self.game.tilemanager)
                elif colour[0] == 255 and colour[1] == 0 and colour[2] == 0:
                    Wall(self, x, y, self.game.getAniSet("red_block"), self.game.tilemanager, 1)
                elif colour[0] == 0 and colour[1] == 255 and colour[2] == 0:
                    Wall(self, x, y, self.game.getAniSet("green_block"), self.game.tilemanager, 2)
                elif colour[0] == 0 and colour[1] == 0 and colour[2] == 255:
                    if self.spawn == None:
                        self.spawn = [x, y]
                elif colour[0] == 100 and colour[1] == 100 and colour[2] == 100:
                    Spike(self, x*self.game.tilemanager.tile_width, (y*self.game.tilemanager.tile_height)+(self.game.tilemanager.tile_height  - 19), 32, 19, self.game.getAniSet("spike"), self.game.entmanager)
                elif colour[0] == 255 and colour[1] >= 205 and colour[2] <= 3:
                    Turret(self, x, y, self.game.getAniSet("turret"), self.game.tilemanager, colour[2], (255  - colour[1]) * 50)
                else:
                    BackgroundTile(self, x, y, self.game.getAniSet("background"), self.game.tilemanager)
        self.map_width = map_image.get_width() * self.game.tilemanager.tile_width
        self.map_height = map_image.get_height() * self.game.tilemanager.tile_height

    def load_JSON(self, info):
        self.map_width = info[0] * self.game.tilemanager.tile_width
        self.map_height = info[1] * self.game.tilemanager.tile_height
        strgrid = info[2]
        sawblocks = {}
        for x in range(self.map_width):
            if x < len(strgrid):
                for y in range(self.map_height):
                    if y < len(strgrid[x]):
                        for z in range(10):
                            if z < len(strgrid[x][y]):
                                text = strgrid[x][y][z]
                                if text != "None":
                                    data = text.split(":")
                                    iname = str(data[3])
                                    iid = int(data[4])
                                    
                                    info = {}
                                    for i in range(5, len(data)):
                                        infodat = data[i].split(";")
                                        info[infodat[0]] = infodat[1]

                                    if iname == "blocks":
                                        if iid == 0: #black
                                            Wall(self, x, y, self.game.getAniSet("black_block"), self.game.tilemanager)
                                        elif iid == 1 or iid == 2: #red
                                            Wall(self, x, y, self.game.getAniSet("red_block"), self.game.tilemanager, 1)
                                        else: #green
                                            Wall(self, x, y, self.game.getAniSet("green_block"), self.game.tilemanager, 2)
                                    elif iname == "spawn":
                                        #self.player = Player(self, x*self.game.tilemanager.tile_width, y*self.game.tilemanager.tile_height, 22, 22, self.game.getAniSet("player"), self.game.entmanager)
                                        if self.spawn == None:
                                            self.spawn = [x*self.game.tilemanager.tile_width, y*self.game.tilemanager.tile_height]
                                    elif iname == "spikes":
                                        Spike(self, x*self.game.tilemanager.tile_width, (y*self.game.tilemanager.tile_height)+(self.game.tilemanager.tile_height  - 19), 32, 19, self.game.getAniSet("spike"), self.game.entmanager)
                                    elif iname == "turrets":
                                        offset = 0
                                        if "offset" in info:
                                            offset = int(info["offset"])
                                        Turret(self, x, y, self.game.getAniSet("turret"), self.game.tilemanager, iid, offset)
                                    elif iname == "saw_block":
                                        saw_id = info["saw_id"]
                                        if not saw_id in sawblocks.keys():
                                            sawblocks[saw_id] = [None] * int(info["path_length"])
                                        saw_pos = int(info["saw_pos"])
                                        sawblocks[saw_id][saw_pos] = [(x*self.game.tilemanager.tile_width) + math.floor(self.game.tilemanager.tile_width/2), (y*self.game.tilemanager.tile_height) + math.floor(self.game.tilemanager.tile_height/2)]
                                        #world, pos_list, speed, radius, aniset, entmanager
                                        #if not None in sawblocks[saw_id]:
                                        #    Saw(self, sawblocks[saw_id], int(info["speed"]), int(info["radius"]), self.game.getAniSet("saw"), self.game.entmanager)
                                    elif iname == "door":
                                        doorid = info["doorid"]
                                        direction = 2
                                        if iid == 0:
                                            direction = 3
                                        elif iid == 1:
                                            direction = 1
                                        elif iid == 2:
                                            direction = 0
                                        #world, x, y, aniset, aniset_lock, tilemanager, direction, doorid = 0
                                        door = Door(self, x, y, self.game.getAniSet("door"), self.game.getAniSet("lock"), self.game.tilemanager, direction, doorid)
                                        self.addDoor(door)
                                    elif iname == "button":
                                        #self, world, x, y, aniset, tilemanager, direction, doorid = 0, button_lock = False
                                        direction_raw = math.floor(iid/20)
                                        direction = 0
                                        if direction_raw == 0:
                                            direction = 0
                                        elif direction_raw == 1:
                                            direction = 2
                                        elif direction == 2:
                                            direction = 1
                                        elif direction == 3:
                                            direction = 3
                                        doorid = math.floor( (iid - (direction_raw * 20)) / 2 )
                                        button_lock = False
                                        if "button lock" in info:
                                            button_lock = bool(info["button lock"])
                                        Button(self, x, y, self.game.getAniSet("button"), self.game.tilemanager, direction, doorid, button_lock)
                                    elif iname == "flag":
                                        if iid == 0:
                                            Checkpoint(self, x * self.game.tilemanager.tile_width + 8, y * self.game.tilemanager.tile_height + 6, 16, 26, self.game.getAniSet("checkpoint"), self.game.entmanager)
                                        elif iid == 1:
                                            FinishLine(self, x * self.game.tilemanager.tile_width + 8, y * self.game.tilemanager.tile_height + 6, 16, 26, self.game.getAniSet("finishline"), self.game.entmanager)
                                    else:
                                        BackgroundTile(self, x, y, self.game.getAniSet("background"), self.game.tilemanager, iid)

    def tick(self, elapsed, paused):
        #blockset = self.player.get_blocks()
        #blockset.append(self.player)
        for i in range(self.max_priority+1):
            if i in self.blocks.keys():
                block_list = self.blocks[i]
                for block in block_list:
                    if not paused:
                        if block.update(elapsed) == True:
                            break
                    block.draw(self.game.screen, self.offset)
        if not paused:
            self.level_timer += elapsed
