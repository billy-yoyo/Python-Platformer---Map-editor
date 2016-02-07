import pygame, math, json, game_main
pygame.init()

#fits text in to the given bounds.
#fontname, bold, italic detail the font to be used
#centre_x, centre_y determine if the text should be centered along the x and y axis respectively
def fitLabel(text, colour, bounds, fontname, bold = False, italic = False, centre_x = True, centre_y = True):
    fontsize = 5
    font = pygame.font.SysFont(fontname, fontsize, bold, italic)
    size = font.size(text)
    while size[0] < bounds[2] and size[1] < bounds[3]:
        fontsize += 1
        font = pygame.font.SysFont(fontname, fontsize, bold, italic)
        size = font.size(text)
    fontsize = fontsize - 1
    font = pygame.font.SysFont(fontname, fontsize, bold, italic)
    size = font.size(text)
    offset = [ bounds[0], bounds[1] ]
    if centre_x:
        offset[0] += math.floor((bounds[2] - size[0]) / 2)
    if centre_y:
        offset[1] += math.floor((bounds[3] - size[1]) / 2)
    return [font.render(text, 2, colour), offset]

#level selector world, contains a list of levels 
class WorldLS:
    def __init__(self, main, name, levels):
        self.name = name
        self.levels = levels
        self.levelbox = main.createLevelBox(levels)

        self.card = None
        self.selected = False

    #gets the card for the world, if no card exists uses createCard() to create one then returns it
    def getCard(self, template):
        if self.card == None:
            self.createCard(template)
        card = self.card
        if self.selected:
            card = card.copy()
            pygame.draw.circle(card, [0,0,0], [45, 45], 45, 0)
            card.blit(self.card, [0,0])
        return card

    #creates a card for the world (renders the world information on to the template)
    def createCard(self, template):
        self.card = pygame.Surface((template.get_width()+10, template.get_height()+10)).convert_alpha()
        self.card.fill([0,0,0,0])
        self.card.blit(template, [5, 5])
        name_bounds = [7, 37, 76, 16]
        self.card.blit(*fitLabel(self.name, [0, 0, 0], name_bounds, "impact"))

#level selector level, contains information about a level (your best time and where to find the level)
class LevelLS:
    #name is the name of the level
    #mapfile is where the level's file can be found
    #grade_boundaries detailes the time required for different grades
    #record is the best time the player has achieved on that level
    def __init__(self, name, mapfile, grade_boundaries, record):
        self.name = name
        self.gb = grade_boundaries
        self.record = record
        self.mapfile = mapfile

        self.grade = None
        if record != None:
            for i in range(min(5, len(self.gb))):
                if record < self.gb[i]:
                    self.grade = i
                    break
            if self.grade == None:
                self.grade = len(self.gb)

        self.card = None

    #gets the players grade on that level (uses grade_bounadries and record)
    def getGrade(self):
        if self.grade != None:
            grades = "SABCDF"
            if len(self.gb) == 4:
                grades = "SABCF"
            elif len(self.gb) == 3:
                grades = "SABC"
            elif len(self.gb) == 2:
                grades == "SAF"
            elif len(self.gb) == 1:
                grades == "SA"
            elif len(self.gb) == 0:
                grades = "A"
            return grades[max(0, min(5, self.grade))]
        return "-"

    #gets the string version of the record (from milliseconds in to minutes:seconds:milliseconds format)
    def getRecordText(self):
        if self.record != None:
            seconds = math.floor(self.record / 1000)
            minutes = math.floor(seconds / 60)
            seconds = seconds - (minutes * 60)
            milliseconds = self.record - (seconds * 1000)
            strseconds = str(seconds)
            strminutes = str(minutes)
            strmilsec = str(milliseconds)
            if len(strseconds) < 2:
                strseconds = "0" + strseconds
            if len(strminutes) < 2:
                strminutes = "0" + strminutes
            if len(strmilsec) < 2:
                strmilsec = "00" + strmilsec
            if len(strmilsec) < 3:
                strmilsec = "0" + strmilsec
            if len(strmilsec) > 3:
                strmilsec = strmilsec[:3]
            return strminutes + ":" + strseconds + ":" + strmilsec
        return "??:??:??"

    #gets the card for the level (see WorldLS.getCard())
    def getCard(self, template):
        if self.card == None:
            self.createLevelCard(template)
        return self.card

    #creates the card for the level (see WorldLS.createCard())
    def createLevelCard(self, template):
        self.card = template.copy()
        levelname_box = [3, 3, 114, 31]
        record_box = [3, 37, 84, 30]
        grade_box = [93, 37, 27, 30]

        self.card.blit(*fitLabel(self.name, [0,0,0], levelname_box, "impact"))
        self.card.blit(*fitLabel(self.getRecordText(), [0,0,0], record_box, "tahoma"))
        self.card.blit(*fitLabel(self.getGrade(), [0,0,0], grade_box, "impact", False, True))

#interface box containing all the level cards for the selected world
class LevelBox:
    #main is the MainBox, x, y are the coordinates of the interface box,
    #levels is the list of levels to get the level cards from, columns is the amount of columns
    #to render, see WorldLS.createCard() for an explanation of templates
    def __init__(self, main, x, y, levels, columns, level_template):
        self.x = x
        self.y = y
        self.main = main
        self.levels = levels
        self.columns = columns
        self.rows = math.floor(len(levels) / columns) + 1
        self.width = ( 120 * self.columns ) + ( 10 * (self.columns ) )
        self.height = ( 70 * self.rows ) + ( 10 * (self.rows) )
        
        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.level_template = level_template
        self.offset = 0
        
        self.render()

    #renders all the cards on to an image
    def render(self):
        self.image.fill([0,0,0,0])
        for i in range(len(self.levels)):
            level = self.levels[i]
            y = math.floor(i / self.columns)
            x = i - (y * self.columns)

            rx, ry = x * 130, y * 80
            card = level.getCard(self.level_template)
            self.image.blit(card, [rx, ry])
        return self.image

    #finds which card is selected
    def getSelectedCard(self, x, y):
        x = x - self.x
        y = y - self.y
        y = y + self.offset
        column = math.floor(x / 130)
        if x < (column+1) * 120:
            row = math.floor(y / 80)
            if y < (row+1) * 70:
                i = (row * self.columns) + column
                if i >= 0 and i < len(self.levels):
                    level = self.levels[i]
                    return level
        return None

    #checks if x,y collides with the interface box
    def check(self, x, y):
        if x >= self.x and y >= self.y and x < self.x + self.width and y < self.y + self.height:
            return True
        return False

    #checks for a card selection
    def left_click(self, event, down):
        if down == False:
            level = self.getSelectedCard(event.x, event.y)
            if level != None:
                self.main.playLevel(level)

    def right_click(self, event, down):
        return

    #scrolls up
    def scroll_up(self, event):
        if self.check(event.x, event.y):
            self.offset = max(0, min(self.height, self.offset - 5))

    #scrolls down
    def scroll_down(self, event):
        if self.check(event.x, event.y):
            self.offset = max(0, min(self.height, self.offset + 5))

    def draw(self, target, height):
        self.render()
        target.blit(self.image, [self.x, self.y], [0, self.offset, self.width, height])

#interface box containing all the world cards
class WorldBox:
    #main is the MainBox, x,y are the coordinates of the interface box,
    #worlds is the list of worlds to get the cards from, see WorldLS.createCard() for an explanation of templates
    def __init__(self, main, x, y, worlds, world_template):
        self.main = main
        self.x = x
        self.y = y
        self.width = (len(worlds) * 80) + ( (len(worlds)) * 10)
        self.height = 100
        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        
        self.offset = 0
        self.worlds = worlds
        self.world_template = world_template
        self.render()

    #adds a world to the list of worlds
    def addWorld(self, world):
        self.worlds.append(world)
        self.width = (len(worlds) * 80) + ( (len(worlds)-1) * 10)
        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.render()

    #renders the cards on to an image
    def render(self):
        self.image = pygame.Surface((self.width, self.height)).convert_alpha()
        self.image.fill([0,0,0,0])
        for i in range(len(self.worlds)):
            world = self.worlds[i]
            card = world.getCard(self.world_template)
            rx, ry = i * 80, 0
            if i > 0:
                rx = rx + (i * 10)
            self.image.blit(card, [rx, ry])
        return self.image

    #checks for collisions between x,y and the interface box
    def check(self, x, y):
        if x >= self.x and y >= self.y and x < self.x + self.width and y < self.y + self.height:
            return True
        return False

    #tries to find the selected card
    def getSelectedCard(self, x, y):
        x = x - self.x
        y = y - self.y
        x = x + self.offset
        i = math.floor(x / 90)
        if x < (i+1) * 80 and i < len(self.worlds) and i >= 0:
            return self.worlds[i]

    def left_click(self, event, down):
        if down == False:
            world = self.getSelectedCard(event.x, event.y)
            if world != None:
                self.main.selectWorld(world)

    def right_click(self, event, down):
        return

    def scroll_up(self, event):
        if self.check(event.x, event.y):
            self.offset = max(0, min(self.height, self.offset + 5))

    def scroll_down(self, event):
        if self.check(event.x, event.y):
            self.offset = max(0, min(self.height, self.offset - 5))


    def draw(self, target, width):
        self.render()
        target.blit(self.image, [self.x, self.y], [self.offset, 0, width, self.height])

#interface box containing the whole interface
class MainBox:
    def __init__(self):
        self.screen = pygame.display.set_mode((400, 700))
        
        self.lastworlddatafile = None
        self.lastsavefile = None
        
        self.worldbox = None
        self.selected = None
        self.clevelbox = None

        self.level_template = pygame.image.load("res/imgs/level_card.png")
        self.world_template = pygame.image.load("res/imgs/world_label.png")

    #changes which world is currently selected
    def selectWorld(self, world):
        if self.selected != None:
            self.selected.selected = False
        world.selected = True
        self.selected = world
        self.clevelbox = world.levelbox

    #reloads the level selector
    def reload(self):
        self.load(self.lastworlddatafile, self.lastsavefile)
        self.screen = pygame.display.set_mode((400, 700))

    #plays the level (game_main.run())
    def playLevel(self, level):
        game_main.run(level.mapfile, level.name, self.selected.name)
        self.reload()

    #creates a level box for the list of levels
    def createLevelBox(self, levels):
        return LevelBox(self, 10, 110, levels, 3, self.level_template)

    def left_click(self, event, down):
        if self.worldbox != None:
            self.worldbox.left_click(event, down)
        if self.clevelbox != None:
            self.clevelbox.left_click(event, down)

    def right_click(self, event, down):
        if self.worldbox != None:
            self.worldbox.right_click(event, down)
        if self.clevelbox != None:
            self.clevelbox.right_click(event, down)

    def scroll_up(self, event):
        if self.worldbox != None:
            self.worldbox.scroll_up(event)
        if self.clevelbox != None:
            self.clevelbox.scroll_up(event)

    def scroll_down(self, event):
        if self.worldbox != None:
            self.worldbox.scroll_down(event)
        if self.clevelbox != None:
            self.clevelbox.scroll_down(event)

    def draw(self):
        if self.worldbox != None:
            self.worldbox.draw(self.screen, self.screen.get_width() - 20)
        if self.clevelbox != None:
            self.clevelbox.draw(self.screen, self.screen.get_height() - 110)

    #loads the level selection information (records, level information and world information)
    def load(self, worlddatafile, savefile = None):
        self.lastworlddatafile = worlddatafile
        self.lastsavefile = savefile
        worlddata = json.load(open(worlddatafile))
        save = {}
        if savefile != None:
            save = json.load(open(savefile))

        worldorder = None
        worlds = []
        for worldname in worlddata.keys():
            if worldname == "WORLD_ORDER":
                worldorder = worlddata[worldname]
            else:
                levels = []
                leveldata = worlddata[worldname]
                levelorder = None
                for levelname in leveldata.keys():
                    if levelname == "LEVEL_ORDER":
                        levelorder = leveldata[levelname]
                    else:
                        info = leveldata[levelname]
                        mapname = info[0]
                        gbraw = info[1].split(",")
                        gb = []
                        for i in range(len(gbraw)):
                            gb.append(int(gbraw[i]))

                        recordname = worldname + ":::" + levelname
                        record = None
                        if recordname in save.keys():
                            record = int(save[recordname])
                        level = LevelLS(levelname, mapname, gb, record)
                        levels.append(level)
                if levelorder != None:
                    nlevels = list(levels)
                    for i in range(len(levelorder)):
                        levelname = levelorder[i]
                        for level in levels:
                            if level.name == levelname:
                                nlevels[i] = level
                                break
                    levels = nlevels
                worlds.append(WorldLS(self, worldname, levels))

        if worldorder != None:
            nworlds = list(worlds)
            for i in range(len(worldorder)):
                worldname = worldorder[i]
                for world in worlds:
                    if world.name == worldname:
                        nworlds[i] = world
                        break
            worlds = nworlds
        self.worldbox = WorldBox(self, 10, 10, worlds, self.world_template)
        self.selectWorld(self.worldbox.worlds[0])

def run():
    main = MainBox()
    main.screen.fill([255,255,255])
    
    main.load("res/levels/leveldat.json", "res/levels/save.jsv")


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                event.x = event.pos[0]
                event.y = event.pos[1]
                if event.button == 1:
                    main.left_click(event, True)
                elif event.button == 3:
                    main.right_click(event, True)
                elif event.button == 4:
                    main.scroll_up(event)
                elif event.button == 5:
                    main.scroll_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                event.x = event.pos[0]
                event.y = event.pos[1]
                if event.button == 1:
                    main.left_click(event, False)
                elif event.button == 3:
                    main.right_click(event, False)
                elif event.button == 4:
                    main.scroll_up(event)
                elif event.button == 5:
                    main.scroll_down(event)
        main.screen.fill([255,255,255])
        main.draw()
        pygame.display.flip()
