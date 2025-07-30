#!/usr/bin/env python

import random

import nccapy


class Found(Exception):
    pass


def _random_start(width, height):
    x = random.randint(2, width - 2)
    y = random.randint(2, height - 2)
    return x, y


def random_seed(canvas):
    x = random.randint(1, canvas.width - 1)
    y = random.randint(1, canvas.height - 1)
    canvas.put_pixel(x, y, 0, 0, 0, 0)


def seed_at(canvas, x, y):
    canvas.put_pixel(x, y, 0, 0, 0, 0)


def _clear_walk_path(canvas):
    # search for red pixels with alpha of 128 and set them back to white
    for x in range(0, canvas.width):
        for y in range(0, canvas.height):
            r, g, b, a = canvas.get_pixel(x, y)
            if r == 255 and g == 0 and b == 0:  # and a == 128 :
                canvas.put_pixel(x, y, 255, 255, 255, 255)


def walk(canvas):
    x, y = _random_start(canvas.width, canvas.height)
    walking = True

    while walking:
        x += random.choice([-1, 0, 1])
        y += random.choice([-1, 0, 1])
        if x < 1 or x >= canvas.width - 1 or y < 1 or y >= canvas.width - 1:
            walking = False
            break
        else:
            to_check = [
                (-1, 1),
                (0, 1),
                (1, 1),
                (-1, 0),
                (1, 0),
                (-1, -1),
                (0, -1),
                (1, -1),
            ]
            for x_offset, y_offset in to_check:
                r, g, b, a = canvas.get_pixel(x + x_offset, y + y_offset)

                if r == 0 and g == 0 and b == 0:
                    canvas.put_pixel(x, y, 0, 0, 0, 255)
                    walking = False
                else:
                    canvas.put_pixel(x + x_offset, y + y_offset, 255, 0, 0, 255)
        canvas.update()

    _clear_walk_path(canvas)


def run_sim(width, height, num_seeds=10):
    canvas = nccapy.Canvas(width, height)
    canvas.clear(255, 255, 255, 255)
    # for _ in range(0,num_seeds):
    #      random_seed(canvas)
    for x in range(0, width, 10):
        seed_at(canvas, x, 50)
    while not canvas.should_quit():
        walk(canvas)
        canvas.update()


if __name__ == "__main__":
    run_sim(200, 200)
