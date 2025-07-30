#!/usr/bin/env python
import random

from nccapy import Canvas


def main():
    width = 800
    height = 800
    with Canvas(width, height) as canvas:
        canvas.set_title("Canvas Test")
        while not canvas.should_quit():
            canvas.clear(255, 255, 255, 255)
            for _ in range(0, 10000):
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                canvas.put_pixel(x, y, r, g, b)
                canvas.put_image(None)
            canvas.update()


if __name__ == "__main__":
    main()
