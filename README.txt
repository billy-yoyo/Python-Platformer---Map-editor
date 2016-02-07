
Simply platformer I made in pygame, created  with Python 3.3 and pygame 1.9.2, 
an installer for pygame can be found at https://bitbucket.org/pygame/pygame/downloads
an installer for Python can be found at https://www.python.org/download/releases/3.3.5/

once you've installed those, download my code, extract it somewhere and run "main.py" to play the game.

Controls for the game are wasd/arrow keys for movement (up is jump), q for toggling the walls, r for restarting the level (killing you). 
Pressing tab in the level editor will let you test your map. If you're unsure what something does in the level editor, there are tooltips to help you out. 
If you're still confused about any of it feel free to ask me. Thanks!

Here are some pictures of the game:
http://imgur.com/a/cW3GN
in order they are the level selection, the game, the level editor and the main menu
(the settings button currently doesn't do anything)

some information of what the files do:
  - main.py is the entry point and is a simply main menu which launches the other parts (editor_main.py and level_selector.py)
  - editor_main.py is the level editor in its entirety, it is messy and largely undocumented, testing the map will launch game_main.py
  - level_selector.py is the level selection ui, this will launch game_main.py to run the game
  - game_main.py loads the game's resources and contains the main loop for the game main block of the game is in pylevel.py
  - pylevel.py details the different entity and blocks that compose the real game, uses pyani.py and pcol.py
  - pycol.py is the collision 'engine' behind the game, fairly lightweight.
  - pyani.py deals with animations, again fairly lightweight.

resources and what they do:
  -  res/imgs/ contains all the images for the game/editor, also contains tiledat.res which details which images to load into the editor
  -  res/levels/ contains information about levels, leveldat.json details the different worlds and which levels they contain. 
     save.jsv contains your best times on the different levels, .tmd files are the actual levels. All of this is in JSON.