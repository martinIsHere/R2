# Example file showing a basic pygame "game loop"
import pygame
from blur_function import INVALID, get_element, blur_equal_size

# pygame setup
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

pixel_array=[(0,0,0)]
row_len = 80
col_len = 80
for i in range(0, row_len*col_len-1):
    color = ((255+25*i)%255, (200+i)%255, (100+50*i)%255)
    pixel_array.append(color)

def draw_pixel_array(pixel_array, row_len, col_len):
    rectangle_width=SCREEN_WIDTH/row_len
    rectangle_height=SCREEN_HEIGHT/col_len
    for j in range(0, col_len):
        for i in range(0, row_len):
            colorTuple=get_element(i, j, pixel_array, row_len, col_len)
            color=pygame.Color(colorTuple[0], colorTuple[1], colorTuple[2])
            pygame.draw.rect(screen, color, pygame.Rect(i*rectangle_width, j*rectangle_height, rectangle_width, rectangle_height))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                mx,my=pygame.mouse.get_pos()
                pixel_array[int(mx/SCREEN_WIDTH*row_len)+col_len*int(my/SCREEN_HEIGHT*col_len)] = (255,0,0)

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(pygame.Color(0,0,0))

    # RENDER YOUR GAME HERE
    draw_pixel_array(pixel_array, row_len, col_len)
    pixel_array=blur_equal_size(pixel_array, row_len, col_len, 1)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
