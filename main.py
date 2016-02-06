import pygame, sys, level_selector, editor_main, math
pygame.init()

def draw():
    screen = pygame.display.set_mode((background.get_width(), background.get_height()))
    screen.blit(background, [0,0])
    pygame.display.flip()

background = pygame.image.load("res/imgs/start_menu.png")
draw()

block_size = math.floor(background.get_height()/3)
main_running = True
while main_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            main_running = False
            sys.exit()
            break
        elif event.type == pygame.MOUSEBUTTONUP:
            mpos = pygame.mouse.get_pos()
            button = math.floor(mpos[1] / block_size)
            print(button)
            if button == 0: #play game
                level_selector.run()
                draw()
            elif button == 1: #level editor
                editor_main.run()
                draw()
            
