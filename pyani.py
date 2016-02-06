import pygame, math

#ImageManager:
#   loads and stores images, if a tilemap is given it fits the images to the
#   tile size.
#
#   tile_width and tile_height can be accessed and set directly from imagemanager and it will set the tilemaps
#   resective value.
#
#   icon-system creates an icon of a certain size for every image loaded and saves them. Is used in editor_main.py
#
#   icon functions:
#       getIcon(index)
#           - returns the icon with the given index
#       iconAmount()
#           - returns the amount of icons in the image manager
#       icondIdAmount
#           - returns the number of icon id's
#       getIdIcon(name, index)
#           - returns an icon with a name and an index
#       createIcon(name)
#           - creates an icon version of the image stored as name.
#
#   loading function:
#       loadImage(image, name, alpha = True)
#           - saves the image under "name", if alpha is true the alpha channel will be enabled
#       loadTiles(image, columns, rows, name, alpha = True)
#           - converts the image in to a set of images (row x column images) then saves them all under name, if alpha is true the alpha channel will be enabled
#       
class ImageManager:
    def __init__(self, tilemap = None, iconsize = None): #tilemap anything with variables tile_width and tile_height
        self.tilemap = tilemap
        self.images = {}
        self.iconsize = iconsize

        self.icons = []
        self.id_icons = {}
        self.icon_names = []

    @property
    def tile_width(self):
        return self.tilemap.tile_width

    @tile_width.setter
    def tile_width(self, new_tile_width):
        self.tilemap.tile_width = new_tile_width

    @property
    def tile_height(self):
        return self.tilemap.tile_height

    @tile_width.setter
    def tile_height(self, new_tile_height):
        self.tilemap.tile_height = new_tile_height

    def getIcon(self, index):
        if index < self.iconAmount() and index >= 0:
            return self.icons[index]
        return None

    def iconAmount(self):
        return len(self.icons)

    def iconIdAmount(self, name):
        if name != None:
            return len(self.id_icons[name])
        return 0

    def getIdIcon(self, name, index):
        if name != None and index >= 0 and index < self.iconIdAmount(name):
            return self.id_icons[name][index]
        return None

    def createIcon(self, name):
        if self.iconsize != None:
            image = self.images[name][0]
            image = pygame.transform.scale(image, self.iconsize)
            self.icons.append(image)
            self.icon_names.append(name)

            length = len(self.images[name])
            idicons = []
            for i in range(length):
                idicons.append(pygame.transform.scale(self.images[name][i], self.iconsize))
            self.id_icons[name] = idicons

    def loadImage(self, image, name, alpha = True):
        if alpha:
            image = image.convert_alpha()
        if self.tilemap != None and not self.checkScale(image):
            image = pygame.transform.scale(image, (self.tilemap.tile_width, self.tilemap.tile_height)).convert()
            #if alpha:
            #    image.convert_alpha()
        self.images[name] = [image]
        self.createIcon(name)

    def loadTiles(self, image, columns, rows, name, alpha = True):
        image = image.convert_alpha()
        tile_width = math.floor(image.get_width()/columns)
        tile_height = math.floor(image.get_height()/rows)
        need_to_scale = True
        if  self.tilemap == None or (tile_width == self.tilemap.tile_width and tile_height == self.tilemap.tile_height):
            need_to_scale = False
        images = [None] * (columns*rows)
        for y in range(rows):
            id_offset = y*columns
            for x in range(columns):
                img = pygame.Surface((tile_width, tile_height), flags=pygame.SRCALPHA)
                if not alpha:
                    img = pygame.Surface((tile_width, tile_height))
                img.blit(image, [0,0], [x*tile_width, y*tile_height, tile_width, tile_height])
                if need_to_scale:
                    img = pygame.transform.scale(img, (self.tilemap.tile_width, self.tilemap.tile_height)).convert_alpha()
                #if alpha:
                #    img = img.convert_alpha()
                images[id_offset+x] = img
        self.images[name] = images
        self.createIcon(name)

    def loadResourceFile(self, name):
        f = open(name)
        line = f.readline()
        while line != '':
            if line != "\n" and line[0] != "#":
                data = line.split(":")
                image = pygame.image.load(data[1]).convert_alpha()
                if len(data) == 2:
                    self.loadImage(image, data[0])
                elif len(data) == 4:
                    columns, rows = int(data[2]), int(data[3])
                    if columns == 1 and rows == 1:
                        self.loadImage(image, data[0])
                    else:
                        self.loadTiles(image, columns, rows, data[0])
                else:
                    print(" INVALID LINE FOUND IN " + name)
            line = f.readline()

    def checkScale(self, image):
        if self.tilemap == None:
            return True
        elif image.get_width() != self.tilemap.tile_width or image.get_height() != self.tilemap.tile_height:
            return False
        return True

    def get(self, name, imgid = 0):
        if name != None and imgid != None:
            img = self.images[name][imgid]
            if self.tilemap != None and not self.checkScale(img):
                img = pygame.transform.scale(img, (self.tilemap.tile_width, self.tilemap.tile_height))
                self.images[name][imgid] = img
            return img

    def getTileImage(self, tile):
        return self.getImage(tile.info["img_name"], tile.info["img_id"])


class Cooldowns:
    def __init__(self):
        self.cooldowns = {}
        self.last_used = ""

    def create(self, name, length):
        self.last_used = name
        self.cooldowns[name] = [length, -1]
        return self

    def start(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name
        
        self.cooldowns[name][1] = pygame.time.get_ticks()
        return self

    def stop(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name
        
        self.cooldowns[name][1] = -1
        return self

    def check(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name
            
        cd = self.cooldowns[name]
        if cd[1] > 0 and pygame.time.get_ticks() - cd[1] >= cd[0]:
            return True
        return False

    def offset(self, offset, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name

        self.cooldowns[name][1] += offset
        return self

    def elapsed(self, name = None):
        if name == None:
            name = self.last_used
        else:
            self.last_used = name

        return pygame.time.get_ticks() - self.cooldowns[name][1]


class Animation:
    def __init__(self, imagemanager, images, frametimes, loop = False):
        self.im = imagemanager
        self.images = images
        self.frametimes = frametimes
        self.frame = 0
        self.last_tick = -1
        self.loop = loop

    def get(self):
        if self.last_tick > 0:
            stop = False
            elapsed = pygame.time.get_ticks() - self.last_tick
            while elapsed > self.frametimes[self.frame]:
                elapsed = elapsed - self.frametimes[self.frame]
                self.frame = (self.frame + 1) % len(self.images)
                if self.frame == 0 and self.loop == False:
                    self.frame = len(self.images) - 1
                    stop = True
                    break
            if stop:
                self.last_tick = -1
            else:
                self.last_tick = pygame.time.get_ticks() - elapsed
        return self.im.get(*self.images[self.frame])

    def start(self):
        self.last_tick = pygame.time.get_ticks()
        return self

    def pause(self):
        self.last_tick = -1
        return self

    def restart(self):
        self.frame = 0
        self.last_tick = pygame.time.get_ticks()
        return self

    def setLoop(self, loop):
        self.loop = loop
        return self

class AnimationSet:
    def __init__(self, imagemanager, info):
        self.im = imagemanager
        self.info = info
        self.animations = {}
        for line in info:
            split0 = line.split(":")
            name = split0[0]
            split1 = split0[1].replace(" ", "").split(";")
            images = []
            frametimes = []
            for i in range(len(split1)):
                frame = split1[i].split(",")
                images.append([frame[0], int(frame[1])])
                frametimes.append(int(frame[2]))
            self.animations[name] = Animation(imagemanager, images, frametimes)
        self.cur = None

    def copy(self):
        return AnimationSet(self.im, self.info)

    def play(self, name = None):
        if name != None:
            self.cur = self.animations[name]
        self.cur.setLoop(False)
        self.cur.start()
        return self

    def loop(self, name = None):
        should_start = False
        if name != None:
            if self.cur != self.animations[name]:
                should_start = True
            self.cur = self.animations[name]
        self.cur.setLoop(True)
        if should_start:
            self.cur.start()
        return self

    def restart(self, name = None):
        if name != None:
            self.cur = self.animations[name]
        self.cur.restart()
        return self

    def pause(self, name = None):
        if name != None:
            self.cur = self.animations[name]
        return self

    def get(self):
        if self.cur != None:
            return self.cur.get()
        return None
