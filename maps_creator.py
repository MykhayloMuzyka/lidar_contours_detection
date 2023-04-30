import pygame
from pygame.locals import *
import pickle
import os
import re
from room import Room
from configs import *

# width, height = 1200, 600
# fps = 30
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
contours, contour = list(), list()
initial_position = None
defining_initial_position = False
font_start = pygame.font.SysFont('Arial', 20, bold=True)

while True:
    screen.fill((255, 255, 255))

    for c in contours:
        if len(c) > 1:
            for i in range(len(c[:-1])):
                x1, y1 = c[i]
                x2, y2 = c[i + 1]
                pygame.draw.line(screen, (0, 0, 0), (x1, y1), (x2, y2), 2)

    if len(contour) > 1:
        for i in range(len(contour[:-1])):
            x1, y1 = contour[i]
            x2, y2 = contour[i + 1]
            pygame.draw.line(screen, (0, 0, 0), (x1, y1), (x2, y2), 2)
    elif len(contour):
        pygame.draw.circle(screen, (0, 0, 0), contour[0], 2, 2)

    if initial_position:
        pygame.draw.circle(screen, (0, 0, 0), initial_position, ROBOT_SIZE, ROBOT_SIZE)

    if not defining_initial_position:
        render_start = font_start.render('DEFINING CONTOURS', True, (255, 0, 0))
    else:
        render_start = font_start.render('DEFINING LIDAR INITIAL POSITION', True, (255, 0, 0))
    screen.blit(render_start, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if not defining_initial_position:
                    contour.append(pygame.mouse.get_pos())
                else:
                    initial_position = pygame.mouse.get_pos()
            elif event.button == 3:
                if len(contour) > 1:
                    contour.append(contour[0])
                    contours.append(contour)
                    contour = list()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if contours:
                    if initial_position:
                        rooms_names = os.listdir('rooms')

                        if rooms_names:
                            last_room_num = max([int(re.findall(r'room_(\d+)', filename)[0]) for filename in rooms_names])
                        else:
                            last_room_num = 0
                        os.mkdir(f'rooms/room_{last_room_num + 1}')
                        with open(f'rooms/room_{last_room_num+1}/object.pickle', 'wb') as f:
                            pickle.dump(Room(contours, initial_position), f)
                        pygame.image.save(screen, f'rooms/room_{last_room_num+1}/image.png')
                        contours.clear()
                        contour.clear()
                        initial_position = None
                        defining_initial_position = False
                    elif not contour:
                        defining_initial_position = True
