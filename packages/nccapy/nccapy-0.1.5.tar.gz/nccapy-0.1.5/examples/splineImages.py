#!/usr/bin/env python
import math
import random

import numpy as np

from nccapy.Image import Image


def splat(image, x, y, r, g, b, splat_size=10, flow=10):
    for i in range(random.randint(10, 10 + flow)):
        r_var = random.randint(-25, 25)
        g_var = random.randint(-25, 25)
        b_var = random.randint(-25, 25)

        alpha = 2 * math.pi * random.random()
        radius = splat_size + random.randint(-10, 10) * math.sqrt(random.random())
        rx = int(radius * math.cos(alpha))
        ry = int(radius * math.sin(alpha))
        try:
            image.set_pixel(x + rx, y + ry, r + r_var, g + g_var, b + b_var)
        except:
            pass


def randxy(w, h):
    x = random.randint(0, w)
    y = random.randint(0, h)
    return x, y


def lerp(a, b, t):
    new_x = int(a[0] + (b[0] - a[0]) * t)
    new_y = int(a[1] + (b[1] - a[1]) * t)
    return new_x, new_y


def create_images(number=1, width=200, height=200, base_name="test"):
    splat_size = 10
    for i in range(0, number):
        image = Image(width, height)
        # clear to white
        image.clear(255, 255, 255, 255)
        for _ in range(0, random.randint(100, 2000)):
            r = random.randint(10, 255)
            g = random.randint(10, 255)
            b = random.randint(10, 255)

            spline_points = [
                randxy(width + splat_size, height - splat_size),
                randxy(width + splat_size, height - splat_size),
                randxy(width + splat_size, height - splat_size),
                randxy(width + splat_size, height - splat_size),
            ]
            for t in np.arange(0, 1, random.uniform(0.001, 0.1)):
                l1 = lerp(spline_points[0], spline_points[1], t)
                l2 = lerp(spline_points[1], spline_points[2], t)
                l3 = lerp(spline_points[2], spline_points[3], t)
                l4 = lerp(l1, l2, t)
                l5 = lerp(l2, l3, t)
                x, y = lerp(l4, l5, t)
                splat(
                    image,
                    x,
                    y,
                    r,
                    g,
                    b,
                    splat_size=random.randint(1, splat_size),
                    flow=random.randint(100, 500),
                )
        print(f"saving {base_name}.{i:04}.png")
        image.save(f"{base_name}.{i:04}.png")


if __name__ == "__main__":
    create_images(10, width=500, height=500, base_name="NewSplat")
