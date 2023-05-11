import pygame.gfxdraw
import pickle
import os
from time import time
from geometry import *
import cv2
import matplotlib.pyplot as plt
from configs import *
from copy import copy, deepcopy


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
surface = pygame.Surface((WIDTH, HEIGHT), pygame.GL_ALPHA_SIZE)
clock = pygame.time.Clock()
with open(f"rooms/{os.listdir('rooms')[-1]}/object.pickle", 'rb') as f:
    room = pickle.load(f)
contours = room.contours
initial_position = room.initial_position
theta = np.linspace(0, 2 * np.pi, int(360 / ANGLE_STEP))
x, y = LIDAR_RADIUS * np.cos(theta) + initial_position[0], LIDAR_RADIUS * np.sin(theta) + initial_position[1]
points_lidar = list(zip(x, y))
screen.fill((0, 0, 0))
pygame.image.save(screen, 'last_frame.png')
imp = pygame.image.load('last_frame.png').convert()
initial_sprite = pygame.image.load('sprites/lidar.png')
initial_sprite = pygame.transform.scale(initial_sprite, (ROBOT_SIZE * 2, ROBOT_SIZE * 2))
sprite = copy(initial_sprite)
directions = {'up': True, 'down': False, 'left': False, 'right': False}
frames = list()

while True:
    st = time()

    keys = pygame.key.get_pressed()
    new_position = deepcopy(initial_position)
    new_x, new_y = new_position
    if keys[pygame.K_w]:
        new_x, new_y = new_x, new_y - STEP
        if not directions['up']:
            sprite = pygame.transform.rotate(initial_sprite, 0)
        directions = {'up': True, 'down': False, 'left': False, 'right': False}
    elif keys[pygame.K_s]:
        new_x, new_y = new_x, new_y + STEP
        if not directions['down']:
            sprite = pygame.transform.rotate(initial_sprite, 180)
        directions = {'up': False, 'down': True, 'left': False, 'right': False}
    elif keys[pygame.K_a]:
        new_x, new_y = new_x - STEP, new_y
        if not directions['left']:
            sprite = pygame.transform.rotate(initial_sprite, 90)
        directions = {'up': False, 'down': False, 'left': True, 'right': False}
    elif keys[pygame.K_d]:
        new_x, new_y = new_x + STEP, new_y
        if not directions['right']:
            sprite = pygame.transform.rotate(initial_sprite, 270)
        directions = {'up': False, 'down': False, 'left': False, 'right': True}

    x, y = LIDAR_RADIUS * np.cos(theta) + new_x, LIDAR_RADIUS * np.sin(theta) + new_y
    new_points_lidar = list(zip(x, y))
    intersects = list()

    min_dists = list()
    for p_i in range(len(new_points_lidar)):
        lidar_line = L.from_p(P(*new_points_lidar[p_i]), P(new_x, new_y))
        min_dist = np.inf
        intersection = None
        for c in contours:
            for i in range(len(c[:-1])):
                intersection_global = lidar_line.intersects(L.from_p(P(*c[i]), P(*c[i + 1])))
                dist = distance(intersection_global, P(new_x, new_y))
                if dist <= LIDAR_RADIUS and dist <= min_dist and \
                    min(c[i][0], c[i + 1][0]) <= intersection_global.x < max(c[i][0], c[i + 1][0]) and \
                        min(c[i][1], c[i + 1][1]) <= intersection_global.y < max(c[i][1], c[i + 1][1]):
                    degrees = np.rad2deg(theta[p_i])
                    if (degrees <= 90 and intersection_global.x >= new_x and intersection_global.y >= new_y) or \
                            (90 < degrees <= 180 and intersection_global.x <= new_x and intersection_global.y >= new_y) or \
                            (180 < degrees <= 270 and intersection_global.x <= new_x and intersection_global.y <= new_y) or \
                            (270 < degrees and intersection_global.x >= new_x and intersection_global.y <= new_y):
                        intersection = intersection_global
                        min_dists.append(dist)
                        min_dist = dist
        if intersection:
            intersects.append(intersection)
            new_points_lidar[p_i] = (intersection.x, intersection.y)

    if not min_dists or (min_dists and min(min_dists) >= ROBOT_SIZE):
        if initial_position != (new_x, new_y):
            imp = cv2.imread('last_frame.png')
            for c in intersects:
                cv2.circle(imp, (round(c.x), round(c.y)), radius=1, color=(255, 255, 255), thickness=1)
            cv2.imwrite('last_frame.png', imp)
            imp = pygame.image.load('last_frame.png').convert()
            initial_position = (new_x, new_y)
        points_lidar = new_points_lidar

    screen.blit(imp, (0, 0))

    pygame.gfxdraw.filled_polygon(screen, points_lidar, (255, 255, 0, 123))
    screen.blit(sprite, (initial_position[0] - ROBOT_SIZE, initial_position[1] - ROBOT_SIZE))

    pygame.display.flip()
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if SHOW_FRAMES_DURATION:
                plt.plot(frames)
                plt.plot([0, len(frames)], [1 / FPS, 1 / FPS])
                plt.show()
            exit()

    if SHOW_FRAMES_DURATION:
        frames.append(time() - st)
