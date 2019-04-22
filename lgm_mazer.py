#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Author: Jo?o S. O. Bueno
#   Copyright: Jo?o 2010 -
#   Created at LibreGraphicsMeeting 2010, Brussels
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pygame, random

FULLSCREEN = False
SIZE  = 1024,720
VSIZE = 64, 47

MAX_THREADS = 50
WIDTH = 5
CHANCE = 0.3
COLOR = (0,0,0)

def flip_coin(chance):
    return random.uniform(0, 1) < chance

def init():
    global SIZE, VSIZE
    pygame.init()
    if FULLSCREEN:
        SIZE = pygame.display.list_modes()[0]
        VSIZE = SIZE[0]/32, SIZE[1]/24
        screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(SIZE)
    return screen

class Point(tuple):
    def __add__(self, other):
        return Point((self[0] + other[0], self[1] + other[1]))
    def __mul__(self, other):
        if hasattr(other, "__len__"):
            return Point((self[0] * other[0], self[1] * other[1]))
        else:
            return Point((self[0] * other, self[1] * other))
    def __hash__(self):
        return 10000 * int(self[0]) + int(self[1])

def builder(x, y, points, color, possible_directions, surface, path=None):
    scale = (SIZE[0] / VSIZE[0], SIZE[1] / VSIZE[1])
    current_point = Point((x,y))
    path = path if path is not None else []
    current_point, direction = builder_new_direction(possible_directions,
                                                     current_point,
                                                     points, path, True)
    can_create = False
    # First yield can't receive values, so 
    # we create a blank yield
    if direction:
        yield
    while direction:
        builder_draw(surface, color, current_point, direction, scale)
        current_point = current_point + direction
        current_point, direction = builder_new_direction(possible_directions,
                                                         current_point,
                                                         points, path, False)
        if current_point and can_create:
            new = current_point[0], current_point[1], path[-20:]
        else:
            new = False
        can_create = yield new

def builder_draw(surface, color, current_point, direction, scale):
        correction = (WIDTH / 2) * direction
        pygame.draw.line(surface, color,  current_point * scale,
                        (current_point + direction) * scale + correction,
                         WIDTH)

def builder_new_direction(possible_directions, current_point, points, path, starting):
    while starting or path:
        starting = False
        directions = list(possible_directions)
        random.shuffle(directions)
        for direction in directions:
            p = current_point + direction  
            if (p not in points) and 0 <= p[0] <= VSIZE[0] and 0 <= p[1] <= VSIZE[1]:
                future = Point(current_point + direction)
                points.add(future)
                path.append(future)
                return current_point, direction
        current_point = path.pop() if path else None
    return None, None

def maze(surface, color, possible_directions):
    name = "Thread %d: " % random.randrange(1000)
    points = set()
    step = SIZE[0] / VSIZE[0]
    threads = set()
    b = builder(random.randrange(VSIZE[0]), 
                random.randrange(VSIZE[1]),
                points, color, possible_directions, surface)
    b.next()
    threads.add(b)
    old = False
    while True:
        to_die = set()
        for thread in list(threads):
            try:
                can_create = (flip_coin(CHANCE) and
                              len(threads) < MAX_THREADS)
                new = thread.send(can_create)
            except StopIteration:
                to_die.add(thread)
            if new:
                try:
                    new_thread = builder(new[0], new[1],
                                         points, color,
                                         possible_directions, surface, new[2])
                    new_thread.next()
                except StopIteration:
                    new = False
            if len(threads) < MAX_THREADS and new:
                threads.add(new_thread)
            if len(threads) > MAX_THREADS * 0.8:
                old = True
        threads.difference_update(to_die)
        if len(threads) < 3 and old:
            break
        yield None


def random_color():
    return tuple(random.randrange(256) for i in range(3))

def fade(surface):
    new_surface = pygame.Surface((surface.get_width(), surface.get_height()))
    new_surface.fill((255,255,255))
    new_surface.set_alpha(128)
    surface.blit(new_surface, (0,0))

orientations = ([Point(p) for p in ((-1,0),(1,0),(0,1),(0,-1))],
                 [Point(p) for p in ((-1,-1),(1,-1),(1,1),(-1,1))])

def main(screen):
    mazes = set ((maze(screen, random_color(), random.choice(orientations)),))
    while True:
        to_die = set()
        for this_maze in mazes:
            try:
                this_maze.next()
            except StopIteration:
                to_die.add(this_maze)
        if flip_coin(CHANCE / 10.0):
            fade(screen)
            m = maze(screen, random_color(), random.choice(orientations))
            mazes.add(m)
        mazes.difference_update(to_die)

        pygame.display.flip()
        pygame.event.pump()
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            raise KeyboardInterrupt
        pygame.time.delay(30)

try:
    screen = init()
    pygame.draw.rect(screen, (255,255,255), screen.get_rect())
    main(screen)
except KeyboardInterrupt:
    pygame.quit()
