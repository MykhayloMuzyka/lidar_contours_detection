import pygame.gfxdraw
import pickle
import os
from time import time
from geometry import *
import cv2
from configs import *
from copy import copy


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surface = pygame.Surface((WIDTH, HEIGHT), pygame.GL_ALPHA_SIZE)
clock = pygame.time.Clock()
with open(f"rooms/{os.listdir('rooms')[-1]}/object.pickle", 'rb') as f:
    room = pickle.load(f)
contours = room.contours
initial_position = room.initial_position
theta = np.linspace(0, 2 * np.pi, int(360 / ANGLE_STEP))
screen.fill((255, 255, 255))
pygame.image.save(screen, 'last_frame.png')
imp = pygame.image.load('last_frame.png').convert()
initial_sprite = pygame.image.load('sprites/lidar.png')
initial_sprite = pygame.transform.scale(initial_sprite, (ROBOT_SIZE * 2, ROBOT_SIZE * 2))
sprite = copy(initial_sprite)
directions = {'up': True, 'down': False, 'left': False, 'right': False}

while True:
    st = time()
    x, y = LIDAR_RADIUS * np.cos(theta) + initial_position[0], LIDAR_RADIUS * np.sin(theta) + initial_position[1]
    points_lidar = list(zip(x, y))
    intersects = list()
    for p_i in range(len(points_lidar)):
        lidar_line = L.from_p(P(*points_lidar[p_i]), P(*initial_position))
        min_dist = np.inf
        intersection = None
        for c in contours:
            for i in range(len(c[:-1])):
                intersection_global = lidar_line.intersects(L.from_p(P(*c[i]), P(*c[i + 1])))
                dist = distance(intersection_global, P(*initial_position))
                # if np.rad2deg(theta[p_i]) == 0:
                #     print(intersection_global, P(*initial_position), dist)
                if dist <= LIDAR_RADIUS and dist <= min_dist and \
                    min(c[i][0], c[i + 1][0]) <= intersection_global.x < max(c[i][0], c[i + 1][0]) and \
                        min(c[i][1], c[i + 1][1]) <= intersection_global.y < max(c[i][1], c[i + 1][1]):
                    degrees = np.rad2deg(theta[p_i])
                    if (degrees <= 90 and intersection_global.x >= initial_position[0] and intersection_global.y >= initial_position[1]) or \
                            (90 <= degrees <= 180 and intersection_global.x <= initial_position[0] and intersection_global.y >= initial_position[1]) or \
                            (180 <= degrees <= 270 and intersection_global.x <= initial_position[0] and intersection_global.y <= initial_position[1]) or \
                            (270 <= degrees and intersection_global.x >= initial_position[0] and intersection_global.y <= initial_position[1]):
                        intersection = intersection_global
                        min_dist = dist
        if intersection:
            intersects.append(intersection)
            points_lidar[p_i] = (intersection.x, intersection.y)

    # contours points
    imp = cv2.imread('last_frame.png')
    for c in intersects:
        cv2.circle(imp, (round(c.x), round(c.y)), radius=1, color=(0, 0, 0), thickness=1)
    cv2.imwrite('last_frame.png', imp)
    imp = pygame.image.load('last_frame.png').convert()

    screen.blit(imp, (0, 0))

    pygame.gfxdraw.filled_polygon(screen, points_lidar, (255, 255, 0, 123))
    screen.blit(sprite, (initial_position[0] - ROBOT_SIZE, initial_position[1] - ROBOT_SIZE))
    pygame.gfxdraw.polygon(screen, contours[1], (255, 255, 255))

    pygame.display.flip()

    keys = pygame.key.get_pressed()
    x, y = initial_position
    if keys[pygame.K_w]:
        initial_position = (x, y - 4)
        if not directions['down']:
            sprite = pygame.transform.rotate(initial_sprite, 0)
        directions = {'up': True, 'down': False, 'left': False, 'right': False}
    elif keys[pygame.K_s]:
        initial_position = (x, y + 4)
        if not directions['down']:
            sprite = pygame.transform.rotate(initial_sprite, 180)
        directions = {'up': False, 'down': True, 'left': False, 'right': False}
    elif keys[pygame.K_a]:
        initial_position = (x - 4, y)
        if not directions['down']:
            sprite = pygame.transform.rotate(initial_sprite, 90)
        directions = {'up': False, 'down': False, 'left': True, 'right': False}
    elif keys[pygame.K_d]:
        initial_position = (x + 4, y)
        if not directions['down']:
            sprite = pygame.transform.rotate(initial_sprite, 270)
        directions = {'up': False, 'down': False, 'left': False, 'right': True}

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

    print(time() - st)
