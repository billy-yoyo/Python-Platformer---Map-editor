import math

#container for collision objects
#
#Uses a system of chunks to speed up collision detection,
#blocks will be placed in the chunks they intersect, when checking
#for collisions they will only be checked against blocks in the same chunks
#as them.
class World:
    #chunkwidth and chunkheight determine how large the chunk size is
    #these should be larger than your largest object.
    def __init__(self, chunkwidth, chunkheight):
        self.chunks = {}
        self.cid = 0
        self.chunk_width = chunkwidth
        self.chunk_height = chunkheight
        self.blocks = {}
        self.max_priority = 0

    #adds a block to the world
    def addBlock(self, block):
        pri = block.get_priority()
        if not pri in self.blocks.keys():
            self.blocks[pri] = []
            if pri > self.max_priority:
                self.max_priority = pri
        if not block in self.blocks[pri]:
            self.blocks[pri].append(block)

    #removes a block from the world
    def removeBlock(self, block):
        pri = block.get_priority()
        if pri in self.blocks.keys():
            if block in self.blocks[pri]:
                self.blocks[pri].remove(block)

    #resets the world, clearing all blocks
    def reset(self):
        self.cid = 0
        for chunklist in self.chunks.values():
            for chunk in chunklist.values():
                del chunk
        del self.chunks
        del self.blocks
        self.chunks = {}
        self.blocks = {}

    #creates a chunk (x, y represent chunk coordinates, not real coordinates)
    def createChunk(self, x, y):
        if not x in self.chunks.keys():
            self.chunks[x] = {}
        chunk = Chunk(self, x, y)
        self.chunks[x][y] = chunk
        return chunk

    #gets a chunk (x, y represent chunk coordinates)
    def getChunk(self, x, y):
        if x in self.chunks.keys():
            if y in self.chunks[x].keys():
                return self.chunks[x][y]
            else:
                return self.createChunk(x, y)
        else:
            return self.createChunk(x, y)

    #creates a block, generally unused as block is mainly designed to be overriden.
    def createBlock(self, x, y, width, height):
        block = Block(self, x, y, width, height, self.nextID())
        block.updateChunks()
        return block

    #gets the next id for a block.
    def nextID(self):
        self.cid+=1
        return self.cid

    #uses "checkAndReturnArea" and checks if any blocks fulfilling the criteria were found, true is they were found.
    #the only difference in parametres is find_all is always set to false, so it will just stop after the first block is found
    def checkArea(self, x, y, width, height, ignorelist = [], strict = True, typelist = None, ignoresolid = False, ignoretype = []):
        return len(self.checkAndReturnArea(x, y, width, height, ignorelist, strict, typelist, ignoresolid, False, ignoretype)) > 0

    #checks the given area for blocks of the given criteria.
    #       x, y, width, height details the area to search in
    #       ignorelist is the list of specific blocks to ignore
    #       strict is whether or not you use strict inequalities in the collision detection
    #       typelist is the whitelist for block types (only types in typelist will be checked), if it is none all block types are checked
    #       ignoresolid determines if the collision detection should ignore whether or not blocks are solid or now
    #       find_all determines if it should find all blocks that fulfill the criteria within the area or just stop after the first one
    #       ignoretype is a blacklist for block types (types in ignoretype won't be checked)
    def checkAndReturnArea(self, x, y, width, height, ignorelist = [], strict = True, typelist = None, ignoresolid = False, find_all = False, ignoretype = []):
        temp_block = Block(self, x, y, width, height, -1)
        temp_block.updateChunks()
        ignorelist.append(temp_block)
        result = []
        for chunk in temp_block.chunks:
            for block in chunk.blocks.values():
                if typelist == None or block.get_type() in typelist:
                    if not block in ignorelist and not block.get_type() in ignoretype:
                        if temp_block.collide_check(block, strict, ignoresolid):
                            result.append(block)
                            if not find_all:
                                break
                #elif typelist != None:
                #    print(str(block.get_type()))
            if len(result) > 0 and not find_all:
                break
        temp_block.destroy()
        return result

#contains blocks, explanation of what chunks do can be found above the World class
class Chunk:
    #world is the world it belongs to
    #x, y are its chunk coordinates (not real coordinates)
    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.blocks = {}

    #remove a block from the chunk
    def remove(self, block):
        if block.blockid in self.blocks.keys():
            del self.blocks[block.blockid]

    #add a block to the chunk
    def add(self, block):
        self.blocks[block.blockid] = block
        if not block in self.world.blocks:
            self.world.addBlock(block)

#the block class is the base collision-object class
#is not really intended for direct use but rather to be overidden.
class Block:
    #world is the world the block belongs to
    #x, y, width, height are the dimensions of the blocks hitbox
    #blockid is the id of the block within the world (see world.nextID())
    def __init__(self, world, x, y, width, height, blockid):
        self.world = world
        self.raw_x = x
        self.raw_y = y
        self.width = width
        self.height = height
        self.blockid = blockid
        self.solid = True
        self.collision_priority = False                   

        self.chunks = []

    @property
    def x(self):
        return self.raw_x

    @property
    def y(self):
        return self.raw_y

    @x.setter
    def x(self, new_x):
        self.raw_x = new_x

    @y.setter
    def y(self, new_y):
        self.raw_y = new_y

    #the priority of the block, determines the order in which things are drawn/updated
    #lower values will be drawn and updated first (so will be underneath higher values)
    def get_priority(self):
        return 0

    #the block type
    def get_type(self):
        return "block"

    #returns the blocks that share chunks with this block
    def get_blocks(self):
        col_blocks = []
        for chunk in self.chunks:
            col_blocks = list(chunk.blocks.values()) + col_blocks
        while self in col_blocks:
            col_blocks.remove(self)
        return col_blocks

    #destroys the block, removing it from all its chunks and the world
    def destroy(self):
        for chunk in self.chunks:
            chunk.remove(self)
        self.world.removeBlock(self)

    #checks if the block is colliding with anything,
    #   strict determines if strict-inequalities should be used in the collision detection
    #   ignoresolid determines if the collision detection should ignore whether or not blocks are solid
    def colliding(self, strict = True, ignoresolid = False):
        col_blocks = self.get_blocks()

        for block in col_blocks:
            if self.collide_check(block, strict, ignoresolid):
                return True
        return False

    #checks for a collision between this block and the other block. strict and ignoresolid mean the same thing as in colliding().
    def collide_check(self, block, strict = True, ignoresolid = False):
        if strict:
            if ignoresolid:
                return self.collides_ignoresolid(block)
            else:
                return self.collides(block)
                
        else:
            if ignoresolid:
                return self.nonstrict_collides_ignoresolid(block)
            else:
                return self.nonstrict_collides(block)

    #checks if this block is colliding with 'block', (strict = True, ignoresolid = False) [note I realise I messed up with which are strict and nonstrict inequalities]
    def collides(self, block):
        if block.solid:
            if block.collision_priority and not self.collision_priority:
                return block.collides(self)
            else:
                return not (block.x >= self.x + self.width or block.x + block.width <= self.x or block.y >= self.y + self.height or block.y + block.height <= self.y)
            return False

    #checks if this block is colliding with 'block', (strict = False, ignoresolid = False)
    def nonstrict_collides(self, block):
        if block.solid:
            if block.collision_priority and not self.collision_priority:
                return block.nonstrict_collides(self)
            else:
                return not (block.x > self.x + self.width or block.x + block.width < self.x or block.y > self.y + self.height or block.y + block.height < self.y)
            return False

    #checks if this block is colliding with 'block', (strict = True, ignoresolid = True)
    def collides_ignoresolid(self, block):
        if block.collision_priority and not self.collision_priority:
            return block.collides_ignoresolid(self)
        else:
            return not (block.x >= self.x + self.width or block.x + block.width <= self.x or block.y >= self.y + self.height or block.y + block.height <= self.y)

    #checks if this block is colliding with 'block', (strict = False, ignoresolid = True)
    def nonstrict_collides_ignoresolid(self, block):
        if block.collision_priority and not self.collision_priority:
            return block.nonstrict_collides_ignoresolid(self)
        else:
            return not (block.x > self.x + self.width or block.x + block.width < self.x or block.y > self.y + self.height or block.y + block.height < self.y)

    #updates the chunks the block is inside.
    #should be called upon the creation of the block (it adds it in to the world) and every time the block moves.
    def updateChunks(self):
        oldchunks = list(self.chunks)
        cx0, cy0 = math.floor(self.x/self.world.chunk_width), math.floor(self.y/self.world.chunk_height)
        cx1, cy1 = math.floor((self.x+self.width)/self.world.chunk_width), math.floor((self.y+self.height)/self.world.chunk_height)
        
        self.chunks = []
        for cx in range(min(cx0, cx1), max(cx0, cx1)+1):
            for cy in range(min(cy0, cy1), max(cy0, cy1)+1):
                self.chunks.append(self.world.getChunk(cx, cy))
        #if cx0 == cx1 and cy0 == cy1:
        #    self.chunks = [self.world.getChunk(cx0, cy0)]
        #elif cx0 != cx1 and cy0 == cy1:
        #    self.chunks = [self.world.getChunk(cx0, cy0), self.world.getChunk(cx1, cy0)]
        #elif cx0 == cx1 and cy0 != cy1:
        #    self.chunks = [self.world.getChunk(cx0, cy0), self.world.getChunk(cx0, cy1)]
        #else:
        #    self.chunks = [self.world.getChunk(cx0, cy0), self.world.getChunk(cx1, cy0), self.world.getChunk(cx0, cy1), self.world.getChunk(cx1, cy1)]

        for chunk in oldchunks:
            if not chunk in self.chunks:
                chunk.remove(self)
        for chunk in self.chunks:
            if not chunk in oldchunks:
                chunk.add(self)

    #decides whether to use safe_move or move.
    def clever_move(self, dx, dy, ignore_solid = False, strict = True, move_back = True, ignore_list = []):
        if math.fabs(dx) > self.width or math.fabs(dy) > self.height:
            return self.safe_move(dx, dy, ignore_solid, strict, move_back, ignore_list)
        else:
            return self.move(dx, dy, ignore_solid, strict, move_back, ignore_list)

    #move function for when the block is moving quickly,
    #checks for multiple collisions along the line of trajectory, can still miss collisions but is less likely to.
    def safe_move(self, dx, dy, ignore_solid = False, strict = True, move_back = True, ignore_list = []):
        x_moving = True
        y_moving = True
        while (math.fabs(dx) > self.width or math.fabs(dy) > self.height) and (x_moving or y_moving):
            cdx = 0
            if dx > self.width and dx > 0:
                dx = dx - self.width
                cdx = self.width
            elif dx < self.width and dx < 0:
                dx = dx + self.width
                cdx = -self.width

            cdy = 0
            if dy > self.height and dy > 0:
                dy = dy - self.height
                cdy = self.height
            elif dy < self.height and dy < 0:
                dy = dy + self.height
                cdy = -self.height
                
            results = self.move(cdx, cdy, ignore_solid, strict, move_back, ignore_list)
            if not results[0]:
                if move_back:
                    dx = 0
                x_moving = False
            if not results[1]:
                if move_back:
                    dy = 0
                y_moving = False
                
        if dx != 0 or dy != 0:
            results = self.move(dx, dy, ignore_solid, strict, move_back, ignore_list)
            if not results[0]:
                x_moving = False
            if not results[1]:
                y_moving = False
        return [x_moving, y_moving]

    #simply collision detection, moves the block by dx and dy, checks for collisions then resolves any issues (moves to the appropriate location)
    #uses a simply detection system of first moving along the x, resolving issues, then moving along the y, then resolving issues again.
    def move(self, dx, dy, ignore_solid = False, strict = True, move_back = True, ignore_list = []):
        col_blocks = self.get_blocks()

        results = [True, True]
        if dx != 0:
            self.x = self.x + dx
            for block in col_blocks:
                if not block.get_type() in ignore_list:
                    if self.collide_check(block, strict, ignore_solid):
                        if move_back:
                            if dx > 0:
                                self.x = block.x - self.width
                            else:
                                self.x = block.x + block.width
                        results[0] = False
                #else:
                #    print(block.get_type())
        if dy != 0:
            self.y = self.y + dy
            for block in col_blocks:
                if not block.get_type() in ignore_list:
                    if self.collide_check(block, strict, ignore_solid):
                        if move_back:
                            if dy > 0:
                                self.y = block.y - self.height
                            else:
                                self.y = block.y + block.height
                        results[1] = False
                #else:
                #    print(block.get_type())
        self.updateChunks()
        return results

    #simply moves the block and doesn't bother doing collision checks
    def simple_move(self, dx, dy):
        self.y = self.y + dy
        self.x = self.x + dx
        self.updateChunks()

    #updates the block, elapsed is the ticks since the last frame
    def update(self, elapsed):
        return

    #draws the block, target is the surface to draw on, offset is the screen offset
    def draw(self, target, offset):
        return

#base collision block for circular collision
#almost functionally identical to the Block class except for the init function and
#it uses a circular hitbox. Supports collision detection between normal Block classes.
class CircleBlock(Block):
    #world is the world the block is in
    #x, y is the centre of the block
    #radius is the radius of the blocks hitbox
    #blockid is the block's id (see world.nextID())
    def __init__(self, world, x, y, radius, blockid):
        Block.__init__(self, world, x - radius, y - radius, radius * 2, radius * 2, blockid)
        self.raw_centre_x = x
        self.raw_centre_y = y
        self.raw_radius = radius
        self.radsqr = self.raw_radius * self.raw_radius

        self.collision_priority = True

    @property
    def centre_x(self):
        return self.raw_centre_x

    @property
    def centre_y(self):
        return self.raw_centre_y

    @property
    def radius(self):
        return self.raw_radius

    @property
    def x(self):
        return self.raw_x

    @property
    def y(self):
        return self.raw_y

    @radius.setter
    def radius(self, new_radius):
        self.raw_radius = new_radius
        self.radsqr = self.raw_radius * self.raw_radius

    @centre_x.setter
    def centre_x(self, new_centre_x):
        self.raw_centre_x = new_centre_x
        self.raw_x = self.raw_centre_x - self.radius

    @centre_y.setter
    def centre_y(self, new_centre_y):
        self.raw_centre_y = new_centre_y
        self.raw_y = self.raw_centre_y - self.radius

    @x.setter
    def x(self, new_x):
        self.raw_x = new_x
        self.raw_centre_x = self.raw_x + self.radius

    @y.setter
    def y(self, new_y):
        self.raw_y = new_y
        self.raw_centre_y = self.raw_y + self.radius

    def collides(self, block):
        if block.solid:
            closeX = max(block.x, min(block.x + self.width, self.centre_x))
            closeY = max(block.y, min(block.y + self.height, self.centre_y))

            diffX = self.centre_x - closeX
            diffY = self.centre_y - closeY

            dist = (diffX*diffX) + (diffY*diffY)
            return dist <= self.radsqr
        return False

    def nonstrict_collides(self, block):
        if block.solid:
            closeX = max(block.x, min(block.x + self.width, self.centre_x))
            closeY = max(block.y, min(block.y + self.height, self.centre_y))

            diffX = self.centre_x - closeX
            diffY = self.centre_y - closeY

            dist = (diffX*diffX) + (diffY*diffY)
            return dist < self.radsqr
        return False

    def collides_ignoresolid(self, block):
        closeX = max(block.x, min(block.x + self.width, self.centre_x))
        closeY = max(block.y, min(block.y + self.height, self.centre_y))

        diffX = self.centre_x - closeX
        diffY = self.centre_y - closeY

        dist = (diffX*diffX) + (diffY*diffY)
        return dist <= self.radsqr

    def nonstrict_collides_ignoresolid(self, block):
        closeX = max(block.x, min(block.x + self.width, self.centre_x))
        closeY = max(block.y, min(block.y + self.height, self.centre_y))

        diffX = self.centre_x - closeX
        diffY = self.centre_y - closeY

        dist = (diffX*diffX) + (diffY*diffY)
        return dist < self.radsqr

#gets the argument for the vector (x y) in degrees
def getDegArg(x, y):
    if x == 0:
        if y == 0: return 0
        if y < 0: return 270
        if y > 0: return 90
    if y == 0:
        if x < 0: return 180
        if x > 0: return 0
    a = math.degrees(math.atan(math.fabs(y)/math.fabs(x)))
    if y > 0 and x > 0:
        return a
    if y > 0 and x < 0:
        return 180 - a
    if y < 0 and x < 0:
        return 180 + a
    if y < 0 and x > 0:
        return 360 - a
    return 0

#gets the argument for the vector (x y) in radians
def getArg(x, y):
    return math.radians(getDegArg(x, y))

#vector class
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.arg = None
        self.mod = None

    #returns the argument of the vector (see getArg()) in radians
    def getArg(self):
        if self.arg == None:
            self.arg = getArg(self.x, self.y)
        return self.arg

    #returns the modulus of the vector
    def getMod(self):
        if self.mod == None:
            self.mod = math.sqrt( (self.x*self.x) + (self.y*self.y) )
        return self.mod

    #returns the x value of the vector
    def getX(self):
        return self.x

    #returns the y value of the vector
    def getY(self):
        return self.y

    #sets the argument of the vector (and changes x,y accordingly)
    def setArg(self, arg):
        if self.mod == None:
            self.mod = math.sqrt( (self.x*self.x) + (self.y*self.y) )
        self.arg = arg
        self.x = self.mod*math.cos(self.arg)
        self.y = self.mod*math.sin(self.arg)
        return self

    #sets the modulus of the vector (and changes x,y accordingly)
    def setMod(self, mod):
        if self.arg == None:
            self.arg = getArg(self.x, self.y)
        self.mod = mod
        self.x = self.mod*math.cos(self.arg)
        self.y = self.mod*math.sin(self.arg)
        return self

    #sets both x and y at the same time
    def setXY(self, x, y):
        self.x, self.y = x, y
        self.arg = getArg(self.x, self.y)
        self.mod = math.sqrt( (self.x*self.x) + (self.y*self.y) )
        return self

    #sets the x value
    def setX(self, x):
        return self.setXY(x, self.y)

    #sets the y value
    def setY(self, y):
        return self.setXY(self.x, y)

    #adds x, y to the vector (returns a new vector)
    def add(self, x, y):
        return Vector(self.x+x, self.y+y)

    #adds x to the x value of the vector (returns a new vector)
    def addX(self, x):
        return Vector(self.x+x, self.y)

    #adds y to the y value of the vector (returns a new vector)
    def addY(self, y):
        return Vector(self.x, self.y+y)

    #adds two vectors together (returns a new vector)
    def addVec(self, vector):
        return Vector(vector.getX()+self.x, vector.getY()+self.y)

    #multiplies the vector by a scalar (returns a new vector)
    def mult(self, a):
        return Vector(self.x*a, self.y*a)

    #creates a copy of the vector
    def copy(self):
        return Vector(self.x, self.y)

    #returns the negative of the vector
    def negative(self):
        return Vector(-self.x, -self.y)

    #returns the vector in integer space
    def intVector(self):
        return Vector(int(self.x), int(self.y))

    #does the same as mult (don't know why I did this)
    def getOffset(self, time):
        return Vector(self.x*time, self.y*time)

    #pointless and disfunctional, not removing because I don't know what it's meant to do
    def getRawAngle(self):
        self.getArg()
        if self.arg > 270:
            return 360 - self.arg
        elif self.arg > 180:
            return self.arg - 180
        elif self.arg > 90:
            return 180 - self.arg
        return self.arg

    #treats the vector as the gradient of a line, returns coordinates of the line at x
    def getVectorAtX(self, x):
        self.getArg()
        if self.arg == math.pi / 2 or self.arg == 3 * (math.pi / 2):
            return None #giving an xcoord when x = 0 :/
        elif self.arg == 0 or self.arg == math.pi:
            return Vector(x, 0)
        else:
            y = math.tan(self.arg) * x
            return Vector(x, y)

    #treats the vector as the gradient of a line, returns the coordinates of the line at y
    def getVectorAtY(self, y):
        self.getArg()
        if self.arg == math.pi / 2 or self.arg == 3 * (math.pi / 2):
            return Vector(0, y)
        elif self.arg == 0 or self.arg == math.pi:
            return None #giving a ycoord when y = 0 :/
        else:
            x = y / math.tan(self.arg)
            return Vector(x, y)

    #clamps the vector using another vector
    def capVector(self, vector):
        return Vector(min(vector.x, max(-vector.x, self.x)), min(vector.y, max(-vector.y, self.y)))

    #returns the string version of the vector.
    def __str__(self):
        return str(self.x) + ", " + str(self.y)
