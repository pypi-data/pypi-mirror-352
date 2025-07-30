#!/usr/bin/env python

import random

import nccapy


class DLA:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.image = nccapy.Image(width, height)
        self.image.clear(255, 255, 255, 255)

    def random_seed(self) -> None:
        x = random.randint(1, self.width - 1)
        y = random.randint(1, self.height - 1)
        self.image.set_pixel(x, y, 255, 255, 255, 0)

    def save_image(self, filename: str) -> bool:
        return self.image.save(filename)

    def _random_start(self):
        x = random.randint(1, self.width - 2)
        y = random.randint(1, self.height - 2)
        return x, y

    def walk(self) -> bool:
        x, y = self._random_start()
        walking = True
        found = False

        while walking:
            # now move
            x += random.choice([-1, 0, 1])
            y += random.choice([-1, 0, 1])
            # check we are in bounds
            if x < 1 or x >= self.width - 1 or y < 1 or y >= self.width - 1:
                # print(f"hit edge {x} {y}")
                walking = False
                found = False
                break
            # now check if we are near the seed
            else:
                steps = [-1, 0, 1]
                for x_offset in steps:
                    for y_offset in steps:
                        try:
                            r, g, b, a = self.image.get_pixel(
                                x + x_offset, y + y_offset
                            )
                            # print(f"{x} {x+x_offset} {y} {y+y_offset} {a}")
                            if a == 0:
                                self.image.set_pixel(x, y, 255, 0, 0, 255)
                                print(f"Found pixel at {x} {y}")
                                walking = False
                                found = True
                                break
                        except IndexError:
                            print("index error not sure why")
                            walking = False
                            found = False
                            break
        return found


def run_sim(width: int, height: int, num_steps: int, num_seeds: int = 100):
    dla = DLA(width, height)
    for _ in range(0, num_seeds):
        dla.random_seed()

    for _ in range(0, num_steps):
        if dla.walk():
            print("found")
        else:
            print("not found")

    dla.save_image("dla.png")


if __name__ == "__main__":
    run_sim(400, 400, 125000, 200)
