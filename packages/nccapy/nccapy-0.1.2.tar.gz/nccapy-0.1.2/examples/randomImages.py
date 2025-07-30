#!/usr/bin/env python
import math
import random

from nccapy import Image


def splat(image, r, g, b, splat_size=10):
    x = random.randint(0, image.width)
    y = random.randint(0, image.height)
    size = image.width + image.height / 10
    for i in range(random.randint(size, size * 2)):
        alpha = 2 * math.pi * random.random()
        radius = splat_size * math.sqrt(random.random())
        rx = int(radius * math.cos(alpha))
        ry = int(radius * math.sin(alpha))
        image.set_pixel(x + rx, y + ry, r, g, b)


def create_images(number=1, width=200, height=200, base_name="test"):
    for i in range(0, number):
        image = Image.Image(width, height)
        # clear to white
        image.clear(255, 255, 255, 255)
        for _ in range(0, 200):
            r = random.randint(10, 255)
            g = random.randint(10, 255)
            b = random.randint(10, 255)
            for _ in range(1, random.randint(1, 30)):
                splat(image, r, g, b, splat_size=random.randint(10, 50))
        print(f"saving {base_name}.{i:04}.png")
        image.save(f"{base_name}.{i:04}.png")


if __name__ == "__main__":
    create_images(10, width=500, height=500)
